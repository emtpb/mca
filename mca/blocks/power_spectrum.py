from scipy.signal import welch
from united import Unit

from mca.framework import validator, data_types, Block, util, parameters
from mca.language import _


class PowerSpectrum(Block):
    """Computes the power spectrum of the input signal using Welch's
    method."""
    name = _("PowerSpectrum")
    description = _("Computes the power spectrum of the input signal using "
                    "Welch's method")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output(metadata=data_types.MetaData(
            "",
            unit_a="1/s",
            unit_o="V*V",
            quantity_a=_("Frequency")
        ))
        self.new_input()

    def setup_parameters(self):
        self.parameters["window"] = parameters.ChoiceParameter(
            name=_("Window"),
            choices=[
                ("boxcar", _("Rectangle")),
                ("hann", _("Hann")),
                ("hamming", _("Hamming")),
                ("triangle", _("Triangle"))], default="hann")
        self.parameters["seg_length"] = parameters.IntParameter(
            name=_("Segment Length"), min_=1, default=100)
        self.parameters["seg_overlap"] = parameters.IntParameter(
            name=_("Segment Overlap"), min_=0, default=10)
        self.parameters["fft_length"] = parameters.IntParameter(
            name=_("FFT Length"), min_=1, default=100)
        self.parameters["scaling"] = parameters.ChoiceParameter(
            name=_("Scaling"), choices=[("density", _("Density")),
                                        ("spectrum", _("Spectrum"))],
            default="spectrum")

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def _process(self):
        input_signal = self.inputs[0].data
        window = self.parameters["window"].value
        seg_length = self.parameters["seg_length"].value
        seg_overlap = self.parameters["seg_overlap"].value
        fft_length = self.parameters["fft_length"].value
        scaling = self.parameters["scaling"].value
        freq, power_density = welch(x=input_signal.ordinate,
                                    fs=1 / input_signal.increment,
                                    window=window,
                                    nperseg=seg_length,
                                    noverlap=seg_overlap,
                                    nfft=fft_length,
                                    scaling=scaling
                                    )
        abscissa_start = freq[0]
        values = len(freq)
        increment = freq[1] - freq[0]
        unit_a = 1 / self.inputs[0].metadata.unit_a
        unit_o = self.inputs[0].metadata.unit_o ** 2
        if scaling == "density":
            unit_o = Unit([unit_o.repr], [unit_a.repr], fix_repr=True)
        metadata = data_types.MetaData(None, unit_a, unit_o)
        self.outputs[0].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=power_density,
        )
        self.outputs[0].external_metadata = metadata
