import math
from PyQt5 import QtCore, QtGui, QtWidgets


class Arrow(QtWidgets.QGraphicsLineItem):
    def __init__(self, startItem, endItem):
        super(Arrow, self).__init__()

        self.arrowHead = QtGui.QPolygonF()

        self.myStartItem = startItem
        self.myEndItem = endItem
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.myColor = QtCore.Qt.black
        self.setPen(QtGui.QPen(self.myColor, 2, QtCore.Qt.SolidLine,
                               QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))

    def setColor(self, color):
        self.myColor = color

    def start_item(self):
        return self.myStartItem

    def end_item(self):
        return self.myEndItem

    def boundingRect(self):
        extra = (self.pen().width() + 20) / 2.0
        p1 = self.line().p1()
        p2 = self.line().p2()
        return QtCore.QRectF(p1, QtCore.QSizeF(p2.x() - p1.x(), p2.y() - p1.y())).normalized().adjusted(-extra, -extra,
                                                                                                        extra, extra)

    def shape(self):
        path = super(Arrow, self).shape()
        path.addPolygon(self.arrowHead)
        return path

    def update_position(self):
        line = QtCore.QLineF(self.mapFromItem(self.myStartItem, 0, 0), self.mapFromItem(self.myEndItem, 0, 0))
        self.setLine(line)

    @staticmethod
    def _getIntersectPoint(myStartItem, myEndItem):
        centerLine = QtCore.QLineF(myStartItem.scenePos(), myEndItem.scenePos())
        endPolygon = myEndItem.polygon()
        p1 = endPolygon.first() + myEndItem.scenePos()

        intersectPoint = QtCore.QPointF()
        for i in endPolygon:
            p2 = i + myEndItem.scenePos()
            polyLine = QtCore.QLineF(p1, p2)
            intersectType = polyLine.intersect(centerLine, intersectPoint)
            if intersectType == QtCore.QLineF.BoundedIntersection:
                break
            p1 = p2

        return intersectPoint

    def paint(self, painter, option, widget=None):
        if self.myStartItem.collidesWithItem(self.myEndItem):
            return

        myStartItem = self.myStartItem
        myEndItem = self.myEndItem
        myColor = self.myColor
        myPen = self.pen()
        myPen.setColor(self.myColor)
        arrowSize = 20.0
        painter.setPen(myPen)
        painter.setBrush(self.myColor)

        intersectPoint = Arrow._getIntersectPoint(myStartItem, myEndItem)

        self.setLine(QtCore.QLineF(intersectPoint, myStartItem.scenePos()))
        line = self.line()

        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = (math.pi * 2.0) - angle

        arrowP1 = line.p1() + QtCore.QPointF(math.sin(angle + math.pi / 3.0) * arrowSize,
                                             math.cos(angle + math.pi / 3) * arrowSize)
        arrowP2 = line.p1() + QtCore.QPointF(math.sin(angle + math.pi - math.pi / 3.0) * arrowSize,
                                             math.cos(angle + math.pi - math.pi / 3.0) * arrowSize)

        self.arrowHead.clear()
        for point in [line.p1(), arrowP1, arrowP2]:
            self.arrowHead.append(point)

        painter.drawLine(line)
        painter.drawPolygon(self.arrowHead)
        if self.isSelected():
            painter.setPen(QtGui.QPen(myColor, 1, QtCore.Qt.DashLine))
            myLine = QtCore.QLineF(line)
            myLine.translate(0, 4.0)
            painter.drawLine(myLine)
            myLine.translate(0, -8.0)
            painter.drawLine(myLine)


class DoubleArrow(Arrow):
    def __init__(self, startItem, endItem):
        super(DoubleArrow, self).__init__(startItem, endItem)

    def paint(self, painter, option, widget=None):
        if self.myStartItem.collidesWithItem(self.myEndItem):
            return

        myStartItem = self.myStartItem
        myEndItem = self.myEndItem
        myColor = self.myColor
        myPen = self.pen()
        myPen.setColor(self.myColor)
        arrowSize = 20.0
        painter.setPen(myPen)
        painter.setBrush(self.myColor)

        intersectPoint1 = Arrow._getIntersectPoint(myStartItem, myEndItem)
        intersectPoint2 = Arrow._getIntersectPoint(myEndItem, myStartItem)

        self.setLine(QtCore.QLineF(intersectPoint1, intersectPoint2))
        line = self.line()

        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = (math.pi * 2.0) - angle

        arrowP1 = line.p1() + QtCore.QPointF(math.sin(angle + math.pi / 3.0) * arrowSize,
                                             math.cos(angle + math.pi / 3) * arrowSize)
        arrowP2 = line.p1() + QtCore.QPointF(math.sin(angle + math.pi - math.pi / 3.0) * arrowSize,
                                             math.cos(angle + math.pi - math.pi / 3.0) * arrowSize)

        arrowP3 = line.p2() - QtCore.QPointF(math.sin(angle + math.pi / 3.0) * arrowSize,
                                             math.cos(angle + math.pi / 3) * arrowSize)
        arrowP4 = line.p2() - QtCore.QPointF(math.sin(angle + math.pi - math.pi / 3.0) * arrowSize,
                                             math.cos(angle + math.pi - math.pi / 3.0) * arrowSize)

        self.arrowHead.clear()
        for point in [line.p1(), arrowP1, arrowP2]:
            self.arrowHead.append(point)
        painter.drawPolygon(self.arrowHead)

        self.arrowHead.clear()
        for point in [line.p2(), arrowP3, arrowP4]:
            self.arrowHead.append(point)
        painter.drawPolygon(self.arrowHead)

        painter.drawLine(line)
        if self.isSelected():
            painter.setPen(QtGui.QPen(myColor, 1, QtCore.Qt.DashLine))
            myLine = QtCore.QLineF(line)
            myLine.translate(0, 4.0)
            painter.drawLine(myLine)
            myLine.translate(0, -8.0)
            painter.drawLine(myLine)


class DiagramTextItem(QtWidgets.QGraphicsTextItem):

    def __init__(self, parent=None, scene=None):
        super(DiagramTextItem, self).__init__(parent, scene)

        self.relatedItem = None
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            if self.relatedItem != None:
                self.relatedItem.setPos(QtCore.QPointF(self.scenePos().x() + 50, self.scenePos().y() + 50))
        return value

    def mousePressEvent(self, event):
        self.setSelected(True)
        super(DiagramTextItem, self).mousePressEvent(event)

    def focusOutEvent(self, event):
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
        self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        super(DiagramTextItem, self).focusOutEvent(event)
        
    def mouseMoveEvent(self, event):
        if self.relatedItem != None:
            self.relatedItem.setPos(QtCore.QPointF(self.scenePos().x() + 50, self.scenePos().y() + 50))
        super(DiagramTextItem, self).mouseMoveEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        self.setEditable()
        super(DiagramTextItem, self).mouseDoubleClickEvent(event)

    def setEditable(self):
        self.setTextInteractionFlags(QtCore.Qt.TextEditable)
        self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.setPlainText(self.toPlainText())
        self.setSelected(True)
        self.setFocus()

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        super(DiagramTextItem, self).keyPressEvent(event)

class DiagramItem(QtWidgets.QGraphicsPolygonItem):
    Step, Conditional, StartEnd, Io = range(4)

    def __init__(self, diagramType, contextMenu):
        super(DiagramItem, self).__init__()

        self.arrows = []

        self.diagramType = diagramType
        self.contextMenu = contextMenu

        self.relatedTextItem = None

        path = QtGui.QPainterPath()
        if self.diagramType == self.StartEnd:
            path.moveTo(200, 50)
            path.arcTo(150, 0, 50, 50, 0, 90)
            path.arcTo(50, 0, 50, 50, 90, 90)
            path.arcTo(50, 50, 50, 50, 180, 90)
            path.arcTo(150, 50, 50, 50, 270, 90)
            path.lineTo(200, 25)
            self.myPolygon = path.toFillPolygon()
        elif self.diagramType == self.Conditional:
            self.myPolygon = QtGui.QPolygonF([
                QtCore.QPointF(-100, 0), QtCore.QPointF(0, 100),
                QtCore.QPointF(100, 0), QtCore.QPointF(0, -100),
                QtCore.QPointF(-100, 0)])
        elif self.diagramType == self.Step:
            self.myPolygon = QtGui.QPolygonF([
                QtCore.QPointF(-100, -100), QtCore.QPointF(100, -100),
                QtCore.QPointF(100, 100), QtCore.QPointF(-100, 100),
                QtCore.QPointF(-100, -100)])
        else:
            self.myPolygon = QtGui.QPolygonF([
                QtCore.QPointF(-120, -80), QtCore.QPointF(-70, 80),
                QtCore.QPointF(120, 80), QtCore.QPointF(70, -80),
                QtCore.QPointF(-120, -80)])

        self.setPolygon(self.myPolygon)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)

    def removeArrow(self, arrow):
        try:
            self.arrows.remove(arrow)
        except ValueError:
            pass

    def removeArrows(self):
        for arrow in self.arrows[:]:
            arrow.start_item().removeArrow(arrow)
            arrow.end_item().removeArrow(arrow)
            self.scene().removeItem(arrow)

    def addArrow(self, arrow):
        self.arrows.append(arrow)

    def image(self):
        pixmap = QtGui.QPixmap(250, 250)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 8))
        painter.translate(125, 125)
        painter.drawPolyline(self.myPolygon)
        return pixmap

    def contextMenuEvent(self, event):
        self.scene().clearSelection()
        self.setSelected(True)
        self.contextMenu.exec_(event.screenPos())

    def focusOutEvent(self, event):
        self.setSelected(False)
        super(DiagramItem, self).focusOutEvent(event)

    def mouseMoveEvent(self, event):
        if self.relatedTextItem != None:
            self.relatedTextItem.setPos(QtCore.QPointF(self.scenePos().x() - 50, self.scenePos().y() - 50))
        super(DiagramItem, self).mouseMoveEvent(event)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            for arrow in self.arrows:
                arrow.update_position()
        return value

    def mouseDoubleClickEvent(self, event):
        if self.relatedTextItem != None:
            self.relatedTextItem.mouseDoubleClickEvent(event)