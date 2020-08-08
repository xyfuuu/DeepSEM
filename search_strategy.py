import autogluon as ag

from SEM import SemModel
from search_space import SearchSpace


class ModelSearcher:

    def __init__(self, search_space, model_evaluator):
        space = search_space.fetch()

        @ag.args(**space)
        def evaluate_callback(args, reporter):
            model = SearchSpace.gluon2lavaan(args)
            reward = model_evaluator.evaluate(model)
            reporter(reward=reward)

        # Running this function might crash Python.
        # This problem is caused by the multiprocessing of the RL algorithm and lavaan in R.
        # But the numeric part has been take care of, so the result is not corrupted.
        self.searcher = ag.scheduler.RLScheduler(evaluate_callback,
                                                 resource={'num_cpus': 1, 'num_gpus': 0},
                                                 num_trials=200,
                                                 reward_attr='reward',
                                                 controller_batch_size=4,
                                                 controller_lr=5e-3, )

        self.evaluator = model_evaluator

    def search(self, verbose=False):
        self.searcher.run()
        self.searcher.join_jobs()

        if verbose:
            print('Best config: {}, best reward: {}'.format(self.searcher.get_best_config(),
                                                            self.searcher.get_best_reward()))

    def print_best_solution(self):
        args = self.searcher.get_best_config()

        model = SearchSpace.gluon2lavaan(args)
        print('The best model looks like:\n' + model)

        reward = self.evaluator.evaluate(model)
        print('The reward is: %f' % reward)
