import copy

import numpy as np

from mca.framework import DynamicBlock, PlotBlock, data_types, parameters, \
    validator
from mca.framework import util


class Plot(PlotBlock, DynamicBlock):
    """Plots all input signals as lines, stems or bars
    in a single figure.

    Attributes:
        fig: Figure for plotting data.
        axes: Axes object of the figure.
        legend: Legend of the plot.
        lines: Lines of the plot which correspond to the inputs.
    """
    name = "Plot"
    description = ("Plots all input signals as lines, stems or bars "
                   "in a single figure.")
    tags = ("Plotting",)

    def __init__(self, **kwargs):
        """Initializes Plot class."""
        super().__init__(rows=1, cols=1, **kwargs)
        self.legend = None
        self.lines = []

    def setup_parameters(self):
        pass

    def setup_plot_parameters(self):
        self.plot_parameters["plot_kind"] = parameters.ChoiceParameter(
                name="Plot kind", choices=(("line", "Line"),
                                            ("stem", "Stem"),
                                            ("bar", "Bar")),
                default="line")
        self.plot_parameters["abscissa_scaling"] = parameters.ChoiceParameter(
            name="Abscissa scaling",
            choices=(("linear", "Linear"), ("log", "Log"),
                     ("symlog", "Symmetrcial log"), ("logit", "Logit")),
            default="linear"
        )
        self.plot_parameters["ordinate_scaling"] = parameters.ChoiceParameter(
            name="Ordinate scaling",
            choices=(("linear", "Linear"), ("log", "Log"),
                     ("symlog", "Symmetrcial log"), ("logit", "Logit")),
            default="linear"
        )
        self.plot_parameters["marker"] = util.get_plt_marker_parameter()

    def setup_io(self):
        self.dynamic_input = [1, None]
        self.new_input()

    def process(self):
        # Clear the axes and the legend
        self.axes.cla()
        if self.legend:
            self.legend.remove()
            self.legend = None
        # Validate the input data of type signal
        for i in self.inputs:
            validator.check_type_signal(i.data)
        # Read the input data
        signals = [copy.copy(i.data) for i in self.inputs if i.data]
        # Read the input metadata
        metadatas = [copy.copy(i.metadata) for i in self.inputs if i.metadata]
        # Read the input metadata units
        abscissa_units = [metadata.unit_a for metadata in metadatas]
        ordinate_units = [metadata.unit_o for metadata in metadatas]
        # Validate the abscissa and ordinate units
        validator.check_same_units(abscissa_units)
        validator.check_same_units(ordinate_units)
        # Read plot parameters values
        plot_kind = self.plot_parameters["plot_kind"].value
        abscissa_scaling = self.plot_parameters["abscissa_scaling"].value
        ordinate_scaling = self.plot_parameters["ordinate_scaling"].value
        marker = self.plot_parameters["marker"].value

        labels_exist = any([metadata.name for metadata in metadatas])
        # Iterate over every signal and its metadata to plot it
        for (index, signal), metadata in zip(enumerate(signals), metadatas):
            # Create the abscissa vector
            abscissa = np.linspace(signal.abscissa_start,
                                   signal.abscissa_start + signal.increment * (
                                               signal.values - 1),
                                   signal.values)
            ordinate = signal.ordinate
            label = metadata.name
            # Plot and pass plot parameters
            if plot_kind == "line":
                self.axes.plot(abscissa, ordinate, f"C{index}", label=label,
                               marker=marker,
                               markerfacecolor=f"C{index}")
            elif plot_kind == "stem":
                self.axes.stem(abscissa, ordinate, f"C{index}", label=label,
                               use_line_collection=True, basefmt=" ",
                               markerfmt=f"C{index}{marker}")
            elif plot_kind == "bar":
                self.axes.bar(abscissa, ordinate, label=label,
                              color=f"C{index}",
                              align="edge", width=signal.increment)
        # If any of the metadata of the inputs is named then create a legend
        if labels_exist:
            self.legend = self.fig.legend()
        # Set the x and y labels depending on the metadata of the inputs
        if signals:
            metadata = metadatas[0]
            abscissa_string = data_types.metadata_to_axis_label(
                quantity=metadata.quantity_a,
                unit=metadata.unit_a,
                symbol=metadata.symbol_a
            )
            ordinate_string = data_types.metadata_to_axis_label(
                quantity=metadata.quantity_o,
                unit=metadata.unit_o,
                symbol=metadata.symbol_o
            )
            self.axes.set_xlabel(abscissa_string)
            self.axes.set_ylabel(ordinate_string)
        # Set the scalings
        self.axes.set_xscale(abscissa_scaling)
        self.axes.set_yscale(ordinate_scaling)
        # Use grids
        self.axes.grid(True)
        # Draw the plot
        self.fig.canvas.draw()
