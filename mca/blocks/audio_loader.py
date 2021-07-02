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

    def setup_parameters(self):
        self.parameters.update(
            {"sampling_freq": parameters.IntParameter(_("Sampling frequency"),
                                                      0, None, "Hz", 44100),
             "file_name": parameters.PathParameter(_("Filename"), [".wav"],
                                                  loading=True),
             "load_file": parameters.ActionParameter(_("Load file"),
                                                     self.load_wav),
             })

    def setup_io(self):
        self._new_output(
            meta_data=data_types.default_meta_data(),
            meta_data_input_dependent=False,
            ordinate_meta_data=True,
            abscissa_meta_data=True,
        )

    def _process(self):
        pass

    def load_wav(self):
        """Reads a .wav and puts the data on the first output."""
        filename = self.parameters["file_name"].value
        if not filename.endswith(".wav"):
            raise exceptions.DataLoadingError("File has to be a .wav")
        try:
            rate, data = scipy.io.wavfile.read(filename)
        except FileNotFoundError:
            raise exceptions.DataLoadingError("File not found")
        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].meta_data,
            abscissa_start=0,
            values=len(data),
            increment=1/rate,
            ordinate=data)
        self.trigger_update()
