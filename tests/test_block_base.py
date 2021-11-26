"""Tests for the Block, the DynamicBlock and the Connection between blocks."""
import pytest

import mca.framework
from mca import exceptions


"""Fixtures for different scenarios."""


@pytest.fixture
def basic_scenario(one_input_block, one_output_block):
    a = one_output_block()
    b = one_input_block()
    b.inputs[0].connect(a.outputs[0])
    a.trigger_update()
    yield a, b
    mca.framework.io_registry.Registry.clear()


@pytest.fixture
def second_scenario(two_output_block, two_input_block):
    a = two_output_block()
    b = two_input_block()
    b.inputs[0].connect(a.outputs[0])
    b.inputs[1].connect(a.outputs[1])
    a.trigger_update()
    yield a, b
    mca.framework.io_registry.Registry.clear()


@pytest.fixture
def third_scenario(one_output_block, two_input_block):
    a = one_output_block()
    b = two_input_block()
    a.trigger_update()
    b.inputs[0].connect(a.outputs[0])
    b.inputs[1].connect(a.outputs[0])
    yield a, b
    mca.framework.io_registry.Registry.clear()


@pytest.fixture
def fourth_scenario(one_output_block, one_input_block):
    a = one_output_block()
    b = one_input_block()
    c = one_input_block()
    a.trigger_update()
    b.inputs[0].connect(a.outputs[0])
    c.inputs[0].connect(a.outputs[0])
    yield a, b, c
    mca.framework.io_registry.Registry.clear()


@pytest.fixture
def fifth_scenario(one_output_block, one_input_one_output_block,
                   one_input_block):
    a = one_output_block()
    b = one_input_one_output_block()
    c = one_input_block()
    a.trigger_update()
    b.inputs[0].connect(a.outputs[0])
    c.inputs[0].connect(b.outputs[0])
    yield a, b, c
    mca.framework.io_registry.Registry.clear()


@pytest.fixture
def sixth_scenario(one_output_block, one_input_one_output_block,
                   two_input_block):
    a = one_output_block()
    b = one_input_one_output_block()
    c = one_input_one_output_block()
    d = two_input_block()
    a.trigger_update()
    b.inputs[0].connect(a.outputs[0])
    c.inputs[0].connect(a.outputs[0])
    d.inputs[0].connect(b.outputs[0])
    d.inputs[1].connect(c.outputs[0])
    yield a, b, c, d
    mca.framework.io_registry.Registry.clear()


@pytest.fixture
def seventh_scenario(one_output_block, two_input_one_output_block,
                     one_input_block):
    a = one_output_block()
    b = one_output_block()
    c = two_input_one_output_block()
    d = one_input_block()
    a.trigger_update()
    b.trigger_update()
    c.inputs[0].connect(a.outputs[0])
    c.inputs[1].connect(b.outputs[0])
    d.inputs[0].connect(c.outputs[0])
    yield a, b, c, d
    mca.framework.io_registry.Registry.clear()


@pytest.fixture
def add_input_scenario(dynamic_input_block):
    a = dynamic_input_block()
    a.add_input(mca.framework.block_io.Input(a))
    a.add_input(mca.framework.block_io.Input(a))
    yield a
    mca.framework.io_registry.Registry.clear()


@pytest.fixture
def delete_input_scenario(add_input_scenario):
    a = add_input_scenario
    a.delete_input(2)
    yield a


@pytest.fixture
def dynamic_input_scenario(add_input_scenario, two_output_block,
                           one_output_block, one_input_block):
    a = add_input_scenario
    b = two_output_block()
    c = one_output_block()
    d = one_input_block()
    b.trigger_update()
    c.trigger_update()
    a.inputs[0].connect(b.outputs[0])
    a.inputs[1].connect(b.outputs[1])
    a.inputs[2].connect(c.outputs[0])
    d.inputs[0].connect(a.outputs[0])
    yield a, b, c, d


@pytest.fixture
def add_output_scenario(dynamic_output_block):
    a = dynamic_output_block()
    a.add_output(mca.framework.block_io.Output(block=a))
    a.add_output(mca.framework.block_io.Output(block=a))
    yield a
    mca.framework.io_registry.Registry.clear()


@pytest.fixture
def delete_output_scenario(add_output_scenario):
    a = add_output_scenario
    a.delete_output(1)
    yield a


@pytest.fixture
def dynamic_output_scenario(add_output_scenario, two_input_one_output_block,
                            one_output_block, one_input_block):
    a = add_output_scenario
    b = two_input_one_output_block()
    c = one_output_block()
    d = one_input_block()
    c.trigger_update()
    a.inputs[0].connect(c.outputs[0])
    b.inputs[0].connect(a.outputs[0])
    b.inputs[1].connect(a.outputs[1])
    d.inputs[0].connect(b.outputs[0])
    yield a, b, c, d


"""Block connecting, disconnecting, data availability tests."""


def test_connect(basic_scenario):
    a, b = basic_scenario
    assert [a.outputs[0], b.inputs[0]] in mca.framework.io_registry.Registry._graph.edges


def test_connect_2(one_input_block):
    a = one_input_block()
    b = one_input_block()
    print(a is b)
    with pytest.raises(exceptions.BlockConnectionError):
        b.inputs[0].connect(a.inputs[0])
    mca.framework.io_registry.Registry.clear()


def test_connect_3(basic_scenario, one_output_block):
    a, b = basic_scenario
    c = one_output_block()
    with pytest.raises(exceptions.BlockConnectionError):
        b.inputs[0].connect(c.outputs[0])


def test_disconnect_input(basic_scenario):
    a, b = basic_scenario
    b.inputs[0].disconnect()
    assert [
        a.outputs[0],
        b.inputs[0],
    ] not in mca.framework.io_registry.Registry._graph.edges
    b.inputs[0].disconnect()
    assert [
        a.outputs[0],
        b.inputs[0],
    ] not in mca.framework.io_registry.Registry._graph.edges


def test_disconnect_output(basic_scenario, one_input_block):
    a, b = basic_scenario
    c = one_input_block()
    c.inputs[0].connect(a.outputs[0])
    a.outputs[0].disconnect()
    assert [
        a.outputs[0],
        b.inputs[0],
    ] not in mca.framework.io_registry.Registry._graph.edges
    assert [
        a.outputs[0],
        c.inputs[0],
    ] not in mca.framework.io_registry.Registry._graph.edges
    a.outputs[0].disconnect()
    assert [
        a.outputs[0],
        c.inputs[0],
    ] not in mca.framework.io_registry.Registry._graph.edges


def test_get_output(basic_scenario):
    a, b = basic_scenario
    assert mca.framework.io_registry.Registry.get_output(b.inputs[0]) is a.outputs[0]
    b.inputs[0].disconnect()
    assert mca.framework.io_registry.Registry.get_output(b.inputs[0]) is None


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
    a.trigger_update()
    assert b.process_count == 3


def test_third_scenario_data(third_scenario):
    a, b = third_scenario
    assert b.inputs[0].data == 1
    assert b.inputs[1].data == 1
    a.outputs[0].disconnect()
    assert b.inputs[0].data is None
    assert b.inputs[1].data is None


def test_fourth_scenario_behaviour(fourth_scenario):
    a, b, c = fourth_scenario
    assert b.process_count == 1
    assert c.process_count == 1
    a.trigger_update()
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
    a.trigger_update()
    assert c.process_count == 2
    b.inputs[0].disconnect()
    assert c.process_count == 3


def test_fifth_scenario_data(fifth_scenario):
    a, b, c = fifth_scenario
    assert c.inputs[0].data == 2
    b.inputs[0].disconnect()
    assert c.inputs[0].data is None


def test_sixth_scenario_behaviour(sixth_scenario):
    a, b, c, d = sixth_scenario
    assert d.process_count == 2
    a.outputs[0].disconnect()
    assert d.process_count == 3
    assert b.process_count == 2
    assert c.process_count == 2
    a.trigger_update()
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


def test_eighth_scenario_behaviour(one_output_block,
                                   two_input_two_output_block,
                                   two_input_block):
    a = one_output_block()
    b = two_input_two_output_block()
    c = two_input_block()
    b.inputs[0].connect(a.outputs[0])
    b.inputs[1].connect(a.outputs[0])
    c.inputs[0].connect(b.outputs[0])
    c.inputs[1].connect(b.outputs[1])
    a.trigger_update()
    assert c.process_count == 3


"""Tests for detection of BlockCircleErrors."""


def test_block_circle_error(seventh_scenario):
    a, b, c, d = seventh_scenario
    c.inputs[0].disconnect()
    with pytest.raises(exceptions.BlockCircleError):
        c.inputs[0].connect(c.outputs[0])


def test_block_circle_error_2(one_output_block, two_input_one_output_block):
    a = one_output_block()
    b = one_output_block()
    c = two_input_one_output_block()
    d = two_input_one_output_block()
    c.inputs[0].connect(a.outputs[0])
    d.inputs[0].connect(b.outputs[0])
    c.inputs[1].connect(d.outputs[0])
    with pytest.raises(exceptions.BlockCircleError):
        d.inputs[1].connect(c.outputs[0])
    mca.framework.io_registry.Registry.clear()


"""Tests concerning the dynamic block."""


def test_add_input(add_input_scenario, dynamic_output_block):
    a = add_input_scenario
    assert len(a.inputs) == 3
    assert [a.inputs[1], a.outputs[0]] in mca.framework.io_registry.Registry._graph.edges
    with pytest.raises(exceptions.DynamicIOError):
        a.add_input(mca.framework.block_io.Input(a))
    b = dynamic_output_block()
    with pytest.raises(exceptions.DynamicIOError):
        b.add_input(mca.framework.block_io.Input(b))


def test_add_input_2(dynamic_input_block):
    a = dynamic_input_block()
    b = mca.framework.block_io.Input(a)
    a.add_input(b)
    with pytest.raises(exceptions.DynamicIOError):
        a.add_input(b)


def test_delete_input(delete_input_scenario, dynamic_output_block):
    a = delete_input_scenario
    assert len(a.inputs) == 2
    assert all([x in mca.framework.io_registry.Registry._graph.nodes() for x in a.inputs])
    a.delete_input(1)
    with pytest.raises(exceptions.DynamicIOError):
        a.delete_input(0)
    b = dynamic_output_block()
    with pytest.raises(exceptions.DynamicIOError):
        b.delete_input(0)


def test_dynamic_input_behaviour(dynamic_input_scenario):
    a, b, c, d = dynamic_input_scenario
    a.delete_input(2)
    assert a.process_count == 4


def test_dynamic_input_data(dynamic_input_scenario):
    a, b, c, d = dynamic_input_scenario
    assert d.inputs[0].data == 4
    a.delete_input(2)
    assert d.inputs[0].data == 3


def test_add_output(add_output_scenario):
    a = add_output_scenario
    assert len(a.outputs) == 3
    assert [a.inputs[0], a.outputs[2]] in mca.framework.io_registry.Registry._graph.edges
    with pytest.raises(exceptions.DynamicIOError):
        a.add_output(mca.framework.block_io.Output(a))
        a.add_output(mca.framework.block_io.Output(a))


def test_delete_output(delete_output_scenario):
    a = delete_output_scenario
    assert len(a.outputs) == 2
    assert all([x in mca.framework.io_registry.Registry._graph.nodes()
                for x in a.outputs])
    a.delete_output(1)
    with pytest.raises(exceptions.DynamicIOError):
        a.delete_output(0)


def test_dynamic_output_behaviour(dynamic_output_scenario):
    a, b, c, d = dynamic_output_scenario
    assert a.process_count == 1
    a.delete_output(2)
    assert a.process_count == 1


def test_dynamic_output_data(dynamic_output_scenario):
    a, b, c, d = dynamic_output_scenario
    assert a.outputs[0].data == 1
    assert a.outputs[2].data == 3


"""Tests for block convenience methods."""


def test_check_all_empty_inputs(two_input_one_output_block, two_output_block):
    a = two_input_one_output_block()
    a.outputs[0].data = 1
    assert a.all_inputs_empty() is True
    assert a.outputs[0].data is None
    b = two_output_block()
    b.outputs[0].data = 1
    a.inputs[0].connect(b.outputs[0])
    assert a.all_inputs_empty() is False


def test_check_any_empty_input(two_input_one_output_block, two_output_block):
    a = two_input_one_output_block()
    a.outputs[0].data = 1
    b = two_output_block()
    b.trigger_update()
    a.inputs[0].connect(b.outputs[0])
    assert a.any_inputs_empty() is True
    assert a.outputs[0].data is None
    a.inputs[1].connect(b.outputs[1])
    assert a.any_inputs_empty() is False
    assert a.outputs[0].data == 3


def test_read_kwargs(parameter_block):
    a = parameter_block(test_parameter=0.1, test_parameter1=1, multiplier=
                        {"factor": 10})
    assert a.parameters["test_parameter"].value == 0.1
    assert a.parameters["test_parameter1"].value == 1
    assert a.parameters["multiplier"].parameters["factor"].value == 10
    assert a.parameters["multiplier"].parameters["decibel"].value == 10


def test_disconnect_all(seventh_scenario):
    a, b, c, d = seventh_scenario
    c.disconnect_all()
    assert [a.outputs[0],
            c.inputs[0]] not in mca.framework.io_registry.Registry._graph.edges
    assert [b.outputs[0],
            c.inputs[1]] not in mca.framework.io_registry.Registry._graph.edges
    assert [c.outputs[0],
            d.inputs[0]] not in mca.framework.io_registry.Registry._graph.edges


def test_get_metadata(default_metadata):
    output_metadata = mca.framework.data_types.MetaData(name="test",
                                                         unit_a="W",
                                                         symbol_a="P",
                                                         unit_o="kg",
                                                         symbol_o="m")
    output = mca.framework.block_io.Output(metadata=output_metadata)
    result_metadata = output.get_metadata(default_metadata)
    assert result_metadata == default_metadata
    assert result_metadata.name == output_metadata.name
    output.abscissa_metadata = True
    output.ordinate_metadata = False
    result_metadata = output.get_metadata(default_metadata)
    assert result_metadata.unit_a == output_metadata.unit_a
    assert result_metadata.symbol_a == output_metadata.symbol_a
    assert result_metadata.quantity_a == output_metadata.quantity_a
    assert result_metadata.unit_o == default_metadata.unit_o
    assert result_metadata.symbol_o == default_metadata.symbol_o
    assert result_metadata.quantity_o == default_metadata.quantity_o
    output.abscissa_metadata = False
    output.ordinate_metadata = True
    result_metadata = output.get_metadata(default_metadata)
    assert result_metadata.unit_a == default_metadata.unit_a
    assert result_metadata.symbol_a == default_metadata.symbol_a
    assert result_metadata.quantity_a == default_metadata.quantity_a
    assert result_metadata.unit_o == output_metadata.unit_o
    assert result_metadata.symbol_o == output_metadata.symbol_o
    assert result_metadata.quantity_o == output_metadata.quantity_o
    output.abscissa_metadata = True
    output.ordinate_metadata = True
    result_metadata = output.get_metadata(default_metadata)
    assert result_metadata == output_metadata

