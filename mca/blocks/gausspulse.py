import numpy as np
from scipy.signal import gausspulse

from mca.framework import Block, data_types, parameters, util


class GaussPulse(Block):
    """Generates a gaussian pulse signal. Returns real- and
    imaginary part as well as the envelope.
    """
    name = "GaussPulse"
    description = ("Generates a gaussian pulse signal. Returns real- and "
                   "imaginary part as well as the envelope.")
    tags = ("Generating",)

    def setup_io(self):
        self.new_output(name="Real part", user_metadata_required=True)
        self.new_output(name="Imaginary part", user_metadata_required=True)
        self.new_output(name="Envelope", user_metadata_required=True)

    def setup_parameters(self):
        self.parameters["amp"] = parameters.FloatParameter(
            name="Amplitude", min_=0, default=1
        )
        self.parameters["cfreq"] = parameters.FloatParameter(
            name="Center Frequency", unit="Hz", min_=0, default=1
        )
        self.parameters["bw"] = parameters.FloatParameter(
            name="Fractional bandwidth", min_=0, max_=1, default=0.5
        )
        self.parameters["bwr"] = parameters.FloatParameter(
            name="Reference level", unit="dB", default=-6
        )
        abscissa = util.create_abscissa_parameter_block()
        # Start at -5 so the peak of the pulse is at 0
        abscissa.parameters["start"].value = -5
        self.parameters["abscissa"] = abscissa

    def process(self):
        # Read parameters values
        amp = self.parameters["amp"].value
        center_freq = self.parameters["cfreq"].value
        frac_bw = self.parameters["bw"].value
        ref_level = self.parameters["bwr"].value
        abscissa_start = self.parameters["abscissa"].parameters["start"].value
        values = self.parameters["abscissa"].parameters["values"].value
        increment = self.parameters["abscissa"].parameters["increment"].value
        # Calculate the abscissa
        abscissa = (
            np.linspace(
                abscissa_start, abscissa_start + (values - 1) * increment,
                values
            )
        )
        # Calculate the ordinates
        real, imag, envelope = gausspulse(
            abscissa, fc=center_freq, bw=frac_bw,
            bwr=ref_level, retquad=True, retenv=True)
        # Amplify the ordinates
        real *= amp
        imag *= amp
        envelope *= amp
        # Apply the signals to the outputs
        self.outputs[0].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=real,
        )
        self.outputs[1].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=imag,
        )
        self.outputs[2].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=envelope,
        )
