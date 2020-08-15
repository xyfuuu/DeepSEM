import autogluon as ag
import rpy2.robjects as ro
import rpy2.rinterface_lib as rlib

from search_space import SearchSpace
from model_evaluation import ModelEvaluator
from search_strategy import ModelSearcher

if __name__ == '__main__':
    # Redirect the R console.
    def logErrorMsg(s):
        pass
    rlib.callbacks.consolewrite_warnerror = logErrorMsg
    
    # Load this dataset in R.
    ro.packages.importr('lavaan')
    rData = ro.r('PoliticalDemocracy')

    # Convert it to Python Dataframe.
    with ro.conversion.localconverter(ro.default_converter + ro.pandas2ri.converter):
        data = ro.conversion.rpy2py(rData)

    factorNames = ['factor1', 'factor2', 'factor3']
    variableNames = data.columns
    search_space = SearchSpace(factorNames, variableNames)

    model_evaluator = ModelEvaluator()

    rl_searcher = ModelSearcher(search_space, model_evaluator, data)

    rl_searcher.search(verbose=True)

    rl_searcher.print_best_solution()

    rl_searcher.plot_learning_curve()
