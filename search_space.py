import autogluon as ag


class SearchSpace:

    def __init__(self, factor_names, variable_names):
        self.factorNames = factor_names
        self.variableNames = variable_names

        self.factorCount = len(factor_names)
        self.variableCount = len(variable_names)

        self.space = self._generate_search_space(factor_names, len(factor_names), variable_names)

    # Define search space using AutoGluon syntax.
    # See more of the syntax at: https://autogluon.mxnet.io/api/autogluon.space.html
    @staticmethod
    def _generate_search_space(factor_names, factor_count, variable_names):
        # Define search space for measurement model
        search_space = {var: ag.space.Categorical(*factor_names)
                        for var in variable_names}

        # Define search space for regressions model
        for i in range(factor_count):
            for j in range(i):
                search_space[str((factor_names[i], factor_names[j]))] = ag.space.Categorical(*list(range(3)))

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
    def gluon2lavaan(self, args):
        measurement_dict = {fac: [] for fac in self.factorNames}
        regressions_dict = {fac: [] for fac in self.factorNames}

        for var, choice in args.items():
            if '▁' in var:
                var = var.split('▁')[0]
            elif var == 'task_id':
                continue

            if var[0] != '(':  # measurement
                # This if is added because the special format of get_best_config() in AutoGlugon.
                if isinstance(choice, int):
                    measurement_dict[self.factorNames[choice]].append(var)
                else:
                    measurement_dict[choice].append(var)
            else:  # regressions
                var_tuple = eval(var)
                if choice == 1:
                    regressions_dict[var_tuple[0]].append(var_tuple[1])
                elif choice == 2:
                    regressions_dict[var_tuple[1]].append(var_tuple[0])

        model_lavaan = self._dict2lavaan(measurement_dict, '=~') + self._dict2lavaan(regressions_dict, '~')

        return model_lavaan

    def fetch(self):
        return self.space
