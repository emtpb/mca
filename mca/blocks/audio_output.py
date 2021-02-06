import numpy as np
import sounddevice as sd
from united import Unit
import scipy.io.wavfile

from mca.framework import validator, parameters, Block
from mca.language import _
from mca import exceptions


class AudioOutput(Block):
    """Saves the input signal as a sound file or plays the input signal as
    a sound.

    This block has one input.
    """
    name = _("AudioOutput")
    description = _("Saves the input signal as a sound file or plays the input "
                    "signal as a sound.")
    tags = (_("Saving"), _("Audio"))

    def __init__(self, **kwargs):
        super().__init__()
        self._new_input()
        self.read_kwargs(kwargs)
        self.parameters.update(
            {"sampling_freq": parameters.IntParameter(_("Sampling frequency"),
                                                      0, None, "Hz", 44100),
             "filename": parameters.PathParameter(_("Filename"), [".wav"]),
             "save_file": parameters.ActionParameter(_("Save as .wav"),
                                                     self.save_as_wav),
             "play_sound": parameters.ActionParameter(_("Play sound"),
                                                      self.play_sound),
             "auto_play": parameters.BoolParameter(_("Auto play"), False)})

    def _process(self):
        if self.parameters["auto_play"].value is True:
            self.play_sound()

    def play_sound(self):
        """Plays a sound through the current default sound device."""
        if self.check_empty_inputs():
            return
        input_signal = self.inputs[0].data
        sampling_frequency = 44100
        validator.check_type_signal(input_signal)
        validator.check_same_units([input_signal.meta_data.unit_a, Unit(["s"])])
        sd.play(input_signal.ordinate, sampling_frequency)

    def save_as_wav(self):
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
