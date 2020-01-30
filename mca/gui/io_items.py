from PySide2 import QtWidgets, QtCore, QtGui
import copy
from mca import exceptions


class InputItem(QtWidgets.QGraphicsItem):
    def __init__(self, x, y, width, height, mca_input, parent=None):
        super(InputItem, self).__init__()
        self.width = width
        self.height = height
        self.setParentItem(parent)
        self.setPos(x, y)
        self.mca_input = mca_input
        self.setAcceptDrops(True)
        self.connection_line = None

        self.output = None

    def boundingRect(self, *args, **kwargs):
        return QtCore.QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        path = QtGui.QPainterPath()
        path.moveTo(self.width, 0)
        path.lineTo(self.width, self.height)
        path.lineTo(0, self.height/2)
        path.lineTo(self.width, 0)
        painter.fillPath(path, QtGui.QBrush(QtGui.QColor(0, 0, 0)))

    def mousePressEvent(self, e):
        if not self.mca_input.connected_output():
            self.connection_line = QtWidgets.QGraphicsLineItem(self.scenePos().x(),
                                                               self.scenePos().y() + self.height / 2,
                                                               e.scenePos().x(), e.scenePos().y())
            self.scene().addItem(self.connection_line)
            e.accept()
        else:
            e.ignore()

    def mouseMoveEvent(self, e):
        self.connection_line.setLine(self.scenePos().x(),
                                     self.scenePos().y() + self.height / 2,
                                     e.scenePos().x(), e.scenePos().y())
        e.accept()

    def mouseReleaseEvent(self, e):
        for i in self.scene().items(e.scenePos()):
            if isinstance(i, OutputItem):
                try:
                    self.mca_input.connect(i.mca_output)
                    self.connection_line.setLine(self.scenePos().x(),
                                                 self.scenePos().y() + self.height / 2,
                                                 i.scenePos().x() + self.width, i.scenePos().y() + i.height/2)
                    i.connection_lines.append(self.connection_line)
                    self.output = i
                    print(self.output)
                    return
                except exceptions.BlockCircleError:
                    self.scene().removeItem(self.connection_line)
                    self.connection_line = None
                    return
        self.scene().removeItem(self.connection_line)
        self.connection_line = None
        self.output = None

    def update_connection_line(self):
        if self.connection_line:
            self.connection_line.setLine(self.scenePos().x(), self.scenePos().y() + self.height / 2,
                                         self.connection_line.line().x2(), self.connection_line.line().y2())

    def contextMenuEvent(self, e):
        menu = QtWidgets.QMenu(self.scene().views()[0])
        disconnect_action = QtWidgets.QAction("Disconnect", self.scene().views()[0])
        disconnect_action.triggered.connect(self.disconnect)
        menu.addAction(disconnect_action)
        menu.exec_(e.screenPos())

    def disconnect(self):
        print(self.output)
        self.mca_input.disconnect()
        if self.connection_line and self.output:
            self.scene().removeItem(self.connection_line)
            self.output.connection_lines.remove(self.connection_line)
        self.connection_line = None


class OutputItem(QtWidgets.QGraphicsItem):

    def __init__(self, x, y, width, height, mca_output, parent=None):
        QtWidgets.QGraphicsItem.__init__(self)
        self.setParentItem(parent)
        self.width = width
        self.height = height
        self.setPos(x, y)
        self.mca_output = mca_output
        self.setAcceptDrops(True)
        self.connection_lines = []

    def boundingRect(self, *args, **kwargs):
        return QtCore.QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        path = QtGui.QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(self.width, self.height/2)
        path.lineTo(0, self.height)
        path.lineTo(0, 0)
        painter.fillPath(path, QtGui.QBrush(QtGui.QColor(0, 0, 0)))

    def mousePressEvent(self, e):
        self.connection_lines.append(QtWidgets.QGraphicsLineItem(self.scenePos().x() + self.width,
                                                                 self.scenePos().y() + self.height / 2,
                                                                 e.scenePos().x(), e.scenePos().y()))
        self.scene().addItem(self.connection_lines[-1])
        e.accept()

    def mouseMoveEvent(self, e):
        self.connection_lines[-1].setLine(self.scenePos().x() + self.width,
                                          self.scenePos().y() + self.height / 2,
                                          e.scenePos().x(), e.scenePos().y())
        e.accept()

    def mouseReleaseEvent(self, e):
        for i in self.scene().items(e.scenePos()):
            if isinstance(i, InputItem):
                if not i.mca_input.connected_output():
                    try:
                        i.mca_input.connect(self.mca_output)
                        self.connection_lines[-1].setLine(i.scenePos().x(),
                                                          i.scenePos().y() + i.height / 2,
                                                          self.scenePos().x() + self.width, self.scenePos().y() + self.height/2)
                        i.connection_line = self.connection_lines[-1]
                        i.output = self
                        return
                    except exceptions.BlockCircleError:
                        self.scene().removeItem(self.connection_lines[-1])
                        self.connection_lines.pop(-1)
                        return
        self.scene().removeItem(self.connection_lines[-1])
        self.connection_lines.pop(-1)

    def update_connection_line(self):
        for i in self.connection_lines:
            i.setLine(i.line().x1(), i.line().y1(),
                      self.scenePos().x() + self.width, self.scenePos().y() + self.height/2)

    def contextMenuEvent(self, e):
        menu = QtWidgets.QMenu(self.scene().views()[0])
        disconnect_action = QtWidgets.QAction("Disconnect", self.scene().views()[0])
        disconnect_action.triggered.connect(self.disconnect)
        menu.addAction(disconnect_action)
        menu.exec_(e.screenPos())

    def disconnect(self):
        self.mca_output.disconnect()
        for connection in self.connection_lines:
            self.scene().removeItem(connection)
        self.connection_lines = []
