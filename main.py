import autogluon as ag
import pandas as pd

from search_space import SearchSpace
from model_evaluation import ModelEvaluator
from search_strategy import ModelSearcher

if __name__ == '__main__':
    # Learn more about this dataset at: https://rdrr.io/cran/lavaan/man/PoliticalDemocracy.html
    data = pd.read_csv('data/political_democracy.csv')

    factorNames = ['factor1', 'factor2', 'factor3']
    variableNames = data.columns
    search_space = SearchSpace(factorNames, variableNames)

    model_evaluator = ModelEvaluator(variableNames)

    rl_searcher = ModelSearcher(search_space, model_evaluator, data)

    rl_searcher.search(verbose=True)

    rl_searcher.print_best_solution()

    rl_searcher.plot_learning_curve()
