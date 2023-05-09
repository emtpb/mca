import numpy as np

from mca.framework import validator, data_types, parameters, PlotBlock, util
from mca.language import _


class Histogramm(PlotBlock):
    """Plots absolute and relative (density) frequency of occurrences of
    values in a histogramm.
    """
    name = "Histogramm"
    description = ("Plots absolute and relative (density frequency of "
                   "occurrences of values in a histogramm.")
    tags = ("Plotting",)

    def __init__(self, **kwargs):
        """Initializes Histogramm class."""
        super().__init__(rows=1, cols=1, **kwargs)
        self.legend = None

    def setup_parameters(self):
        self.parameters["plot_type"] = parameters.ChoiceParameter(
            "Plot type", choices=(
                ("absolute", "Absolute frequency"),
                ("relative", "Relative frequency"),
                ("density", "Relative (density frequency)")),
            default = "absolute")
        self.parameters["bins"] = parameters.IntParameter("Bins",
                                                          min_=1, default=100)

    def setup_plot_parameters(self):
        self.plot_parameters["color"] = util.get_plt_color_parameter()
        self.plot_parameters["align"] = parameters.ChoiceParameter(
            name="Align", choices=(("left", "Left"), ("mid", "Mid"),
                                   ("right", "Right")),
            default="mid"
        )

    def setup_io(self):
        self.new_input()

    def process(self):
        # Clear the axes and the legend
        self.axes.cla()
        if self.legend:
            self.legend.remove()
            self.legend = None
        # Draw empty plot if the input has no data
        if self.all_inputs_empty():
            self.fig.canvas.draw()
            return
        # Read the input data
        signal = self.inputs[0].data
        # Read the input metadata
        metadata = self.inputs[0].metadata
        # Validate the input data of type signal
        validator.check_type_signal(signal)
        # Read the parameters values
        plot_type = self.parameters["plot_type"].value
        bins = self.parameters["bins"].value
        # Read plot parameters values
        align = self.plot_parameters["align"].value
        color = self.plot_parameters["color"].value
        # Adapt y label depending on the plot type
        if plot_type == "absolute":
            density = False
            y_label = "Absolute frequency of occurrence"
        elif plot_type == "relative":
            density = False
            y_label = "Relative frequency of occurrence"
        else:
            density = True
            y_label = _(
                "Relative density frequency of occurrence") + f" in {1 / metadata.unit_o}"
        # Get the label for the legend
        label = self.inputs[0].metadata.name
        # Plot and pass plot parameters
        if plot_type == "relative":
            self.axes.hist(signal.ordinate,
                           weights=np.ones(signal.ordinate.shape) / len(
                               signal.ordinate),
                           bins=bins,
                           label=label, color=color, align=align)
        else:
            self.axes.hist(signal.ordinate, bins=bins, density=density,
                           label=label, color=color, align=align)
        # Add the legend
        if label:
            self.legend = self.fig.legend()
        # Set the x label depending on the metadata of the input
        ordinate_string = data_types.metadata_to_axis_label(
            quantity=metadata.quantity_o,
            unit=metadata.unit_o,
            symbol=metadata.symbol_o
        )
        self.axes.set_ylabel(y_label)
        self.axes.set_xlabel(ordinate_string)
        # Use grids
        self.axes.grid(True)
        # Draw the plot
        self.fig.canvas.draw()
