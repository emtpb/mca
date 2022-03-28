import numpy as np
import matplotlib.pyplot as plt
import copy

from mca.framework import validator, data_types, parameters, DynamicBlock
from mca.language import _


class LinePlot(DynamicBlock):
    """Plots all input signals in single figure.

    Attributes:
        fig: Figure for plotting data.
        axes: Axes object of the figure.
        legend: Legend of the plot.
        lines: Lines of the plot which correspond to the inputs.
    """
    name = _("LinePlot")
    description = _("Plots all input signals as lines in a single figure.")
    tags = (_("Plotting"),)

    def __init__(self, **kwargs):
        """Initializes LinePlot class."""
        super().__init__(**kwargs)
        self.fig = plt.figure()
        self.axes = self.fig.add_subplot(111)
        self.axes.grid(True)
        self.legend = None
        self.lines = []

    def setup_parameters(self):
        self.parameters.update({
            "show": parameters.ActionParameter(_("Show plot"), self.show),
            "auto_show": parameters.BoolParameter(_("Auto plot"), False)
        })

    def setup_io(self):
        self.dynamic_input = [1, None]
        self.new_input()

    def _process(self):
        for line in self.lines:
            line.remove()
        if self.legend:
            self.legend.remove()
            self.legend = None
        for i in self.inputs:
            validator.check_type_signal(i.data)

        signals = [copy.copy(i.data) for i in self.inputs if i.data]
        abscissa_units = [signal.metadata.unit_a for signal in signals]
        ordinate_units = [signal.metadata.unit_o for signal in signals]

        validator.check_same_units(abscissa_units)
        validator.check_same_units(ordinate_units)

        auto_show = self.parameters["auto_show"].value

        label = None
        self.lines = []
        for index, signal in enumerate(signals):
            abscissa = np.linspace(signal.abscissa_start,
                                   signal.abscissa_start + signal.increment * (signal.values - 1),
                                   signal.values)
            ordinate = signal.ordinate
            label = signal.metadata.name
            self.lines.append(self.axes.plot(abscissa, ordinate, f"C{index}",
                                             label=label)[0])
        if label:
            self.legend = self.fig.legend()
        if signals:
            metadata = signals[0].metadata
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
        self.fig.tight_layout()
        self.fig.canvas.draw()

        if auto_show:
            self.show()

    def show(self):
        """Shows the plot."""
        self.fig.show()
