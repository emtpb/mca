from scipy.signal import stft

from mca.framework import PlotBlock, data_types, parameters, validator
from mca.language import _


class STFTPlot(PlotBlock):
    """Plots the Short-Time Fourier Transformation of the input signal."""
    name = _("STFTPlot")
    description = _("Plots the Short-Time Fourier Transformation of the "
                    "input signal.")
    tags = (_("Plotting"), _("Fouriertransformation"))

    def __init__(self, **kwargs):
        """Initializes STFTPlot class."""
        super().__init__(rows=1, cols=1, **kwargs)
        self.color_bar = None

    def setup_io(self):
        self.new_input()

    def setup_parameters(self):
        self.parameters["window"] = parameters.ChoiceParameter(
                name=_("Window"),
                choices=(("boxcar", _("Rectangle")),
                         ("hann", _("Hann")),
                         ("hamming", _("Hamming")),
                         ("triangle", _("Triangle"))
                        ),
                default="hann"
        )
        self.parameters["seg_length"] = parameters.IntParameter(
                name=_("Segment Length"), min_=1, default=20
        )
        self.parameters["seg_overlap"] = parameters.IntParameter(
                name=_("Segment Overlap"), min_=0, default=10
        )
        self.parameters["fft_length"] = parameters.IntParameter(
                name=_("FFT Length"), min_=1, default=20
        )

    def setup_plot_parameters(self):
        self.plot_parameters["cmap"] = parameters.ChoiceParameter(
            name=_("Colormap"),
            choices=(("viridis", _("Viridis")),
                     ("plasma", _("Plasma")),
                     ("inferno", _("Inferno")),
                     ("magma", _("Magma")),
                     ("cividis", _("Cividis"))
                     ),
            default="viridis"
        )

    def process(self):
        # Clear the axes and the color bar
        if self.color_bar:
            self.color_bar.remove()
            self.color_bar = None
        self.axes.cla()
        # Draw empty plot when input has no data
        if self.all_inputs_empty():
            self.fig.canvas.draw()
            return
        # Validate the input data of type signal
        validator.check_type_signal(self.inputs[0].data)
        # Read the input data
        input_signal = self.inputs[0].data
        # Read the parameters values
        window = self.parameters["window"].value
        seg_length = self.parameters["seg_length"].value
        seg_overlap = self.parameters["seg_overlap"].value
        fft_length = self.parameters["fft_length"].value
        # Read plot parameters values
        cmap = self.plot_parameters["cmap"].value
        # Calculate the stft of the input signal
        f, t, z = stft(x=input_signal.ordinate, fs=1 / input_signal.increment,
                       window=window, nperseg=seg_length, noverlap=seg_overlap,
                       nfft=fft_length)
        # Plot the stft
        im = self.axes.pcolormesh(t, f, abs(z), cmap=cmap)
        # Add the colorbar
        self.color_bar = self.fig.colorbar(im, ax=self.axes)
        # Get the new metadata
        metadata = data_types.MetaData(self.inputs[0].metadata.name,
                                       unit_a=self.inputs[0].metadata.unit_a,
                                       unit_o=1 / self.inputs[0].metadata.unit_a)
        # Set axis label depending on the metadata
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
        # Use grid
        self.axes.grid(True)
        # Draw the plot
        self.fig.canvas.draw()
