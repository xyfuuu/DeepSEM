import logging

from SEM import SemModel


class ModelEvaluator:

    def __init__(self):
        self.sem = SemModel()

    def _evaluate_with_SEM(self, model):
        try:
            if_built = self.sem.build_sem_model(model)
            if not if_built:
                return False, _

            if_fit = self.sem.fit_sem_model(data)
            if not if_fit['is_fitted']:
                return False, _

            measure_indexes = self.sem.evaluate_sem_model()
            if not measure_indexes['is_evaluated']:
                return False, _

            return True, measure_indexes
        except Exception:
            logging.error(Exception)

            return False, _

    @staticmethod
    def evaluate(model):
        if_evaluation_success, indexes = _evaluate_with_SEM(model)

        if not if_evaluation_success:
            return 0

        AGFI = indexes['agfi']
        RMSEA = indexes['rmsea']

        index = AGFI - RMSEA * 10
        index = 1 / (1 + np.exp(-index))

        return index
