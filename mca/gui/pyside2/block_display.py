import json
import random

from PySide2 import QtWidgets, QtCore, QtGui

from mca.framework import load, save
from mca.gui.pyside2 import block_item
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
        # Define actions
        self.zoom_in_action = QtWidgets.QAction(
            QtGui.QIcon.fromTheme("zoom-in"), _("Zoom in"))
        self.zoom_in_action.setShortcut("Ctrl++")
        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.zoom_in_action.setToolTip(
            "{}, {}".format(_("Zoom in"), _("Ctrl +")))
        self.addAction(self.zoom_in_action)

        self.zoom_out_action = QtWidgets.QAction(
            QtGui.QIcon.fromTheme("zoom-out"), _("Zoom out"))
        self.zoom_out_action.setShortcut("Ctrl+-")
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.zoom_out_action.setToolTip("{}, {}".format(_("Zoom out"),
                                                        _("Ctrl -")))
        self.addAction(self.zoom_out_action)

        self.zoom_original_action = QtWidgets.QAction(
            QtGui.QIcon.fromTheme("zoom-original"), _("Zoom original"))
        self.zoom_original_action.triggered.connect(self.zoom_original)

        self.copy_action = QtWidgets.QAction(QtGui.QIcon.fromTheme("edit-copy"),
                                             _("Copy"))
        self.copy_action.triggered.connect(self.scene().copy_selected)
        self.copy_action.setShortcut("Ctrl+C")
        self.copy_action.setToolTip("{}, {}".format(_("Copy"), _("Ctrl+C")))

        self.paste_action = QtWidgets.QAction(
            QtGui.QIcon.fromTheme("edit-paste"),
            _("Paste"))
        self.paste_action.triggered.connect(self.scene().paste_selected)
        self.paste_action.setShortcut("Ctrl+V")
        self.paste_action.setToolTip("{}, {}".format(_("Paste"), "Ctrl+V"))

        self.cut_action = QtWidgets.QAction(QtGui.QIcon.fromTheme("edit-cut"),
                                            _("Cut"))
        self.cut_action.triggered.connect(self.scene().cut_selected)
        self.cut_action.setShortcut("Ctrl+X")
        self.cut_action.setToolTip("{}, {}".format(_("Cut"), _("Ctrl+X")))

        self.delete_action = QtWidgets.QAction(
            QtGui.QIcon.fromTheme("edit-delete"), _("Delete"))
        self.delete_action.triggered.connect(self.scene().delete_selected)
        self.delete_action.setShortcut("Del")
        self.delete_action.setToolTip("{}, {}".format(_("Delete"), _("Del")))
        self.clear_action = QtWidgets.QAction(
            QtGui.QIcon.fromTheme("edit-clear"),
            _("Clear"))
        self.clear_action.triggered.connect(self.scene().clear)

        self.setBackgroundBrush(draw_pattern(40, QtGui.Qt.gray))
        self.setDragMode(self.RubberBandDrag)

        self.default_context_menu = QtWidgets.QMenu(self)
        self.default_context_menu.addAction(self.paste_action)

        self.selection_context_menu = QtWidgets.QMenu(self)
        self.selection_context_menu.addAction(self.copy_action)
        self.selection_context_menu.addAction(self.paste_action)
        self.selection_context_menu.addAction(self.cut_action)
        self.selection_context_menu.addAction(self.delete_action)

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
        self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
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
        if event.button() == QtGui.Qt.RightButton:
            if self.scene().selectedItems() and not self.itemAt(event.pos()):
                self.selection_context_menu.exec_(event.screenPos().toPoint())
            elif not self.itemAt(event.pos()):
                self.default_context_menu.exec_(event.screenPos().toPoint())
        else:
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
        self.create_block_item(block_class(), x, y, open_edit_window=True)

    def clear(self):
        """Removes all items from the BlockScene."""
        for item in self.items():
            if isinstance(item, block_item.BlockItem):
                item.delete()

    def create_block_item(self, block, x, y, width=100, height=100,
                          open_edit_window=False, random_pos=False):
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
            random_pos (bool): True, if the position should be random within
                               the view.

        """
        new_block = block_item.BlockItem(self.views()[0], block, x, y, width,
                                         height)
        if random_pos:
            width = self.views()[0].width()
            height = self.views()[0].height()
            x_min = 0
            x_max = width - new_block.width
            if x_min > x_max:
                x_max = x_min
            x = random.randint(x_min, x_max)
            y_min = 0
            y_max = height - new_block.height
            if y_min > y_max:
                y_max = y_min
            y = random.randint(y_min, y_max)
            new_block.setPos(x, y)

        self.addItem(new_block)
        if open_edit_window:
            new_block.open_edit_window()
        self.parent().parent().modified = True

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
            self.create_block_item(block, x_pos, y_pos, width, height,
                                   open_edit_window=False,
                                   random_pos=False)
        for block in blocks:
            for input_index, input_ in enumerate(block.inputs):
                if input_.connected_output:
                    output = input_.connected_output
                    block_item = block.gui_data["run_time_data"]["pyside2"][
                        "block_item"]
                    input_item = block_item.inputs[input_index]
                    block_item = \
                    output.block.gui_data["run_time_data"]["pyside2"][
                        "block_item"]
                    output_item = block_item.outputs[
                        output.block.outputs.index(output)]
                    input_item.connect(output_item, loading=True)

    def copy_selected(self):
        """Copies the selected blocks from the scene as a json string
        to the clipboard.
        """
        app = QtWidgets.QApplication.instance()
        clipboard = app.clipboard()
        if self.selectedItems():
            mime_data = QtCore.QMimeData()
            backend_blocks = [block.block for block in self.selectedItems()]
            x_min = min(
                map(lambda block: block.gui_data["save_data"]["pyside2"]["pos"][
                    0], backend_blocks))
            y_min = min(
                map(lambda block: block.gui_data["save_data"]["pyside2"]["pos"][
                    1], backend_blocks))
            for block in backend_blocks:
                block.gui_data["save_data"]["pyside2"]["pos"][0] -= x_min
                block.gui_data["save_data"]["pyside2"]["pos"][1] -= y_min
            json_blocks = save.blocks_to_json(backend_blocks)
            mime_data.setText(json_blocks)
            clipboard.setMimeData(mime_data)
        else:
            clipboard.clear()

    def paste_selected(self):
        """Pastes copied blocks from the clipboard into the scene."""
        app = QtWidgets.QApplication.instance()
        clipboard = app.clipboard()
        if not clipboard.mimeData().text():
            return
        # Check if clipboard has json string
        try:
            pasted_blocks = load.json_to_blocks(clipboard.mimeData().text())
        except json.decoder.JSONDecodeError:
            return
        # Map global mouse pos to view pos
        global_pos = QtGui.QCursor.pos()
        view_pos = self.views()[0].mapFromGlobal(global_pos)
        view_size = self.views()[0].size()
        # Check if mouse is within view
        if (view_pos.x() >= 0) & (view_pos.y() >= 0) & (
                view_pos.x() <= view_size.width()) & (
                view_pos.y() <= view_size.height()):
            scene_pos = self.views()[0].mapToScene(view_pos)
            # Paste all block centered to the mouse
            x_min = min(
                map(lambda block: block.gui_data["save_data"]["pyside2"]["pos"][
                    0], pasted_blocks))
            y_min = min(
                map(lambda block: block.gui_data["save_data"]["pyside2"]["pos"][
                    1], pasted_blocks))
            x_max = max(
                map(lambda block: block.gui_data["save_data"]["pyside2"]["pos"][
                                      0] +
                                  block.gui_data["save_data"]["pyside2"][
                                      "size"][0], pasted_blocks))
            y_max = max(
                map(lambda block: block.gui_data["save_data"]["pyside2"]["pos"][
                                      1] +
                                  block.gui_data["save_data"]["pyside2"][
                                      "size"][1], pasted_blocks))
            paste_width = x_max - x_min
            paste_height = y_max - y_min
            for block in pasted_blocks:
                block.gui_data["save_data"]["pyside2"]["pos"][
                    0] += scene_pos.x() - paste_width // 2
                block.gui_data["save_data"]["pyside2"]["pos"][
                    1] += scene_pos.y() - paste_height // 2
        self.create_blocks(pasted_blocks)

    def cut_selected(self):
        """Copies the selected blocks from the scene as a json string
        to the clipboard. Deletes the selected block afterwards.
        """
        self.copy_selected()
        self.delete_selected()

    def delete_selected(self):
        """Deletes the selected block from the scene."""
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
