import sounddevice as sd
from united import Unit

from mca.framework import Block, parameters, util, validator


class AudioPlayer(Block):
    """Plays the input signal as a sound by using the current default
    sound device.
    """
    name = "AudioPlayer"
    description = ("Plays the input signal as a sound by using the current "
                   "default sound device.")
    tags = ("Audio",)

    def setup_io(self):
        self.new_input()

    def setup_parameters(self):
        self.parameters["sampling_freq"] = parameters.IntParameter(
            "Sampling frequency", 1, None, "Hz", 44100
        )
        self.parameters["play_sound"] = parameters.ActionParameter(
            "Play sound", self.play_sound, display_options=("block_button",
                                                               "edit_window")
        )
        self.parameters["auto_play"] = parameters.BoolParameter("Auto play",
                                                                False)

    def process(self):
        if self.parameters["auto_play"].value is True:
            self.play_sound()

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def play_sound(self):
        """Plays a sound through the current default sound device."""
        # Read the input data
        input_signal = self.inputs[0].data
        # Read parameters values
        sampling_frequency = self.parameters["sampling_freq"].value
        # Validate that the abscissa is in seconds
        validator.check_same_units([self.inputs[0].metadata.unit_a,
                                    Unit(["s"])])
        # Play the input signal as sound through the default sound device
        sd.play(input_signal.ordinate, sampling_frequency)
