import sounddevice as sd
import scipy.io.wavfile

from mca.framework import parameters, Block, data_types
from mca.language import _
from mca import exceptions


class AudioInput(Block):
    """Reads a .wav to create an output signal or records the default
    audio input device.

    This block has two outputs. First output for carries the signal
    created by a .wav file. Second output carries the signal from the recorded
    sound.
    """
    name = _("AudioInput")
    description = _("Reads a .wav to create an output signal or records the "
                    "default audio input device.")
    tags = (_("Loading"), _("Audio"))

    def __init__(self, **kwargs):
        super().__init__()
        self._new_output(
            name=_("Audio file"),
            meta_data=data_types.MetaData(
                name="",
                unit_a="s",
                unit_o="V",
                quantity_a=_("Time"),
                quantity_o=_("Voltage")
            ),
            meta_data_input_dependent=False
        )
        self._new_output(
            name=_("Recording"),
            meta_data=data_types.MetaData(
                name="",
                unit_a="s",
                unit_o="V",
                quantity_a=_("Time"),
                quantity_o=_("Voltage")
            ),
            meta_data_input_dependent=False
        )
        self.parameters.update(
            {"sampling_freq": parameters.IntParameter(_("Sampling frequency"),
                                                      0, None, "Hz", 44100),
             "filename": parameters.PathParameter(_("Filename"), [".wav"],
                                                  loading=True),
             "load_file": parameters.ActionParameter(_("Load file"),
                                                     self.load_wav),
             "record_time": parameters.FloatParameter(_("Record time"), 0,
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
        self.outputs[1].data = data_types.Signal(
            meta_data=self.outputs[0].meta_data,
            abscissa_start=0,
            values=frames,
            increment=1/sampling_frequency,
            ordinate=recording)
        self.update()

    def load_wav(self):
        """Reads a .wav and puts the data on the first output."""
        filename = self.parameters["filename"].value
        if not filename.endswith(".wav"):
            raise exceptions.DataLoadingError("File has to be a .wav.")
        rate, data = scipy.io.wavfile.read(filename)
        self.outputs[0].data = data_types.Signal(
            meta_data=self.outputs[0].meta_data,
            abscissa_start=0,
            values=len(data),
            increment=1/rate,
            ordinate=data)
        self.update()

