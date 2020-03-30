from PySide2 import QtWidgets, QtCore

from mca.gui import block_item
from mca.language import _


class BlockView(QtWidgets.QGraphicsView):
    def __init__(self, scene, parent):
        QtWidgets.QGraphicsView.__init__(self, scene=scene, parent=parent)
        zoom_in_action = QtWidgets.QAction(_("Zoom in"), self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        self.addAction(zoom_in_action)

        zoom_out_action = QtWidgets.QAction(_("Zoom out"), self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        self.addAction(zoom_out_action)

    @QtCore.Slot()
    def zoom_in(self):
        self.scale(1.2, 1.2)

    def zoom_out(self):
        self.scale(1 / 1.2, 1 / 1.2)


class BlockScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent):
        QtWidgets.QGraphicsScene.__init__(self, parent=parent)
        self.setSceneRect(0, 0, 1000, 800)
        self.setStickyFocus(True)
        self.mouse_pos = None

    def dragEnterEvent(self, e):
        if e.mimeData().hasText:
            e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().hasText:
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        if e.source() in self.parent().children():
            e.setDropAction(QtCore.Qt.CopyAction)
            e.accept()
            x = e.scenePos().x()
            y = e.scenePos().y()
            new_block = block_item.BlockItem(self.views()[0], x, y, e.source().selectedItems()[0].data(1))
            self.addItem(new_block)
        else:
            e.ignore()
