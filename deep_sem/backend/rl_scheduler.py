import math
import mxnet as mx
import pickle as pkl
from tqdm import tqdm
import autogluon as ag
import mxnet.ndarray as F
import multiprocessing as mp
from PyQt5.QtCore import QThread, pyqtSignal

from .model_evaluation import ModelEvaluator


class RLScheduler(ag.scheduler.RLScheduler, QThread):
    sinOut = pyqtSignal(int)

    def __init__(self, train_fn, data, search_space, verified_proportion, **kwargs):
        ag.scheduler.RLScheduler.__init__(self, train_fn, **kwargs)
        QThread.__init__(self)
        self.working = True
        self.num = 0

        self.results = dict()
        self.data = data
        self.search_space = search_space
        self.verified_proportion = verified_proportion

    def get_topk_config(self, k):
        """Returns top k configurations found so far.
        """
        if self.results:
            topk_configs = list()
            for config_pkl, reward in sorted(self.results.items(), key=lambda item: -item[1]):
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

        p = mp.Pool(mp.cpu_count())
        test_results = p.starmap(RLScheduler._verify, zip(configs_dict, [self.data for _ in range(sample_size)]))

        for config, index in zip(configs_batch, test_results):
            config['indexes'] = index

        return configs_batch, log_probs_batch

    def _sample_verified(self, batch_size, verified_proportion=1.0):
        assert 0.0 <= verified_proportion <= 1.0

        configs, log_probs = [], []

        sample_size = batch_size
        while True:
            configs_batch, log_probs_batch = self._sample(sample_size)

            for idx, config in enumerate(configs_batch):
                if config['indexes'] is not None:
                    configs.append(configs_batch[idx])
                    log_probs.append(log_probs_batch[idx])

                if len(configs) >= batch_size * verified_proportion:
                    unverified_sample_size = math.floor((1.0 - verified_proportion) * batch_size)
                    if unverified_sample_size >= 1:
                        configs_unverified, log_probs_unverified = self._sample(unverified_sample_size)
                        configs.extend(configs_unverified)
                        log_probs.extend(log_probs_unverified)
                    return configs, F.stack(*log_probs),

            sample_size *= 2
            print("%d calculating %d\n" % (len(configs), sample_size))

    def _run_sync(self):
        decay = self.ema_baseline_decay
        for i in tqdm(range(self.num_trials // self.controller_batch_size + 1)):
            with mx.autograd.record():
                # sample controller_batch_size number of configurations
                self.sinOut.emit(i * 100 // (self.num_trials // self.controller_batch_size + 1))
                batch_size = self.num_trials % self.num_trials \
                    if i == self.num_trials // self.controller_batch_size \
                    else self.controller_batch_size
                if batch_size == 0:
                    continue
                configs, log_probs = self._sample_verified(batch_size, self.verified_proportion)
                # schedule the training tasks and gather the reward
                # rewards = self.sync_schedule_tasks(configs)
                rewards = list(map(self.train_fn, configs))
                for config, reward in zip(configs, rewards):
                    self.results[pkl.dumps(config)] = reward
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
