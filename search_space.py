import autogluon as ag


class SearchSpace:

    def __init__(self, factor_names, variable_names):
        self.factorNames = factor_names
        self.variableNames = variable_names

        self.factorCount = len(factor_names)
        self.variableCount = len(variable_names)

        self.space = _generate_search_space()

    # Define search space using AutoGluon syntax.
    # See more of the syntax at: https://autogluon.mxnet.io/api/autogluon.space.html
    def _generate_search_space(self):
        # Define search space for measurement model
        search_space = {var: ag.space.Categorical(*self.factorNames)
                        for var in self.variableNames}

        # Define search space for regressions model
        for i in range(self.factorCount):
            for j in range(i):
                searchSpace[str((self.factorNames[i], self.factorNames[j]))] = ag.space.Categorical(*list(range(3)))

        return search_space

    # This is a helper function to convert model in python dictionary format to lavaan string format.
    # To understand this function, you need to understand lavaan syntax and the function `gluon2lavaan`.
    @staticmethod
    def _dict2lavaan(data_dict, separator):
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

    # This function convert a model sampled from the search space in AutoGluon format to lavaan format.
    # This function is useful when you wanna evaluated the sampled model using the conventional SEM method.
    @staticmethod
    def gluon2lavaan(args):
        measurement_dict = {fac: [] for fac in facNames}
        regressions_dict = {fac: [] for fac in facNames}

        for var, choice in args.items():
            if var == 'task_id':
                continue
            elif var[0] != '(':  # measurement
                measurement_dict[choice].append(var)
            else:  # regressions
                var_tuple = eval(var)
                if choice == 1:
                    regressions_dict[var_tuple[0]].append(var_tuple[1])
                elif choice == 2:
                    regressions_dict[var_tuple[1]].append(var_tuple[0])

        # Prior knowledge from SEM: factors usually have more than 2 indicators.
        for fac, ind in measurement_dict.items():
            if len(ind) < 2:
                reporter(reward=0)
                return

        model_lavaan = _dict2lavaan(measurementDict, '=~') + _dict2lavaan(regressionsDict, '~')

        return model_lavaan

    def fetch(self):
        return self.space
