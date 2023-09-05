import numpy as np
import sounddevice as sd
from united import Unit

from mca.framework import Block, parameters, util, validator
from mca import exceptions


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
        self.parameters["manual_sampl_freq"] = parameters.BoolParameter(
            name="Manually set sampling frequency", default=False)
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
        # Validate the units of the input signal
        for input_ in self.inputs:
            if input_.metadata:
                validator.check_same_units([input_.metadata.unit_a,
                                            Unit(["s"])])
        # Read parameters values
        manual_sampling = self.parameters["manual_sampl_freq"].value
        manual_sampling_frequency = self.parameters["sampling_freq"].value
        if manual_sampling:
            sampling_frequency = manual_sampling_frequency
        else:
            if self.inputs[0].data and self.inputs[1].data:
                increment_0 = self.inputs[0].data.increment
                increment_1 = self.inputs[1].data.increment
                if increment_0 != increment_1:
                    raise exceptions.IntervalError("Cannot play stereo sound "
                                                   "with different sampling frequencies")
                sampling_frequency = 1/increment_0
            elif self.inputs[0].data:
                sampling_frequency = 1/self.inputs[0].data.increment
            elif self.inputs[1].data:
                sampling_frequency = 1 / self.inputs[1].data.increment
        # Play the input signal as sound through the default sound device
        sd.play(data, sampling_frequency)
