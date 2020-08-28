import math
import numpy as np
import mxnet as mx
import pickle as pkl
from tqdm import tqdm
import autogluon as ag
import multiprocessing
import mxnet.ndarray as F
import matplotlib.pyplot as plt

from frontend_python.output import GraphvizVisualization
from model_evaluation import ModelEvaluator


class RLScheduler(ag.scheduler.RLScheduler):
    def __init__(self, train_fn, data, search_space, verified_proportion, **kwargs):
        super().__init__(train_fn, **kwargs)

        self.data = data
        self.search_space = search_space
        self.verified_proportion = verified_proportion

    def get_topk_config(self, k):
        """Returns top k configurations found so far.
        """
        with self.LOCK:
            if self.searcher.results:
                topk_configs = list()
                for config_pkl, reward in sorted(self.searcher.results.items(), key=lambda item: -item[1]):
                    topk_configs.append(pkl.loads(config_pkl))
                    if len(topk_configs) >= k:
                        break
                return topk_configs
            else:
                return list()

    @staticmethod
    def _verify(config, data):
        sem_indexes = ModelEvaluator.evaluate_with_sem(config, data)
        return sem_indexes

    def _sample(self, sample_size):
        configs_batch, log_probs_batch, _ = self.controller.sample(sample_size, with_details=True)
        configs_dict = map(self.search_space.gluon2dict, configs_batch)

        p = multiprocessing.Pool(multiprocessing.cpu_count())
        test_results = p.starmap(RLScheduler._verify, zip(configs_dict, [self.data for _ in range(sample_size)]))

        return configs_batch, log_probs_batch, test_results

    def _sample_verified(self, batch_size, verified_proportion=1.0):
        assert 0.0 <= verified_proportion <= 1.0

        configs, log_probs, indexes = [], [], []

        sample_size = batch_size
        while True:
            configs_batch, log_probs_batch, test_results = self._sample(sample_size)

            for idx, result in enumerate(test_results):
                if result is not None:
                    configs.append(configs_batch[idx])
                    log_probs.append(log_probs_batch[idx])
                    indexes.append(result)

                if len(configs) >= batch_size * verified_proportion:
                    unverified_sample_size = math.floor((1.0 - verified_proportion) * batch_size)
                    if unverified_sample_size >= 1:
                        configs_unverified, log_probs_unverified, results_unverified = self._sample(
                            unverified_sample_size)
                        configs.extend(configs_unverified)
                        log_probs.extend(log_probs_unverified)
                        indexes.extend(results_unverified)

                    return configs, F.stack(*log_probs), indexes

            sample_size *= 2
            print("%d calculating %d\n" % (len(configs), sample_size))

    def _run_sync(self):
        decay = self.ema_baseline_decay
        for i in tqdm(range(self.num_trials // self.controller_batch_size + 1)):
            with mx.autograd.record():
                # sample controller_batch_size number of configurations
                batch_size = self.num_trials % self.num_trials \
                    if i == self.num_trials // self.controller_batch_size \
                    else self.controller_batch_size
                if batch_size == 0:
                    continue
                configs, log_probs, indexes = self._sample_verified(batch_size, self.verified_proportion)
                # schedule the training tasks and gather the reward
                rewards = self.sync_schedule_tasks(configs)
                print(rewards)
                # substract baseline
                if self.baseline is None:
                    self.baseline = rewards[0]
                avg_rewards = mx.nd.array([reward - self.baseline for reward in rewards], ctx=self.controller.context)
                # EMA baseline
                for reward in rewards:
                    self.baseline = decay * self.baseline + (1 - decay) * reward
                # negative policy gradient
                log_probs = log_probs.sum(axis=1)
                loss = - log_probs * avg_rewards  # .reshape(-1, 1)
                loss = loss.sum()  # or loss.mean()

            # update
            loss.backward()
            self.controller_optimizer.step(batch_size)


class ModelSearcher:

    def __init__(self, search_space, model_evaluator, data, args=None):
        space = search_space.fetch()

        @ag.args(**space)
        def evaluate_callback(config, reporter):
            model = search_space.gluon2dict(config)
            reward = model_evaluator.evaluate(model, data)
            reporter(reward=reward)

        self.searcher = RLScheduler(evaluate_callback, data, search_space, 0.7,
                                    args=args,
                                    resource={'num_cpus': 1, 'num_gpus': 0},
                                    num_trials=500,
                                    reward_attr='reward',
                                    controller_batch_size=5,
                                    controller_lr=1e-3)

        self.evaluator = model_evaluator
        self.searchSpace = search_space
        self.data = data

    def search(self, verbose=False):
        # Running this function might crash Python.
        # This problem is caused by the multiprocessing of the RL algorithm and lavaan in R.
        # But the numeric part has been take care of, so the result is not corrupted.
        self.searcher.run()
        self.searcher.join_jobs()

        if verbose:
            print('Best config: {}, best reward: {}'.format(self.searcher.get_best_config(),
                                                            self.searcher.get_best_reward()))

    def print_topk_solution(self, k, graphviz=False):
        args = self.searcher.get_topk_config(k)

        if graphviz:
            models = [self.searchSpace.gluon2dict(arg) for arg in args]
            vis = GraphvizVisualization(models, self.evaluator.variable_descriptions)
            vis.show()
        else:
            for rank, arg in enumerate(args):
                model = self.searchSpace.gluon2dict(arg)
                model_lavaan = self.evaluator.dict2lavaan(model)
                print('The %dth good model looks like:\n%s' % (rank, model_lavaan))

                reward = self.evaluator.evaluate(model, self.data)
                print('The reward is: %f' % reward)

    def print_best_solution(self, graphviz=False):
        self.print_topk_solution(1, graphviz)

    def plot_learning_curve(self):
        learning_curve = [v[0]['reward'] for v in self.searcher.training_history.values()]
        curve_smoothed = [np.max(learning_curve[i:i + 5]) for i in range(0, len(learning_curve), 5)]

        plt.plot(range(len(curve_smoothed)), curve_smoothed)
        plt.show()
