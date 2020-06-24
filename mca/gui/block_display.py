from PySide2 import QtWidgets, QtCore

from mca.gui import block_item
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
        zoom_in_action = QtWidgets.QAction(_("Zoom in"), self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        self.addAction(zoom_in_action)

        zoom_out_action = QtWidgets.QAction(_("Zoom out"), self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        self.addAction(zoom_out_action)

    def zoom_in(self):
        """Zooms in by scaling the size of all items."""
        self.scale(1.2, 1.2)

    def zoom_out(self):
        """Zooms out by scaling the size of all items."""
        self.scale(1 / 1.2, 1 / 1.2)


class BlockScene(QtWidgets.QGraphicsScene):
    """Main class for basic operations with graphic items. This class manages
    for example adding items, finding items or removing items from itself.
    """

    def __init__(self, parent):
        """Initialize BlockScene class.

        Args:
            parent: Parent of this widget.
        """
        QtWidgets.QGraphicsScene.__init__(self, parent=parent)
        self.setSceneRect(0, 0, 880, 800)

    def dragEnterEvent(self, event):
        """Reimplements the event when a drag enters this widget. Accepts only
        events that were created from this application.
        """
        if event.source() in self.parent().children():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Reimplements the event when a drag moves in this widget.
        Accepts only events that were created from this application.
        """
        if event.source() in self.parent().children():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Reimplements the event when something gets dropped in this widget.
        Accepts only events that were created from this application.
        Creates a block and adds it to the scene if source of the event was
        from an item of the :class:`.BlockList`.
        """
        if event.source() in self.parent().children():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            x = event.scenePos().x()
            y = event.scenePos().y()
            block_class = event.source().selectedItems()[0].data(3)
            self.create_block(x, y, block_class)
        else:
            event.ignore()

    def create_block(self, x, y, block_class):
        for i in range(int(y), self.parent().height(), 4):
            for j in range(int(x), self.parent().width(), 4):
                if not self.items(QtCore.QRect(j, i, 100, 100)):
                    new_block = block_item.BlockItem(self.views()[0], j, i,
                                                     block_class)
                    self.addItem(new_block)
                    return
            x = 0

