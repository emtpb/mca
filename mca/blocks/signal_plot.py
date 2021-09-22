import numpy as np
import matplotlib.pyplot as plt
import copy

from mca.framework import validator, data_types, parameters, DynamicBlock
from mca.language import _


class SignalPlot(DynamicBlock):
    """Plots all input signals in single figure.

    Attributes:
        fig: Figure for plotting data.
        axes: Reference of the axes.
        legend: Reference of the legend.
    """
    name = _("SignalPlot")
    description = _("Plots all input signals in a single figure.")
    tags = (_("Plotting"),)

    def __init__(self, **kwargs):
        """Initializes SignalPlot class."""
        super().__init__(**kwargs)
        self.fig = plt.figure()
        self.axes = self.fig.add_subplot(111)
        self.legend = None

    def setup_parameters(self):
        self.parameters.update({
            "show": parameters.ActionParameter(_("Show plot"), self.show),
            "auto_show": parameters.BoolParameter(_("Auto plot"), False)
        })

    def setup_io(self):
        self.dynamic_input = [1, None]
        self._new_input()

    def _process(self):
        self.axes.cla()
        if self.legend:
            self.legend.remove()
            self.legend = None
        for i in self.inputs:
            validator.check_type_signal(i.data)

        signals = [copy.copy(i.data) for i in self.inputs if i.data]
        abscissa_units = [signal.meta_data.unit_a for signal in signals]
        ordinate_units = [signal.meta_data.unit_o for signal in signals]
        validator.check_same_units(abscissa_units)
        validator.check_same_units(ordinate_units)
        auto_show = self.parameters["auto_show"].value
        labels = False
        for signal in signals:
            abscissa = np.linspace(signal.abscissa_start,
                                   signal.abscissa_start + signal.increment * (signal.values - 1),
                                   signal.values)
            ordinate = signal.ordinate
            label = signal.meta_data.name
            if label:
                labels = True
            self.axes.plot(abscissa, ordinate, label=label)
        if labels:
            self.legend = self.fig.legend()
        if signals:
            meta_data = signals[0].meta_data
            abscissa_string = data_types.meta_data_to_axis_label(
                quantity=meta_data.quantity_a,
                unit=meta_data.unit_a,
                symbol=meta_data.symbol_a
            )
            ordinate_string = data_types.meta_data_to_axis_label(
                quantity=meta_data.quantity_o,
                unit=meta_data.unit_o,
                symbol=meta_data.symbol_o
            )
            self.axes.set_xlabel(abscissa_string)
            self.axes.set_ylabel(ordinate_string)
        self.axes.grid(True)
        self.fig.tight_layout()
        self.fig.canvas.draw()

        if auto_show:
            self.show()

    def show(self):
        """Shows the plot."""
        self.fig.show()
