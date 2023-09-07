from PySide6 import QtWidgets, QtCore, QtGui

from mca.framework import data_types, DynamicBlock, block_io, parameters, PlotBlock
from mca.gui.pyside6 import edit_window, io_items
from mca.language import _


class BlockItem(QtWidgets.QGraphicsItem):
    """Class to display any kind of :class:`.Block` and support all its
    functionalities.

    Attributes:
        view: Reference of the :class:`.BlockView` instance.
        block_width (int): Current width of the block.
        block_height (int): Current height of the block.
        min_width (int): Minimum width of the block.
        min_height (int): Minimum height of the block.
        input_height (int): Height of its inputs.
        input_width (int): Width of its inputs.
        input_dist (int): Distance between two inputs.
        output_height (int): Height of its outputs.
        output_width (int): Width of its output.
        output_dist (int): Distance between two outputs.
        select_point_diameter: Diameter of the selection points.
        inputs (list): List of all its inputs.
        outputs (list): List of all its outputs.
        block: Instance of :class:`.Block' this block item is holding.
        default_color: Default color of the block.
        hover_color: Hover color of the block.
        selection_color: Color for the selection rectangle.
        name_color: Color of the name fonts.
        default_font: Default font of the block.
        custom_name_font: Font for the custom username.
        _resize_all (bool): Flag to indicate whether user is resizing or
                           moving the block.
        _start_pos (tuple): Starting position of a resize event.
        _hovering (bool): Flag to indicate whether the mouse is hovering over
                         the block.
        _original_width (int): Original width of the block.
        _original_height (int): Original height of the block.
        _resize_width (bool): Indicates whether the width should be resized.
        _resize_height (bool): Indicates whether the height should be resized.
        menu: Menu which pops up when the right mouse button is pressed.
        add_input_action: Action added to the menu which only exists when the
                          block instance is a :class:`.DynamicBlock`. Adds an
                          :class:`.InputItem` dynamically to the block.
        delete_input_action: Action added to the menu which only exists when
                             the block instance is a :class:`.DynamicBlock`. The
                             last :class:`.InputItem is deleted of the input list.
        delete_action: Action added to the menu to delete the block.
    """

    def __init__(self, view, block, x, y, block_width=100, block_height=100):
        QtWidgets.QGraphicsItem.__init__(self)
        self.setPos(x, y)

        self.view = view
        self.block = block
        self.block.gui_data["run_time_data"]["pyside6"] = {"block_item": self}

        # Color settings
        self.default_color = None
        self.hover_color = None
        self.selection_color = None
        self.name_color = None

        # Set fonts
        app = QtWidgets.QApplication.instance()
        self.default_font = QtGui.QFont(app.font())
        self.custom_name_font = QtGui.QFont(app.font())
        self.custom_name_font.setPointSize(13)

        self.setToolTip(f"<html><head/><body><p>{self.block.description}</p></body></html>")
        self.setAcceptHoverEvents(True)

        # Define heights and widths
        self.input_height = 26
        self.input_width = 13
        self.input_dist = 10

        self.output_height = 26
        self.output_width = 13
        self.output_dist = 10

        self.select_point_diameter = 10

        self.block_width = block_width
        self.block_height = block_height

        name_width = self.required_name_width()

        if name_width > self.block_width:
            self.block_width = name_width

        self.min_width = 100
        self.min_height = 100

        self.inputs = []
        self.outputs = []
        # Set Flags
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)

        # Create visual inputs and outputs for the existing ones
        for i in self.block.inputs:
            self.add_input(i)
        for o in self.block.outputs:
            self.add_output(o)

        self.action_buttons = []
        self.button_height = 20
        self.button_margin = 5
        num_buttons = 0
        # Add button if the block is a PlotBlock
        if isinstance(self.block, PlotBlock):
            main_window = self.view.parent().parent().parent()
            dock_widget = QtWidgets.QDockWidget(self.block.name,
                                                main_window)
            dock_widget.setWidget(self.block.plot_window)
            main_window.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                                      dock_widget)
            block.gui_data["run_time_data"]["pyside6"]["dock_widget"] = dock_widget
            show_function = show_function_generator(self.block)
            self.action_buttons.append(
                BlockButton(
                    name=_("Show plot"),
                    function=show_function,
                    parent=self,
                    x=self.input_offset + self.select_point_diameter // 2 + 5,
                    y=50 + num_buttons * (
                            self.button_height + self.button_margin),
                    width=self.block_width - 2 * self.button_margin,
                    height=self.button_height))
            num_buttons += 1
        # Add button for an action parameter if needed
        for parameter in self.block.parameters.values():
            if isinstance(parameter,
                          parameters.ActionParameter) and "block_button" in parameter.display_options:
                self.action_buttons.append(
                    BlockButton(
                        name=_(parameter.name),
                        function=parameter.function,
                        parent=self,
                        x=self.input_offset + self.select_point_diameter // 2 + 5,
                        y=50 + num_buttons * (
                                    self.button_height + self.button_margin),
                        width=self.block_width - 2 * self.button_margin,
                        height=self.button_height))
                num_buttons += 1
        # Runtime variables
        self._resize_all = False
        self._resize_width = False
        self._resize_height = False
        self._hovering = False
        self._start_pos = None
        self._original_width = None
        self._original_height = None

        self.menu = QtWidgets.QMenu(self.view)
        # Add edit action
        if self.block.parameters:
            self.edit_action = QtGui.QAction(_("Edit"), self.view)
            self.edit_action.triggered.connect(self.open_edit_window)
            self.menu.addAction(self.edit_action)
        # Add actions for dynamic blocks
        if isinstance(self.block, DynamicBlock):
            if self.block.dynamic_input:
                self.add_input_action = QtGui.QAction(_("Add Input"), self.view)
                self.add_input_action.triggered.connect(self.create_new_input)
                if self.block.dynamic_input[1] is not None and \
                        len(self.block.inputs) == self.block.dynamic_input[1]:
                    self.add_input_action.setEnabled(False)
                self.menu.addAction(self.add_input_action)
                self.delete_input_action = QtGui.QAction(_("Delete Input"),
                                                             self.view)
                self.delete_input_action.triggered.connect(self.delete_input)
                if self.block.dynamic_input[0] is not None and \
                        len(self.block.inputs) == self.block.dynamic_input[0]:
                    self.delete_input_action.setEnabled(False)
                self.menu.addAction(self.delete_input_action)
            if self.block.dynamic_output:
                self.add_output_action = QtGui.QAction(_("Add Output"),
                                                           self.view)
                self.add_output_action.triggered.connect(self.create_new_output)
                if self.block.dynamic_output[1] is not None and \
                        len(self.block.outputs) == self.block.dynamic_output[1]:
                    self.add_output_action.setEnabled(False)
                self.menu.addAction(self.add_output_action)
                self.delete_output_action = QtGui.QAction(
                    _("Delete Output"),
                    self.view)
                self.delete_output_action.triggered.connect(self.delete_output)
                if self.block.dynamic_output[0] is not None and \
                        len(self.block.outputs) == self.block.dynamic_output[0]:
                    self.delete_output_action.setEnabled(False)
                self.menu.addAction(self.delete_output_action)
        self.delete_action = QtGui.QAction(
            QtGui.QIcon.fromTheme("edit-delete"), _("Delete"), self.view)
        self.delete_action.triggered.connect(self.delete)
        self.menu.addAction(self.delete_action)
        self.add_block_actions_to_menu()

        self.block.update()

        self.save_gui_data()

    def add_block_actions_to_menu(self):
        """Add the :class:`.ActionParameter` of the block specified by
        the display_options.
        """
        self.menu.addSeparator()
        for parameter in self.block.parameters.values():
            if isinstance(parameter, parameters.ActionParameter) and \
                    "menu_action" in parameter.display_options:
                action = QtGui.QAction(_(parameter.name), self.view)
                action.triggered.connect(parameter.function)
                self.menu.addAction(action)

    def boundingRect(self, *args, **kwargs):
        """Rectangle which marks where events should be invoked."""
        return QtCore.QRectF(0, 0, self.width, self.height)

    def required_name_width(self):
        """Width required to display the block name and the custom block name.
        """
        name_width = QtGui.QFontMetrics(self.default_font).boundingRect(
            _(self.block.name)).width()
        custom_name_width = QtGui.QFontMetrics(self.custom_name_font).boundingRect(
            self.block.parameters["name"].value).width()
        # Check if name has been changed
        if self.block.parameters["name"].value != self.block.name:
            min_name_length = max(name_width, custom_name_width) + 10
        else:
            min_name_length = name_width + 10
        return min_name_length

    @property
    def width(self):
        """Get the total width of the block item. This includes its inputs,
        outputs and the selection circles around the block.
        """
        return self.block_width + self.select_point_diameter + self.output_offset + self.input_offset

    @property
    def height(self):
        """Get the total height of the block item. This includes the selection
        circles around the block.
        """
        return self.block_height + self.select_point_diameter

    @property
    def input_offset(self):
        """Get the block offset caused by inputs."""
        if self.inputs:
            return self.input_width
        else:
            return 0

    @property
    def output_offset(self):
        """Get the block offset caused by outputs."""
        if self.outputs:
            return self.output_width
        else:
            return 0

    def paint(self, painter, option, widget):
        """Method to paint the block. This method gets invoked after
        initialization and every time the block gets updated.
        """
        self.name_color = self.view.palette().color(QtGui.QPalette.Text)
        self.default_color = QtGui.QColor("#608a5c")
        self.hover_color = QtGui.QColor("#82bd7d")
        self.selection_color = QtGui.QColor("#259AE9")

        select_point_radius = self.select_point_diameter // 2
        x_offset_block = select_point_radius + self.input_offset
        y_offset_block = select_point_radius
        # Draw the main block
        if self._hovering:
            painter.setBrush(self.hover_color)
        else:
            painter.setBrush(self.default_color)

        painter.setPen(QtGui.Qt.black)
        painter.drawRoundedRect(x_offset_block, select_point_radius,
                                self.block_width, self.block_height, 5, 5)

        total_width = self.width - self.select_point_diameter
        total_height = self.height - self.select_point_diameter
        # Draw the selection rectangle with 8 circles
        if self.isSelected():
            painter.setPen(self.selection_color)
            painter.setBrush(QtGui.Qt.transparent)
            path = QtGui.QPainterPath()
            path.addRect(
                select_point_radius,
                select_point_radius,
                total_width,
                total_height
            )
            painter.drawPath(path)
            painter.setBrush(self.selection_color)
            select_point_coordinates = (
                (0, 0),
                (total_width // 2, 0),
                (total_width, 0),
                (total_width, total_height // 2),
                (total_width, total_height),
                (total_width // 2, total_height),
                (0, total_height),
                (0, total_height // 2)
            )
            for coordinates in select_point_coordinates:
                painter.drawEllipse(coordinates[0],
                                    coordinates[1],
                                    self.select_point_diameter,
                                    self.select_point_diameter)
        # Draw block name
        painter.setPen(self.name_color)
        painter.drawText(x_offset_block + 5, y_offset_block + 2,
                         self.block_width - 5, 25, 0,
                         _(self.block.name))
        custom_name = self.block.parameters["name"].value
        # Draw user block name
        if custom_name != self.block.name:
            painter.setFont(self.custom_name_font)
            fm = QtGui.QFontMetrics(self.custom_name_font).boundingRect(custom_name)
            custom_name_width = fm.width()
            painter.drawText(
                x_offset_block + 5,
                y_offset_block + 20, custom_name_width, 25, 0,
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
        # Disconnect the input in the gui
        self.inputs[-1].disconnect()
        # Remove the backend input from the backend block
        self.block.delete_input(-1)
        # Delete the gui input item
        self.scene().removeItem(self.inputs.pop(-1))

        self.modified()
        # Check if removing inputs needs to be disabled
        if self.block.dynamic_input[0] is not None and \
                len(self.block.inputs) == self.block.dynamic_input[0]:
            self.delete_input_action.setEnabled(False)
        # Check if adding inputs can be enabled
        if self.block.dynamic_input[1] is not None and \
                len(self.block.inputs) < self.block.dynamic_input[1]:
            self.add_input_action.setEnabled(True)

    def create_new_input(self):
        """Creates a new :class:`.Input` adds it to the block instance and puts
        into a :class:`.InputItem`. This method is connected to
        create_input_action.
        """
        # Open window to set the input name
        name_window = NameWindow(parent=self.view.scene().parent().parent(),
                                 connection_type="input")
        exit_code = name_window.exec_()
        # Abort if window was cancelled
        if exit_code == 0:
            return
        else:
            # Get the input name
            name = name_window.name_edit.text()
        # Create a new backend input
        new_mca_input = block_io.Input(block=self.block, name=name)
        # Add the backend input to the block
        self.block.add_input(new_mca_input)
        # Add a new gui input
        self.add_input(new_mca_input)
        self.modified()
        # Check if adding inputs needs to be disabled
        if self.block.dynamic_input[1] is not None and \
                len(self.block.inputs) == self.block.dynamic_input[1]:
            self.add_input_action.setEnabled(False)
        # Check if removing inputs can be enabled
        if self.block.dynamic_input[0] is not None and \
                len(self.block.inputs) > self.block.dynamic_input[0]:
            self.delete_input_action.setEnabled(True)

    def create_new_output(self):
        """Creates a new :class:`.Output` adds it to the block instance and puts
        into a :class:`.OutputItem`. This method is connected to
        create_output_action.
        """
        # Open window to set the output name
        name_window = NameWindow(parent=self.view.scene().parent().parent(),
                                 connection_type="output")
        exit_code = name_window.exec_()
        # Abort if window was cancelled
        if exit_code == 0:
            return
        else:
            # Get the output name
            name = name_window.name_edit.text()
        # Set the metadata to default
        metadata = data_types.default_metadata()
        # Create a backend output
        new_mca_output = block_io.Output(block=self.block, name=_(name),
                                         metadata=metadata)
        # Add the backend output to the block
        self.block.add_output(new_mca_output)
        # Add a new gui output
        self.add_output(new_mca_output)
        self.modified()
        # Check if adding outputs needs to be disabled
        if self.block.dynamic_output[1] is not None and \
                len(self.block.outputs) == self.block.dynamic_output[1]:
            self.add_output_action.setEnabled(False)
        # Check if removing outputs can be enabled
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
        # Disconnect the inputs
        for i in self.inputs:
            i.disconnect()
        # Disconnect the outputs
        for o in self.outputs:
            o.disconnect()

        self.modified()
        # Remove the DockWidget for plot blocks
        if isinstance(self.block, PlotBlock):
            self.scene().parent().parent().removeDockWidget(
                self.block.gui_data["run_time_data"]["pyside6"]["dock_widget"])
        # Remove itself from the scene and clean up
        self.scene().removeItem(self)
        self.block.delete()
        self.block = None

    def open_edit_window(self):
        """Opens up the parameter window."""
        edit_window.EditWindow(self, self.block).exec_()
        self.update()

    def add_input(self, input_):
        """Adds an existing :class:`.Input` from the block instance to a new
        :class:`.InputItem` and adds it to its input list.
        """
        # Create a new input
        new_input = io_items.InputItem(
            x=self.select_point_diameter // 2,
            y=len(self.inputs) * (self.input_height + self.input_dist) +
            self.select_point_diameter // 2 + 5,
            width=self.input_width,
            height=self.input_height,
            mca_input=input_,
            view=self.view,
            parent=self)
        # Add the input
        self.inputs.append(new_input)
        # Calculate the minimum needed height of the block
        needed_height = len(self.inputs) * (
                    self.input_height + self.input_dist) + 5
        if needed_height > self.block_height:
            self.adjust_block_height(needed_height)

    def add_output(self, output):
        """Adds an existing :class:`.Output` from the block instance to a new
        :class:`.OutputItem` and adds it to its output list.
        """
        # Get the x-coordinate for the output
        pos_x = self.block_width + self.select_point_diameter // 2 + self.input_offset
        # Create a new output
        new_output = io_items.OutputItem(
            x=pos_x,
            y=len(self.outputs) * (
                        self.output_height + self.output_dist) + 5 + self.select_point_diameter // 2,
            width=self.output_width,
            height=self.output_height,
            mca_output=output,
            view=self.view, parent=self)
        # Add the output
        self.outputs.append(new_output)
        # Calculate the minimum needed height of the block
        needed_height = len(self.outputs) * (
                    self.output_height + self.output_dist) + 5
        if needed_height > self.block_height:
            self.adjust_block_height(needed_height)

    def itemChange(self, change, value):
        """Updates the connection line positions of all its inputs and outputs
        when the block moves.

        Additionally updates the gui data for the backend block
        """
        try:
            self.save_gui_data()
        except AttributeError:
            pass
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            for i in self.inputs:
                i.update_connection_line()
            for o in self.outputs:
                o.update_connection_line()
        return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, event):
        """Opens the edit_window with a double click."""
        self.open_edit_window()

    def mousePressEvent(self, event):
        """Method invoked when the block gets clicked with a mouse button.
        Increases its Z value guarantee to be displayed in front of
        other colliding blocks. If the borders of the block get clicked the
        block will switch into the resize mode.
        """
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            event.ignore()
        # Set block into the foreground
        self.setZValue(1.0)
        self._start_pos = (event.screenPos().x(), event.screenPos().y())
        self._original_width = self.block_width
        self._original_height = self.block_height
        # Decide whether to prepare resizing or dragging the block
        if self.isSelected():
            if event.pos().x() > self.width - 10 and \
                    event.pos().y() > self.height - 10:
                self._resize_all = True
            elif 0 <= event.pos().x() < self.width - 10 and \
                    event.pos().y() >= self.height - 10:
                self._resize_height = True
            elif 0 <= event.pos().y() < self.height - 10 and \
                    event.pos().x() >= self.width - 10:
                self._resize_width = True
            else:
                self.setCursor(QtCore.Qt.OpenHandCursor)
        else:
            self.setCursor(QtCore.Qt.OpenHandCursor)
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Method invoked when a mouse button was pressed whilst moving the
        mouse. If resize_mode is False then the block gets moved otherwise
        the block gets resized.
        """
        # Resize or drag the block
        if self._resize_all:
            # Resizes width and height
            self.adjust_block_width(
                self._original_width + event.screenPos().x() - self._start_pos[
                    0])
            self.adjust_block_height(
                self._original_height + event.screenPos().y() - self._start_pos[
                    1])
        elif self._resize_width:
            # Resizes only the width
            self.adjust_block_width(
                self._original_width + event.screenPos().x() - self._start_pos[
                    0])
        elif self._resize_height:
            # Resizes only the height
            self.adjust_block_height(
                self._original_height + event.screenPos().y() - self._start_pos[
                    1])
        else:
            # Drags the block
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Method invoked when a mouse button on the block gets released."""
        # Set block back to same z value as all the other blocks
        self.setZValue(0.0)
        # End resizing
        self._resize_all = False
        self._resize_width = False
        self._resize_height = False

        self.modified()

        self.setCursor(QtCore.Qt.ArrowCursor)
        # Mouse release has to be passed manually to the action buttons
        for action_button in self.action_buttons:
            if action_button in self.scene().items(event.scenePos()):
                action_button.mouseReleaseEvent(event)

        super().mouseReleaseEvent(event)

    def adjust_block_height(self, height):
        """Adjust the height of the block. Check if height is greater than the
        minimum height and the needed height for inputs and outputs.

        Args:
            height (int): Height to adjust the block to.
        """
        # Compute the height needed by the inputs or outputs
        io_height = max(
            len(self.outputs) * (self.output_height + self.output_dist) + 5,
            len(self.inputs) * (self.input_height + self.input_dist) + 5)

        height = max(io_height, height, self.min_height)
        self.prepareGeometryChange()
        self.block_height = height

    def adjust_block_width(self, width):
        """Adjust the width of the block. Check if the given width is greater
        than the minimum width.

        Args:
            width (int): Width to adjust the block to.
        """
        name_length = self.required_name_width()
        width = max(width, name_length, self.min_width)
        # Reposition outputs and update connection lines
        x_offset = width + self.select_point_diameter // 2 + self.input_offset
        for o in self.outputs:
            o.setPos(x_offset, o.pos().y())
            o.update_connection_line()
        self.prepareGeometryChange()
        self.block_width = width

    def hoverEnterEvent(self, event):
        """Method invoked when the mouse enters the area of a block and starts
        hovering over it. Changes color of the block to the hover color.
        """
        event.accept()
        self._hovering = True
        self.update()

    def hoverMoveEvent(self, event):
        """Method invoked when the mouse moves and keeps hovering over the
        block.
        """
        event.accept()
        # Set the cursor to indicate resizing of the blocks
        if self.isSelected():
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
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)

    def hoverLeaveEvent(self, event):
        """Method invoked when the mouse leaves the area of a block and
        stops hovering it. Changes color of the block back to the default
        color.
        """
        event.accept()
        self._hovering = False
        self.update()

    def save_gui_data(self):
        """Stores position and size in the :class:`.Block` gui_data dict."""
        self.block.gui_data["save_data"]["pyside6"] = {
            "pos": [self.scenePos().x(),
                    self.scenePos().y()],
            "size": [self.block_width, self.block_height]}

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


class BlockButton(QtWidgets.QGraphicsItem):
    """Button class for the :class:`.BlockItem` to display an
    :class:`.ActionParameter` .

    Attributes:
        name (str): Name of the button.
        function: Function to execute when the button is pressed.
        width (int): Width of the button.
        height (int): Height of the button.
        text_margin (int): Margin of the button text within the button.
        default_color: Color of the button. Changes according to the style.
        name_color: Color of the button text. Changes according to the style.
        press_color: Color of the button when pressed.
                     Changes according to the style.
        pressed (bool): Flag whether the button is pressed.
    """

    def __init__(self, name, function, parent, x, y, width, height):
        """Initialize BlockButton class.

        Args:
            name (str): Name of the button.
            function: Function to execute when the button is pressed.
            x (int): X Position of the button.
            y (int): Y Position of the button.
            width (int): Width of the button.
            height (int): Height of the button.
        """
        QtWidgets.QGraphicsItem.__init__(self)
        self.name = name
        self.function = function
        self.setParentItem(parent)
        self.width = width
        self.height = height

        self.text_margin = 4
        self.setPos(x, y)

        self.default_color = None
        self.name_color = None
        self.press_color = None

        self.pressed = False

        self.apply_colors()

    def paint(self, painter, option, widget):
        """Method to paint the button. This method gets invoked after
        initialization and every time the button gets updated.
        """
        # Apply colors depending on the theme
        self.apply_colors()
        painter.setPen(QtCore.Qt.NoPen)
        # Set different color when the button is pressed
        if self.pressed:
            painter.setBrush(self.press_color)
        else:
            painter.setBrush(self.default_color)

        painter.drawRoundedRect(0, 0, self.width, self.height, 5, 5)

        painter.setPen(self.name_color)
        font = painter.font()
        fm = QtGui.QFontMetrics(font)
        name_width = fm.boundingRect(self.name).width()

        painter.drawText(self.width // 2 - name_width // 2,
                         self.text_margin + self.height // 2,
                         self.name)

    def boundingRect(self):
        return QtCore.QRectF(0, 0, self.width, self.height)

    def mousePressEvent(self, event):
        self.pressed = True
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.pressed = False
        try:
            self.function()
        except Exception as error:
            QtWidgets.QMessageBox.warning(
                self.parentItem().view, _("MCA"), _("Could not apply action") + "\n" + repr(error),
                QtWidgets.QMessageBox.Ok)

        super().mousePressEvent(event)

    def apply_colors(self):
        """Applies the current colors depending on the chosen style."""
        self.name_color = self.parentItem().view.palette().color(QtGui.QPalette.ButtonText)
        self.default_color = QtGui.QColor("#076959")
        self.press_color = QtGui.QColor("#288575")


def show_function_generator(block):
    """Generates functions for reopening plot windows of plot blocks."""
    def show_function():
        block.gui_data["run_time_data"]["pyside6"]["dock_widget"].setVisible(True)
        block.fig.tight_layout()
    return show_function
