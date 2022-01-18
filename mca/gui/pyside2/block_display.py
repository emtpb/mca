from PySide2 import QtWidgets, QtCore, QtGui

from mca.gui.pyside2 import block_item, io_items
from mca.language import _
from mca.framework import load, save


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
        # Define all
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

        self.copy_action = QtWidgets.QAction(QtGui.QIcon.fromTheme("edit-copy"),
                                             _("Copy"))
        self.copy_action.triggered.connect(self.scene().copy)
        self.copy_action.setShortcut("Ctrl+C")

        self.paste_action = QtWidgets.QAction(QtGui.QIcon.fromTheme("edit-paste"),
                                              _("Paste"))
        self.paste_action.triggered.connect(self.scene().paste)
        self.paste_action.setShortcut("Ctrl+V")

        self.cut_action = QtWidgets.QAction(QtGui.QIcon.fromTheme("edit-cut"),
                                            _("Cut"))
        self.cut_action.triggered.connect(self.scene().cut)
        self.cut_action.setShortcut("Ctrl+X")

        self.setBackgroundBrush(draw_pattern(40, QtGui.Qt.gray))
        self.setDragMode(self.RubberBandDrag)

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

    def mousePressEvent(self, event):
        """Method invoked when a mouse button has been pressed."""
        if event.button() == QtGui.Qt.MiddleButton:
            self.setDragMode(self.ScrollHandDrag)
            new_event = QtGui.QMouseEvent(
                QtCore.QEvent.GraphicsSceneMousePress,
                event.pos(), QtGui.Qt.MouseButton.LeftButton,
                event.buttons(),
                QtGui.Qt.KeyboardModifier.NoModifier)
            self.mousePressEvent(new_event)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Method invoked when a mouse button has been released."""
        if event.button() == QtGui.Qt.MiddleButton:
            new_event = QtGui.QMouseEvent(
                QtCore.QEvent.GraphicsSceneMouseRelease,
                event.pos(), QtGui.Qt.MouseButton.LeftButton,
                event.buttons(),
                QtGui.Qt.KeyboardModifier.NoModifier)
            self.mouseReleaseEvent(new_event)
            self.setDragMode(self.RubberBandDrag)
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        """Method invoked when the mouse wheel is used."""
        if event.modifiers() == QtCore.Qt.CTRL:
            if event.delta() > 0:
                self.zoom_in_action.trigger()
            else:
                self.zoom_out_action.trigger()


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

    def copy(self):
        """Copies the selected blocks from the scene as a json string
        to the clipboard.
        """
        app = QtWidgets.QApplication.instance()
        clipboard = app.clipboard()
        if self.selectedItems():
            mime_data = QtCore.QMimeData()
            backend_blocks = [block.block for block in self.selectedItems()]
            json_blocks = save.blocks_to_json(backend_blocks)
            mime_data.setText(json_blocks)
            clipboard.setMimeData(mime_data)
        else:
            clipboard.clear()

    def paste(self):
        """Pastes copied blocks from the clipboard into the scene."""
        app = QtWidgets.QApplication.instance()
        clipboard = app.clipboard()
        if clipboard.mimeData().text():
            pasted_blocks = load.json_to_blocks(clipboard.mimeData().text())
            self.create_blocks(pasted_blocks)

    def cut(self):
        """Copies the selected blocks from the scene as a json string
        to the clipboard. Deletes the selected block afterwards.
        """
        self.copy()
        for item in self.selectedItems():
            if isinstance(item, block_item.BlockItem):
                item.delete()


def draw_pattern(step, color):
    """Draws the background pattern of the block view."""
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