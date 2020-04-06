from PySide2 import QtWidgets


class BaseWidget:
    """Basic widget class for all specific parameter widgets.

    Attributes:
        parameter: Given parameter to display.
    """
    def __init__(self, parameter, parent):
        """Initialize BaseWidget class.

        Args:
            parameter: Given parameter to display.
            parent: Parent of the widget.
        """
        self.parameter = parameter
        self.setParent(parent)

    def set_parameter(self):
        """Takes the current value in the widget and sets it in the parameter."""
        pass

    def read_parameter(self):
        """Reads the current value in the parameter and sets it in the widget."""
        pass


class FloatWidget(BaseWidget, QtWidgets.QLineEdit):
    """Widget to display a FloatParameter."""
    def __init__(self, parameter, parent):
        """Initialize FloatWidget class."""
        QtWidgets.QLineEdit.__init__(self)
        BaseWidget.__init__(self, parameter, parent)

    def set_parameter(self):
        self.parameter.value = float(self.text())

    def read_parameter(self):
        self.setText(str(self.parameter.value))


class IntWidget(BaseWidget, QtWidgets.QLineEdit):
    """Widget to display a IntParameter."""
    def __init__(self, parameter, parent):
        """Initialize IntWidget class."""
        QtWidgets.QLineEdit.__init__(self)
        BaseWidget.__init__(self, parameter, parent)

    def set_parameter(self):
        self.parameter.value = int(self.text())

    def read_parameter(self):
        self.setText(str(self.parameter.value))


class ChoiceWidget(BaseWidget, QtWidgets.QComboBox):
    """Widget to display a ChoiceParameter."""
    def __init__(self, parameter, parent):
        """Initialize ChoiceWidget class."""
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
    """Widget to display a StringParameter."""
    def __init__(self, parameter, parent):
        """Initialize StringWidget class."""
        QtWidgets.QLineEdit.__init__(self)
        BaseWidget.__init__(self, parameter, parent)

    def set_parameter(self):
        self.parameter.value = self.text()

    def read_parameter(self):
        self.setText(self.parameter.value)


class BoolWidget(BaseWidget, QtWidgets.QCheckBox):
    """Widget to display a BoolParameter."""
    def __init__(self, parameter, parent):
        """Initialize BoolWidget class."""
        QtWidgets.QCheckBox.__init__(self)
        BaseWidget.__init__(self, parameter, parent)

    def set_parameter(self):
        self.parameter.value = self.isChecked()

    def read_parameter(self):
        self.setChecked(self.parameter.value)
