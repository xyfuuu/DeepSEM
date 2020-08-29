import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects import r, pandas2ri
from rpy2.robjects.vectors import ListVector
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
        self.lavaan = importr('lavaan')
        self.base = importr('base')

    # TODO: Add more parameter options.
    # Input 'data' can be either pandas dataframe or R dataframe.
    def fit_sem_model(self, stmt, data):
        with robjects.conversion.localconverter(robjects.default_converter + robjects.pandas2ri.converter):
            rdata = robjects.conversion.py2rpy(data)
        start_time = time.time()
        try:
            self.fit = self.base.do_call("sem", ListVector({'model': stmt, 'data': rdata}))
        except:
            print('Error in fit_sem_model function.')
            return {'is_fitted': False}
        end_time = time.time()
        return {'is_fitted': True, 'training_time': end_time - start_time}

    def evaluate_sem_model(self):
        try:
            fit_measure_res = self.base.do_call("fitMeasures", ListVector({'object': self.fit}))
        except:
            print('Error in evaluate_sem_model function.')
            return {'is_evaluated': False}

        # See available indexes at: https://rdrr.io/cran/lavaan/man/fitMeasures.html
        agfi = tuple(fit_measure_res.rx('agfi'))[0]
        rmsea = tuple(fit_measure_res.rx('rmsea'))[0]
        pvalue = tuple(fit_measure_res.rx('pvalue'))[0]
        nfi = tuple(fit_measure_res.rx('nfi'))[0]
        cfi = tuple(fit_measure_res.rx('cfi'))[0]
        rfi = tuple(fit_measure_res.rx('rfi'))[0]
        pgfi = tuple(fit_measure_res.rx('pgfi'))[0]

        return {'is_evaluated': True,
                'agfi': agfi,
                'rmsea': rmsea,
                'pvalue': pvalue,
                'nfi': nfi,
                'cfi': cfi,
                'rfi': rfi,
                'pgfi': pgfi}


if __name__ == '__main__':
    sem = SemModel()
    rData = robjects.r('PoliticalDemocracy')

    with robjects.conversion.localconverter(robjects.default_converter + robjects.pandas2ri.converter):
        data = robjects.conversion.rpy2py(rData)

    fit_res = sem.fit_sem_model(CREATE_MODEL_STMT_EXAMPLE, data)
    fit_measure_res = sem.evaluate_sem_model()
    print(fit_measure_res)
