from PySide2 import QtWidgets, QtCore, QtGui

from mca.gui.pyside2 import block_item, io_items
from mca.language import _


class BlockView(QtWidgets.QGraphicsView):
    """Class for visualizing the blocks in the connected :class:`.BlockScene`.
    Manages how blocks are displayed like deciding which :class:`.BlockItem`
    or `.ConnectionLine` is painted over other colliding items.
    """

    def __init__(self, scene, parent):
        """Initialize BlockView class.

        Args:
            scene: Scene belonging to this view which holds the items to
                   display.
            parent: Parent of this widget.
        """
        QtWidgets.QGraphicsView.__init__(self, scene=scene, parent=parent)
        self.setMinimumSize(500, 400)

        self.zoom_factor = 1

        self.zoom_in_action = QtWidgets.QAction(QtGui.QIcon.fromTheme("zoom-in"), _("Zoom in"))
        self.zoom_in_action.setShortcut("Ctrl++")
        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.addAction(self.zoom_in_action)

        self.zoom_out_action = QtWidgets.QAction(QtGui.QIcon.fromTheme("zoom-out"), _("Zoom out"))
        self.zoom_out_action.setShortcut("Ctrl+-")
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.addAction(self.zoom_out_action)

        self.zoom_original_action = QtWidgets.QAction(QtGui.QIcon.fromTheme("zoom-original"), _("Zoom original"))
        self.zoom_original_action.triggered.connect(self.zoom_original)

        self.toggle_drag_mode_action = QtWidgets.QAction(_("Toggle Drag"))
        self.toggle_drag_mode_action.setCheckable(True)
        self.toggle_drag_mode_action.toggled.connect(self.set_drag_mode)

        self.setBackgroundBrush(draw_pattern(40, QtGui.Qt.gray))

        self.toggle_drag_mode(False)

    def zoom_in(self):
        """Zooms in by scaling the size of all items up."""
        self.scale(1.2, 1.2)
        self.zoom_factor *= 1.2

    def zoom_out(self):
        """Zooms out by scaling the size of all items down."""
        self.scale(1 / 1.2, 1 / 1.2)
        self.zoom_factor /= 1.2

    def zoom_original(self):
        """Zooms to the original scale."""
        self.scale(1/self.zoom_factor, 1/self.zoom_factor)
        self.zoom_factor = 1

    def set_drag_mode(self, checked):
        """Sets the drag mode.

        Args:
            checked: True to set the drag mode to scroll hand drag.
        """
        if checked:
            self.setDragMode(self.ScrollHandDrag)
        else:
            self.setDragMode(self.RubberBandDrag)


class BlockScene(QtWidgets.QGraphicsScene):
    """Main class for basic operations with graphic items. This class manages
    for example adding items, finding items or removing items from itself.

    Attributes:
        block_list: Reference of the widget that holds all block classes.
    """

    def __init__(self, parent):
        """Initializes BlockScene class.

        Args:
            parent: Parent of this widget.
        """
        QtWidgets.QGraphicsScene.__init__(self, parent=parent)
        self.block_list = None

    def dragEnterEvent(self, event):
        """Method invoked when a drag enters this widget. Accepts only
        events that were created from the :class:`.BlockList`.
        """
        if event.source() is self.block_list:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Method invoked when a drag moves in this widget."""
        event.accept()

    def dropEvent(self, event):
        """Method invoked when a drag gets dropped in this widget.
        Creates a block and adds it to the scene if source of the event was
        from an item of the :class:`.BlockList`.
        """
        event.accept()
        event.setDropAction(QtCore.Qt.CopyAction)
        x = event.scenePos().x()
        y = event.scenePos().y()
        block_class = event.source().selectedItems()[0].data(3)
        self.create_block_item(block_class(), x, y)

    def clear(self):
        """Removes all items from the BlockScene."""
        for item in self.items():
            if isinstance(item, block_item.BlockItem):
                item.delete()

    def create_block_item(self, block, x, y, width=100, height=100,
                          open_edit_window=True):
        """Creates a new :class:`.BlockItem` to an existing :class:`.Block`.
        Tries to find the next free spot of (x,y) to create the block. A free
        spot means there is enough space to crate 100x100 block without
        overlapping another block.

        Args:
            x (int): X coordinate of the BlockItem in the scene.
            y (int): Y coordinate of the BlockItem in the scene.
            block: :class:`.Block` instance the block item represents.
            width (int): Width of the BlockItem.
            height (int): Width of the BlockItem.
            open_edit_window (bool): True, if the edit window
                                     should be opened immediately after
                                     initializing the block.

        """
        for i in range(int(y), self.parent().height(), 4):
            for j in range(int(x), self.parent().width(), 4):
                if not self.items(QtCore.QRect(j, i, 100, 100)):
                    new_block = block_item.BlockItem(self.views()[0], j, i,
                                                     block, width, height)
                    self.addItem(new_block)
                    if open_edit_window:
                        new_block.open_edit_window()
                    self.parent().parent().modified = True
                    return
            x = 0

    def create_blocks(self, blocks):
        """Create the graphical :class:`.BlockItem` structure of an existing
        :class:`.Block` structure.

        Args:
            blocks (list): Existing block structure to represent.
        """
        for block in blocks:
            if block.gui_data["save_data"].get("pyside2"):
                x_pos = block.gui_data["save_data"]["pyside2"]["pos"][0]
                y_pos = block.gui_data["save_data"]["pyside2"]["pos"][1]
                width = block.gui_data["save_data"]["pyside2"]["size"][0]
                height = block.gui_data["save_data"]["pyside2"]["size"][1]
            else:
                x_pos = 0
                y_pos = 0
                width = 100
                height = 100
            self.create_block_item(block, x_pos, y_pos, width, height, False)
        for block in blocks:
            for input_index, input_ in enumerate(block.inputs):
                if input_.connected_output:
                    output = input_.connected_output
                    block_item = block.gui_data["run_time_data"]["pyside2"]["block_item"]
                    input_item = block_item.inputs[input_index]
                    block_item = output.block.gui_data["run_time_data"]["pyside2"]["block_item"]
                    output_item = block_item.outputs[output.block.outputs.index(output)]
                    self.addItem(
                        io_items.ConnectionLine(
                            output_item, input_item
                        )
                    )


def draw_pattern(step, color):
    pixmap = QtGui.QPixmap(step, step)
    pixmap.fill(QtGui.Qt.transparent)
    painter = QtGui.QPainter()
    painter.begin(pixmap)
    painter.setPen(color)
    width = step - 1
    painter.drawLine(0, 0, 2, 0)
    painter.drawLine(0, 0, 0, 2)
    painter.drawLine(0, width - 1, 0, width)
    painter.drawLine(width - 1, 0, width, 0)
    return pixmap