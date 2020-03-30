from PySide2 import QtWidgets


class BaseWidget:
    def __init__(self, parameter, parent):
        self.parameter = parameter
        self.setParent(parent)

    def set_parameter(self):
        pass

    def read_parameter(self):
        pass


class FloatWidget(BaseWidget, QtWidgets.QLineEdit):
    def __init__(self, parameter, parent):
        QtWidgets.QLineEdit.__init__(self)
        BaseWidget.__init__(self, parameter, parent)

    def set_parameter(self):
        self.parameter.value = float(self.text())

    def read_parameter(self):
        self.setText(str(self.parameter.value))


class IntWidget(BaseWidget, QtWidgets.QLineEdit):
    def __init__(self, parameter, parent):
        QtWidgets.QLineEdit.__init__(self)
        BaseWidget.__init__(self, parameter, parent)

    def set_parameter(self):
        self.parameter.value = int(self.text())

    def read_parameter(self):
        self.setText(str(self.parameter.value))


class ChoiceWidget(BaseWidget, QtWidgets.QComboBox):
    def __init__(self, parameter, parent):
        QtWidgets.QComboBox.__init__(self)
        BaseWidget.__init__(self, parameter, parent)
        for i in range(len(self.parameter.choices)):
            self.addItem(self.parameter.choices[i][1], userData=self.parameter.choices[i][0])

    def set_parameter(self):
        index = self.findText(self.currentText())
        data = self.itemData(index)
        self.parameter.value = data

    def read_parameter(self):
        for i in range(len(self.parameter.choices)):
            if self.parameter.choices[i][0] == self.parameter.value:
                self.setCurrentText(self.parameter.choices[i][1])


class StringWidget(BaseWidget, QtWidgets.QLineEdit):
    def __init__(self, parameter, parent):
        QtWidgets.QLineEdit.__init__(self)
        BaseWidget.__init__(self, parameter, parent)

    def set_parameter(self):
        self.parameter.value = self.text()

    def read_parameter(self):
        self.setText(self.parameter.value)


class BoolWidget(BaseWidget, QtWidgets.QCheckBox):
    def __init__(self, parameter, parent):
        QtWidgets.QCheckBox.__init__(self)
        BaseWidget.__init__(self, parameter, parent)

    def set_parameter(self):
        self.parameter.value = self.isChecked()

    def read_parameter(self):
        self.setChecked(self.parameter.value)
