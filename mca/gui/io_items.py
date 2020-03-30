from PySide2 import QtWidgets, QtCore, QtGui
from mca import exceptions


class InputItem(QtWidgets.QGraphicsItem):
    def __init__(self, x, y, width, height, mca_input, view, parent=None):
        super(InputItem, self).__init__(parent=parent)

        self.width = width
        self.height = height
        self.setPos(x, y)

        self.view = view
        self.mca_input = mca_input
        self.setAcceptDrops(True)
        self.connection_line = None

        self.menu = QtWidgets.QMenu(self.view)
        self.disconnect_action = QtWidgets.QAction("Disconnect", self.view)
        self.disconnect_action.triggered.connect(self.disconnect)
        self.menu.addAction(self.disconnect_action)

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
        if self.mca_input.connected_output() or e.button() == QtCore.Qt.MouseButton.RightButton:
            e.ignore()
            return
        self.connection_line = ConnectionLine(e.scenePos().x(),
                                              e.scenePos().y(),
                                              self.scenePos().x()+5, self.scenePos().y() + self.height/2)
        self.connection_line.input = self
        self.scene().addItem(self.connection_line)

    def mouseMoveEvent(self, e):
        self.connection_line.x1 = e.scenePos().x()
        self.connection_line.y1 = e.scenePos().y()

    def mouseReleaseEvent(self, e):
        for i in self.scene().items(e.scenePos()):
            if isinstance(i, OutputItem):
                try:
                    self.mca_input.connect(i.mca_output)
                    self.connection_line.x1 = i.scenePos().x() - 5 + self.width
                    self.connection_line.y1 = i.scenePos().y() + i.height/2
                    i.connection_lines.append(self.connection_line)
                    self.connection_line.output = i
                    return
                except exceptions.BlockCircleError:
                    self.scene().removeItem(self.connection_line)
                    self.connection_line = None
                    QtWidgets.QMessageBox().warning(None, "MCA", "Cyclic structures are not allowed.")
                    return
        self.scene().removeItem(self.connection_line)
        self.connection_line = None

    def update_connection_line(self):
        if self.connection_line:
            self.connection_line.x2 = self.scenePos().x() + 5
            self.connection_line.y2 = self.scenePos().y() + self.height / 2

    def contextMenuEvent(self, e):
        self.menu.exec_(e.screenPos())

    def disconnect(self):
        self.mca_input.disconnect()
        if self.connection_line:
            self.connection_line.output.connection_lines.remove(self.connection_line)
            self.scene().removeItem(self.connection_line)
            self.connection_line = None


class OutputItem(QtWidgets.QGraphicsItem):

    def __init__(self, x, y, width, height, mca_output, view, parent=None):
        super(OutputItem, self).__init__(parent=parent)

        self.width = width
        self.height = height
        self.setPos(x, y)

        self.view = view
        self.mca_output = mca_output
        self.setAcceptDrops(True)
        self.connection_lines = []

        self.menu = QtWidgets.QMenu(self.view)
        self.disconnect_action = QtWidgets.QAction("Disconnect", self.view)
        self.disconnect_action.triggered.connect(self.disconnect)
        self.menu.addAction(self.disconnect_action)

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
        if e.button() == QtCore.Qt.MouseButton.RightButton:
            e.ignore()
            return
        self.connection_lines.append(ConnectionLine(self.scenePos().x()+5,
                                                    self.scenePos().y() + self.height / 2,
                                                    e.scenePos().x(),
                                                    e.scenePos().y()))
        self.connection_lines[-1].output = self
        self.scene().addItem(self.connection_lines[-1])

    def mouseMoveEvent(self, e):
        self.connection_lines[-1].x2 = e.scenePos().x()
        self.connection_lines[-1].y2 = e.scenePos().y()

    def mouseReleaseEvent(self, e):
        for i in self.scene().items(e.scenePos()):
            if isinstance(i, InputItem):
                try:
                    i.mca_input.connect(self.mca_output)
                    self.connection_lines[-1].x2 = i.scenePos().x() + 5
                    self.connection_lines[-1].y2 = i.scenePos().y() + i.height/2
                    i.connection_line = self.connection_lines[-1]
                    self.connection_lines[-1].input = i
                    return
                except exceptions.BlockCircleError:
                    self.scene().removeItem(self.connection_lines.pop(-1))
                    QtWidgets.QMessageBox().warning(None, "MCA", "Cyclic structures are not allowed.")
                    return
        self.scene().removeItem(self.connection_lines.pop(-1))

    def update_connection_line(self):
        for connection_line in self.connection_lines:
            connection_line.x1 = self.scenePos().x() + 5
            connection_line.y1 = self.scenePos().y() + self.height / 2

    def disconnect(self):
        self.mca_output.disconnect()
        for connection_line in self.connection_lines:
            connection_line.input.connection_line = None
            self.scene().removeItem(connection_line)
        self.connection_lines = []

    def contextMenuEvent(self, e):
        self.menu.exec_(e.screenPos())


class ConnectionLine(QtWidgets.QGraphicsLineItem):
    def __init__(self, x1, y1, x2, y2):
        QtWidgets.QGraphicsLineItem.__init__(self, x1, y1, x2, y2)
        self.output = None
        self.input = None

    @property
    def x1(self):
        self.line().x1()

    @x1.setter
    def x1(self, value):
        self.setLine(value, self.line().y1(), self.line().x2(), self.line().y2())

    @property
    def y1(self):
        self.line().y1()

    @y1.setter
    def y1(self, value):
        self.setLine(self.line().x1(), value, self.line().x2(), self.line().y2())

    @property
    def x2(self):
        self.line().x2()

    @x2.setter
    def x2(self, value):
        self.setLine(self.line().x1(), self.line().y1(), value, self.line().y2())

    @property
    def y2(self):
        self.line().x1()

    @y2.setter
    def y2(self, value):
        self.setLine(self.line().x1(), self.line().y1(), self.line().x2(), value)




