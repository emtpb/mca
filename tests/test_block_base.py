"""Tests for `mca` package."""
import pytest

from mca.base import (
    block_base,
    output_base,
    input_base,
    block_registry,
    dynamic_block_base,
)
from mca import exceptions


class DynamicInputBlock(dynamic_block_base.DynamicBlock):
    def __init__(self):
        super().__init__()
        self.dynamic_input = [1, 3]
        self.outputs.append(
            block_registry.Registry.add_node(output_base.Output(self,None))
        )
        self.inputs.append(
            block_registry.Registry.add_node(input_base.Input(self))
        )
        self.process_count = 0

    def _process(self):
        self.outputs[0].data = 0
        for i in self.inputs:
            if i.data:
                self.outputs[0].data += i.data
        self.process_count += 1


class DynamicOutputBlock(dynamic_block_base.DynamicBlock):
    def __init__(self):
        super().__init__()
        self.dynamic_output = [1, None]
        self.outputs.append(
            block_registry.Registry.add_node(output_base.Output(self,None))
        )
        self.inputs.append(
            block_registry.Registry.add_node(input_base.Input(self))
        )
        self.process_count = 0

    def _process(self):
        for o in self.outputs:
            if self.inputs[0].data:
                o.data = self.inputs[0].data
            else:
                o.data = None
        self.process_count += 1


class TestBlock(block_base.Block):
    def __init__(self, inputs, outputs):
        super().__init__()
        for i in range(inputs):
            self.inputs.append(
                block_registry.Registry.add_node(input_base.Input(self))
            )
        for o in range(outputs):
            self.outputs.append(
                block_registry.Registry.add_node(output_base.Output(self,None))
            )
        self.process_count = 0


class OneOutputBlock(TestBlock):
    def __init__(self, **kwargs):
        super().__init__(0, 1)

    def _process(self):
        self.outputs[0].data = 1
        self.process_count += 1


class OneInputBlock(TestBlock):
    def __init__(self, **kwargs):
        super().__init__(1, 0)

    def _process(self):
        self.process_count += 1


class TwoOutputBlock(TestBlock):
    def __init__(self, **kwargs):
        super().__init__(0, 2)

    def _process(self):
        self.outputs[0].data = 1
        self.outputs[1].data = 2
        self.process_count += 1


class TwoInputBlock(TestBlock):
    def __init__(self, **kwargs):
        super().__init__(2, 0)

    def _process(self):
        self.process_count += 1


class OneInputOneOutputBlock(TestBlock):
    def __init__(self, **kwargs):
        super().__init__(1, 1)

    def _process(self):
        self.process_count += 1
        if self.inputs[0].data:
            self.outputs[0].data = self.inputs[0].data + 1
        else:
            self.outputs[0].data = None


class TwoInputOneOutputBlock(TestBlock):
    def __init__(self, **kwargs):
        super().__init__(2, 1)

    def _process(self):
        self.process_count += 1
        if self.inputs[0].data and self.inputs[1].data:
            self.outputs[0].data = self.inputs[0].data + self.inputs[1].data
        else:
            self.outputs[0].data = None


class OneInputTwoOutputBlock(TestBlock):
    def __init__(self, **kwargs):
        super().__init__(1, 2)

    def _process(self):
        self.process_count += 1
        if self.inputs[0].data:
            self.outputs[0].data = self.inputs[0].data
            self.outputs[1].data = self.outputs[0].data + 1


class TwoInputTwoOutputBlock(TestBlock):
    def __init__(self, **kwargs):
        super().__init__(2, 2)

    def _process(self):
        self.process_count += 1
        if self.inputs[0].data and self.inputs[1].data:
            self.outputs[0].data = self.inputs[0].data + self.inputs[1].data
            self.outputs[1].data = self.outputs[0].data + 1


"""Fixtures for different scenarios."""


@pytest.fixture
def basic_scenario():
    a = OneOutputBlock()
    b = OneInputBlock()
    b.inputs[0].connect(a.outputs[0])
    a.apply_parameter_changes()
    yield a, b
    block_registry.Registry.clear()


@pytest.fixture
def second_scenario():
    a = TwoOutputBlock()
    b = TwoInputBlock()
    b.inputs[0].connect(a.outputs[0])
    b.inputs[1].connect(a.outputs[1])
    a.apply_parameter_changes()
    yield a, b
    block_registry.Registry.clear()


@pytest.fixture
def third_scenario():
    a = OneOutputBlock()
    b = TwoInputBlock()
    a.apply_parameter_changes()
    b.inputs[0].connect(a.outputs[0])
    b.inputs[1].connect(a.outputs[0])
    yield a, b
    block_registry.Registry.clear()


@pytest.fixture
def fourth_scenario():
    a = OneOutputBlock()
    b = OneInputBlock()
    c = OneInputBlock()
    a.apply_parameter_changes()
    b.inputs[0].connect(a.outputs[0])
    c.inputs[0].connect(a.outputs[0])
    yield a, b, c
    block_registry.Registry.clear()


@pytest.fixture
def fifth_scenario():
    a = OneOutputBlock()
    b = OneInputOneOutputBlock()
    c = OneInputBlock()
    a.apply_parameter_changes()
    b.inputs[0].connect(a.outputs[0])
    c.inputs[0].connect(b.outputs[0])
    yield a, b, c
    block_registry.Registry.clear()


@pytest.fixture
def sixth_scenario():
    a = OneOutputBlock()
    b = OneInputOneOutputBlock()
    c = OneInputOneOutputBlock()
    d = TwoInputBlock()
    a.apply_parameter_changes()
    b.inputs[0].connect(a.outputs[0])
    c.inputs[0].connect(a.outputs[0])
    d.inputs[0].connect(b.outputs[0])
    d.inputs[1].connect(c.outputs[0])
    yield a, b, c, d
    block_registry.Registry.clear()


@pytest.fixture
def seventh_scenario():
    a = OneOutputBlock()
    b = OneOutputBlock()
    c = TwoInputOneOutputBlock()
    d = OneInputBlock()
    a.apply_parameter_changes()
    b.apply_parameter_changes()
    c.inputs[0].connect(a.outputs[0])
    c.inputs[1].connect(b.outputs[0])
    d.inputs[0].connect(c.outputs[0])
    yield a, b, c, d
    block_registry.Registry.clear()


@pytest.fixture
def add_input_scenario():
    a = DynamicInputBlock()
    a.add_input(input_base.Input(a))
    a.add_input(input_base.Input(a))
    yield a
    block_registry.Registry.clear()


@pytest.fixture
def delete_input_scenario(add_input_scenario):
    a = add_input_scenario
    a.delete_input(2)
    yield a


@pytest.fixture
def dynamic_input_scenario(add_input_scenario):
    a = add_input_scenario
    b = TwoOutputBlock()
    c = OneOutputBlock()
    d = OneInputBlock()
    b.apply_parameter_changes()
    c.apply_parameter_changes()
    a.inputs[0].connect(b.outputs[0])
    a.inputs[1].connect(b.outputs[1])
    a.inputs[2].connect(c.outputs[0])
    d.inputs[0].connect(a.outputs[0])
    yield a, b, c, d


"""Block connecting, disconnecting, data availability tests."""


def test_connect(basic_scenario):
    a, b = basic_scenario
    assert [a.outputs[0], b.inputs[0]] in block_registry.Registry._graph.edges


def test_connect_2():
    a = OneInputBlock()
    b = OneInputBlock()
    with pytest.raises(exceptions.ConnectionsError):
        b.inputs[0].connect(a.inputs[0])
    block_registry.Registry.clear()


def test_connect_3(basic_scenario):
    a, b = basic_scenario
    c = OneOutputBlock()
    with pytest.raises(exceptions.ConnectionsError):
        b.inputs[0].connect(c.outputs[0])


def test_disconnect_input(basic_scenario):
    a, b = basic_scenario
    b.inputs[0].disconnect()
    assert [
        a.outputs[0],
        b.inputs[0],
    ] not in block_registry.Registry._graph.edges
    b.inputs[0].disconnect()
    assert [
        a.outputs[0],
        b.inputs[0],
    ] not in block_registry.Registry._graph.edges


def test_disconnect_output(basic_scenario):
    a, b = basic_scenario
    c = OneInputBlock()
    c.inputs[0].connect(a.outputs[0])
    a.outputs[0].disconnect()
    assert [
        a.outputs[0],
        b.inputs[0],
    ] not in block_registry.Registry._graph.edges
    assert [
        a.outputs[0],
        c.inputs[0],
    ] not in block_registry.Registry._graph.edges
    a.outputs[0].disconnect()
    assert [
        a.outputs[0],
        c.inputs[0],
    ] not in block_registry.Registry._graph.edges


def test_get_output(basic_scenario):
    a, b = basic_scenario
    assert block_registry.Registry.get_output(b.inputs[0]) is a.outputs[0]
    b.inputs[0].disconnect()
    assert block_registry.Registry.get_output(b.inputs[0]) is None


def test_data_availability(basic_scenario):
    a, b = basic_scenario
    assert b.inputs[0].data == 1
    b.inputs[0].disconnect()
    assert b.inputs[0].data is None


"""Tests to analyze block communication behaviour and correct
data transfer with different scenarios."""


def test_first_scenario_behaviour(basic_scenario):
    a, b = basic_scenario
    assert b.process_count == 2
    assert a.process_count == 1
    b.inputs[0].disconnect()
    assert b.process_count == 3
    assert a.process_count == 1


def test_first_scenario_data(basic_scenario):
    a, b = basic_scenario
    assert b.inputs[0].data == 1
    b.inputs[0].disconnect()
    assert b.inputs[0].data is None


def test_second_scenario_behaviour(second_scenario):
    a, b = second_scenario
    assert b.process_count == 3
    a.outputs[1].disconnect()
    assert b.process_count == 4


def test_second_scenario_data(second_scenario):
    a, b = second_scenario
    assert b.inputs[0].data == 1
    assert b.inputs[1].data == 2


def test_third_scenario_behaviour(third_scenario):
    a, b = third_scenario
    assert b.process_count == 2
    a.apply_parameter_changes()
    assert b.process_count == 3


def test_third_scenario_data(third_scenario):
    a, b = third_scenario
    b.inputs[0].data == 1
    b.inputs[1].data == 1
    a.outputs[0].disconnect()
    b.inputs[0].data is None
    b.inputs[1].data is None


def test_fourth_scenario_behaviour(fourth_scenario):
    a, b, c = fourth_scenario
    assert b.process_count == 1
    assert c.process_count == 1
    a.apply_parameter_changes()
    assert b.process_count == 2
    assert c.process_count == 2


def test_fourth_scenario_data(fourth_scenario):
    a, b, c = fourth_scenario
    assert b.inputs[0].data == 1
    assert c.inputs[0].data == 1


def test_fifth_scenario_behaviour(fifth_scenario):
    a, b, c = fifth_scenario
    assert b.process_count == 1
    assert c.process_count == 1
    a.apply_parameter_changes()
    assert c.process_count == 2
    b.inputs[0].disconnect()
    assert c.process_count == 3


def test_fifth_scenario_data(fifth_scenario):
    a, b, c = fifth_scenario
    c.inputs[0].data == 2
    b.inputs[0].disconnect()
    assert c.inputs[0].data is None


def test_sixth_scenario_behaviour(sixth_scenario):
    a, b, c, d = sixth_scenario
    assert d.process_count == 2
    a.outputs[0].disconnect()
    assert d.process_count == 3
    assert b.process_count == 2
    assert c.process_count == 2
    a.apply_parameter_changes()
    assert d.process_count == 3


def test_sixth_scenario_data(sixth_scenario):
    a, b, c, d = sixth_scenario
    assert d.inputs[0].data == 2
    assert d.inputs[1].data == 2
    a.outputs[0].disconnect()
    assert d.inputs[0].data is None
    assert d.inputs[1].data is None


def test_seventh_scenario_behaviour(seventh_scenario):
    a, b, c, d = seventh_scenario
    assert c.process_count == 2
    assert d.process_count == 1
    a.outputs[0].disconnect()
    assert c.process_count == 3
    assert d.process_count == 2


def test_seventh_scenario_data(seventh_scenario):
    a, b, c, d = seventh_scenario
    assert d.inputs[0].data == 2
    a.outputs[0].disconnect()
    assert d.inputs[0].data is None


def test_eighth_scenario_behaviour():
    a = OneOutputBlock()
    b = TwoInputTwoOutputBlock()
    c = TwoInputBlock()
    b.inputs[0].connect(a.outputs[0])
    b.inputs[1].connect(a.outputs[0])
    c.inputs[0].connect(b.outputs[0])
    c.inputs[1].connect(b.outputs[1])
    a.apply_parameter_changes()
    assert c.process_count == 3


"""Tests for detection of BlockCircleErrors."""


def test_block_circle_error(seventh_scenario):
    a, b, c, d = seventh_scenario
    c.inputs[0].disconnect()
    with pytest.raises(exceptions.BlockCircleError):
        c.inputs[0].connect(c.outputs[0])


def test_block_circle_error_2():
    a = OneOutputBlock()
    b = OneOutputBlock()
    c = TwoInputOneOutputBlock()
    d = TwoInputOneOutputBlock()
    c.inputs[0].connect(a.outputs[0])
    d.inputs[0].connect(b.outputs[0])
    c.inputs[1].connect(d.outputs[0])
    with pytest.raises(exceptions.BlockCircleError):
        d.inputs[1].connect(c.outputs[0])
    block_registry.Registry.clear()


"""Tests concerning the dynamic block"""


def test_add_input(add_input_scenario):
    a = add_input_scenario
    assert len(a.inputs) == 3
    assert [a.inputs[1], a.outputs[0]] in block_registry.Registry._graph.edges
    with pytest.raises(exceptions.InputOutputError):
        a.add_input(input_base.Input(a))


def test_delete_input(delete_input_scenario):
    a = delete_input_scenario
    assert len(a.inputs) == 2
    assert all([x in block_registry.Registry._graph.nodes() for x in a.inputs])
    a.delete_input(1)
    with pytest.raises(exceptions.InputOutputError):
        a.delete_input(0)


def test_dynamic_input_behaviour(dynamic_input_scenario):
    a, b, c, d = dynamic_input_scenario
    a.delete_input(2)
    assert a.process_count == 4


def test_dynamic_input_data(dynamic_input_scenario):
    a, b, c, d = dynamic_input_scenario
    assert d.inputs[0].data == 4
    a.delete_input(2)
    assert d.inputs[0].data == 3


def test_dynamic_output_data():
    a = DynamicOutputBlock()
    b = OneOutputBlock()
    c = TwoInputBlock()
    d = TwoInputBlock()
    b.apply_parameter_changes()
    a.inputs[0].connect(b.outputs[0])
    a.add_output(output_base.Output(a, None))
    a.add_output(output_base.Output(a, None))
    c.inputs[0].connect(a.outputs[0])
    c.inputs[1].connect(a.outputs[1])
    assert c.inputs[0].data == 1 and c.inputs[1].data == 1
    d.inputs[0].connect(a.outputs[2])
    d.inputs[1].connect(a.outputs[1])
    a.delete_output(1)
    assert d.inputs[1].data is None and d.inputs[0].data == 1
    block_registry.Registry.clear()


def test_check_empty_inputs():
    a = TwoInputBlock()
    assert a.check_empty_inputs() is True
    b = TwoOutputBlock()
    b.outputs[0].data = 1
    a.inputs[0].connect(b.outputs[0])
    assert a.check_empty_inputs() is None
