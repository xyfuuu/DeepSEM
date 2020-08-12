import logging
import numpy as np
from sentence_transformers import SentenceTransformer

from SEM import SemModel


class ModelEvaluator:

    def __init__(self, variable_names):
        model = SentenceTransformer('distiluse-base-multilingual-cased')
        self.variable_embedded = model.encode(variable_names)

    @staticmethod
    def _evaluate_with_sem(model, data):
        model = ModelEvaluator.dict2lavaan(model)
        sem = SemModel()

        try:
            if_built = sem.build_sem_model(model)
            if not if_built:
                return None

            if_fit = sem.fit_sem_model(data)
            if not if_fit['is_fitted']:
                return None

            measure_indexes = sem.evaluate_sem_model()
            if not measure_indexes['is_evaluated']:
                return None

            return measure_indexes
        except Exception:
            logging.error(Exception)

            return None

    # This is a helper function to convert model in python dictionary format to lavaan string format.
    # Before modifying, you need to understand lavaan syntax and the function `gluon2dict` in `search_space.py`.
    @staticmethod
    def _dict2str(data_dict, separator):
        data_lavaan = ''
        for parent in data_dict.keys():
            if not data_dict[parent]:
                continue

            related_nodes = ''
            for son in data_dict[parent]:
                if not related_nodes:
                    related_nodes += son
                else:
                    related_nodes += ' + ' + son

            data_lavaan += parent + ' ' + separator + ' ' + related_nodes + '\n'

        return data_lavaan

    @staticmethod
    def dict2lavaan(model):
        measurement_dict = model['measurement_dict']
        regressions_dict = model['regressions_dict']
        covariance_dict = model['covariance_dict']

        model_lavaan = ModelEvaluator._dict2str(measurement_dict, '=~') + \
                       ModelEvaluator._dict2str(regressions_dict, '~') + \
                       ModelEvaluator._dict2str(covariance_dict, '~~')

        return model_lavaan

    def evaluate(self, model, data):
        sem_indexes = ModelEvaluator._evaluate_with_sem(model, data)

        if sem_indexes is None:
            return 0

        agfi = sem_indexes['agfi']
        rmsea = sem_indexes['rmsea']

        index = agfi - rmsea * 10
        index = 1 / (1 + np.exp(-index))

        return index
