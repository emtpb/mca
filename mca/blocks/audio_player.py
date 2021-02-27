import sounddevice as sd
from united import Unit

from mca.framework import validator, parameters, Block
from mca.language import _


class AudioPlayer(Block):
    """Plays the input signal as a sound.

    This block has one input.
    """
    name = _("AudioPlayer")
    description = _("Plays the input signal as a sound.")
    tags = (_("Audio"),)

    def __init__(self, **kwargs):
        """Initializes the AudioPlayer class."""
        super().__init__()
        self._new_input()
        self.parameters.update(
            {"sampling_freq": parameters.IntParameter(_("Sampling frequency"),
                                                      1, None, "Hz", 44100),
             "play_sound": parameters.ActionParameter(_("Play sound"),
                                                      self.play_sound),
             "auto_play": parameters.BoolParameter(_("Auto play"), False)})
        self.read_kwargs(kwargs)

    def _process(self):
        if self.parameters["auto_play"].value is True:
            self.play_sound()

    def play_sound(self):
        """Plays a sound through the current default sound device."""
        if self.check_empty_inputs():
            return
        input_signal = self.inputs[0].data
        sampling_frequency = self.parameters["sampling_freq"].value
        validator.check_type_signal(input_signal)
        validator.check_same_units([input_signal.meta_data.unit_a, Unit(["s"])])
        sd.play(input_signal.ordinate, sampling_frequency)