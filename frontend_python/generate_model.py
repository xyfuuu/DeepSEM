from diagram_items import Arrow, DoubleArrow, DiagramTextItem, DiagramItem


class generateModel():
    observed_list = list()
    observed_dict = dict()
    observed_cnt = 0
    latent_list = list()
    latent_dict = dict()
    latent_cnt = 0
    factorType = dict()
    measurement_dict = dict()
    regressions_dict = dict()
    covariance_dict = dict()

    def __init__(self):
        super(generateModel, self).__init__()

    def addFactor(self, item, itemType):
        self.factorType[item] = itemType
        item_rename = ""
        if itemType == 0:
            item_rename = "x" + str(self.observed_cnt)
            self.observed_dict[item] = item_rename
            self.observed_list.append(item_rename)
            self.observed_cnt = self.observed_cnt + 1
        else:
            item_rename = "factor" + str(self.latent_cnt)
            self.latent_dict[item] = item_rename
            self.latent_list.append(item_rename)
            self.latent_cnt = self.latent_cnt + 1
        self.covariance_dict[item_rename] = []
        self.measurement_dict[item_rename] = []
        self.regressions_dict[item_rename] = []
        return {'item': item, 'itemName': item_rename}

    def addDirectedEdge(self, startItem, endItem):
        startName = ""
        endName = ""
        if self.factorType[startItem] != self.factorType[endItem]:
            if self.factorType[startItem] == 0:
                startName = self.observed_dict[startItem]
                endName = self.latent_dict[endItem]
            else:
                startName = self.observed_dict[endItem]
                endName = self.latent_dict[startItem]
            self.measurement_dict[startName].append(endName)
        else:
            if self.factorType[startItem] == 0:
                startName = self.observed_dict[startItem]
                endName = self.observed_dict[endItem]
            else:
                startName = self.latent_dict[startItem]
                endName = self.latent_dict[endItem]
            self.regressions_dict[startName].append(endName)

    def addCovarianceEdge(self, startItem, endItem):
        startName = ""
        endName = ""
        if self.factorType[startItem] == 0:
            startName = self.observed_dict[startItem]
        else:
            startName = self.latent_dict[startItem]
        if self.factorType[endItem] == 0:
            endName = self.observed_dict[endItem]
        else:
            endName = self.latent_dict[endItem]
        if self.factorType[startItem] == 0 and self.factorType[endItem] == 0:
            temp = startName
            startName = endName
            endName = temp
        self.covariance_dict[startName].append(endName)

    def removeFactor(self, item):
        item_rename = ""
        if self.factorType[item] == 0:
            item_rename = self.observed_dict.pop(item)
            self.observed_list.remove(item_rename)
        else:
            item_rename = self.latent_dict.pop(item)
            self.latent_list.remove(item_rename)
        if item_rename in self.measurement_dict:
            self.measurement_dict.pop(item_rename)
        if item_rename in self.regressions_dict:
            self.regressions_dict.pop(item_rename)
        if item_rename in self.covariance_dict:
            self.covariance_dict.pop(item_rename)
        for tmp in self.measurement_dict:
            if item_rename in self.measurement_dict[tmp]:
                self.measurement_dict[tmp].pop(self.measurement_dict[tmp].index(item_rename))
        for tmp in self.regressions_dict:
            if item_rename in self.regressions_dict[tmp]:
                self.regressions_dict[tmp].pop(self.regressions_dict[tmp].index(item_rename))
        for tmp in self.covariance_dict:
            if item_rename in self.covariance_dict[tmp]:
                self.covariance_dict[tmp].pop(self.covariance_dict[tmp].index(item_rename))

    def removeRelation(self, item):
        startItem = item.start_item
        endItem = item.end_item
        startName = ""
        endName = ""
        if self.factorType[startItem] == 0:
            startName = self.observed_dict[startItem]
        else:
            startName = self.latent_dict[startItem]
        if self.factorType[endItem] == 0:
            endName = self.observed_dict[endItem]
        else:
            endName = self.latent_dict[endItem]
        if self.factorType[startItem] != self.factorType[endItem]:
            if self.factorType[startItem] == 1:
                temp = startName
                startName = endName
                endName = temp
        if isinstance(item, Arrow):
            if startName in self.observed_dict:
                if endName in self.observed_dict[startName]:
                    self.observed_dict[startName].pop(endName)
            if startName in self.regressions_dict:
                if endName in self.regressions_dict[startName]:
                    self.regressions_dict[startName].pop(endName)
        else:
            if startName in self.covariance_dict:
                self.covariance_dict[startName].pop(endName)
            else:
                self.covariance_dict[endName].pop(startName)

    def outputModel(self):
        return {'measurement_dict': self.measurement_dict,
                'regressions_dict': self.regressions_dict,
                'covariance_dict': self.covariance_dict}
