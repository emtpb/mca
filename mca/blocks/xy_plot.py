from mca import exceptions
from mca.framework import parameters, data_types, util, PlotBlock
from mca.language import _


class XYPlot(PlotBlock):
    """Plots the ordinates of the input signals against each other."""
    name = _("XYPlot")
    description = _("Plots the ordinates of the input signals against "
                    "each other.")
    tags = (_("Plotting"),)

    def __init__(self, **kwargs):
        """Initializes XYPlot class."""
        super().__init__(rows=1, cols=1, **kwargs)

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

    def setup_plot_parameters(self):
        self.plot_parameters["color"] = util.get_plt_color_parameter()
        self.plot_parameters["marker"] = util.get_plt_marker_parameter()

    def _process(self):
        self.axes.cla()
        if self.any_inputs_empty():
            self.fig.canvas.draw()
            return
        y_axis = self.parameters["y_axis"].value
        x_axis = self.parameters["x_axis"].value
        marker = self.plot_parameters["marker"].value
        color = self.plot_parameters["color"].value

        if y_axis == "first":
            input_signal_o = self.inputs[0].data
            metadata_o = self.inputs[0].metadata
        elif y_axis == "second":
            input_signal_o = self.inputs[1].data
            metadata_o = self.inputs[1].metadata

        ordinate = input_signal_o.ordinate
        unit_o = metadata_o.unit_o
        quantity_o = metadata_o.quantity_o
        symbol_o = metadata_o.symbol_o

        if x_axis == "first":
            input_signal_a = self.inputs[0].data
            metadata_a = self.inputs[0].metadata
        elif x_axis == "second":
            input_signal_a = self.inputs[1].data
            metadata_a = self.inputs[1].metadata

        abscissa = input_signal_a.ordinate
        unit_a = metadata_a.unit_o
        quantity_a = metadata_a.quantity_o
        symbol_a = metadata_a.symbol_o

        if len(ordinate) != len(abscissa):
            raise exceptions.IntervalError("Cannot plot ordinates with "
                                           "different lengths.")

        self.axes.scatter(abscissa, ordinate, color=color, marker=marker)
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
        self.axes.grid(True)
        self.fig.canvas.draw()
