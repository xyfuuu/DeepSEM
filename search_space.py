import autogluon as ag


class SearchSpace:

    def __init__(self, factor_names, variable_names):
        self.factorNames = factor_names
        self.variableNames = variable_names

        self.factorCount = len(factor_names)
        self.variableCount = len(variable_names)

        self.space = _generate_search_space()

    def _generate_search_space(self):
        # Define search space for measurement model
        search_space = {var: ag.space.Categorical(*self.factorNames)
                        for var in self.variableNames}

        # Define search space for regressions model
        for i in range(self.factorCount):
            for j in range(i):
                searchSpace[str((self.factorNames[i], self.factorNames[j]))] = ag.space.Categorical(*list(range(3)))

        return search_space
