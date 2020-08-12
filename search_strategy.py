import numpy as np
import autogluon as ag
import matplotlib.pyplot as plt

from SEM import SemModel
from search_space import SearchSpace


class ModelSearcher:

    def __init__(self, search_space, model_evaluator, data):
        space = search_space.fetch()

        @ag.args(**space)
        def evaluate_callback(args, reporter):
            model = search_space.gluon2dict(args)
            reward = model_evaluator.evaluate(model, data)
            reporter(reward=reward)

        self.searcher = ag.scheduler.RLScheduler(evaluate_callback,
                                                 resource={'num_cpus': 1, 'num_gpus': 0},
                                                 num_trials=200,
                                                 reward_attr='reward',
                                                 controller_batch_size=4,
                                                 controller_lr=5e-3, )

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

    def print_best_solution(self):
        args = self.searcher.get_best_config()

        model = self.searchSpace.gluon2dict(args)
        model_lavaan = self.evaluator.dict2lavaan(model)
        print('The best model looks like:\n' + model_lavaan)

        reward = self.evaluator.evaluate(model, self.data)
        print('The reward is: %f' % reward)

    def plot_learning_curve(self):
        learning_curve = [v[0]['reward'] for v in self.searcher.training_history.values()]
        curve_smoothed = [np.max(learning_curve[i:i + 5]) for i in range(0, len(learning_curve), 5)]

        plt.plot(range(len(curve_smoothed)), curve_smoothed)
        plt.show()
