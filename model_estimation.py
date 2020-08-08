from SEM import SemModel


class ModelEvaluation:

    def __init__(self):
        self.sem = SemModel()

    def evaluate(self, model):
        try:
            buildRes = sem.build_sem_model(model)
            if not buildRes:
                return 0

            fitRes = sem.fit_sem_model(data)
            if not fitRes['is_fitted']:
                return 0

            measureRes = sem.evaluate_sem_model()
            if not measureRes['is_evaluated']:
                return 0

            AGFI = measureRes['agfi']
            RMSEA = measureRes['rmsea']
            index = AGFI - RMSEA * 10
            sigmoidIndex = 1 / (1 + np.exp(-index))
            return sigmoidIndex
        except:
            return 0
