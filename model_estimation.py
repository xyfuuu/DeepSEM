import logging
import numpy as np

from SEM import SemModel


class ModelEvaluator:

    @staticmethod
    def _evaluate_with_SEM(model, data):
        sem = SemModel()

        try:
            if_built = sem.build_sem_model(model)
            if not if_built:
                return False, {}

            if_fit = sem.fit_sem_model(data)
            if not if_fit['is_fitted']:
                return False, {}

            measure_indexes = sem.evaluate_sem_model()
            if not measure_indexes['is_evaluated']:
                return False, {}

            return True, measure_indexes
        except Exception:
            logging.error(Exception)

            return False, {}

    @staticmethod
    def evaluate(model, data):
        if_evaluation_success, indexes = ModelEvaluator._evaluate_with_SEM(model, data)

        if not if_evaluation_success:
            return 0

        AGFI = indexes['agfi']
        RMSEA = indexes['rmsea']

        index = AGFI - RMSEA * 10
        index = 1 / (1 + np.exp(-index))

        return index
