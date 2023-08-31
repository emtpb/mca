import numpy as np
import sounddevice as sd
from united import Unit

from mca.framework import Block, parameters, util, validator


class AudioPlayer(Block):
    """Plays the input signals as a sound by using the current default
    sound device. If only one input is connected, then the sound will be played
    using 1 channel (mono) and if both inputs are connected then
    the 2 channels will be used (stereo).
    """
    name = "Audio Player"
    description = ("Plays the input signal as a sound by using the current "
                   "default sound device.")
    tags = ("Audio",)

    def setup_io(self):
        self.new_input()
        self.new_input()

    def setup_parameters(self):
        self.parameters["sampling_freq"] = parameters.IntParameter(
            name="Sampling frequency", min_=1, max_=None, unit="Hz",
            default=44100
        )
        self.parameters["play_sound"] = parameters.ActionParameter(
            name="Play sound", function=self.play_sound,
            display_options=("block_button", "edit_window")
        )
        self.parameters["auto_play"] = parameters.BoolParameter(
            name="Auto play", default=False)

    def process(self):
        if self.parameters["auto_play"].value is True:
            self.play_sound()

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def play_sound(self):
        """Plays a sound through the current default sound device."""
        # Read the input data
        if self.inputs[0].data and not self.inputs[1].data:
            data = self.inputs[0].data.ordinate
        elif not self.inputs[0].data and self.inputs[1].data:
            data = self.inputs[1].data.ordinate
        else:
            data = np.hstack((self.inputs[0].data.ordinate,
                              self.inputs[1].data.ordinate))
        # Read parameters values
        sampling_frequency = self.parameters["sampling_freq"].value
        # Validate that the abscissa is in seconds
        validator.check_same_units([self.inputs[0].metadata.unit_a,
                                    Unit(["s"])])
        # Play the input signal as sound through the default sound device
        sd.play(data, sampling_frequency)
