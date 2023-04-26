import scipy.io.wavfile
from united import Unit

from mca import exceptions
from mca.framework import validator, parameters, Block
from mca.language import _


class AudioSaver(Block):
    """Saves the input signal as a .wav sound file."""
    name = _("AudioSaver")
    description = _("Saves the input signal as a .wav sound file.")
    tags = (_("Saving"), _("Audio"))

    def setup_parameters(self):
        self.parameters.update(
            {"sampling_freq": parameters.IntParameter(_("Sampling frequency"),
                                                      1, None, "Hz", 44100),
             "file_name": parameters.PathParameter(_("Filename"), [".wav"]),
             "save_file": parameters.ActionParameter(_("Save as .wav"),
                                                     self.save_as_wav)})

    def setup_io(self):
        self.new_input()

    def _process(self):
        pass

    def save_as_wav(self):
        """Saves the input signal as a .wav file."""
        if self.all_inputs_empty():
            raise exceptions.DataSavingError("No data to save.")
        input_signal = self.inputs[0].data
        validator.check_type_signal(input_signal)
        validator.check_same_units([self.inputs[0].metadata.unit_a,
                                    Unit(["s"])])
        sampling_frequency = self.parameters["sampling_freq"].value
        filename = self.parameters["file_name"].value
        if not filename.endswith(".wav"):
            raise exceptions.DataSavingError("File has to be a .wav.")
        scipy.io.wavfile.write(filename, sampling_frequency,
                               input_signal.ordinate)
