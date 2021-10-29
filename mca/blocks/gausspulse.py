import numpy as np
from scipy.signal import gausspulse

from mca.framework import data_types, parameters, helpers,  Block
from mca.language import _


class GaussPulse(Block):
    """Generates a gaussian pulse signal. Returns real- and
    imaginary part as well as the envelope.
    """
    name = _("GaussPulse")
    description = _("Generates a gaussian pulse signal. Returns real- and "
                    "imaginary part as well as the envelope.")
    tags = (_("Generating"),)

    def setup_io(self):
        self.new_output(
            name=_("Real part"),
            metadata_input_dependent=False,
            ordinate_metadata=True,
            abscissa_metadata=True,
        )
        self.new_output(
            name=_("Imaginary part"),
            metadata_input_dependent=False,
            ordinate_metadata=True,
            abscissa_metadata=True,
        )
        self.new_output(
            name=_("Envelope"),
            metadata_input_dependent=False,
            ordinate_metadata=True,
            abscissa_metadata=True,
        )

    def setup_parameters(self):
        abscissa = helpers.create_abscissa_parameter_block()
        abscissa.parameters["start"].value = -5
        self.parameters.update({
            "amp": parameters.FloatParameter("Amplitude", min_=0, default=1),
            "cfreq": parameters.FloatParameter(_("Center Frequency"), unit="Hz",
                                               min_=0, default=1),
            "bw": parameters.FloatParameter(_("Fractional bandwidth"), min_=0,
                                            max_=1, default=0.5),
            "bwr": parameters.FloatParameter(_("Reference level"), unit="dB",
                                             default=-6),
            "abscissa": abscissa,
        })

    def _process(self):
        amp = self.parameters["amp"].value
        center_freq = self.parameters["cfreq"].value
        frac_bw = self.parameters["bw"].value
        ref_level = self.parameters["bwr"].value
        abscissa_start = self.parameters["abscissa"].parameters["start"].value
        values = self.parameters["abscissa"].parameters["values"].value
        increment = self.parameters["abscissa"].parameters["increment"].value
        abscissa = (
            np.linspace(
                abscissa_start, abscissa_start + (values - 1) * increment,
                values
            )
        )
        real, imag, envelope = gausspulse(
            abscissa, fc=center_freq, bw=frac_bw,
            bwr=ref_level, retquad=True, retenv=True)
        real *= amp
        imag *= amp
        envelope *= amp
        self.outputs[0].data = data_types.Signal(
            self.outputs[0].get_metadata(None),
            abscissa_start,
            values,
            increment,
            real,
        )
        self.outputs[1].data = data_types.Signal(
            self.outputs[1].get_metadata(None),
            abscissa_start,
            values,
            increment,
            imag,
        )
        self.outputs[2].data = data_types.Signal(
            self.outputs[2].get_metadata(None),
            abscissa_start,
            values,
            increment,
            envelope,
        )
