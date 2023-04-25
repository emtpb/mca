import numpy as np
import pytest

from mca import blocks
import mca.framework
from mca.language import _


class TestBlock(mca.framework.block_base.Block):
    name = "Testblock"

    def __init__(self, inputs, outputs, **kwargs):
        super().__init__(**kwargs)
        for i in range(inputs):
            self.new_input("Test")
        for o in range(outputs):
            self.new_output(None)
        self.process_count = 0

    def setup_io(self):
        pass

    def setup_parameters(self):
        pass

    def _process(self):
        pass


@pytest.fixture()
def test_block():
    return TestBlock


"""Define dynamic test blocks."""


class DynamicInputBlock(mca.framework.DynamicBlock):
    name = "DynamicInputBlock"

    def __init__(self):
        super().__init__()
        self.process_count = 0

    def setup_io(self):
        self.dynamic_input = [1, 3]
        self.new_output(None)
        self.new_input()

    def setup_parameters(self):
        pass

    def _process(self):
        self.outputs[0].data = 0
        for i in self.inputs:
            if i.data:
                self.outputs[0].data += i.data
        self.process_count += 1


@pytest.fixture()
def dynamic_input_block():
    return DynamicInputBlock


class DynamicOutputBlock(mca.framework.DynamicBlock):
    name = "DynamicOutputBlock"

    def __init__(self):
        super().__init__()
        self.process_count = 0

    def setup_io(self):
        self.dynamic_output = [1, 4]
        self.new_output(None)
        self.new_input()

    def setup_parameters(self):
        pass

    def _process(self):
        if self.all_inputs_empty():
            return
        data = self.inputs[0].data
        for index, output in enumerate(self.outputs):
            output.data = data + index
        self.process_count += 1


@pytest.fixture()
def dynamic_output_block():
    return DynamicOutputBlock


"""Defines test blocks with various input-output variations."""


class OneOutputBlock(TestBlock):
    name = "OneOutputBlock"

    def __init__(self, **kwargs):
        super().__init__(0, 1)

    def _process(self):
        self.outputs[0].data = 1
        self.process_count += 1


@pytest.fixture()
def one_output_block():
    return OneOutputBlock


class OneInputBlock(TestBlock):
    name = "OneInputBlock"

    def __init__(self, **kwargs):
        super().__init__(1, 0)

    def _process(self):
        self.process_count += 1


@pytest.fixture()
def one_input_block():
    return OneInputBlock


class TwoOutputBlock(TestBlock):
    name = "TwoOutputBlock"

    def __init__(self, **kwargs):
        super().__init__(0, 2)

    def _process(self):
        self.outputs[0].data = 1
        self.outputs[1].data = 2
        self.process_count += 1
        

@pytest.fixture()
def two_output_block():
    return TwoOutputBlock


class TwoInputBlock(TestBlock):
    name = "TwoInputBlock"

    def __init__(self, **kwargs):
        super().__init__(2, 0)

    def _process(self):
        self.process_count += 1


@pytest.fixture()
def two_input_block():
    return TwoInputBlock


class OneInputOneOutputBlock(TestBlock):
    name = "OneInputOneOutputBlock"

    def __init__(self, **kwargs):
        super().__init__(1, 1)

    def _process(self):
        self.process_count += 1
        if self.inputs[0].data:
            self.outputs[0].data = self.inputs[0].data + 1
        else:
            self.outputs[0].data = None


@pytest.fixture()
def one_input_one_output_block():
    return OneInputOneOutputBlock


class TwoInputOneOutputBlock(TestBlock):
    name = "TwoInputOneOutputBlock"

    def __init__(self, **kwargs):
        super().__init__(2, 1)

    def _process(self):
        self.process_count += 1
        if self.inputs[0].data and self.inputs[1].data:
            self.outputs[0].data = self.inputs[0].data + self.inputs[1].data
        else:
            self.outputs[0].data = None


@pytest.fixture()
def two_input_one_output_block():
    return TwoInputOneOutputBlock


class OneInputTwoOutputBlock(TestBlock):
    name = "OneInputTwoOutputBlock"

    def __init__(self, **kwargs):
        super().__init__(1, 2)

    def _process(self):
        self.process_count += 1
        if self.inputs[0].data:
            self.outputs[0].data = self.inputs[0].data
            self.outputs[1].data = self.outputs[0].data + 1


@pytest.fixture()
def one_input_two_output_block():
    return OneInputTwoOutputBlock


class TwoInputTwoOutputBlock(TestBlock):

    def __init__(self, **kwargs):
        super().__init__(2, 2)

    def _process(self):
        self.process_count += 1
        if self.inputs[0].data and self.inputs[1].data:
            self.outputs[0].data = self.inputs[0].data + self.inputs[1].data
            self.outputs[1].data = self.outputs[0].data + 1


@pytest.fixture()
def two_input_two_output_block():
    return TwoInputTwoOutputBlock


class ParameterBlock(mca.framework.block_base.Block):
    name = "ParameterBlock"

    def setup_io(self):
        pass

    def setup_parameters(self):
        factor = mca.framework.parameters.FloatParameter(name=_("Test"), default=1)
        decibel = mca.framework.parameters.FloatParameter(name=_("Decibel"), default=0, unit="dB")

        def factor_to_decibel():
            decibel.value = 10*np.log10(factor.value)

        def decibel_to_factor():
            factor.value = 10 ** (decibel.value / 10)

        conversion = mca.framework.parameters.ParameterConversion(
            [factor], [decibel], factor_to_decibel
        )
        conversion_1 = mca.framework.parameters.ParameterConversion(
            [decibel], [factor], decibel_to_factor)
        multiplier = mca.framework.parameters.ParameterBlock(name=_("Multiplier"),
                                               parameters={"factor": factor, "decibel": decibel},
                                               param_conversions=[conversion, conversion_1],
                                               default_conversion=0)
        self.parameters.update({
            "test_parameter": mca.framework.parameters.FloatParameter(
                name="Test", default=0
            ),
            "test_parameter1": mca.framework.parameters.IntParameter(
                name="Test", default=100, min_=1
            ),
            "multiplier": multiplier
        })

    def _process(self):
        pass


@pytest.fixture()
def parameter_block():
    return ParameterBlock


class TestOutputBlock(mca.framework.block_base.Block):
    name = "TestOutputBlock"

    def __init__(self, sig):
        super().__init__()
        self.outputs[0].data = sig

    def setup_io(self):
        self.new_output(metadata=None)

    def setup_parameters(self):
        pass

    def _process(self):
        pass


@pytest.fixture(scope="module")
def default_metadata():
    return mca.framework.data_types.MetaData("", "s", "V", _("Time"),
                                             _("Voltage"))


@pytest.fixture(scope="module")
def test_output_block():
    return TestOutputBlock


@pytest.fixture(scope="module")
def sin_signal():
    return mca.framework.data_types.Signal(0, 628, 0.01,
        np.sin(2*np.pi*np.linspace(0, 0.01*627, 628)))


@pytest.fixture(scope="module")
def sin_block(sin_signal):
    return TestOutputBlock(sin_signal)


@pytest.fixture(scope="module")
def unit_step_signal():
    return mca.framework.data_types.Signal(-1, 200, 0.01,
                             np.where(np.arange(-1, 1, 0.01) >= 0, 1, 0))


@pytest.fixture(scope="module")
def unit_step_block(unit_step_signal):
    return TestOutputBlock(unit_step_signal)
