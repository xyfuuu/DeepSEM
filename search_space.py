import autogluon as ag


class SearchSpace:

    def __init__(self, factor_names, variable_names, model_fixed=None):
        self.factorNames = factor_names
        self.variableNames = variable_names
        self.model_fixed = model_fixed
        self.choice2name = {var: factor_names for var in variable_names}

        self.factorCount = len(factor_names)
        self.variableCount = len(variable_names)

        self.space = self._generate_search_space()

    # Define search space using AutoGluon syntax.
    # See more of the syntax at: https://autogluon.mxnet.io/api/autogluon.space.html
    def _generate_search_space(self):
        # Define search space for measurement model
        search_space = {var: ag.space.Categorical(*self.factorNames) for var in self.variableNames}

        # Define search space for regressions model
        for i in range(self.factorCount):
            for j in range(i):
                # 3 means ignoring covariance choices
                search_space[str((self.factorNames[i], self.factorNames[j]))] = ag.space.Categorical(*list(range(3)))

        if self.model_fixed is not None and 'measurement_dict' in self.model_fixed.keys():
            measurement_model = self.model_fixed['measurement_dict']
            for factor, variables in measurement_model.items():
                for variable in variables:
                    search_space[variable] = ag.space.Categorical(*[factor])
                    self.choice2name[variable] = [factor]

        return search_space

    # This function convert a model sampled from the search space in AutoGluon format to lavaan format.
    # This function is useful when you wanna evaluated the sampled model using the conventional SEM method.
    def gluon2dict(self, args):
        if 'measurement_dict' in args.keys():
            return args

        measurement_dict = {fac: [] for fac in self.factorNames}
        regressions_dict = {fac: [] for fac in self.factorNames}
        covariance_dict = {fac: [] for fac in self.factorNames}

        for var, choice in args.items():
            if '▁' in var:
                var = var.split('▁')[0]
            elif var == 'task_id':
                continue

            if var[0] != '(':  # measurement
                # This if is added because the special format of get_best_config() in AutoGlugon.
                if isinstance(choice, int):
                    measurement_dict[self.choice2name[var][choice]].append(var)
                else:
                    measurement_dict[choice].append(var)
            else:  # regressions
                var_tuple = eval(var)
                if choice == 1:
                    regressions_dict[var_tuple[0]].append(var_tuple[1])
                elif choice == 2:
                    regressions_dict[var_tuple[1]].append(var_tuple[0])
                elif choice == 3:
                    covariance_dict[var_tuple[0]].append(var_tuple[1])

        model_compressed = {'measurement_dict': measurement_dict,
                            'regressions_dict': regressions_dict,
                            'covariance_dict': covariance_dict}

        return model_compressed

    def fetch(self):
        return self.space
