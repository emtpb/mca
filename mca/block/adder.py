import numpy as np
import copy

import mca.base as base
from mca.datatypes import signal
from mca import validator, language


class Adder(base.dynamic_block_base.DynamicBlock):
    name = language._("Adder")
    description = language._("Adds multiple signals to one signal.")

    def __init__(self, **kwargs):
        super().__init__()

        self.dynamic_input = (1, None)
        self._new_output(
            meta_data=signal.MetaData(
                "Test", "Zeit", "t", "s", "Spannung", "U", "V"
            )
        )
        self._new_input()
        self._new_input()
        self.read_kwargs(kwargs)

    def _process(self):
        if self.check_empty_inputs():
            return
        for i in self.inputs:
            validator.check_type_signal(i)

        signals = [copy.deepcopy(i.data) for i in self.inputs if i.data]
        validator.check_intervals(signals)
        modified_signals = fill_zeros(signals)
        y = np.zeros(modified_signals[0].values)
        for sgn in modified_signals:
            y += sgn.ordinate
            abscissa_start = sgn.abscissa_start
            values = sgn.values
            increment = sgn.increment
        self.outputs[0].data = signal.Signal(
            self.outputs[0].meta_data, abscissa_start, values, increment, y
        )


def fill_zeros(signals):
    """This is a helper method for :meth:`.Adder._process`.
    
    Intervals often overlap and are not always the same. So this method
    fills up the arrays with zeros.
    """
    new_signals = []
    increment = signals[0].increment
    min_abscissa_start = min(
        list(map(lambda sgn: sgn.abscissa_start, signals))
    )
    max_abscissa_end = max(
        list(
            map(
                lambda sgn: sgn.abscissa_start + sgn.values * sgn.increment,
                signals,
            )
        )
    )
    max_values = int((max_abscissa_end - min_abscissa_start) / increment)
    for sgn in signals:
        zeros_to_beginning = round(
            (sgn.abscissa_start - min_abscissa_start) / increment
        )
        zeros_to_ending = round(
            (
                (min_abscissa_start + max_values * increment)
                - (sgn.abscissa_start + sgn.values * increment)
            )
            / increment
        )
        sgn.abscissa_start = min_abscissa_start
        sgn.values = max_values
        sgn.ordinate = np.hstack(
            (
                np.zeros(zeros_to_beginning),
                sgn.ordinate,
                np.zeros(zeros_to_ending),
            )
        )
        new_signals.append(sgn)
    return new_signals
