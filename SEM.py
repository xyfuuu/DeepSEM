import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects import r, pandas2ri
import time

CREATE_MODEL_STMT_EXAMPLE = '''
    # measurement model
    eta_1  =~ y1 + l2*y2 + l3*y3 + l4*y4
    eta_2  =~ y5 + l2*y6 + l3*y7 + l4*y8
    xi_1   =~ x1 + x2 + x3
    # regressions
    eta_1 ~ xi_1
    eta_2 ~ eta_1 + xi_1
    # residual correlations
    y1 ~~ y5
    y2 ~~ y4 + y6
    y3 ~~ y7
    y4 ~~ y8
    y6 ~~ y8
'''


class SemModel:

    def __init__(self):
        importr('lavaan')
        robjects.r('fit_sem <- function(data){fit <<- sem(model, data)}')
        robjects.r('evaluate_sem<-function(){res<<-fitMeasures(fit)}')

    # This function uses 'create_model_stmt' to create model.
    # Please format the 'create_model_stmt' as the example above.
    @staticmethod
    def build_sem_model(create_model_stmt):
        create_model_stmt = 'model <- \'{}\''.format(create_model_stmt)
        try:
            robjects.r(create_model_stmt)
        except:
            print('Error in build_sem_model function.')
            return False
        else:
            return True

    # TODO: Add more parameter options.
    # Input 'data' can be either pandas dataframe or R dataframe.
    @staticmethod
    def fit_sem_model(data):
        start_time = time.time()
        try:
            pandas2ri.activate()
            robjects.r['fit_sem'](data)
            pandas2ri.deactivate()
        except:
            print('Error in fit_sem_model function.')
            return {'is_fitted': False}
        end_time = time.time()
        return {'is_fitted': True, 'training_time': end_time - start_time}

    @staticmethod
    def evaluate_sem_model():
        try:
            robjects.r['evaluate_sem']()
            fit_measure_res = robjects.r['res']
        except:
            print('Error in evaluate_sem_model function.')
            return {'is_evaluated': False}
        agfi = tuple(fit_measure_res.rx('agfi'))[0]
        rmsea = tuple(fit_measure_res.rx('rmsea'))[0]
        return {'is_evaluated': True, 'agfi': agfi, 'rmsea': rmsea}


if __name__ == '__main__':
    sem = SemModel()
    data = robjects.r('PoliticalDemocracy')

    build_res = sem.build_sem_model(CREATE_MODEL_STMT_EXAMPLE)
    fit_res = sem.fit_sem_model(data)
    fit_measure_res = sem.evaluate_sem_model()
    print(fit_measure_res)
