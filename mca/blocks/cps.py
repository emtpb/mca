from scipy.signal import csd
from united import Unit

from mca.framework import validator, data_types, Block, parameters
from mca.language import _


class CrossPowerSpectrum(Block):
    """Computes the cross power spectrum of the input signals."""
    name = _("CrossPowerSpectrum")
    description = _("Computes the cross power spectrum of the "
                    "input signals.")
    tags = (_("Processing"),)

    def setup_io(self):
        self.new_output(metadata=data_types.MetaData(
            "",
            unit_a="1/s",
            unit_o="V*V",
            quantity_a=_("Frequency")
        ))
        self.new_input()
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

    def _process(self):
        if self.any_inputs_empty():
            return
        validator.check_type_signal(self.inputs[0].data)
        validator.check_type_signal(self.inputs[1].data)

        first_signal = self.inputs[0].data
        second_signal = self.inputs[1].data

        validator.check_intervals([first_signal, second_signal])

        window = self.parameters["window"].value
        seg_length = self.parameters["seg_length"].value
        seg_overlap = self.parameters["seg_overlap"].value
        fft_length = self.parameters["fft_length"].value
        scaling = self.parameters["scaling"].value
        freq, power_density = csd(x=first_signal.ordinate,
                                  y=second_signal.ordinate,
                                  fs=1 / first_signal.increment,
                                  window=window,
                                  nperseg=seg_length,
                                  noverlap=seg_overlap,
                                  nfft=fft_length,
                                  scaling=scaling
                                  )

        abscissa_start = freq[0]
        values = len(freq)
        unit_o = first_signal.metadata.unit_o * second_signal.metadata.unit_o
        unit_a = 1 / first_signal.metadata.unit_a
        if scaling == "density":
            unit_o = Unit([unit_o.repr], [unit_a.repr], fix_repr=True)
        metadata = data_types.MetaData(None, unit_a, unit_o)
        increment = 1 / (
                first_signal.increment * values)
        self.outputs[0].data = data_types.Signal(
            metadata=self.outputs[0].get_metadata(metadata),
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=power_density,
        )
