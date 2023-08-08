import numpy as np
import scipy.io.wavfile

from mca import exceptions
from mca.framework import Block, data_types, parameters


class AudioLoader(Block):
    """Loads a .wav to create an output signal."""
    name = "Audio Loader"
    description = "Loads a .wav to create an output signal."
    tags = ("Loading", "Audio")

    def setup_io(self):
        self.new_output(user_metadata_required=True)

    def setup_parameters(self):
        self.parameters["file_name"] = parameters.PathParameter(
            name="Filename", file_formats=[".wav"], loading=True
        )
        self.parameters["load_file"] = parameters.ActionParameter(
            name="Load file", function=self.load_wav
        )
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
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=0,
            values=len(data),
            increment=1 / rate,
            ordinate=data)
        # Trigger an update manually since this is not executed within process
        self.trigger_update()
