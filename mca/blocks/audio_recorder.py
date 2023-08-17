import sounddevice as sd

from mca.framework import Block, data_types, parameters


class AudioRecorder(Block):
    """Records a sound via the default audio input device."""
    name = "Audio Recorder"
    description = "Records a sound via the default audio input device."
    tags = ("Audio",)

    def setup_io(self):
        self.new_output(user_metadata_required=True)

    def setup_parameters(self):
        self.parameters["sampling_freq"] = parameters.IntParameter(
            name="Sampling Frequency",min_=1, max_=None, unit="Hz",
            default=44100
        )
        self.parameters["record_time"] = parameters.FloatParameter(
            name="Record time", min_=0, max_=None,unit="s", default=5
        )
        self.parameters["record_sound"] = parameters.ActionParameter(
            name="Record sound", function=self.record_sound,
            display_options=("block_button",
                             "edit_window")
        )

    def process(self):
        pass

    def record_sound(self):
        """Record the default audio device and puts the data on the second
        output.
        """
        # Read parameters values
        sampling_frequency = self.parameters["sampling_freq"].value
        record_time = self.parameters["record_time"].value
        # Calculate the amount of frames needed
        frames = int(sampling_frequency * record_time)
        # Record the audio from the default audio device
        recording = sd.rec(frames=frames, samplerate=sampling_frequency,
                           channels=1).reshape(frames)
        # Blocking call until the recording is finished
        sd.wait()
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=0,
            values=frames,
            increment=1 / sampling_frequency,
            ordinate=recording)
        # Trigger an update manually since this is not executed within process
        self.trigger_update()
