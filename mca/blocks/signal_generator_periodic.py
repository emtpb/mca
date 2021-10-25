import numpy as np
from scipy import signal as sgn

from mca.framework import data_types, parameters, helpers,  Block
from mca.language import _


class SignalGeneratorPeriodic(Block):
    """Generates a periodic sinus, rectangle or triangle signal."""
    name = "SignalGeneratorPeriodic"
    description = _("Generates a periodic sinus, rectangle or "
                    "triangle signal.")
    tags = (_("Generating"),)

    def setup_io(self):
        self._new_output(
            meta_data_input_dependent=False,
            ordinate_meta_data=True,
            abscissa_meta_data=True,
        )

    def setup_parameters(self):
        abscissa = helpers.create_abscissa_parameter_block()
        self.parameters.update({
            "function": parameters.ChoiceParameter(
                _("Function"),
                choices=[("rect", _("Rectangle")), ("tri", _("Triangle")),
                         ("sin", _("Sine"))],
                default="sin"
            ),
            "freq": parameters.FloatParameter(_("Frequency"), unit="Hz", min_=0,
                                              default=1),
            "amp": parameters.FloatParameter("Amplitude", min_=0, default=1),
            "phase": parameters.FloatParameter("Phase", default=0, unit="rad"),
            "abscissa": abscissa,
        })

    def _process(self):
        amp = self.parameters["amp"].value
        freq = self.parameters["freq"].value
        abscissa_start = self.parameters["abscissa"].parameters["start"].value
        values = self.parameters["abscissa"].parameters["values"].value
        increment = self.parameters["abscissa"].parameters["increment"].value
        phase = self.parameters["phase"].value
        function = self.parameters["function"].value
        abscissa = (
            np.linspace(
                abscissa_start, abscissa_start + (values - 1) * increment,
                values
            )
        )
        if function == "sin":
            ordinate = amp * np.sin(2 * np.pi * freq * abscissa - phase)
        elif function == "rect":
            ordinate = rect(abscissa, freq, amp, phase)
        elif function == "tri":
            ordinate = triangle(abscissa, freq, amp, phase)
        self.outputs[0].data = data_types.Signal(
            self.outputs[0].get_meta_data(None),
            abscissa_start,
            values,
            increment,
            ordinate,
        )


def triangle(abscissa, freq, amp, phase):
    """Generates a triangular signal."""
    tri = amp * sgn.sawtooth(
        2 * np.pi * freq * abscissa - phase + np.pi / 2, 0.5)
    return tri


def rect(abscissa, freq, amp, phase):
    """Generates a rectangular signal."""
    return amp * np.sign(np.sin(2 * np.pi * freq * abscissa - phase))
