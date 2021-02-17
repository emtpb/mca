import scipy.io.wavfile

from mca.framework import parameters, Block, data_types
from mca.language import _
from mca import exceptions


class AudioLoader(Block):
    """Reads a .wav to create an output signal.

    This block has one output.
    """
    name = _("AudioLoader")
    description = _("Reads a .wav to create an output signal.")
    tags = (_("Loading"), _("Audio"))

    def __init__(self, **kwargs):
        """Initializes the AudioInput class."""
        super().__init__()
        self._new_output(
            meta_data=data_types.MetaData(
                name="",
                unit_a="s",
                unit_o="V",
                quantity_a=_("Time"),
                quantity_o=_("Voltage")
            ),
            meta_data_input_dependent=False,
            ordinate_meta_data=True,
            abscissa_meta_data=True,
        )
        self.parameters.update(
            {"sampling_freq": parameters.IntParameter(_("Sampling frequency"),
                                                      0, None, "Hz", 44100),
             "filename": parameters.PathParameter(_("Filename"), [".wav"],
                                                  loading=True),
             "load_file": parameters.ActionParameter(_("Load file"),
                                                     self.load_wav),
             })
        self.read_kwargs(kwargs)

    def _process(self):
        pass

    def load_wav(self):
        """Reads a .wav and puts the data on the first output."""
        filename = self.parameters["filename"].value
        if not filename.endswith(".wav"):
            raise exceptions.DataLoadingError("File has to be a .wav.")
        rate, data = scipy.io.wavfile.read(filename)
        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].meta_data,
            abscissa_start=0,
            values=len(data),
            increment=1/rate,
            ordinate=data)
        self.update()
