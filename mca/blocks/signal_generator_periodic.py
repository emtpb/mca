import numpy as np
from scipy import signal as sgn

from mca.framework import Block, data_types, parameters, util


class SignalGeneratorPeriodic(Block):
    """Generates a periodic sinus, cosine, rectangle or triangle signal."""

    name = "Signal Generator (Periodic)"
    description = "Generates a periodic sinus, cosine, rectangle or triangle signal."
    tags = ("Generating",)

    def setup_io(self):
        self.new_output(user_metadata_required=True)

    def setup_parameters(self):
        self.parameters["signal_type"] = parameters.ChoiceParameter(
            name="Signal type",
            choices=(
                ("rect", "Rectangle"),
                ("tri", "Triangle"),
                ("sin", "Sine"),
                ("cos", "Cosine"),
            ),
            default="sin",
        )
        self.parameters["freq"] = parameters.FloatParameter(
            name="Frequency", unit="Hz", min_=0, default=1
        )
        self.parameters["amp"] = parameters.FloatParameter(
            name="Amplitude", min_=0, default=1
        )
        radiant = parameters.FloatParameter(name="Radiant", default=0, unit="rad")
        degree = parameters.FloatParameter(name="Degree", default=0, unit="°")

        # Define the conversions between the parameters
        def degree_to_radiant():
            radiant.value = (degree.value / 360) * 2 * np.pi

        def radiant_to_degree():
            degree.value = radiant.value / (2 * np.pi)

        conversion = parameters.ParameterConversion(
            [radiant], [degree], radiant_to_degree
        )
        conversion_1 = parameters.ParameterConversion(
            [degree], [radiant], degree_to_radiant
        )
        # Create a parameter block of the amplification parameters
        phase = parameters.ParameterBlock(
            name="Phase",
            parameters={"degree": degree, "radiant": radiant},
            param_conversions=[conversion_1, conversion],
            default_conversion=0,
        )

        self.parameters["phase"] = phase

        abscissa = util.create_abscissa_parameter_block()
        self.parameters["abscissa"] = abscissa

    def process(self):
        # Read parameters values
        amp = self.parameters["amp"].value
        freq = self.parameters["freq"].value
        abscissa_start = self.parameters["abscissa"].parameters["start"].value
        values = self.parameters["abscissa"].parameters["values"].value
        increment = self.parameters["abscissa"].parameters["increment"].value
        phase = self.parameters["phase"].parameters["radiant"].value
        signal_type = self.parameters["signal_type"].value
        # Calculate the abscissa
        abscissa = np.linspace(
            abscissa_start, abscissa_start + (values - 1) * increment, values
        )
        # Apply different signal types to calculate the ordinate
        if signal_type == "cos":
            ordinate = amp * np.cos(2 * np.pi * freq * abscissa - phase)
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
    tri = amp * sgn.sawtooth(2 * np.pi * freq * abscissa - phase + np.pi / 2, 0.5)
    return tri


def rect(abscissa, freq, amp, phase):
    """Generates a rectangular signal."""
    return amp * np.sign(np.sin(2 * np.pi * freq * abscissa - phase))
