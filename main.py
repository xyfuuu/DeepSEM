import pandas as pd
import autogluon as ag
import rpy2.rinterface_lib as rlib

from search_space import SearchSpace
from model_evaluation import ModelEvaluator
from search_strategy import ModelSearcher

if __name__ == '__main__':
    # Redirect the R console.
    def logErrorMsg(s):
        pass
    rlib.callbacks.consolewrite_warnerror = logErrorMsg

    # Learn more about this dataset at: https://rdrr.io/cran/lavaan/man/PoliticalDemocracy.html
    data = pd.read_csv('data/political_democracy.csv')

    factorNames = ['factor1', 'factor2', 'factor3']
    variableNames = data.columns
    search_space = SearchSpace(factorNames, variableNames)

    variableDescription = {
        'y1': 'Expert ratings of the freedom of the press in 1960',
        'y2': 'The freedom of political opposition in 1960',
        'y3': 'The fairness of elections in 1960',
        'y4': 'The effectiveness of the elected legislature in 1960',
        'y5': 'Expert ratings of the freedom of the press in 1965',
        'y6': 'The freedom of political opposition in 1965',
        'y7': 'The fairness of elections in 1965',
        'y8': 'The effectiveness of the elected legislature in 1965',
        'x1': 'The gross national product (GNP) per capita in 1960',
        'x2': 'The inanimate energy consumption per capita in 1960',
        'x3': 'The percentage of the labor force in industry in 1960'
    }
    model_evaluator = ModelEvaluator(variableDescription)

    rl_searcher = ModelSearcher(search_space, model_evaluator, data)

    rl_searcher.search(verbose=True)

    rl_searcher.print_best_solution()

    rl_searcher.plot_learning_curve()
