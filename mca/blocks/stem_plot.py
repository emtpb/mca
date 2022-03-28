import numpy as np
import matplotlib.pyplot as plt

from mca.framework import validator, data_types, parameters, Block
from mca.language import _


class StemPlot(Block):
    """Plots the input signal in a stem plot.

    Attributes:
        fig: Figure for plotting data.
        axes: Axes object of the figure.
        legend: Legend of the plot.
        line: Line container of the stem plot.
    """
    name = _("StemPlot")
    description = _("Plots all input signals as lines in a single figure.")
    tags = (_("Plotting"),)

    def __init__(self, **kwargs):
        """Initializes StemPlot class."""
        super().__init__(**kwargs)
        self.fig = plt.figure()
        self.axes = self.fig.add_subplot(111)
        self.axes.grid(True)
        self.legend = None
        self.line = None

    def setup_parameters(self):
        self.parameters.update({
            "show": parameters.ActionParameter(_("Show plot"), self.show),
            "auto_show": parameters.BoolParameter(_("Auto plot"), False)
        })

    def setup_io(self):
        self.new_input()

    def _process(self):
        if self.line:
            self.line.remove()
            self.line = None
        if self.legend:
            self.legend.remove()
            self.legend = None
        if self.all_inputs_empty():
            self.fig.canvas.draw()
            return
        signal = self.inputs[0].data
        validator.check_type_signal(self.inputs[0].data)
        auto_show = self.parameters["auto_show"].value

        abscissa = np.linspace(signal.abscissa_start,
                               signal.abscissa_start + signal.increment * (signal.values - 1),
                               signal.values)
        ordinate = signal.ordinate
        label = signal.metadata.name
        self.line = self.axes.stem(abscissa, ordinate, label=label,
                                   use_line_collection=True)
        if label:
            self.legend = self.fig.legend()
        metadata = signal.metadata
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
