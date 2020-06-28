from PySide2 import QtWidgets, QtCore, QtGui

from mca import exceptions
from mca.language import _


class InputItem(QtWidgets.QGraphicsItem):
    """Class to display an :class:`.Input` in the UI. This class supports all
    functionalities of :class:`.Input`.

    Attributes:
        width (int): Current width of the input.
        height (int): Current height of the input.
        mca_input: Reference of the :class:`.Input` to display.
        view: Reference of the :class:`.BlockView` instance.
        connection_line: :class:`.ConnectionLine` to the :class:`.OutputItem`
                         it is connected to. None if its not connected.
        menu: Menu which pops up when the right mouse button is pressed.
        disconnect_action: Action which calls :meth:`.disconnect`.
    """

    def __init__(self, x, y, width, height, mca_input, view, parent=None):
        """Initialize InputItem class.

        Args:
            x: X-Position of the input.
            y: Y-Position of the input.
            width (int): Current width of the input.
            height (int): Current height of the input.
            mca_input: Reference of the :class:`Input` to display.
            view: Reference of the :class:`.BlockView` instance.
            parent: Parent of this widget.
        """
        super(InputItem, self).__init__(parent=parent)

        self.width = width
        self.height = height
        self.setPos(x, y)

        self.mca_input = mca_input
        self.view = view
        self.setAcceptDrops(True)
        self.connection_line = None

        self.menu = QtWidgets.QMenu(self.view)
        self.disconnect_action = QtWidgets.QAction(_("Disconnect"), self.view)
        self.disconnect_action.triggered.connect(self.disconnect)
        self.menu.addAction(self.disconnect_action)

        if mca_input.name:
            self.setToolTip(mca_input.name)

    def boundingRect(self, *args, **kwargs):
        """Rectangle which marks where events should be invoked."""
        return QtCore.QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        """Method to paint the the input. This method gets invoked after
        initialization and every time the input gets updated.
       """
        path = QtGui.QPainterPath()
        path.moveTo(self.width, 0)
        path.lineTo(self.width, self.height)
        path.lineTo(0, self.height / 2)
        path.lineTo(self.width, 0)
        painter.fillPath(path, QtGui.QBrush(QtGui.QColor(0, 0, 0)))

    def mousePressEvent(self, event):
        """Method invoked when the block gets clicked. Creates a
        :class:`.ConnectionLine` if the input is not yet connected else the
        event is ignored.
        """
        if self.mca_input.connected_output() or \
                event.button() == QtCore.Qt.MouseButton.RightButton:
            event.ignore()
            return
        self.connection_line = ConnectionLine(event.scenePos().x(),
                                              event.scenePos().y(),
                                              self.scenePos().x() + 5,
                                              self.scenePos().y() + self.height / 2)
        self.connection_line.input = self
        self.scene().addItem(self.connection_line)

    def mouseMoveEvent(self, event):
        """Updates the connection_line when the input is being dragged."""
        self.connection_line.x1 = event.scenePos().x()
        self.connection_line.y1 = event.scenePos().y()

    def mouseReleaseEvent(self, event):
        """Attaches the connection line to an :class:`.OutputItem` if the mouse
        gets released above one. Otherwise the connection line gets removed.
        """
        for i in self.scene().items(event.scenePos()):
            if isinstance(i, OutputItem):
                try:
                    self.mca_input.connect(i.mca_output)
                    self.connection_line.x1 = i.scenePos().x() - 5 + self.width
                    self.connection_line.y1 = i.scenePos().y() + i.height / 2
                    i.connection_lines.append(self.connection_line)
                    self.connection_line.output = i
                    return
                except exceptions.BlockCircleError:
                    self.scene().removeItem(self.connection_line)
                    self.connection_line = None
                    QtWidgets.QMessageBox().warning(None, _("MCA"), _(
                        "Cyclic structures are not allowed."))
                    return
        self.scene().removeItem(self.connection_line)
        self.connection_line = None

    def update_connection_line(self):
        """Method to update its connection line according to its own
        position.
        """
        if self.connection_line:
            self.connection_line.x2 = self.scenePos().x() + 5
            self.connection_line.y2 = self.scenePos().y() + self.height / 2

    def contextMenuEvent(self, event):
        """Method that is invoked when the user right-clicks the input.
        Opens the context menu of the input.
        """
        self.menu.exec_(event.screenPos())

    def disconnect(self):
        """Disconnects the :class:`.InputItem` from its :class:`.OutputItem`
        if they are connected.
        """
        self.mca_input.disconnect()
        if self.connection_line:
            self.connection_line.output.connection_lines.remove(
                self.connection_line)
            self.scene().removeItem(self.connection_line)
            self.connection_line = None


class OutputItem(QtWidgets.QGraphicsItem):
    """Class to display an :class:`.Output` in the UI. This class supports all
    functionalities of :class:`.Output`.

       Attributes:
           width (int): Current width of the output.
           height (int): Current height of the output.
           mca_output: Reference of the :class:`.Output` to display.
           view: Reference of the :class:`.BlockView` instance.
           connection_lines (list): List of :class:`.ConnectionLine` s.
           menu: Menu which pops up when the right mouse button is pressed.
           disconnect_action: Action which calls :meth:`.disconnect`.
       """

    def __init__(self, x, y, width, height, mca_output, view, parent=None):
        """Initialize InputItem class.

                Args:
                    x: X-Position of the output.
                    y: Y-Position of the output.
                    width (int): Current width of the output.
                    height (int): Current height of the output.
                    mca_output: Reference of the :class:`Output` to display.
                    view: Reference of the :class:`.BlockView` instance.
                    parent: Parent of this widget.
                """
        super(OutputItem, self).__init__(parent=parent)

        self.width = width
        self.height = height
        self.setPos(x, y)

        self.mca_output = mca_output
        self.view = view
        self.setAcceptDrops(True)
        self.connection_lines = []

        self.menu = QtWidgets.QMenu(self.view)
        self.disconnect_action = QtWidgets.QAction(_("Disconnect"), self.view)
        self.disconnect_action.triggered.connect(self.disconnect)
        self.menu.addAction(self.disconnect_action)

        if mca_output.name:
            self.setToolTip(mca_output.name)

    def boundingRect(self, *args, **kwargs):
        """Rectangle which marks where events should be invoked."""
        return QtCore.QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        """Method to paint the output. This method gets invoked after
        initialization and every time the output gets updated.
        """
        path = QtGui.QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(self.width, self.height / 2)
        path.lineTo(0, self.height)
        path.lineTo(0, 0)
        painter.fillPath(path, QtGui.QBrush(QtGui.QColor(0, 0, 0)))

    def mousePressEvent(self, event):
        """Method invoked when the block gets clicked. Creates a
        :class:`.ConnectionLine` and adds it to the connection line list.
        """
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            event.ignore()
            return
        self.connection_lines.append(ConnectionLine(self.scenePos().x() + 5,
                                                    self.scenePos().y() + self.height / 2,
                                                    event.scenePos().x(),
                                                    event.scenePos().y()))
        self.connection_lines[-1].output = self
        self.scene().addItem(self.connection_lines[-1])

    def mouseMoveEvent(self, event):
        """Updates all connection lines when the output is being dragged."""
        self.connection_lines[-1].x2 = event.scenePos().x()
        self.connection_lines[-1].y2 = event.scenePos().y()

    def mouseReleaseEvent(self, event):
        """Attaches the last added connection line to an :class:`.InputItem`
        if the mouse gets released above one. Otherwise the last added
        connection line gets removed.
        """
        for i in self.scene().items(event.scenePos()):
            if isinstance(i, InputItem):
                try:
                    i.mca_input.connect(self.mca_output)
                    self.connection_lines[-1].x2 = i.scenePos().x() + 5
                    self.connection_lines[
                        -1].y2 = i.scenePos().y() + i.height / 2
                    i.connection_line = self.connection_lines[-1]
                    self.connection_lines[-1].input = i
                    return
                except exceptions.BlockCircleError:
                    self.scene().removeItem(self.connection_lines.pop(-1))
                    QtWidgets.QMessageBox().warning(None, _("MCA"), _(
                        "Cyclic structures are not allowed."))
                    return
        self.scene().removeItem(self.connection_lines.pop(-1))

    def update_connection_line(self):
        """Method to update all its connection lines according to its own
        position.
        """
        for connection_line in self.connection_lines:
            connection_line.x1 = self.scenePos().x() + 5
            connection_line.y1 = self.scenePos().y() + self.height / 2

    def disconnect(self):
        """Disconnects the :class:`.OutputItem` from all its
        :class:`.InputItem` s.
        """
        self.mca_output.disconnect()
        for connection_line in self.connection_lines:
            connection_line.input.connection_line = None
            self.scene().removeItem(connection_line)
        self.connection_lines = []

    def contextMenuEvent(self, event):
        """Method that is invoked when the user right-clicks the output.
        Opens the context menu of the output.
        """
        self.menu.exec_(event.screenPos())


class ConnectionLine(QtWidgets.QGraphicsLineItem):
    """Class which represents the connection between an :class:`.Input` and
    an :class:`.Output`.

    Attributes:
        output: :class:`.OutputItem` which is part of the connection.
        input: :class:`.InputItem` which is part of the connection.
    """

    def __init__(self, x1, y1, x2, y2):
        """Initialize ConnectionLine class.

        Args:
            x1 (int): X-Position of the first point of the line.
            y1 (int): Y-Position of the first point of the line.
            x2 (int): X-Position of the second point of the line.
            y2 (int): Y-Position of the second point of the line.

        """
        QtWidgets.QGraphicsLineItem.__init__(self, x1, y1, x2, y2)
        self.output = None
        self.input = None

    @property
    def x1(self):
        """Sets or gets the X-Position of the first point of the line.

        Args:
            value (int): Sets the new value.
        """
        self.line().x1()

    @x1.setter
    def x1(self, value):
        self.setLine(value, self.line().y1(), self.line().x2(),
                     self.line().y2())

    @property
    def y1(self):
        """Sets or gets the Y-Position of the first point of the line.

        Args:
            value (int): Sets the new value.
        """
        self.line().y1()

    @y1.setter
    def y1(self, value):
        self.setLine(self.line().x1(), value, self.line().x2(),
                     self.line().y2())

    @property
    def x2(self):
        """Sets or gets the X-Position of the second point of the line.

        Args:
            value (int): Sets the new value.
        """
        self.line().x2()

    @x2.setter
    def x2(self, value):
        self.setLine(self.line().x1(), self.line().y1(), value,
                     self.line().y2())

    @property
    def y2(self):
        """Sets or gets the Y-Position of the second point of the line.

        Args:
            value (int): Sets the new value.
        """
        self.line().x1()

    @y2.setter
    def y2(self, value):
        self.setLine(self.line().x1(), self.line().y1(), self.line().x2(),
                     value)
