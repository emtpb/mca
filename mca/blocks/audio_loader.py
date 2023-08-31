import copy

import numpy as np
import scipy.io.wavfile

from mca import exceptions
from mca.framework import Block, data_types, parameters


class AudioLoader(Block):
    """Loads a .wav to create an output signal. The audio file can have either
    1 or 2 channels. If the audio file has only 1 channel then the channel is
    just duplicated on both outputs. If the audio file has 2 channels then
    the channels are split onto the 2 outputs.
    """
    name = "Audio Loader"
    description = "Loads a .wav to create an output signal."
    tags = ("Loading", "Audio")

    def setup_io(self):
        self.new_output(user_metadata_required=True)
        self.new_output(user_metadata_required=True)

    def setup_parameters(self):
        self.parameters["file_name"] = parameters.PathParameter(
            name="Filename", file_formats=[".wav"], loading=True
        )
        self.parameters["load_file"] = parameters.ActionParameter(
            name="Load file", function=self.load_wav
        )
        self.parameters["file_name"].triggers = [self.parameters["load_file"]]
        self.parameters["normalize"] = parameters.BoolParameter(
            name="Normalize", default=True
        )

    def process(self):
        pass

    def load_wav(self):
        """Reads a .wav and puts the data on the output."""
        # Read out the parameters
        filename = self.parameters["file_name"].value
        normalize = self.parameters["normalize"].value
        # Verify that the file ends with .wav
        if not filename.endswith(".wav"):
            raise exceptions.DataLoadingError("File has to be a .wav")
        # Read wave file and raise custom error when FileNotFound error is raised
        try:
            rate, data = scipy.io.wavfile.read(filename)
        except FileNotFoundError:
            raise exceptions.DataLoadingError("File not found")
        # Normalize the data
        if normalize:
            data = data / np.max(data)

        values = data.shape[0]
        if len(data.shape) == 2:
            data = np.swapaxes(data, 0, 1)
            left = data[0]
            right = data[1]
        else:
            left = data
            right = copy.copy(data)
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=0,
            values=values,
            increment=1 / rate,
            ordinate=left)
        self.outputs[1].data = data_types.Signal(
            abscissa_start=0,
            values=values,
            increment=1 / rate,
            ordinate=right)
        # Trigger an update manually since this is not executed within process
        self.trigger_update()
