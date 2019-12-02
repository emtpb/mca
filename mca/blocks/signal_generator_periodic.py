import numpy as np
from scipy import signal as sgn

import mca.framework
from mca.language import _


class SignalGenerator(mca.framework.Block):
    """Block class which generates a periodic signal.

    This block has one input.

    Parameters:
        function: Rect, Triangle or Sin.
        freq: Frequency of the signal (float).
        amp: Amplitude of the signal (float).
        phase: Phase shift (float).
        start_a: Start of the of the signal (float).
        values: Amount of values taken (int).
        increment: Sampling frequency (float).
    """
    name = "SignalGenerator"
    description = _("Generates a Sinus, a Rectangle function or "
                    "a Triangle function.")

    def __init__(self, **kwargs):
        super().__init__()

        self._new_output(
            meta_data=mca.framework.data_types.MetaData(
                "Test", _("Time"), "t", "s", _("Voltage"), "U", "V"
            )
        )
        self.parameters = {
            "function": mca.framework.parameters.ChoiceParameter(
                _("Function"), choices=["Rect", "Triangle", "Sin"], value="Sin"
            ),
            "freq": mca.framework.parameters.IntParameter(_("Frequency"),
                                                          unit="Hz", value=1),
            "amp": mca.framework.parameters.FloatParameter("Amplitude",
                                                           value=1),
            "phase": mca.framework.parameters.FloatParameter("Phase", value=1),
            "start_a": mca.framework.parameters.FloatParameter("Start",
                                                               value=0),
            "values": mca.framework.parameters.IntParameter(_("Values"),
                                                            min_=1, value=600),
            "increment": mca.framework.parameters.FloatParameter(
                _("Increment"), min_=0, value=0.01)
        }
        self.read_kwargs(kwargs)

    def _process(self):
        amp = self.parameters["amp"].value
        freq = self.parameters["freq"].value
        abscissa_start = self.parameters["start_a"].value
        values = self.parameters["values"].value
        increment = self.parameters["increment"].value
        phase = self.parameters["phase"].value
        function = self.parameters["function"].value
        abscissa = (
                np.linspace(
                    abscissa_start, abscissa_start + values * increment,
                    values
                )
                - phase
        )
        if function == "Sin":
            ordinate = amp * np.sin(freq * abscissa)
        elif function == "Rect":
            ordinate = rect(abscissa, freq, amp, phase)
        elif function == "Triangle":
            ordinate = triangle(abscissa, freq, amp, phase)
        self.outputs[0].data = mca.framework.data_types.Signal(
            self.outputs[0].meta_data,
            abscissa_start,
            values,
            increment,
            ordinate,
        )


def triangle(abscissa, freq, amp, phase):
    ordinate = amp * sgn.sawtooth(
        (np.pi / 2 * freq) * (abscissa - phase) + np.pi / 2, 0.5
    )
    return ordinate


def rect(abscissa, freq, amp, phase):
    return amp * np.where(((abscissa - phase) % (2 / freq)) < 1 / freq, 1, -1)
