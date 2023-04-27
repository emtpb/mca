import numpy as np
from scipy import signal as sgn

from mca.framework import Block, data_types, parameters, util
from mca.language import _


class SignalGeneratorPeriodic(Block):
    """Generates a periodic sinus, rectangle or triangle signal."""
    name = _("SignalGeneratorPeriodic")
    description = _("Generates a periodic sinus, rectangle or "
                    "triangle signal.")
    tags = (_("Generating"),)

    def setup_io(self):
        self.new_output(
            metadata_input_dependent=False,
            ordinate_metadata=True,
            abscissa_metadata=True,
        )

    def setup_parameters(self):

        self.parameters["signal_type"] = parameters.ChoiceParameter(
                name=_("Signal type"),
                choices=(("rect", _("Rectangle")), ("tri", _("Triangle")),
                         ("sin", _("Sine"))),
                default="sin"
        )
        self.parameters["signal_type"] = parameters.ChoiceParameter(
            name=_("Signal type"),
            choices=(("rect", _("Rectangle")), ("tri", _("Triangle")),
                     ("sin", _("Sine"))),
            default="sin"
        )
        self.parameters["freq"] = parameters.FloatParameter(
            name=_("Frequency"), unit="Hz", min_=0, default=1
        )
        self.parameters["amp"] = parameters.FloatParameter(
            name=_("Amplitude"), min_=0, default=1
        )
        self.parameters["phase"] = parameters.FloatParameter(
            name=_("Phase"), default=0, unit="rad"
        )
        abscissa = util.create_abscissa_parameter_block()
        self.parameters["abscissa"] = abscissa

    def _process(self):
        # Read parameters values
        amp = self.parameters["amp"].value
        freq = self.parameters["freq"].value
        abscissa_start = self.parameters["abscissa"].parameters["start"].value
        values = self.parameters["abscissa"].parameters["values"].value
        increment = self.parameters["abscissa"].parameters["increment"].value
        phase = self.parameters["phase"].value
        signal_type = self.parameters["signal_type"].value
        # Calculate the abscissa
        abscissa = (
            np.linspace(
                abscissa_start, abscissa_start + (values - 1) * increment,
                values
            )
        )
        # Apply different signal types to calculate the ordinate
        if signal_type == "sin":
            ordinate = amp * np.sin(2 * np.pi * freq * abscissa - phase)
        elif signal_type == "rect":
            ordinate = rect(abscissa, freq, amp, phase)
        elif signal_type == "tri":
            ordinate = triangle(abscissa, freq, amp, phase)
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
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
