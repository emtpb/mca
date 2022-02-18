import matplotlib.pyplot as plt

from mca.framework import Block, parameters, data_types
from mca.language import _

from mca import exceptions


class XYPlot(Block):
    """Plots the ordinates of the input signals against each other."""
    name = _("XYPlot")
    description = _("Plots the ordinates of the input signals against "
                    "each other.")
    tags = (_("Plotting"),)

    def __init__(self, **kwargs):
        """Initializes XYPlot class."""
        super().__init__(**kwargs)
        self.fig = plt.figure()
        self.axes = self.fig.add_subplot(111)
        self.axes.grid(True)

    def setup_io(self):
        self.new_input()
        self.new_input()

    def setup_parameters(self):
        self.parameters["y_axis"] = parameters.ChoiceParameter(
            name=_("Input signal for ordinate axis"),
            choices=[("first", _("First")),
                     ("second", _("Second"))],
            default="first"
        )
        self.parameters["x_axis"] = parameters.ChoiceParameter(
            name=_("Input signal for abscissa axis"),
            choices=[("first", _("First")),
                     ("second", _("Second"))],
            default="second"
        )
        self.parameters["show"] = parameters.ActionParameter(_("Show"), self.show)

    def _process(self):
        self.axes.lines.clear()
        if self.any_inputs_empty():
            return
        y_axis = self.parameters["y_axis"].value
        x_axis = self.parameters["x_axis"].value

        if y_axis == "first":
            input_signal_o = self.inputs[0].data
        elif y_axis == "second":
            input_signal_o = self.inputs[1].data

        metadata_o = input_signal_o.metadata
        ordinate = input_signal_o.ordinate
        unit_o = metadata_o.unit_o
        quantity_o = metadata_o.quantity_o
        symbol_o = metadata_o.symbol_o

        if x_axis == "first":
            input_signal_a = self.inputs[0].data
        elif x_axis == "second":
            input_signal_a = self.inputs[1].data

        metadata_a = input_signal_a.metadata
        abscissa = input_signal_a.ordinate
        unit_a = metadata_a.unit_o
        quantity_a = metadata_a.quantity_o
        symbol_a = metadata_a.symbol_o

        if len(ordinate) != len(abscissa):
            raise exceptions.IntervalError("Cannot plot ordinates with "
                                           "different lengths.")

        self.axes.scatter(abscissa, ordinate, color="C0")
        self.axes.set_xlabel(data_types.metadata_to_axis_label(
                quantity=quantity_a,
                unit=unit_a,
                symbol=symbol_a
            ))
        self.axes.set_ylabel(data_types.metadata_to_axis_label(
                quantity=quantity_o,
                unit=unit_o,
                symbol=symbol_o
            ))
        self.fig.tight_layout()
        self.fig.canvas.draw()

    def show(self):
        self.fig.show()
