import numpy as np
from scipy import signal as sgn

from mca.framework import Block, data_types, parameters, util


class SignalGeneratorPeriodic(Block):
    """Generates a periodic sinus, rectangle or triangle signal."""
    name = "SignalGeneratorPeriodic"
    description = ("Generates a periodic sinus, rectangle or "
                   "triangle signal.")
    tags = ("Generating",)

    def setup_io(self):
        self.new_output(user_metadata_required=True)

    def setup_parameters(self):
        self.parameters["signal_type"] = parameters.ChoiceParameter(
            name="Signal type",
            choices=(("rect", "Rectangle"), ("tri", "Triangle"),
                     ("sin", "Sine")),
            default="sin"
        )
        self.parameters["freq"] = parameters.FloatParameter(
            name="Frequency", unit="Hz", min_=0, default=1
        )
        self.parameters["amp"] = parameters.FloatParameter(
            name="Amplitude", min_=0, default=1
        )
        self.parameters["phase"] = parameters.FloatParameter(
            name="Phase", default=0, unit="rad"
        )
        abscissa = util.create_abscissa_parameter_block()
        self.parameters["abscissa"] = abscissa

    def process(self):
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
