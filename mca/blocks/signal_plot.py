import numpy as np
import matplotlib.pyplot as plt
import copy

import mca.framework
from mca.framework import validator
from mca.language import _


class SignalPlot(mca.framework.DynamicBlock):
    """This block class plots all input signals.

    This block has at least one input and no upper limit for the inputs.
    """
    name = "SignalPlot"
    description = _("Plots all input signals in matplotlib.")

    def __init__(self, **kwargs):
        super().__init__()

        self.dynamic_input = [1, None]
        self._new_input()
        self.read_kwargs(kwargs)
        self.fig = plt.figure()
        self.parameters.update({
            "show": mca.framework.parameters.ActionParameter("Show",
                                                             self.show),
            "auto_show": mca.framework.parameters.BoolParameter("Auto plot",
                                                                False)
        })

    def _process(self):
        plt.close(self.fig)
        for i in self.inputs:
            validator.check_type_signal(i.data)
        signals = [copy.copy(i.data) for i in self.inputs if i.data]
        abscissa_units = [signal.meta_data.unit_a for signal in signals]
        ordinate_units = [signal.meta_data.unit_o for signal in signals]
        validator.check_same_units(abscissa_units)
        validator.check_same_units(ordinate_units)
        auto_show = self.parameters["auto_show"].value
        self.fig = plt.figure()
        for signal in signals:
            plt.plot(
                np.linspace(
                    signal.abscissa_start,
                    signal.abscissa_start
                    + signal.increment * (signal.values - 1),
                    signal.values,
                ),
                signal.ordinate,
                label=signal.meta_data.name,
            )
        plt.legend()
        if len(signals) >= 1:
            meta_data = signals[0].meta_data
            plt.xlabel(mca.framework.data_types.meta_data_to_axis_label(
                quantity=meta_data.quantity_a,
                unit=meta_data.unit_a,
                symbol=meta_data.symbol_a
            )
            )
            plt.ylabel(mca.framework.data_types.meta_data_to_axis_label(
                quantity=meta_data.quantity_o,
                unit=meta_data.unit_o,
                symbol=meta_data.symbol_o
            )
            )
        plt.grid(True)
        if auto_show:
            self.fig.show()

    def show(self):
        self.fig.show()
