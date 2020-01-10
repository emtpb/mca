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

    def _process(self):
        plt.close(self.fig)
        for i in self.inputs:
            validator.check_type_signal(i.data)
        signals = [copy.deepcopy(i.data) for i in self.inputs if i.data]
        self.fig = plt.figure()
        for signal in signals:
            plt.plot(
                np.linspace(
                    signal.abscissa_start,
                    signal.abscissa_start
                    + signal.increment * (signal.values-1),
                    signal.values,
                ),
                signal.ordinate,
                label=signal.meta_data.name,
            )
        plt.legend()

        if len(signals) == 1:
            meta_data = signals[0].meta_data
            plt.xlabel(
                "{} {} / {}".format(
                    meta_data.quantity_a, meta_data.symbol_a, meta_data.unit_a
                )
            )
            plt.ylabel(
                "{} {} / {}".format(
                    meta_data.quantity_o, meta_data.symbol_o, meta_data.unit_o
                )
            )
        plt.grid(True)

    def show(self):
        self.fig.show()
