from scipy.signal import stft
import matplotlib.pyplot as plt

from mca.framework import validator, Block, parameters, data_types
from mca.language import _


class STFTPlot(Block):
    """Plots the Short-Time Fourier Transformation of the input signal."""
    name = _("STFTPlot")
    description = _("Plots the Short-Time Fourier Transformation of the "
                    "input signal.")
    tags = (_("Plotting"), _("Fourier"))

    def __init__(self, **kwargs):
        """Initializes STFTPlot class."""
        super().__init__(**kwargs)
        self.fig = plt.figure()
        self.axes = self.fig.add_subplot(111)
        self.axes.grid(True)
        self.color_bar = None

    def setup_io(self):
        self.new_input()

    def setup_parameters(self):
        self.parameters.update({
            "window": parameters.ChoiceParameter(
                name=_("Window"),
                choices=[("hann", _("Hann")),
                         ("hamming", _("Hamming")),
                         ("triangle", _("Triangle"))],
                default="hann"),
            "seg_length": parameters.IntParameter(
                name=_("Segment Length"), min_=1, default=20),
            "seg_overlap": parameters.IntParameter(
                name=_("Segment Overlap"), min_=0, default=10),
            "fft_length": parameters.IntParameter(
                name=_("FFT Length"), min_=1, default=20),
            "show": parameters.ActionParameter(
                name=_("Show plot"), function=self.show,
                display_options=("block_button", "edit_window")
            )
        })

    def _process(self):
        if self.color_bar:
            self.color_bar.remove()
            self.color_bar = None
        self.axes.lines.clear()
        if self.all_inputs_empty():
            self.fig.canvas.draw()
            return

        validator.check_type_signal(self.inputs[0].data)
        input_signal = self.inputs[0].data

        window = self.parameters["window"].value
        seg_length = self.parameters["seg_length"].value
        seg_overlap = self.parameters["seg_overlap"].value
        fft_length = self.parameters["fft_length"].value

        f, t, z = stft(x=input_signal.ordinate, fs=1/input_signal.increment,
                       window=window, nperseg=seg_length, noverlap=seg_overlap,
                       nfft=fft_length)
        im = self.axes.pcolormesh(t, f, abs(z))
        self.color_bar = self.fig.colorbar(im, ax=self.axes)
        metadata = data_types.MetaData(input_signal.metadata.name,
                                        unit_a=input_signal.metadata.unit_a,
                                        unit_o=1/input_signal.metadata.unit_a)
        abscissa_string = data_types.metadata_to_axis_label(
            quantity=metadata.quantity_a,
            unit=metadata.unit_a,
            symbol=metadata.symbol_a
        )
        ordinate_string = data_types.metadata_to_axis_label(
            quantity=metadata.quantity_o,
            unit=metadata.unit_o,
            symbol=metadata.symbol_o
        )
        self.axes.set_xlabel(abscissa_string)
        self.axes.set_ylabel(ordinate_string)
        self.fig.tight_layout()
        self.fig.canvas.draw()

    def show(self):
        """Shows the plot."""
        self.fig.show()
