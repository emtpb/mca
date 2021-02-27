from united import Unit
import scipy.io.wavfile

from mca.framework import validator, parameters, Block
from mca.language import _
from mca import exceptions


class AudioSaver(Block):
    """Saves the input signal as a .wav file.

    This block has one input.
    """
    name = _("AudioSaver")
    description = _("Saves the input signal as a sound file")
    tags = (_("Saving"), _("Audio"))

    def __init__(self, **kwargs):
        """Initializes the AudioSaver class."""
        super().__init__()
        self._new_input()
        self.parameters.update(
            {"sampling_freq": parameters.IntParameter(_("Sampling frequency"),
                                                      1, None, "Hz", 44100),
             "filename": parameters.PathParameter(_("Filename"), [".wav"]),
             "save_file": parameters.ActionParameter(_("Save as .wav"),
                                                     self.save_as_wav)})
        self.read_kwargs(kwargs)

    def _process(self):
        pass

    def save_as_wav(self):
        """Saves the input signal as a .wav file."""
        if self.check_empty_inputs():
            raise exceptions.DataSavingError("No data to save.")
        input_signal = self.inputs[0].data
        validator.check_type_signal(input_signal)
        validator.check_same_units([input_signal.meta_data.unit_a, Unit(["s"])])
        sampling_frequency = self.parameters["sampling_freq"].value
        filename = self.parameters["filename"].value
        if not filename.endswith(".wav"):
            raise exceptions.DataSavingError("File has to be a .wav.")
        scipy.io.wavfile.write(filename, sampling_frequency,
                               input_signal.ordinate)
