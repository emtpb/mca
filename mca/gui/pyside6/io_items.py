import logging

from PySide6 import QtWidgets, QtCore, QtGui

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
        connection_line: Reference of the :class:`.ConnectionLine` object.
        menu: Menu which pops up when the right mouse button is pressed.
        disconnect_action: Action which calls :meth:`.disconnect`.
    """

    def __init__(self, x, y, width, height, mca_input, view, parent=None):
        """Initializes InputItem class.

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
        # Define the colors
        self.default_color = QtGui.QColor(0, 0, 204)
        self.hover_color = QtGui.QColor(51, 51, 255)
        self.current_color = self.default_color
        self.width = width
        self.height = height
        self.setPos(x, y)

        self.mca_input = mca_input
        self.view = view
        self.setAcceptDrops(True)
        self.setAcceptHoverEvents(True)
        self.connection_line = None

        self.menu = QtWidgets.QMenu(self.view)
        self.disconnect_action = QtGui.QAction(_("Disconnect"), self.view)
        self.disconnect_action.triggered.connect(self.disconnect)
        self.menu.addAction(self.disconnect_action)

        if self.mca_input.name:
            self.setToolTip(mca_input.name)

    def boundingRect(self, *args, **kwargs):
        """Rectangle which marks where events should be invoked."""
        return QtCore.QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        """Method to paint the input. This method gets invoked after
        initialization and every time the input gets updated.
       """
        path = QtGui.QPainterPath()
        path.moveTo(self.width, 0)
        path.lineTo(self.width, self.height)
        path.lineTo(0, self.height / 2)
        path.lineTo(self.width, 0)
        painter.fillPath(path, QtGui.QBrush(self.current_color))

    def mousePressEvent(self, event):
        """A :class:`.ConnectionLine` is created if the input is not yet
        connected or the right mouse button has been pressed (since it shadows
        the contextMenuEvent) else the event is ignored.
        """
        if self.mca_input.connected_output or \
                event.button() == QtCore.Qt.MouseButton.RightButton:
            event.ignore()
            return
        self.connection_line = ConnectionLine(event.scenePos().x(),
                                              event.scenePos().y(),
                                              self.scenePos().x() + 5,
                                              self.scenePos().y() +
                                              self.height / 2, input_item=self)
        self.scene().addItem(self.connection_line)
        self.setCursor(QtCore.Qt.BlankCursor)

    def mouseMoveEvent(self, event):
        """Updates the connection line position."""
        self.connection_line.p1 = (event.scenePos().x(), event.scenePos().y())

    def mouseReleaseEvent(self, event):
        """If the mouse is released over an :class:`.OutputItem`, it gets
        connected to it. Else the connection line is removed.
        """
        self.setCursor(QtCore.Qt.ArrowCursor)
        output_found = False
        for item in self.scene().items(event.scenePos()):
            if isinstance(item, OutputItem):
                self.connect(item, self.connection_line)
                output_found = True
        if not output_found:
            self.scene().removeItem(self.connection_line)
            self.connection_line = None

    def update_connection_line(self):
        """Updates the connection line according to its own position."""
        if self.connection_line is not None:
            self.connection_line.p2 = (self.scenePos().x(),
                                       self.scenePos().y() + self.height / 2)

    def contextMenuEvent(self, event):
        """Method invoked when the user right-clicks the input.
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

    def connect(self, output_item, connection_line=None, loading=False):
        """Connects itself to an :class:`.OutputItem`.

        Args:
            output_item: Output to connect to.
            connection_line: Already existing connection line (from dragging).
                             The position gets adjusted, and it is made sure
                             that all reference are passed. By default, set to
                             None. If set to None a new :class:`.ConnectionLine`
                             object is created.
            loading (bool): If set to True, connecting the backend input is
                            skipped. It is assumed that has already been done
                            by the backend.
        """
        remove_connection_line = False
        try:
            if not loading:
                self.mca_input.connect(output_item.mca_output)
        except exceptions.BlockCircleError:
            logging.error("Cyclic structures are not allowed.")
            QtWidgets.QMessageBox().warning(None, _("MCA"), _(
                "Cyclic structures are not allowed."))
            remove_connection_line = True
        except exceptions.UnitError:
            logging.error("Signals have incompatible metadata.")
            QtWidgets.QMessageBox().warning(None, _("MCA"), _(
                "Signals have incompatible metadata."))
            self.mca_input.disconnect()
            remove_connection_line = True
        except exceptions.IntervalError:
            logging.error("Signals have incompatible abscissas.")
            QtWidgets.QMessageBox().warning(None, _("MCA"), _(
                "Signals have incompatible abscissas."))
            self.mca_input.disconnect()
            remove_connection_line = True
        except exceptions.BlockConnectionError:
            self.disconnect()
            self.mca_input.connect(output_item.mca_output)
        except Exception as error:
            logging.error(repr(error))
            QtWidgets.QMessageBox().warning(
                None, _("MCA"),
                _("Could not connect blocks") + "\n" +
                repr(error))
            self.mca_input.disconnect()
            remove_connection_line = True
        if not remove_connection_line:
            # Create a new connection line
            if connection_line is None:
                self.connection_line = ConnectionLine(
                    output_item.scenePos().x() + output_item.width,
                    output_item.scenePos().y() + output_item.height / 2,
                    self.scenePos().x(),
                    self.scenePos().y() + self.height / 2,
                    input_item=self, output_item=output_item)
                output_item.connection_lines.append(self.connection_line)
                self.scene().addItem(self.connection_line)
            else:
                # Update existing connection line
                if connection_line not in output_item.connection_lines:
                    output_item.connection_lines.append(connection_line)
                    connection_line.output_item = output_item
                connection_line.input_item = self
                self.connection_line = connection_line
                self.connection_line.p2 = (self.scenePos().x(),
                                           self.scenePos().y() + self.height / 2)
                self.connection_line.p1 = (
                output_item.scenePos().x() + output_item.width,
                output_item.scenePos().y() + output_item.height / 2)
            self.modified()
            return

        # Remove the connection line in case an error occurred
        else:
            self.scene().removeItem(connection_line)
            if connection_line in output_item.connection_lines:
                output_item.connection_lines.remove(connection_line)
            self.connection_line = None

    def hoverEnterEvent(self, event):
        """Method invoked when the mouse enters the area of the input and starts
        hovering over it. Changes color of the input to the hover color.
        """
        event.accept()
        self.current_color = self.hover_color
        self.update()

    def hoverMoveEvent(self, event):
        """Method invoked when the mouse moves and keeps hovering over the
        input.
        """
        event.accept()

    def hoverLeaveEvent(self, event):
        """Method invoked when the mouse leaves the area of the input and
        stops hovering it. Changes color of the input back to the default
        color.
        """
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
       menu: Menu which pops up when the right mouse button is pressed.
       disconnect_action: Action which calls :meth:`.disconnect` .
    """

    def __init__(self, x, y, width, height, mca_output, view, parent=None):
        """Initializes InputItem class.

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

        self.default_color = QtGui.QColor(204, 0, 0)
        self.hover_color = QtGui.QColor(255, 51, 51)
        self.current_color = self.default_color
        self.width = width
        self.height = height
        self.setPos(x, y)

        self.mca_output = mca_output
        self.view = view

        self.setAcceptHoverEvents(True)
        self.setAcceptDrops(True)
        self.connection_lines = []

        self.menu = QtWidgets.QMenu(self.view)
        self.disconnect_action = QtGui.QAction(_("Disconnect"), self.view)
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
        """Creates new connection line and adds it to its list of connection
        lines.
        """
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            event.ignore()
            return
        self.connection_lines.append(ConnectionLine(
            self.scenePos().x() + self.width,
            self.scenePos().y() + self.height / 2,
            event.scenePos().x(),
            event.scenePos().y(), output_item=self))
        self.scene().addItem(self.connection_lines[-1])
        self.setCursor(QtCore.Qt.BlankCursor)

    def mouseMoveEvent(self, event):
        """Updates the connection lines."""
        self.connection_lines[-1].p2 = (event.scenePos().x(),
                                        event.scenePos().y())

    def mouseReleaseEvent(self, event):
        """If the mouse is released over an :class:`.InputItem`, it gets
        connected to it. Else the last added connection line is removed.
        """
        self.setCursor(QtCore.Qt.ArrowCursor)
        input_found = False
        for item in self.scene().items(event.scenePos()):
            if isinstance(item, InputItem):
                item.connect(self, self.connection_lines[-1])
                input_found = True
        if not input_found:
            self.scene().removeItem(self.connection_lines.pop(-1))

    def update_connection_line(self):
        """Updates all its connection lines positions."""
        for connection_line in self.connection_lines:
            connection_line.p1 = (self.scenePos().x() + self.width,
                                  self.scenePos().y() + self.height / 2)

    def disconnect(self):
        """Disconnects from all its :class:`.InputItem` s."""
        self.mca_output.disconnect()
        for connection_line in self.connection_lines:
            connection_line.input_item.connection_line = None
            self.scene().removeItem(connection_line)
        self.connection_lines = []
        self.modified()

    def contextMenuEvent(self, event):
        """Method invoked when the user right-clicks the output.
        Opens the context menu of the output.
        """
        self.menu.exec_(event.screenPos())

    def hoverEnterEvent(self, event):
        """Method invoked when the mouse enters the area of the output and
        starts hovering over it. Changes color of the output to the hover color.
        """
        event.accept()
        self.current_color = self.hover_color
        self.update()

    def hoverMoveEvent(self, event):
        """Method invoked when the mouse moves and keeps hovering over the
        output.
        """
        event.accept()

    def hoverLeaveEvent(self, event):
        """Method invoked when the mouse leaves the area of the output and
        stops hovering it. Changes color of the output back to the default
        color.
        """
        event.accept()
        self.current_color = self.default_color
        self.update()

    def modified(self):
        """Signalizes the :class:`.MainWindow` the scene has been modified."""
        self.scene().parent().parent().modified = True


class ConnectionLine(QtWidgets.QGraphicsLineItem):
    """Class which represents the visual connection between an :class:`.Input`
    and an :class:`.Output`.

    Attributes:
        output_item: :class:`.OutputItem` to connect.
        input_item: :class:`.InputItem` to connect.
    """

    def __init__(self, x1, y1, x2, y2, input_item=None, output_item=None):
        """Initialize ConnectionLine class.

        Args:
            output_item: :class:`.OutputItem` to connect.
            input_item::class:`.InputItem` to connect.
        """

        QtWidgets.QGraphicsLineItem.__init__(self, x1, y1, x2, y2)

        self.setAcceptHoverEvents(True)
        self.default_color = QtGui.QColor("#00f73a")
        self.hover_color = QtGui.QColor("#4cfc75")
        self.line_width = 3
        self.setPen(QtGui.QPen(self.default_color, self.line_width))

        self.input_item = input_item
        self.output_item = output_item

    @property
    def p1(self):
        """Sets or gets coordinates of the first point of the line.

        Args:
            value (tuple): Sets the new value.
        """
        return self.line().p1().x(), self.line().p1().y()

    @p1.setter
    def p1(self, value):
        self.setLine(value[0], value[1], self.line().x2(), self.line().y2())

    @property
    def p2(self):
        """Sets or gets the coordinates of the second point of the line.

        Args:
            value (tuple): Sets the new value.
        """
        return self.line().p1().x(), self.line().p1().y()

    @p2.setter
    def p2(self, value):
        self.setLine(self.line().x1(), self.line().y1(), value[0], value[1])

    def hoverEnterEvent(self, event):
        """Sets the colour of the line to the hover color."""
        self.setPen(QtGui.QPen(self.hover_color, self.line_width))
        event.accept()

    def hoverMoveEvent(self, event):
        event.accept()

    def hoverLeaveEvent(self, event):
        """Sets the colour of the line to the defualt color."""
        self.setPen((QtGui.QPen(self.default_color, self.line_width)))
        event.accept()

    def contextMenuEvent(self, event):
        """Disconnects the referenced :class:`.InputItem` from
        its :class:`.Output`.
        """
        self.input_item.disconnect()
