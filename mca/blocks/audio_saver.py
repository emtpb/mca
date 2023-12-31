import scipy.io.wavfile
from united import Unit

from mca import exceptions
from mca.framework import Block, parameters, validator


class AudioSaver(Block):
    """Saves the input signal as a .wav sound file."""
    name = "Audio Saver"
    description = "Saves the input signal as a .wav sound file."
    tags = ("Saving", "Audio")
    references = {"scipy.io.wavfile.write":
        "https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.write.html"}

    def setup_parameters(self):
        self.parameters["sampling_freq"] = parameters.IntParameter(
            name="Sampling frequency", min_=1, max_=None, unit="Hz",
            default=44100
        )
        self.parameters["file_name"] = parameters.PathParameter(
            name="Filename", file_formats=[".wav"]
        )
        self.parameters["save_file"] = parameters.ActionParameter(
            name="Save as .wav", function=self.save_as_wav)

    def setup_io(self):
        self.new_input()

    def process(self):
        pass

    def save_as_wav(self):
        """Saves the input signal as a .wav file."""
        # Raise error when the input has no data to save
        if self.all_inputs_empty():
            raise exceptions.DataSavingError("No data to save.")
        # Read the input data
        input_signal = self.inputs[0].data
        # Validate that the input data is of type signal
        validator.check_type_signal(input_signal)
        # Validate that the abscissa is in seconds
        validator.check_same_units([self.inputs[0].metadata.unit_a,
                                    Unit(["s"])])
        # Read parameters values
        sampling_frequency = self.parameters["sampling_freq"].value
        filename = self.parameters["file_name"].value
        # Verify that the file ends with .wav
        if not filename.endswith(".wav"):
            raise exceptions.DataSavingError("File has to be a .wav.")
        # Write the file
        scipy.io.wavfile.write(filename, sampling_frequency,
                               input_signal.ordinate)
