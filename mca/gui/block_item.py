from PySide2 import QtWidgets, QtCore, QtGui
from mca.gui.parameter_window import ParameterWindow
from mca.gui.io_items import InputItem, OutputItem
from mca import framework
from mca import exceptions


class BlockItem(QtWidgets.QGraphicsItem):

    def __init__(self, x, y, block_class):
        QtWidgets.QGraphicsItem.__init__(self)
        self.setPos(x, y)

        self.width = 100
        self.height = 100
        self.input_height = 20
        self.input_width = 10
        self.input_dist = 10
        self.output_height = 20
        self.output_width = 10
        self.output_dist = 10

        self.text = QtWidgets.QGraphicsTextItem()
        self.text.setParentItem(self)
        self.text.setPos(0, 0)
        self.text.setPlainText(block_class.name)

        self.inputs = []
        self.outputs = []
        self.block = block_class()

        self.difference = 0
        self.height = 100
        self.setToolTip("This is a test tool tip of {}".format(block_class.name))
        self.parameter_window()
        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemSendsGeometryChanges, True)
        for i in self.block.inputs:
            self.add_new_input(i)
        for o in self.block.outputs:
            self.add_new_output(o)
        # self.setFlags(self.ItemIsSelectable)

    def boundingRect(self, *args, **kwargs):
        return QtCore.QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        painter.setBrush(QtGui.QBrush(QtGui.QColor(122, 122, 122)))
        painter.drawRoundedRect(0, 0, self.width, self.height, 5, 5)

    def contextMenuEvent(self, e):
        menu = QtWidgets.QMenu(self.scene().views()[0])
        inspect_action = QtWidgets.QAction("Inspect", self.scene().views()[0])
        inspect_action.triggered.connect(self.inspect_window)
        menu.addAction(inspect_action)
        parameter_action = QtWidgets.QAction("Edit Parameters", self.scene().views()[0])
        parameter_action.triggered.connect(self.parameter_window)
        menu.addAction(parameter_action)
        if isinstance(self.block, framework.DynamicBlock):
            add_input_action = QtWidgets.QAction("Add Input", self.scene().views()[0])
            add_input_action.triggered.connect(self.new_input)
            menu.addAction(add_input_action)
            delete_input_action = QtWidgets.QAction("Delete Input", self.scene().views()[0])
            delete_input_action.triggered.connect(self.delete_input)
            menu.addAction(delete_input_action)
        if callable(getattr(self.block, "show", None)):
            show_plot_action = QtWidgets.QAction("Show Plot", self.scene().views()[0])
            show_plot_action.triggered.connect(self.block.show)
            menu.addAction(show_plot_action)
        delete_action = QtWidgets.QAction("Delete Block", self.scene().views()[0])
        delete_action.triggered.connect(self.delete)
        menu.addAction(delete_action)
        menu.exec_(e.screenPos())

    def delete_input(self):
        try:
            self.inputs[-1].disconnect()
            self.block.delete_input(-1)
            self.scene().removeItem(self.inputs.pop(-1))
        except exceptions.InputOutputError:
            return

    def new_input(self):
        try:
            new_mca_input = framework.block_io.Input(self.block)
            self.block.add_input(new_mca_input)
            self.add_new_input(new_mca_input)
        except exceptions.InputOutputError:
            return

    def delete(self):
        for i in self.inputs:
            i.disconnect()
        for o in self.outputs:
            o.disconnect()
        self.scene().removeItem(self)

    @QtCore.Slot()
    def parameter_window(self):
        window = ParameterWindow(self.block)
        window.exec_()

    @QtCore.Slot()
    def inspect_window(self):
        test = InspectWindow()
        test.exec_()

    def add_new_input(self, input):
            new_input = InputItem(-self.input_width, len(self.inputs)*(self.input_height + self.input_dist) + 5,
                                  self.input_width, self.input_height, input, self)
            self.inputs.append(new_input)
            if len(self.inputs) * (self.input_height + self.input_dist) + 5 > self.height:
                self.height = len(self.inputs) * (self.input_height + self.input_dist) + 5
                self.update()

    def add_new_output(self, output):
            new_output = OutputItem(self.width, len(self.outputs)*(self.output_height + self.output_dist) + 5,
                                    self.output_width, self.output_height, output, self)
            self.outputs.append(new_output)
            if len(self.outputs) * (self.output_height + self.output_dist) + 5 > self.height:
                self.height = len(self.outputs) * (self.output_height + self.output_dist) + 5
                self.update()

    def itemChange(self, change, value):
        if change == self.ItemPositionChange:
            for i in self.inputs:
                i.update_connection_line()
            for o in self.outputs:
                o.update_connection_line()
        return super().itemChange(change, value)
