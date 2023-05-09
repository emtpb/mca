from scipy.signal import csd
from united import Unit

from mca.framework import Block, data_types, parameters, util


class CrossPowerSpectrum(Block):
    """Computes the cross power spectrum of the input signals."""
    name = "CrossPowerSpectrum"
    description = ("Computes the cross power spectrum of the "
                   "input signals.")
    tags = ("Processing",)

    def setup_io(self):
        self.new_output(metadata=data_types.MetaData(
            name="",
            unit_a="1/s",
            unit_o="V*V",
            quantity_a="Frequency"
        ))
        self.new_input()
        self.new_input()

    def setup_parameters(self):
        self.parameters["window"] = parameters.ChoiceParameter(
            name="Window",
            choices=[
                ("boxcar", "Rectangle"),
                ("hann", "Hann"),
                ("hamming", "Hamming"),
                ("triangle", "Triangle")], default="hann")
        self.parameters["seg_length"] = parameters.IntParameter(
            name="Segment Length", min_=1, default=100)
        self.parameters["seg_overlap"] = parameters.IntParameter(
            name="Segment Overlap", min_=0, default=10)
        self.parameters["fft_length"] = parameters.IntParameter(
            name="FFT Length", min_=1, default=100)
        self.parameters["scaling"] = parameters.ChoiceParameter(
            name="Scaling", choices=[("density", "Density"),
                                        ("spectrum", "Spectrum")],
            default="spectrum")

    @util.abort_any_inputs_empty
    @util.validate_type_signal
    @util.validate_intervals
    def process(self):
        # Read the input data
        first_signal = self.inputs[0].data
        second_signal = self.inputs[1].data
        # Read parameters values
        window = self.parameters["window"].value
        seg_length = self.parameters["seg_length"].value
        seg_overlap = self.parameters["seg_overlap"].value
        fft_length = self.parameters["fft_length"].value
        scaling = self.parameters["scaling"].value
        # Calculate the ordinate
        freq, power_density = csd(x=first_signal.ordinate,
                                  y=second_signal.ordinate,
                                  fs=1 / first_signal.increment,
                                  window=window,
                                  nperseg=seg_length,
                                  noverlap=seg_overlap,
                                  nfft=fft_length,
                                  scaling=scaling
                                  )
        # Calculate the abscissa start
        abscissa_start = freq[0]
        # Calculate the amount of values
        values = len(freq)
        # Calculate the increment
        increment = 1 / (
                first_signal.increment * values)
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=power_density,
        )
        # Calculate units for abscissa and ordinate
        unit_o = self.inputs[0].metadata.unit_o * self.inputs[1].metadata.unit_o
        unit_a = 1 / self.inputs[0].metadata.unit_a
        # Divide ordinate unit by abscissa in case of density scaling
        if scaling == "density":
            unit_o = Unit(numerators=[unit_o.repr], denominators=[unit_a.repr],
                          fix_repr=True)
        # Apply new metadata to the output
        self.outputs[0].process_metadata = data_types.MetaData(
            name=None, unit_a=unit_a, unit_o=unit_o
        )
