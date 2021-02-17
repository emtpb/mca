import sounddevice as sd
import scipy.io.wavfile

from mca.framework import parameters, Block, data_types
from mca.language import _
from mca import exceptions


class AudioRecorder(Block):
    """Records the default audio input device.

    This block has one output.
    """
    name = _("AudioRecorder")
    description = _("Records the default audio input device.")
    tags = (_("Audio"),)

    def __init__(self, **kwargs):
        """Initializes the AudioRecorder class."""
        super().__init__()
        self._new_output(
            meta_data=data_types.MetaData(
                name="",
                unit_a="s",
                unit_o="V",
                quantity_a=_("Time"),
                quantity_o=_("Voltage")
            ),
            meta_data_input_dependent=False,
            ordinate_meta_data=True,
            abscissa_meta_data=True,
        )
        self.parameters.update(
            {"record_time": parameters.FloatParameter(_("Record time"), 0,
                                                      None, "s", 5),
             "record_sound": parameters.ActionParameter(_("Record sound"),
                                                        self.record_sound),
             })
        self.read_kwargs(kwargs)

    def _process(self):
        pass

    def record_sound(self):
        """Record the default audio device and puts the data on the second
        output.
        """
        sampling_frequency = 44100
        record_time = self.parameters["record_time"].value
        frames = int(sampling_frequency*record_time)
        recording = sd.rec(frames=frames, samplerate=44100, channels=1)
        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].meta_data,
            abscissa_start=0,
            values=frames,
            increment=1/sampling_frequency,
            ordinate=recording)
        self.update()
