import numpy as np

from mca.framework import Block, data_types, parameters, util


class SignalGeneratorStochastic(Block):
    """Generates a stochastic signal with either normal or equal
    distribution.
    """
    name = "Signal Generator (Stochastic)"
    description = ("Generates a stochastic signal "
                   "with either normal or equal distribution.")
    tags = ("Generating", "Stochastic")

    def setup_io(self):
        self.new_output(user_metadata_required=True)

    def setup_parameters(self):
        self.parameters["dist"] = parameters.ChoiceParameter(
                name="Distribution",
                choices=(("normal", "Normal distribution"),
                         ("uniform", "Uniform distribution")),
                default="normal"
        )
        self.parameters["mean"] = parameters.FloatParameter(
            name="Mean µ", default=0
        )
        self.parameters["std_dev"] = parameters.FloatParameter(
            name="Standard deviation σ", min_=0, default=1
        )
        abscissa = util.create_abscissa_parameter_block()
        self.parameters["abscissa"] = abscissa

    def process(self):
        # Read the input data
        mean = self.parameters["mean"].value
        std_dev = self.parameters["std_dev"].value
        abscissa_start = self.parameters["abscissa"].parameters["start"].value
        values = self.parameters["abscissa"].parameters["values"].value
        increment = self.parameters["abscissa"].parameters["increment"].value
        dist = self.parameters["dist"].value
        # Calculate the ordinate depending on the distribution
        if dist == "normal":
            ordinate = mean + std_dev * np.random.randn(values)
        elif dist == "uniform":
            ordinate = mean + std_dev * np.sqrt(12) * (
                        np.random.rand(values) - 0.5)
        # Apply new signal to the output
        self.outputs[0].data = data_types.Signal(
            abscissa_start=abscissa_start,
            values=values,
            increment=increment,
            ordinate=ordinate,
        )
