from PySide2 import QtWidgets, QtCore, QtGui

from mca.gui.parameter_window import ParameterWindow
from mca.gui.io_items import InputItem, OutputItem
from mca import framework
from mca import exceptions
from mca.language import _

class BlockItem(QtWidgets.QGraphicsItem):

    def __init__(self, view, x, y, block_class):
        QtWidgets.QGraphicsItem.__init__(self)
        self.setPos(x, y)
        self.view = view
        self.width = 100
        self.height = 100

        self.min_heigth = 100
        self.min_width = 100

        self.input_height = 20
        self.input_width = 10
        self.input_dist = 10

        self.output_height = 20
        self.output_width = 10
        self.output_dist = 10

        self.inputs = []
        self.outputs = []
        self.block = block_class()

        self.setToolTip(type(self.block).description)
        self.parameter_window()
        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemSendsGeometryChanges, True)
        for i in self.block.inputs:
            self.add_new_input(i)
        for o in self.block.outputs:
            self.add_new_output(o)

        self.resize_mode = False
        self.last_point = (None, None)

        self.menu = QtWidgets.QMenu(self.view)
        if self.block.parameters:
            self.parameter_action = QtWidgets.QAction(_("Edit Parameters"), self.view)
            self.parameter_action.triggered.connect(self.parameter_window)
            self.menu.addAction(self.parameter_action)
        if isinstance(self.block, framework.DynamicBlock):
            self.add_input_action = QtWidgets.QAction(_("Add Input"), self.view)
            self.add_input_action.triggered.connect(self.new_input)
            if self.block.dynamic_input[1] and len(self.block.inputs) == self.block.dynamic_input[1]:
                self.add_input_action.setEnabled(False)
            self.menu.addAction(self.add_input_action)
            self.delete_input_action = QtWidgets.QAction(_("Delete Input"), self.view)
            self.delete_input_action.triggered.connect(self.delete_input)
            if self.block.dynamic_input[0] and len(self.block.inputs) == self.block.dynamic_input[0]:
                self.delete_input_action.setEnabled(False)
            self.menu.addAction(self.delete_input_action)
        if callable(getattr(self.block, "show", None)):
            self.show_plot_action = QtWidgets.QAction(_("Show Plot"), self.view)
            self.show_plot_action.triggered.connect(self.block.show)
            self.menu.addAction(self.show_plot_action)
        self.delete_action = QtWidgets.QAction(_("Delete Block"), self.view)
        self.delete_action.triggered.connect(self.delete)
        self.menu.addAction(self.delete_action)

    def boundingRect(self, *args, **kwargs):
        return QtCore.QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        painter.setBrush(QtGui.QBrush(QtGui.QColor(122, 122, 122)))
        painter.drawRoundedRect(0, 0, self.width, self.height, 5, 5)
        painter.drawText(5, 2, self.width-5, 20, 0, self.block.parameters["name"].value)
        if self.block.parameters["name"].value != self.block.name:
            painter.drawText(5, 22, self.width-5, 20, 0, self.block.name)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        painter.drawRoundedRect(self.width-20, self.height-20, 20, 20, 5, 5)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        painter.drawLine(self.width-10, self.height-20, self.width-10, self.height)
        painter.drawLine(self.width-20, self.height-10, self.width, self.height-10)

    def contextMenuEvent(self, e):
        self.menu.exec_(e.screenPos())

    def delete_input(self):
        self.inputs[-1].disconnect()
        self.block.delete_input(-1)
        self.scene().removeItem(self.inputs.pop(-1))
        if self.block.dynamic_input[0] and len(self.block.inputs) == self.block.dynamic_input[0]:
            self.delete_input_action.setEnabled(False)
        if self.block.dynamic_input[1] and len(self.block.inputs) < self.block.dynamic_input[1]:
            self.add_input_action.setEnabled(True)

    def new_input(self):
        new_mca_input = framework.block_io.Input(self.block)
        self.block.add_input(new_mca_input)
        self.add_new_input(new_mca_input)
        if self.block.dynamic_input[1] and len(self.block.inputs) == self.block.dynamic_input[1]:
            self.add_input_action.setEnabled(False)
        if self.block.dynamic_input[0] and len(self.block.inputs) > self.block.dynamic_input[0]:
            self.delete_input_action.setEnabled(True)

    def delete(self):
        for i in self.inputs:
            i.disconnect()
        for o in self.outputs:
            o.disconnect()
        self.scene().removeItem(self)

    @QtCore.Slot()
    def parameter_window(self):
        if self.block.parameters:
            window = ParameterWindow(self.block)
            window.exec_()
        self.update()

    def add_new_input(self, input):
        new_input = InputItem(-self.input_width, len(self.inputs)*(self.input_height + self.input_dist) + 5,
                              self.input_width, self.input_height, input, self.view, self)
        self.inputs.append(new_input)
        if len(self.inputs) * (self.input_height + self.input_dist) + 5 > self.height:
            self.resize(self.width, len(self.inputs) * (self.input_height + self.input_dist) + 5)

    def add_new_output(self, output):
        new_output = OutputItem(self.width, len(self.outputs)*(self.output_height + self.output_dist) + 5,
                                self.output_width, self.output_height, output, self.view, self)
        self.outputs.append(new_output)
        if len(self.outputs) * (self.output_height + self.output_dist) + 5 > self.height:
            self.resize(self.width, len(self.outputs) * (self.output_height + self.output_dist) + 5)

    def itemChange(self, change, value):
        if change == self.ItemPositionChange:
            for i in self.inputs:
                i.update_connection_line()
            for o in self.outputs:
                o.update_connection_line()
        return super().itemChange(change, value)

    def mouseDoubleClickEvent(self, e):
        if self.block.parameters:
            self.parameter_window()

    def mousePressEvent(self, e):
        if e.button() == QtCore.Qt.MouseButton.RightButton:
            e.ignore()
        self.setZValue(1.0)
        if e.pos().x() > self.width - 20 and e.pos().y() > self.height - 20:
            self.resize_mode = True
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if self.resize_mode:
            if self.last_point[0] is not None and self.last_point[1] is not None:
                self.resize(self.width + e.screenPos().x() - self.last_point[0], self.height + e.screenPos().y() - self.last_point[1])
            self.last_point = (e.screenPos().x(), e.screenPos().y())
        else:
            super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        self.setZValue(0.0)
        self.resize_mode = False
        self.last_point = (None, None)
        super().mouseReleaseEvent(e)

    def resize(self, width, height):
        if max(len(self.outputs) * (self.output_height + self.output_dist) + 5,
               len(self.inputs) * (self.input_height + self.input_dist) + 5) > height or height < self.min_heigth:
            return
        if width < self.min_width:
            return
        for o in self.outputs:
            o.setPos(width, o.pos().y())
            o.update_connection_line()
        self.scene().update(self.scenePos().x(), self.scenePos().y(), self.width, self.height)
        self.height = height
        self.width = width
        self.update()
