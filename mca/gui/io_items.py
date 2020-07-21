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
        temp_connection_line: Line visible when the user is dragging from the
                              Input.
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

        self.default_color = QtGui.QColor(0, 0, 0)
        self.hover_color = QtGui.QColor(84, 84, 84)
        self.current_color = self.default_color
        self.width = width
        self.height = height
        self.setPos(x, y)

        self.mca_input = mca_input
        self.view = view
        self.setAcceptDrops(True)
        self.setAcceptHoverEvents(True)
        self.connection_line = None
        self.temp_connection_line = None

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
        painter.fillPath(path, QtGui.QBrush(self.current_color))

    def mousePressEvent(self, event):
        """Method invoked when the block gets clicked. Creates a
        temporary line if the input is not yet connected else the
        event is ignored.
        """
        if self.mca_input.connected_output or \
                event.button() == QtCore.Qt.MouseButton.RightButton:
            event.ignore()
            return
        self.temp_connection_line = QtWidgets.QGraphicsLineItem(
                                                   event.scenePos().x(),
                                                   event.scenePos().y(),
                                                   self.scenePos().x() + 5,
                                                   self.scenePos().y() +
                                                   self.height / 2)
        self.scene().addItem(self.temp_connection_line)

    def mouseMoveEvent(self, event):
        """Updates the temp_connection_line when the input is being dragged."""
        self.temp_connection_line.setLine(
            event.scenePos().x(),
            event.scenePos().y(),
            self.temp_connection_line.line().x2(),
            self.temp_connection_line.line().y2())

    def mouseReleaseEvent(self, event):
        """The temporary line gets removed. If the mouse is released over an
        :class:`.OutputItem`, it will get replaced by a
        :class:`.ConnectionLine`.
        """
        for item in self.scene().items(event.scenePos()):
            if isinstance(item, OutputItem):
                try:
                    self.mca_input.connect(item.mca_output)
                except exceptions.BlockCircleError:
                    QtWidgets.QMessageBox().warning(None, _("Error"), _(
                        "Cyclic structures are not allowed."))
                else:
                    self.scene().addItem(ConnectionLine(
                        output_item=item,
                        input_item=self
                        )
                    )
                    self.modified()
        self.scene().removeItem(self.temp_connection_line)
        self.temp_connection_line = None

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
            self.connection_line.output_item.connection_lines.remove(
                self.connection_line)
            self.scene().removeItem(self.connection_line)
            self.connection_line = None
        self.modified()

    def hoverEnterEvent(self, event):
        """Change color of the output to the hover color."""
        event.accept()
        self.current_color = self.hover_color
        self.update()

    def hoverMoveEvent(self, event):
        event.accept()

    def hoverLeaveEvent(self, event):
        """Change color of the input back to the default color."""
        event.accept()
        self.current_color = self.default_color
        self.update()

    def modified(self):
        """Signalizes the :class:`.MainWindow` the scene has been modified."""
        self.scene().parent().parent().modified = True


class OutputItem(QtWidgets.QGraphicsItem):
    """Class to display an :class:`.Output` in the UI. This class supports all
    functionalities of :class:`.Output`.

       Attributes:
           width (int): Current width of the output.
           height (int): Current height of the output.
           mca_output: Reference of the :class:`.Output` to display.
           view: Reference of the :class:`.BlockView` instance.
           connection_lines (list): List of :class:`.ConnectionLine` s.
           temp_connection_line: Line visible when the user is dragging from
                                 the Input.
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

        self.default_color = QtGui.QColor(0, 0, 0)
        self.hover_color = QtGui.QColor(84, 84, 84)
        self.current_color = self.default_color
        self.width = width
        self.height = height
        self.setPos(x, y)

        self.mca_output = mca_output
        self.view = view

        self.setAcceptHoverEvents(True)
        self.setAcceptDrops(True)
        self.connection_lines = []
        self.temp_connection_line = None

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
        """Paints and sets shape of the output. This method gets invoked after
        initialization and every time the output gets updated.
        """
        path = QtGui.QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(self.width, self.height / 2)
        path.lineTo(0, self.height)
        path.lineTo(0, 0)
        painter.fillPath(path, QtGui.QBrush(self.current_color))

    def mousePressEvent(self, event):
        """Method invoked when the block gets clicked. Creates a
        temp_connection_line.
        """
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            event.ignore()
            return
        self.temp_connection_line = QtWidgets.QGraphicsLineItem(
            self.scenePos().x() + 5,
            self.scenePos().y() + self.height / 2,
            event.scenePos().x(),
            event.scenePos().y())
        self.scene().addItem(self.temp_connection_line)

    def mouseMoveEvent(self, event):
        """Updates the temp_connection_line when the mouse is being dragged."""
        self.temp_connection_line.setLine(
            self.temp_connection_line.line().x1(),
            self.temp_connection_line.line().y1(),
            event.scenePos().x(),
            event.scenePos().y())

    def mouseReleaseEvent(self, event):
        """Removes the temp_connection_line. If the mouse gets released over
        an :class:`InputItem` it will get replaced by a
        :class:`.ConnectionLine`.
        """
        for item in self.scene().items(event.scenePos()):
            if isinstance(item, InputItem):
                try:
                    item.mca_input.connect(self.mca_output)
                except exceptions.BlockCircleError:
                    QtWidgets.QMessageBox().warning(None, _("MCA"), _(
                        "Cyclic structures are not allowed."))
                else:
                    self.scene().addItem(ConnectionLine(
                        output_item=self,
                        input_item=item
                        )
                    )
                    self.modified()
        self.scene().removeItem(self.temp_connection_line)
        self.temp_connection_line = None

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
            connection_line.input_item.connection_line = None
            self.scene().removeItem(connection_line)
        self.connection_lines = []
        self.modified()

    def contextMenuEvent(self, event):
        """Method that is invoked when the user right-clicks the output.
        Opens the context menu of the output.
        """
        self.menu.exec_(event.screenPos())

    def hoverEnterEvent(self, event):
        """Change color of the output to the hover color."""
        event.accept()
        self.current_color = self.hover_color
        self.update()

    def hoverMoveEvent(self, event):
        event.accept()

    def hoverLeaveEvent(self, event):
        """Change color of the output back to the default color."""
        event.accept()
        self.current_color = self.default_color
        self.update()

    def modified(self):
        """Signalizes the :class:`.MainWindow` the scene has been modified."""
        self.scene().parent().parent().modified = True


class ConnectionLine(QtWidgets.QGraphicsLineItem):
    """Class which represents the connection between an :class:`.Input` and
    an :class:`.Output`.

    Attributes:
        output_item: :class:`.OutputItem` to connect.
        input_item: :class:`.InputItem` to connect.
    """

    def __init__(self, output_item, input_item):
        """Initialize ConnectionLine class.

        Args:
            output_item: :class:`.OutputItem` to connect.
            input_item::class:`.InputItem` to connect.
        """

        QtWidgets.QGraphicsLineItem.__init__(
            self,
            output_item.scenePos().x() - 5,
            output_item.scenePos().y() + output_item.height / 2,
            input_item.scenePos().x() + 5,
            input_item.scenePos().y() + input_item. height / 2)
        self.output_item = output_item
        self.input_item = input_item
        if self.output_item and self.input_item:
            self.output_item.connection_lines.append(self)
            self.input_item.connection_line = self

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
