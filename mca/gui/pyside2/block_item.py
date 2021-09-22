from PySide2 import QtWidgets, QtCore, QtGui

from mca.gui.pyside2 import edit_window, io_items
from mca.framework import data_types, DynamicBlock, block_io, block_registry
from mca.language import _


class BlockItem(QtWidgets.QGraphicsItem):
    """Class to display any kind of :class:`.Block` and support all its
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
        resize_all (bool): Flag to indicate whether user is resizing or
                           moving the block.
        start_pos (tuple): Starting position of an resize event.
        original_width (int): Original width of the block.
        original_height (int): Original height of the block.
        resize_width (bool): Indicates whether the width should be resized.
        resize_height (bool): Indicates whether the height should be resized.
        menu: Menu which pops up when the right mouse button is pressed.
        edit_window: Window which carries all parameters and meta data
                     of the block.
        edit_action: Action added to the menu which opens the
                     :class:`.EditWindow` of the class.
        add_input_action: Action added to the menu which only exists when the
                          block instance is a :class:`.DynamicBlock`. Adds an
                          :class:`.InputItem` dynamically to the block.
        delete_input_action: Action added to the menu which only exists when
                             the block instance is a :class:`.DynamicBlock`. The
                             last :class:`.InputItem is deleted of the input list.
        delete_action: Action added to the menu to delete the block.
    """

    def __init__(self, view, x, y, block, width=100, height=100):
        QtWidgets.QGraphicsItem.__init__(self)
        self.setPos(x, y)
        # Color settings
        self.default_color = QtGui.QColor(250, 235, 215)
        self.hover_color = QtGui.QColor(255, 228, 181)
        self.current_color = self.default_color

        self.view = view
        self.block = block
        self.block.gui_data["run_time_data"]["pyside2"] = {"block_item": self}

        self.setToolTip(self.block.description)
        self.setAcceptHoverEvents(True)
        # Define fonts
        self.name_font = QtGui.QFont("Times", 12, QtGui.QFont.Bold)
        self.custom_name_font = QtGui.QFont("Times", 14)
        self.custom_name_font.setItalic(True)

        # Define heights and widths
        fm = QtGui.QFontMetrics(self.name_font)
        name_width = fm.width(self.block.name) + 10
        if name_width > width:
            self.width = name_width
        else:
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

        # Create visual inputs and outputs for the existing ones
        for i in self.block.inputs:
            self.add_input(i)
        for o in self.block.outputs:
            self.add_output(o)

        self.resize_all = False
        self.resize_width = False
        self.resize_height = False
        self.start_pos = None
        self.original_width = None
        self.original_height = None

        self.menu = QtWidgets.QMenu(self.view)
        self.edit_window = edit_window.EditWindow(self.view.scene().parent().parent(),
                                                  self, self.block)

        if self.block.parameters:
            self.edit_action = QtWidgets.QAction(_("Edit"), self.view)
            self.edit_action.triggered.connect(self.open_edit_window)
            self.menu.addAction(self.edit_action)
        if isinstance(self.block, DynamicBlock):
            if self.block.dynamic_input:
                self.add_input_action = QtWidgets.QAction(_("Add Input"),
                                                          self.view)
                self.add_input_action.triggered.connect(self.create_new_input)
                if self.block.dynamic_input[1] is not None and \
                        len(self.block.inputs) == self.block.dynamic_input[1]:
                    self.add_input_action.setEnabled(False)
                self.menu.addAction(self.add_input_action)
                self.delete_input_action = QtWidgets.QAction(_("Delete Input"),
                                                             self.view)
                self.delete_input_action.triggered.connect(self.delete_input)
                if self.block.dynamic_input[0] is not None and \
                        len(self.block.inputs) == self.block.dynamic_input[0]:
                    self.delete_input_action.setEnabled(False)
                self.menu.addAction(self.delete_input_action)
            if self.block.dynamic_output:
                self.add_output_action = QtWidgets.QAction(_("Add Output"),
                                                           self.view)
                self.add_output_action.triggered.connect(self.create_new_output)
                if self.block.dynamic_output[1] is not None and \
                        len(self.block.outputs) == self.block.dynamic_output[1]:
                    self.add_output_action.setEnabled(False)
                self.menu.addAction(self.add_output_action)
                self.delete_output_action = QtWidgets.QAction(_("Delete Output"),
                                                              self.view)
                self.delete_output_action.triggered.connect(self.delete_output)
                if self.block.dynamic_output[0] is not None and \
                        len(self.block.outputs) == self.block.dynamic_output[0]:
                    self.delete_output_action.setEnabled(False)
                self.menu.addAction(self.delete_output_action)
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
        painter.setFont(self.name_font)
        painter.drawText(5, 2, self.width - 5, 25, 0,
                         self.block.name)
        custom_name = self.block.parameters["name"].value
        if custom_name != self.block.name:
            painter.setFont(self.custom_name_font)
            fm = QtGui.QFontMetrics(self.custom_name_font)
            custom_name_width = fm.width(custom_name)
            painter.drawText(self.width/2-custom_name_width/2,
                             self.height/2-12, self.width - 5, 25, 0,
                             custom_name)

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
        if self.block.dynamic_input[0] is not None and \
                len(self.block.inputs) == self.block.dynamic_input[0]:
            self.delete_input_action.setEnabled(False)
        if self.block.dynamic_input[1] is not None and \
                len(self.block.inputs) < self.block.dynamic_input[1]:
            self.add_input_action.setEnabled(True)

    def create_new_input(self):
        """Creates a new :class:`.Input` adds it to the block instance and puts
        into a :class:`.InputItem`. This method is connected to
        create_input_action.
        """
        name_window = NameWindow(parent=self.view.scene().parent().parent(),
                                 connection_type="input")
        exit_code = name_window.exec_()
        if exit_code == 0:
            return
        else:
            name = name_window.name_edit.text()
        new_mca_input = block_io.Input(block=self.block, name=name)
        self.block.add_input(new_mca_input)
        self.add_input(new_mca_input)
        self.modified()
        if self.block.dynamic_input[1] is not None and \
                len(self.block.inputs) == self.block.dynamic_input[1]:
            self.add_input_action.setEnabled(False)
        if self.block.dynamic_input[0] is not None and \
                len(self.block.inputs) > self.block.dynamic_input[0]:
            self.delete_input_action.setEnabled(True)

    def create_new_output(self):
        """Creates a new :class:`.Output` adds it to the block instance and puts
        into a :class:`.OutputItem`. This method is connected to
        create_output_action.
        """
        name_window = NameWindow(parent=self.view.scene().parent().parent(),
                                 connection_type="output")
        exit_code = name_window.exec_()
        if exit_code == 0:
            return
        else:
            name = name_window.name_edit.text()
        meta_data = data_types.MetaData("", "s", "V")
        new_mca_output = block_io.Output(block=self.block, name=name,
                                         meta_data=meta_data)
        self.block.add_output(new_mca_output)
        self.add_output(new_mca_output)
        self.modified()
        if self.block.dynamic_output[1] is not None and \
                len(self.block.outputs) == self.block.dynamic_output[1]:
            self.add_output_action.setEnabled(False)
        if self.block.dynamic_output[0] is not None and \
                len(self.block.outputs) > self.block.dynamic_output[0]:
            self.delete_output_action.setEnabled(True)

    def delete_output(self):
        """Deletes the last output in the output list and deletes it also from
        the block instance. This method is connected to delete_output_action.
        """
        self.outputs[-1].disconnect()
        self.block.delete_output(-1)
        self.scene().removeItem(self.outputs.pop(-1))
        self.modified()
        if self.block.dynamic_output[0] is not None and \
                len(self.block.outputs) == self.block.dynamic_output[0]:
            self.delete_output_action.setEnabled(False)
        if self.block.dynamic_output[1] is not None and \
                len(self.block.outputs) < self.block.dynamic_output[1]:
            self.add_output_action.setEnabled(True)

    def delete(self):
        """Disconnects all its inputs and outputs and removes itself
        from the scene.
        """
        for i in self.inputs:
            i.disconnect()
        for o in self.outputs:
            o.disconnect()
        self.modified()
        block_registry.Registry.remove_block(self.block)
        self.scene().removeItem(self)

    def open_edit_window(self):
        """Opens up the parameter window."""
        self.edit_window.show()
        self.update()

    def add_input(self, input_):
        """Adds an existing :class:`.Input` from the block instance to a new
        :class:`.InputItem` and adds it to its input list.
        """
        new_input = io_items.InputItem(-self.input_width,
                                       len(self.inputs) * (self.input_height +
                                                           self.input_dist) + 5,
                                       self.input_width,
                                       self.input_height,
                                       input_,
                                       self.view, self)
        self.inputs.append(new_input)
        if len(self.inputs) * (
                self.input_height + self.input_dist) + 5 > self.height:
            self.resize(self.width, len(self.inputs) * (
                        self.input_height + self.input_dist) + 5)

    def add_output(self, output):
        """Adds an existing :class:`.Output` from the block instance to a new
        :class:`.OutputItem` and adds it to its output list.
        """
        new_output = io_items.OutputItem(self.width, len(self.outputs) * (
                    self.output_height + self.output_dist) + 5,
                                self.output_width, self.output_height, output,
                                self.view, self)
        self.outputs.append(new_output)
        if len(self.outputs) * (
                self.output_height + self.output_dist) + 5 > self.height:
            self.resize(self.width, len(self.outputs) * (
                        self.output_height + self.output_dist) + 5)

    def itemChange(self, change, value):
        """Updates the connection lines of all its inputs and outputs when
        the block moves.
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
        """Method invoked when the block gets clicked with the left mouse
        button. Increases its Z value guarantee to be displayed in front of
        other colliding blocks. If the bottom right 20x20 pixels of the block
        are clicked the block switches to resize mode.
        """
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            event.ignore()
        self.setZValue(1.0)
        self.start_pos = (event.screenPos().x(), event.screenPos().y())
        self.original_width = self.width
        self.original_height = self.height
        if event.pos().x() > self.width - 10 and \
                event.pos().y() > self.height - 10:
            self.resize_all = True
        elif 0 <= event.pos().x() < self.width - 10 and \
                event.pos().y() >= self.height - 10:
            self.resize_height = True
        elif 0 <= event.pos().y() < self.height - 10 and \
                event.pos().x() >= self.width - 10:
            self.resize_width = True
        else:
            self.setCursor(QtCore.Qt.OpenHandCursor)
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Method invoked when a mouse button was pressed whilst moving the
        mouse. If resize_mode is False then the block gets moved otherwise
        the block gets resized.
        """
        if self.resize_all:
            self.adjust_width(
                self.original_width + event.screenPos().x() - self.start_pos[0])
            self.adjust_height(
                self.original_height + event.screenPos().y() - self.start_pos[1])
        elif self.resize_width:
            self.adjust_width(
                self.original_width + event.screenPos().x() - self.start_pos[0])
        elif self.resize_height:
            self.adjust_height(
                self.original_height + event.screenPos().y() - self.start_pos[1])
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Method invoked when a mouse button on the block gets released."""
        self.setZValue(0.0)
        self.resize_all = False
        self.resize_width = False
        self.resize_height = False
        self.save_gui_data()
        self.modified()
        self.setCursor(QtCore.Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

    def adjust_height(self, height):
        """Adjust the height of the block. Check if height is greater than the
        minimum height and the needed height for inputs and outputs.

        Args:
            height (int): Height to adjust the block to.
        """
        io_height = max(len(self.outputs) * (self.output_height + self.output_dist) + 5,
                        len(self.inputs) * (self.input_height + self.input_dist) + 5)
        if io_height > height:
            height = io_height
        if self.min_height > height:
            height = self.min_height
        self.scene().update(self.scenePos().x(), self.scenePos().y(),
                            self.width, self.height)
        self.height = height
        self.update()

    def adjust_width(self, width):
        """Adjust the width of the block. Check if the given width is greater
        than the minimum width.

        Args:
            width (int): Width to adjust the block to.
        """
        name_width = QtGui.QFontMetrics(self.name_font).width(self.block.name)
        custom_name_width = QtGui.QFontMetrics(self.custom_name_font).width(self.block.parameters["name"].value)
        if self.block.parameters["name"].value != self.block.name:
            min_name_length = max(name_width, custom_name_width) + 10
        else:
            min_name_length = name_width + 10
        if width < min_name_length:
            width = min_name_length
        elif width < self.min_width:
            width = self.min_width
        # Reposition outputs and update connection lines
        for o in self.outputs:
            o.setPos(width, o.pos().y())
            o.update_connection_line()
        self.scene().update(self.scenePos().x(), self.scenePos().y(),
                            self.width, self.height)
        self.width = width
        self.update()

    def hoverEnterEvent(self, event):
        """Method invoked when the mouse enters the area of a block and starts
        hovering over it. Changes color of the block to the hover color.
        """
        event.accept()
        self.current_color = self.hover_color
        self.update()

    def hoverMoveEvent(self, event):
        """Method invoked when the mouse moves and keeps hovering over the
        block.
        """
        event.accept()
        if event.pos().x() >= self.width - 10 and \
                event.pos().y() >= self.height - 10:
            self.setCursor(QtCore.Qt.SizeFDiagCursor)
        elif 0 <= event.pos().x() < self.width - 10 and \
                event.pos().y() >= self.height - 10:
            self.setCursor(QtCore.Qt.SizeVerCursor)
        elif 0 <= event.pos().y() < self.height - 10 and \
                event.pos().x() >= self.width - 10:
            self.setCursor(QtCore.Qt.SizeHorCursor)
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)

    def hoverLeaveEvent(self, event):
        """Method invoked when the mouse leaves the area of a block and
        stops hovering it. Changes color of the block back to the default
        color.
        """
        event.accept()
        self.current_color = self.default_color
        self.update()

    def save_gui_data(self):
        """Stores position and size in the :class:`.Block` gui_data dict."""
        self.block.gui_data["save_data"]["pyside2"] = {"pos": [self.scenePos().x(),
                                                               self.scenePos().y()],
                                                       "size": [self.width, self.height]}

    def modified(self):
        """Signalizes the :class:`.MainWindow` that the file is modified."""
        self.scene().parent().parent().modified = True


class NameWindow(QtWidgets.QDialog):
    """Window for naming inputs or outputs.

    Attributes:
        main_layout: Main widget of the dialog window.
        name_widget: Widget holding all relevant widgets.
        name_layout: Layout arranging all relevant widgets.
        name_label: Label above the line editing.
        name_edit: Line edit to enter the name of the input or output.
        button_box: Button box for confirming the name.
    """
    def __init__(self, parent, connection_type):
        """Initialize NameWindow.

        Args:
            parent: Parent of this widget.
            connection_type: Connection type that can be either input or
                             output object.
        """
        QtWidgets.QDialog.__init__(self, parent=parent)

        self.resize(300, 120)
        self.setMaximumSize(QtCore.QSize(300, 120))

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.name_widget = QtWidgets.QWidget(parent=self)
        self.name_layout = QtWidgets.QHBoxLayout()
        self.name_widget.setLayout(self.name_layout)
        if connection_type == "input":
            label_text = _("Name of the Input:")
        else:
            label_text = _("Name of the Output:")
        self.name_label = QtWidgets.QLabel(
            parent=self.name_widget,
            text=label_text)
        self.name_edit = QtWidgets.QLineEdit(parent=self.name_widget)
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_edit)

        self.button_box = QtWidgets.QDialogButtonBox()
        self.button_box.setContentsMargins(0, 0, 10, 10)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)

        self.button_box.button(QtWidgets.QDialogButtonBox.Ok).setText(
            _("Ok"))
        self.button_box.button(QtWidgets.QDialogButtonBox.Cancel).setText(
            _("Cancel"))

        self.main_layout.addWidget(self.name_widget)
        self.main_layout.addWidget(self.button_box)

        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL("accepted()"),
                               self.accept)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL("rejected()"),
                               self.reject)
