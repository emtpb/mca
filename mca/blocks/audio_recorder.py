import sounddevice as sd

from mca.framework import parameters, Block, data_types
from mca.language import _


class AudioRecorder(Block):
    """Records a sound via the default audio input device."""
    name = _("AudioRecorder")
    description = _("Records a sound via the default audio input device.")
    tags = (_("Audio"),)

    def setup_parameters(self):
        self.parameters.update(
            {"sampling_freq": parameters.IntParameter(_("Sampling Frequency"),
                                                      1, None, "Hz", 44100),
             "record_time": parameters.FloatParameter(_("Record time"), 0,
                                                      None, "s", 5),
             "record_sound": parameters.ActionParameter(_("Record sound"),
                                                        self.record_sound,
                                                        display_options=(
                                                        "block_button",
                                                        "edit_window")),

             })

    def setup_io(self):
        self.new_output(
            metadata_input_dependent=False,
            ordinate_metadata=True,
            abscissa_metadata=True,
        )

    def _process(self):
        pass

    def record_sound(self):
        """Record the default audio device and puts the data on the second
        output.
        """
        sampling_frequency = self.parameters["sampling_freq"].value
        record_time = self.parameters["record_time"].value
        frames = int(sampling_frequency * record_time)
        recording = sd.rec(frames=frames, samplerate=sampling_frequency,
                           channels=1).reshape(frames)
        sd.wait()
        self.outputs[0].data = data_types.Signal(
            metadata=self.outputs[0].metadata,
            abscissa_start=0,
            values=frames,
            increment=1 / sampling_frequency,
            ordinate=recording)
        self.trigger_update()
