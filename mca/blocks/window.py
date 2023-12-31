from scipy import signal

from mca.framework import Block, data_types, parameters, util


class Window(Block):
    """Applies a window function to the input signal."""
    name = "Window"
    description = "Applies a window function to the input signal."
    tags = ("Processing",)
    references = {"scipy.signal.windows.tukey":
        "https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.windows.tukey.html",
        "scipy.signal.windows.hamming":
        "https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.windows.hamming.html",
        "scipy.signal.windows.exponential":
        "https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.windows.exponential.html",
        "scipy.signal.windows.gaussian":
        "https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.windows.gaussian.html",
        "scipy.signal.windows.triang":
        "https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.windows.triang.html"}

    def setup_io(self):
        self.new_output()
        self.new_input()

    def setup_parameters(self):
        self.parameters["window_func"] = parameters.ChoiceParameter(
                name="Window Function",
                choices=(("tukey", "Tukey"), ("hann", "Hann"),
                         ("hamming", "Hamming"),
                         ("exponential", "Exponential"),
                         ("gaussian", "Gaussian"),
                         ("triangle", "Triangle")),
                default="hann"
            )
        self.parameters["alpha"] = parameters.FloatParameter(
            name="Alpha (Tukey)", min_=0, max_=1, default=0.5
        )
        self.parameters["std"] = parameters.FloatParameter(
            name="Standard Deviation (Gaussian)", min_=0, default=1
        )

    @util.abort_all_inputs_empty
    @util.validate_type_signal
    def process(self):
        # Read the input data
        input_signal = self.inputs[0].data
        # Read parameters values
        window_name = self.parameters["window_func"].value
        # Set the args
        if window_name == "gaussian":
            args = (window_name, self.parameters["std"].value)
        elif window_name == "tukey":
            args = (window_name, self.parameters["alpha"].value)
        else:
            args = window_name
        # Get the window function
        window = signal.get_window(args, input_signal.values)
        # Calculate the ordinate
        ordinate = input_signal.ordinate * window
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=input_signal.abscissa_start,
            values=input_signal.values,
            increment=input_signal.increment,
            ordinate=ordinate,
        )
        # Apply metadata from the input to the output
        self.outputs[0].process_metadata = self.inputs[0].metadata
