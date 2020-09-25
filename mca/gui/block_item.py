from PySide2 import QtWidgets, QtCore, QtGui

from mca.gui.edit_window import EditWindow
from mca.gui.edit_widgets import ActionParameterWidget
from mca.gui.io_items import InputItem, OutputItem
from mca import framework
from mca.language import _


class BlockItem(QtWidgets.QGraphicsItem):
    """Class to display any kind of :class:`.Block` and supports all its
    functionalities.

    Attributes:
        view: Reference of the :class:`.BlockView` instance.
        width (int): Current width of the block.
        height (int): Current height of the block.
        min_width (int): Minimum width of the block.
        min_height (int): Minimum height of the block.
        input_height (int): Height of its inputs.
        input_width (int): Width of its inputs.
        input_dist (int): Distance between two inputs.
        output_height (int): Height of its outputs.
        output_width (int): Width of its output.
        output_dist (int): Distance between two outputs.
        inputs (list): List of all its inputs.
        outputs (list): List of all its outputs.
        block: Instance of :class:`.Block' this block item is holding.
        resize_mode (bool): Flag to indicate whether user is resizing or
                            moving the block.
        last_point (tuple): Used when resizing the block to remember the
                            coordinates of the last mouse movement to
                            calculate the current size.
        menu: Menu which pops up when the right mouse button is pressed.
        edit_window: Window which carries all parameters and meta data
                     of the block.
        edit_action: Action added to the menu which opens the
                     :class:`.EditWindow` of the class.
        add_input_action: Action added to the menu which only exists when the
                          block instance is a :class:`.DynamicBlock`. A new
                          :class:`.InputItem` is dynamically added.
        delete_input_action: Action added to the menu which only exists when
                          the block instance is a :class:`.DynamicBlock`. The
                          last :class:`.InputItem is deleted of the input list.
        show_plot_action: Action added to the menu when the block has a
                          function called "show". The action invokes the
                          function.
        delete_action: Action added to the menu to delete the block.
    """

    def __init__(self, view, x, y, block, width=100, height=100):
        QtWidgets.QGraphicsItem.__init__(self)
        self.setPos(x, y)
        self.view = view

        self.block = block
        self.block.gui_data["run_time_data"]["pyside2"] = {"block_item": self}
        self.default_color = QtGui.QColor(250, 235, 215)
        self.hover_color = QtGui.QColor(255, 228, 181)
        self.setToolTip(self.block.description)
        self.setAcceptHoverEvents(True)
        self.current_color = self.default_color
        self.width = width
        self.height = height

        self.min_width = 100
        self.min_height = 100

        self.input_height = 20
        self.input_width = 10
        self.input_dist = 10

        self.output_height = 20
        self.output_width = 10
        self.output_dist = 10

        self.inputs = []
        self.outputs = []

        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemSendsGeometryChanges, True)

        for i in self.block.inputs:
            self.add_existing_input(i)
        for o in self.block.outputs:
            self.add_existing_output(o)

        self.resize_mode = False
        self.last_point = (None, None)

        self.menu = QtWidgets.QMenu(self.view)
        self.edit_window = EditWindow(self.view.scene().parent().parent(),
                                      self.block)

        if self.block.parameters:
            self.edit_action = QtWidgets.QAction(_("Edit"), self.view)
            self.edit_action.triggered.connect(self.open_edit_window)
            self.menu.addAction(self.edit_action)
            for parameter in self.block.parameters.values():
                if isinstance(parameter, framework.parameters.ActionParameter):
                    widget = ActionParameterWidget(parameter, self.view)
                    self.menu.addAction(widget)
        if isinstance(self.block, framework.DynamicBlock):
            self.add_input_action = QtWidgets.QAction(_("Add Input"),
                                                      self.view)
            self.add_input_action.triggered.connect(self.create_new_input)
            if self.block.dynamic_input[1] and len(self.block.inputs) == \
                    self.block.dynamic_input[1]:
                self.add_input_action.setEnabled(False)
            self.menu.addAction(self.add_input_action)
            self.delete_input_action = QtWidgets.QAction(_("Delete Input"),
                                                         self.view)
            self.delete_input_action.triggered.connect(self.delete_input)
            if self.block.dynamic_input[0] and len(self.block.inputs) == \
                    self.block.dynamic_input[0]:
                self.delete_input_action.setEnabled(False)
            self.menu.addAction(self.delete_input_action)
        self.delete_action = QtWidgets.QAction(_("Delete Block"), self.view)
        self.delete_action.triggered.connect(self.delete)
        self.menu.addAction(self.delete_action)

        self.save_gui_data()

    def boundingRect(self, *args, **kwargs):
        """Rectangle which marks where events should be invoked."""
        return QtCore.QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        """Method to paint the the block. This method gets invoked after
        initialization and every time the block gets updated.
        """
        painter.setBrush(QtGui.QBrush(self.current_color))
        painter.drawRoundedRect(0, 0, self.width, self.height, 5, 5)
        painter.drawText(5, 2, self.width - 5, 20, 0,
                         self.block.parameters["name"].value)
        if self.block.parameters["name"].value != self.block.name:
            painter.drawText(5, 22, self.width - 5, 20, 0, self.block.name)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        painter.drawRoundedRect(self.width - 20, self.height - 20, 20, 20, 5,
                                5)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        painter.drawLine(self.width - 10, self.height - 20, self.width - 10,
                         self.height)
        painter.drawLine(self.width - 20, self.height - 10, self.width,
                         self.height - 10)

    def contextMenuEvent(self, event):
        """Method that is invoked when the user right-clicks the block.
        Opens the context menu of the block.
        """
        self.menu.exec_(event.screenPos())

    def delete_input(self):
        """Deletes the last input in the input list and deletes it also from
        the block instance. This method is connected to delete_input_action.
        """
        self.inputs[-1].disconnect()
        self.block.delete_input(-1)
        self.scene().removeItem(self.inputs.pop(-1))
        self.modified()
        if self.block.dynamic_input[0] and len(self.block.inputs) == \
                self.block.dynamic_input[0]:
            self.delete_input_action.setEnabled(False)
        if self.block.dynamic_input[1] and len(self.block.inputs) < \
                self.block.dynamic_input[1]:
            self.add_input_action.setEnabled(True)

    def create_new_input(self):
        """Creates a new :class:`.Input` adds it to the block instance and puts
        into a :class:`.InputItem`. This method is connected to
        create_input_action.
        """
        new_mca_input = framework.block_io.Input(self.block)
        self.block.add_input(new_mca_input)
        self.add_existing_input(new_mca_input)
        self.modified()
        if self.block.dynamic_input[1] and len(self.block.inputs) == \
                self.block.dynamic_input[1]:
            self.add_input_action.setEnabled(False)
        if self.block.dynamic_input[0] and len(self.block.inputs) > \
                self.block.dynamic_input[0]:
            self.delete_input_action.setEnabled(True)

    def delete(self):
        """Disconnects all its inputs and outputs and removes itself
        from the scene.
        """
        for i in self.inputs:
            i.disconnect()
        for o in self.outputs:
            o.disconnect()
        self.modified()
        framework.block_registry.Registry.remove_block(self.block)
        self.scene().removeItem(self)

    def open_edit_window(self):
        """Opens up the parameter window."""
        self.edit_window.show()
        self.update()

    def add_existing_input(self, input_):
        """Adds an existing :class:`.Input` from the block instance to a new
        :class:`.InputItem` and adds it to its input list.
        """
        new_input = InputItem(-self.input_width, len(self.inputs) * (
                    self.input_height + self.input_dist) + 5,
                              self.input_width, self.input_height, input_,
                              self.view, self)
        self.inputs.append(new_input)
        if len(self.inputs) * (
                self.input_height + self.input_dist) + 5 > self.height:
            self.resize(self.width, len(self.inputs) * (
                        self.input_height + self.input_dist) + 5)

    def add_existing_output(self, output):
        """Adds an existing :class:`.Output` from the block instance to a new
        :class:`.OutputItem` and adds it to its output list.
        """
        new_output = OutputItem(self.width, len(self.outputs) * (
                    self.output_height + self.output_dist) + 5,
                                self.output_width, self.output_height, output,
                                self.view, self)
        self.outputs.append(new_output)
        if len(self.outputs) * (
                self.output_height + self.output_dist) + 5 > self.height:
            self.resize(self.width, len(self.outputs) * (
                        self.output_height + self.output_dist) + 5)

    def itemChange(self, change, value):
        """Reimplements the itemChange method. Updates the connection lines
        of all its inputs and outputs when the block moves.
        """
        if change == self.ItemPositionChange:
            for i in self.inputs:
                i.update_connection_line()
            for o in self.outputs:
                o.update_connection_line()
        return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        """Opens the edit_window with a double click."""
        self.open_edit_window()

    def mousePressEvent(self, event):
        """Method invoked when the block gets clicked. Increases its Z value
        guarantee to be displayed in front of other colliding blocks. If the
        bottom right 20x20 pixels of the block is pressed the block switches to
        resize mode.
        """
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            event.ignore()
        self.setZValue(1.0)
        if event.pos().x() > self.width - 20 and \
                event.pos().y() > self.height - 20:
            self.resize_mode = True
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Method invoked when a mouse button was pressed whilst moving the
        mouse. If resize_mode is False then the block gets moved otherwise
        the block gets resized.
        """
        if self.resize_mode:
            if self.last_point[0] is not None and \
                    self.last_point[1] is not None:
                self.resize(
                    self.width + event.screenPos().x() - self.last_point[0],
                    self.height + event.screenPos().y() - self.last_point[1])
            self.last_point = (event.screenPos().x(), event.screenPos().y())
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Method invoked when a mouse button on the block gets released."""
        self.setZValue(0.0)
        self.resize_mode = False
        self.last_point = (None, None)
        self.save_gui_data()
        self.modified()
        super().mouseReleaseEvent(event)

    def resize(self, width, height):
        """Resizes the block to the given width and height if they are bigger
        than the min_height and the min_width and also bigger than the space
        the inputs or outputs are requiring.

        Args:
            width: Width to which the block should be resized.
            height: Height to which the block should be resized.
        """
        if max(len(self.outputs) * (self.output_height + self.output_dist) + 5,
               len(self.inputs) * (
                       self.input_height + self.input_dist) + 5) > height or \
                height < self.min_height:
            return
        if width < self.min_width:
            return
        for o in self.outputs:
            o.setPos(width, o.pos().y())
            o.update_connection_line()
        self.scene().update(self.scenePos().x(), self.scenePos().y(),
                            self.width, self.height)
        self.height = height
        self.width = width
        self.update()

    def hoverEnterEvent(self, event):
        """Change color of the block to the hover color."""
        event.accept()
        self.current_color = self.hover_color
        self.update()

    def hoverMoveEvent(self, event):
        event.accept()

    def hoverLeaveEvent(self, event):
        """Change color of the block back to the default color."""
        event.accept()
        self.current_color = self.default_color
        self.update()

    def save_gui_data(self):
        """Store position and size into the :class:`.Block`."""
        self.block.gui_data["save_data"]["pyside2"] = {"pos": [self.scenePos().x(), self.scenePos().y()],
                                                       "size": [self.width, self.height]}

    def modified(self):
        """Signalizes the :class:`.MainWindow` the scene has been modified."""
        self.scene().parent().parent().modified = True
