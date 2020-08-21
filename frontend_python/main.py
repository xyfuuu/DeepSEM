import sys
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets

from diagram_items import Arrow, DoubleArrow, DiagramTextItem, DiagramItem

# pyrcc5 diagramscene.qrc -o diagramscene_rc.py
import diagramscene_rc
from output import GraphvizVisualization


class DiagramScene(QtWidgets.QGraphicsScene):
    InsertItem, InsertLine, InsertDoubleLine, InsertText, MoveItem = range(5)
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

    itemInserted = QtCore.pyqtSignal(DiagramItem)

    textInserted = QtCore.pyqtSignal(QtWidgets.QGraphicsTextItem)

    itemSelected = QtCore.pyqtSignal(QtWidgets.QGraphicsItem)

    def __init__(self, itemMenu, parent=None):
        super(DiagramScene, self).__init__(parent)

        self.myItemMenu = itemMenu
        self.myMode = self.MoveItem
        self.myItemType = DiagramItem.Step
        self.line = None
        self.textItem = None
        self.myItemColor = QtCore.Qt.white
        self.myTextColor = QtCore.Qt.black
        self.myLineColor = QtCore.Qt.black
        self.myFont = QtGui.QFont()

    def setLineColor(self, color):
        self.myLineColor = color
        if self.isItemChange(Arrow):
            item = self.selectedItems()[0]
            item.setColor(self.myLineColor)
            self.update()

    def setTextColor(self, color):
        self.myTextColor = color
        if self.isItemChange(DiagramTextItem):
            item = self.selectedItems()[0]
            item.setDefaultTextColor(self.myTextColor)

    def setItemColor(self, color):
        self.myItemColor = color
        if self.isItemChange(DiagramItem):
            item = self.selectedItems()[0]
            item.setBrush(self.myItemColor)

    def setMode(self, mode):
        self.myMode = mode

    def setItemType(self, type):
        self.myItemType = type

    def editorLostFocus(self, item):
        cursor = item.textCursor()
        cursor.clearSelection()
        item.setTextCursor(cursor)

        if item.toPlainText():
            self.removeItem(item)
            item.deleteLater()

    def mousePressEvent(self, mouseEvent):
        if mouseEvent.button() != QtCore.Qt.LeftButton:
            return

        if self.myMode == self.InsertItem:
            self.addFactor(self.myItemType, mouseEvent.scenePos())
        elif self.myMode in [self.InsertLine, self.InsertDoubleLine]:
            self.line = QtWidgets.QGraphicsLineItem(QtCore.QLineF(mouseEvent.scenePos(),
                                                                  mouseEvent.scenePos()))

            self.line.setPen(QtGui.QPen(self.myLineColor, 2))
            self.addItem(self.line)
        elif self.myMode == self.InsertText:
            self.addTextItem('', mouseEvent.scenePos())

        super(DiagramScene, self).mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        if self.myMode in [self.InsertLine, self.InsertDoubleLine] and self.line:
            newLine = QtCore.QLineF(self.line.line().p1(), mouseEvent.scenePos())
            self.line.setLine(newLine)
        elif self.myMode == self.MoveItem:
            super(DiagramScene, self).mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        if self.myMode in [self.InsertLine, self.InsertDoubleLine] and self.line:
            startItems = self.items(self.line.line().p1())
            startItem = None
            for item in startItems:
                if isinstance(item, DiagramItem) :
                    startItem = item
                    break

            endItems = self.items(self.line.line().p2())
            endItem = None
            for item in endItems:
                if isinstance(item, DiagramItem):
                    endItem = item
                    break

            self.removeItem(self.line)
            self.line = None

            if startItem == None or endItem == None or startItem == endItem:
                return

            if self.myMode == self.InsertLine:
                arrow = Arrow(startItem, endItem)
                self.AddDirectedEdge(startItem, endItem)
            else:
                arrow = DoubleArrow(startItem, endItem)
                self.AddCovarianceEdge(startItem, endItem)

            arrow.setColor(self.myLineColor)
            startItem.addArrow(arrow)
            endItem.addArrow(arrow)
            arrow.setZValue(-1000.0)
            self.addItem(arrow)
            arrow.update_position()

        self.line = None
        super(DiagramScene, self).mouseReleaseEvent(mouseEvent)

    def isItemChange(self, type):
        for item in self.selectedItems():
            if isinstance(item, type):
                return True
        return False
        
    def addFactor(self, itemType, itemPosition):
        item = DiagramItem(itemType, self.myItemMenu)
        item.setBrush(self.myItemColor)
        self.addItem(item)
        item.setPos(itemPosition)
        self.itemInserted.emit(item)
        self.factorType[item] = itemType
        item_rename = ""
        if itemType == 1:
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

    def addTextItem(self, textContent, itemPosition):
        textItem = DiagramTextItem()
        textItem.setTextWidth(100)
        textItem.setPlainText(textContent)
        textItem.setFont(self.myFont)
        textItem.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        textItem.setZValue(1000.0)
        textItem.lostFocus.connect(self.editorLostFocus)
        textItem.selectedChange.connect(self.itemSelected)
        self.addItem(textItem)
        textItem.setDefaultTextColor(self.myTextColor)
        textItem.setPos(itemPosition)
        format = QtGui.QTextBlockFormat()
        format.setAlignment(QtCore.Qt.AlignCenter)
        cursor = QtGui.QTextCursor()
        cursor.select(QtGui.QTextCursor.Document)
        cursor.mergeBlockFormat(format)
        cursor.clearSelection()
        textItem.setTextCursor(cursor)
        return textItem

    def AddDirectedEdge(self, startItem, endItem):
        startName = ""
        endName = ""
        if self.factorType[startItem] != self.factorType[endItem]:
            if self.factorType[startItem] == 1:
                startName = self.observed_dict[startItem]
                endName = self.latent_dict[endItem]
            else:
                startName = self.observed_dict[endItem]
                endName = self.latent_dict[startItem]
            self.measurement_dict[startName].append(endName)
        else:
            if self.factorType[startItem] == 1:
                startName = self.observed_dict[startItem]
                endName = self.observed_dict[endItem]
            else:
                startName = self.latent_dict[startItem]
                endName = self.latent_dict[endItem]
            self.regressions_dict[startName].append(endName)

    def AddCovarianceEdge(self, startItem, endItem):
        startName = ""
        endName = ""
        if self.factorType[startItem] == 1:
            startName = self.observed_dict[startItem]
        else:
            startName = self.latent_dict[startItem]
        if self.factorType[endItem] == 1:
            endName = self.observed_dict[endItem]
        else:
            endName = self.latent_dict[endItem]
        if self.factorType[startItem] == 0 and self.factorType[endItem] == 1 :
            temp = startName
            startName = endName
            endName = temp
        self.covariance_dict[startName].append(endName)
    
    def RemoveFactor(self, item):
        item_rename = ""
        if self.factorType[item] == 1:
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
    
    def RemoveRelation(self, item):
        startItem = item.start_item
        endItem = item.end_item
        startName = ""
        endName = ""
        if self.factorType[startItem] == 1:
            startName = self.observed_dict[startItem]
        else:
            startName = self.latent_dict[startItem]
        if self.factorType[endItem] == 1:
            endName = self.observed_dict[endItem]
        else:
            endName = self.latent_dict[endItem]
        if self.factorType[startItem] != self.factorType[endItem]:
            if self.factorType[startItem] != 1:
                temp = startName
                startName = endName
                endName = startName
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
                
    def Output(self):
        return {'measurement_dict':self.measurement_dict,
                'regressions_dict':self.regressions_dict,
                'covariance_dict':self.covariance_dict}


class MainWindow(QtWidgets.QMainWindow):
    InsertTextButton = 10

    def __init__(self):
        super(MainWindow, self).__init__()

        self.createActions()
        self.createMenus()
        self.createToolBox()

        self.scene = DiagramScene(self.itemMenu)
        self.scene.setSceneRect(QtCore.QRectF(0, 0, 5000, 5000))
        self.scene.itemInserted.connect(self.itemInserted)
        self.scene.textInserted.connect(self.textInserted)
        self.scene.itemSelected.connect(self.itemSelected)

        self.createToolbars()

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.toolBox)
        self.view = QtWidgets.QGraphicsView(self.scene)
        layout.addWidget(self.view)

        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(layout)

        self.setCentralWidget(self.widget)
        self.setWindowTitle("Diagramscene")

    def backgroundButtonGroupClicked(self, button):
        buttons = self.backgroundButtonGroup.buttons()
        for myButton in buttons:
            if myButton != button:
                button.setChecked(False)

        text = button.text()
        if text == "Blue Grid":
            self.scene.setBackgroundBrush(QtGui.QBrush(QtGui.QPixmap(':/images/background1.png')))
        elif text == "White Grid":
            self.scene.setBackgroundBrush(QtGui.QBrush(QtGui.QPixmap(':/images/background2.png')))
        elif text == "Gray Grid":
            self.scene.setBackgroundBrush(QtGui.QBrush(QtGui.QPixmap(':/images/background3.png')))
        else:
            self.scene.setBackgroundBrush(QtGui.QBrush(QtGui.QPixmap(':/images/background4.png')))

        self.scene.update()
        self.view.update()

    def buttonGroupClicked(self, id):
        buttons = self.buttonGroup.buttons()
        for button in buttons:
            if self.buttonGroup.button(id) != button:
                button.setChecked(False)

        if id == self.InsertTextButton:
            self.scene.setMode(DiagramScene.InsertText)
        else:
            self.scene.setItemType(id)
            self.scene.setMode(DiagramScene.InsertItem)

    # Call the backend in this function.
    def doCalculation(self):
        model = self.scene.Output()
        vis = GraphvizVisualization([model])
        vis.show()
        
    def deleteItem(self):
        print("begin remove")
        for item in self.scene.selectedItems():
            if isinstance(item, DiagramItem):
                item.removeArrows()
                self.scene.RemoveFactor(item)
            else:
                self.scene.RemoveRelation(item)
            self.scene.removeItem(item)
            
    def pointerGroupClicked(self, i):
        self.scene.setMode(self.pointerTypeGroup.checkedId())

    def bringToFront(self):
        if not self.scene.selectedItems():
            return

        selectedItem = self.scene.selectedItems()[0]
        overlapItems = selectedItem.collidingItems()

        zValue = 0
        for item in overlapItems:
            if (item.zValue() >= zValue and isinstance(item, DiagramItem)):
                zValue = item.zValue() + 0.1
        selectedItem.setZValue(zValue)

    def sendToBack(self):
        if not self.scene.selectedItems():
            return

        selectedItem = self.scene.selectedItems()[0]
        overlapItems = selectedItem.collidingItems()

        zValue = 0
        for item in overlapItems:
            if (item.zValue() <= zValue and isinstance(item, DiagramItem)):
                zValue = item.zValue() - 0.1
        selectedItem.setZValue(zValue)

    def itemInserted(self, item):
        self.pointerTypeGroup.button(DiagramScene.MoveItem).setChecked(True)
        self.scene.setMode(self.pointerTypeGroup.checkedId())
        self.buttonGroup.button(item.diagramType).setChecked(False)
        print(item)
        print(item.diagramType)

    def textInserted(self, item):
        self.buttonGroup.button(self.InsertTextButton).setChecked(False)
        self.scene.setMode(self.pointerTypeGroup.checkedId())

    def currentFontChanged(self, font):
        self.handleFontChange()

    def fontSizeChanged(self, font):
        self.handleFontChange()

    def sceneScaleChanged(self, scale):
        newScale = float(scale.split('%')[0]) / 100.0
        self.view.resetTransform()
        self.view.scale(newScale, newScale)

    def textColorChanged(self):
        self.textAction = self.sender()
        self.fontColorToolButton.setIcon(self.createColorToolButtonIcon(
            ':/images/textpointer.png',
            QtGui.QColor(self.textAction.data())))
        self.textButtonTriggered()

    def itemColorChanged(self):
        self.fillAction = self.sender()
        self.fillColorToolButton.setIcon(self.createColorToolButtonIcon(
            ':/images/floodfill.png',
            QtGui.QColor(self.fillAction.data())))
        self.fillButtonTriggered()

    def lineColorChanged(self):
        self.lineAction = self.sender()
        self.lineColorToolButton.setIcon(self.createColorToolButtonIcon(
            ':/images/linecolor.png',
            QtGui.QColor(self.lineAction.data())))
        self.lineButtonTriggered()

    def textButtonTriggered(self):
        self.scene.setTextColor(QtGui.QColor(self.textAction.data()))

    def fillButtonTriggered(self):
        self.scene.setItemColor(QtGui.QColor(self.fillAction.data()))

    def lineButtonTriggered(self):
        self.scene.setLineColor(QtGui.QColor(self.lineAction.data()))

    def itemSelected(self, item):
        font = item.font()
        color = item.defaultTextColor()
        self.fontCombo.setCurrentFont(font)
        self.fontSizeCombo.setEditText(str(font.pointSize()))
        self.boldAction.setChecked(font.weight() == QtGui.QFont.Bold)
        self.italicAction.setChecked(font.italic())
        self.underlineAction.setChecked(font.underline())

    def about(self):
        QtWidgets.QMessageBox.about(self, "About Diagram Scene",
                                    "The <b>Diagram Scene</b> example shows use of the graphics framework.")


    def updateData(self):
        fileDialog = QtWidgets.QFileDialog()
        fileDialog.setWindowTitle('Select Data Source')
        fileDialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        fileDialog.setViewMode(QtWidgets.QFileDialog.Detail)
        fileDialog.setDirectory('.')

        if fileDialog.exec() == QtWidgets.QFileDialog.Accepted :
            path = fileDialog.selectedFiles()[0]

        self.data = pd.read_excel(path)
        self.description = self.data.columns

        columns = []

        xLabel = 2000
        yLabel = 2200
        for column in self.data.columns:
            group = self.scene.createItemGroup(self.scene.selectedItems())
            group.setFlags(QtWidgets.QGraphicsItem.ItemIsMovable)
            item = self.scene.addFactor(1, QtCore.QPointF(xLabel, yLabel))
            group.addToGroup(item['item'])
            columns.append(item['itemName'])
            textItem = self.scene.addTextItem('{}\n{}'.format(item['itemName'], column),
                                             QtCore.QPointF(xLabel - 50, yLabel - 50))
            group.addToGroup(textItem)

            xLabel = xLabel + 200
            if xLabel % 2000 == 0:
                xLabel = 2000
                yLabel += 300

        self.data.columns = columns

    def createToolBox(self):
        self.buttonGroup = QtWidgets.QButtonGroup()
        self.buttonGroup.setExclusive(False)
        self.buttonGroup.buttonClicked[int].connect(self.buttonGroupClicked)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.createCellWidget("Observed Variables", DiagramItem.Conditional), 0, 0)
        layout.addWidget(self.createCellWidget("Latent Variables", DiagramItem.Step), 0, 1)

        textButton = QtWidgets.QToolButton()
        textButton.setCheckable(True)
        self.buttonGroup.addButton(textButton, self.InsertTextButton)
        textButton.setIcon(QtGui.QIcon(QtGui.QPixmap(':/images/textpointer.png')
                                       .scaled(30, 30)))
        textButton.setIconSize(QtCore.QSize(50, 50))

        textLayout = QtWidgets.QGridLayout()
        textLayout.addWidget(textButton, 0, 0, QtCore.Qt.AlignHCenter)
        textLayout.addWidget(QtWidgets.QLabel("Text"), 1, 0,
                             QtCore.Qt.AlignCenter)
        textWidget = QtWidgets.QWidget()
        textWidget.setLayout(textLayout)
        layout.addWidget(textWidget, 1, 1)

        layout.setRowStretch(3, 10)
        layout.setColumnStretch(2, 10)

        itemWidget = QtWidgets.QWidget()
        itemWidget.setLayout(layout)

        self.backgroundButtonGroup = QtWidgets.QButtonGroup()
        self.backgroundButtonGroup.buttonClicked.connect(self.backgroundButtonGroupClicked)

        backgroundLayout = QtWidgets.QGridLayout()
        backgroundLayout.addWidget(self.createBackgroundCellWidget("Blue Grid",
                                                                   ':/images/background1.png'), 0, 0)
        backgroundLayout.addWidget(self.createBackgroundCellWidget("White Grid",
                                                                   ':/images/background2.png'), 0, 1)
        backgroundLayout.addWidget(self.createBackgroundCellWidget("Gray Grid",
                                                                   ':/images/background3.png'), 1, 0)
        backgroundLayout.addWidget(self.createBackgroundCellWidget("No Grid",
                                                                   ':/images/background4.png'), 1, 1)

        backgroundLayout.setRowStretch(2, 10)
        backgroundLayout.setColumnStretch(2, 10)

        backgroundWidget = QtWidgets.QWidget()
        backgroundWidget.setLayout(backgroundLayout)

        self.toolBox = QtWidgets.QToolBox()
        self.toolBox.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Ignored))
        self.toolBox.setMinimumWidth(itemWidget.sizeHint().width())
        self.toolBox.addItem(itemWidget, "Basic Flowchart Shapes")
        self.toolBox.addItem(backgroundWidget, "Backgrounds")

    def createActions(self):
        self.toFrontAction = QtWidgets.QAction(
            QtGui.QIcon(':/images/bringtofront.png'), "Bring to &Front",
            self, shortcut="Ctrl+F", statusTip="Bring item to front",
            triggered=self.bringToFront)

        self.sendBackAction = QtWidgets.QAction(
            QtGui.QIcon(':/images/sendtoback.png'), "Send to &Back", self,
            shortcut="Ctrl+B", statusTip="Send item to back",
            triggered=self.sendToBack)

        self.deleteAction = QtWidgets.QAction(QtGui.QIcon(':/images/delete.png'),
                                              "&Delete", self, shortcut="Delete",
                                              statusTip="Delete item from diagram",
                                              triggered=self.deleteItem)

        self.calculateAction = QtWidgets.QAction(QtGui.QIcon(':/images/do_calculation.png'),
                                                 "&Calculate", self, shortcut="Calculate",
                                                 statusTip="Run DESM!",
                                                 triggered=self.doCalculation)

        self.exitAction = QtWidgets.QAction("E&xit", self, shortcut="Ctrl+X",
                                            statusTip="Quit Scenediagram example", triggered=self.close)

        self.aboutAction = QtWidgets.QAction("A&bout", self, shortcut="Ctrl+B",
                                             triggered=self.about)

        self.updateDataAction = QtWidgets.QAction("Update &Data", self, shortcut="Ctrl+U",
                                             triggered=self.updateData)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.updateDataAction)
        self.fileMenu.addAction(self.exitAction)

        self.itemMenu = self.menuBar().addMenu("&Item")
        self.itemMenu.addAction(self.calculateAction)
        self.itemMenu.addSeparator()
        self.itemMenu.addAction(self.deleteAction)
        self.itemMenu.addSeparator()
        self.itemMenu.addAction(self.toFrontAction)
        self.itemMenu.addAction(self.sendBackAction)

        self.aboutMenu = self.menuBar().addMenu("&Help")
        self.aboutMenu.addAction(self.aboutAction)

    def createToolbars(self):
        self.editToolBar = self.addToolBar("Edit")
        self.editToolBar.addAction(self.calculateAction)
        self.editToolBar.addAction(self.deleteAction)
        self.editToolBar.addAction(self.toFrontAction)
        self.editToolBar.addAction(self.sendBackAction)

        self.fillColorToolButton = QtWidgets.QToolButton()
        self.fillColorToolButton.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)
        self.fillColorToolButton.setMenu(
            self.createColorMenu(self.itemColorChanged, QtCore.Qt.white))
        self.fillAction = self.fillColorToolButton.menu().defaultAction()
        self.fillColorToolButton.setIcon(
            self.createColorToolButtonIcon(':/images/floodfill.png',
                                           QtCore.Qt.white))
        self.fillColorToolButton.clicked.connect(self.fillButtonTriggered)

        self.lineColorToolButton = QtWidgets.QToolButton()
        self.lineColorToolButton.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)
        self.lineColorToolButton.setMenu(
            self.createColorMenu(self.lineColorChanged, QtCore.Qt.black))
        self.lineAction = self.lineColorToolButton.menu().defaultAction()
        self.lineColorToolButton.setIcon(
            self.createColorToolButtonIcon(':/images/linecolor.png',
                                           QtCore.Qt.black))
        self.lineColorToolButton.clicked.connect(self.lineButtonTriggered)

        self.colorToolBar = self.addToolBar("Color")
        self.colorToolBar.addWidget(self.fillColorToolButton)
        self.colorToolBar.addWidget(self.lineColorToolButton)

        pointerButton = QtWidgets.QToolButton()
        pointerButton.setCheckable(True)
        pointerButton.setChecked(True)
        pointerButton.setIcon(QtGui.QIcon(':/images/pointer.png'))
        linePointerButton = QtWidgets.QToolButton()
        linePointerButton.setCheckable(True)
        linePointerButton.setIcon(QtGui.QIcon(':/images/arrow.png'))
        doublePointerButton = QtWidgets.QToolButton()
        doublePointerButton.setCheckable(True)
        doublePointerButton.setIcon(QtGui.QIcon(':/images/double_arrow.png'))

        self.pointerTypeGroup = QtWidgets.QButtonGroup()
        self.pointerTypeGroup.addButton(pointerButton, DiagramScene.MoveItem)
        self.pointerTypeGroup.addButton(linePointerButton, DiagramScene.InsertLine)
        self.pointerTypeGroup.addButton(doublePointerButton, DiagramScene.InsertDoubleLine)
        self.pointerTypeGroup.buttonClicked[int].connect(self.pointerGroupClicked)

        self.sceneScaleCombo = QtWidgets.QComboBox()
        self.sceneScaleCombo.addItems(["50%", "75%", "100%", "125%", "150%"])
        self.sceneScaleCombo.setCurrentIndex(2)
        self.sceneScaleCombo.currentIndexChanged[str].connect(self.sceneScaleChanged)

        self.pointerToolbar = self.addToolBar("Pointer type")
        self.pointerToolbar.addWidget(pointerButton)
        self.pointerToolbar.addWidget(linePointerButton)
        self.pointerToolbar.addWidget(doublePointerButton)
        self.pointerToolbar.addWidget(self.sceneScaleCombo)

    def createBackgroundCellWidget(self, text, image):
        button = QtWidgets.QToolButton()
        button.setText(text)
        button.setIcon(QtGui.QIcon(image))
        button.setIconSize(QtCore.QSize(50, 50))
        button.setCheckable(True)
        self.backgroundButtonGroup.addButton(button)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(button, 0, 0, QtCore.Qt.AlignHCenter)
        layout.addWidget(QtWidgets.QLabel(text), 1, 0, QtCore.Qt.AlignCenter)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        return widget

    def createCellWidget(self, text, diagramType):
        item = DiagramItem(diagramType, self.itemMenu)
        icon = QtGui.QIcon(item.image())

        button = QtWidgets.QToolButton()
        button.setIcon(icon)
        button.setIconSize(QtCore.QSize(50, 50))
        button.setCheckable(True)
        self.buttonGroup.addButton(button, diagramType)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(button, 0, 0, QtCore.Qt.AlignHCenter)
        layout.addWidget(QtWidgets.QLabel(text), 1, 0, QtCore.Qt.AlignCenter)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        return widget

    def createColorMenu(self, slot, defaultColor):
        colors = [QtCore.Qt.black, QtCore.Qt.white, QtCore.Qt.red, QtCore.Qt.blue, QtCore.Qt.yellow]
        names = ["black", "white", "red", "blue", "yellow"]

        colorMenu = QtWidgets.QMenu(self)
        for color, name in zip(colors, names):
            action = QtWidgets.QAction(self.createColorIcon(color), name, self,
                                       triggered=slot)
            action.setData(QtGui.QColor(color))
            colorMenu.addAction(action)
            if color == defaultColor:
                colorMenu.setDefaultAction(action)
        return colorMenu

    def createColorToolButtonIcon(self, imageFile, color):
        pixmap = QtGui.QPixmap(50, 80)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        image = QtGui.QPixmap(imageFile)
        target = QtCore.QRect(0, 0, 50, 60)
        source = QtCore.QRect(0, 0, 42, 42)
        painter.fillRect(QtCore.QRect(0, 60, 50, 80), color)
        painter.drawPixmap(target, image, source)
        painter.end()

        return QtGui.QIcon(pixmap)

    def createColorIcon(self, color):
        pixmap = QtGui.QPixmap(20, 20)
        painter = QtGui.QPainter(pixmap)
        painter.setPen(QtCore.Qt.NoPen)
        painter.fillRect(QtCore.QRect(0, 0, 20, 20), color)
        painter.end()

        return QtGui.QIcon(pixmap)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    mainWindow = MainWindow()
    mainWindow.setGeometry(0, 0, 1600, 1000)
    mainWindow.show()

    sys.exit(app.exec_())
