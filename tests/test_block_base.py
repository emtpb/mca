"""Tests for the Block, the DynamicBlock and the Connection between blocks."""
import pytest
import os
import json

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
    mca.framework.block_registry.Registry.clear()


@pytest.fixture
def second_scenario(two_output_block, two_input_block):
    a = two_output_block()
    b = two_input_block()
    b.inputs[0].connect(a.outputs[0])
    b.inputs[1].connect(a.outputs[1])
    a.trigger_update()
    yield a, b
    mca.framework.block_registry.Registry.clear()


@pytest.fixture
def third_scenario(one_output_block, two_input_block):
    a = one_output_block()
    b = two_input_block()
    a.trigger_update()
    b.inputs[0].connect(a.outputs[0])
    b.inputs[1].connect(a.outputs[0])
    yield a, b
    mca.framework.block_registry.Registry.clear()


@pytest.fixture
def fourth_scenario(one_output_block, one_input_block):
    a = one_output_block()
    b = one_input_block()
    c = one_input_block()
    a.trigger_update()
    b.inputs[0].connect(a.outputs[0])
    c.inputs[0].connect(a.outputs[0])
    yield a, b, c
    mca.framework.block_registry.Registry.clear()


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
    mca.framework.block_registry.Registry.clear()


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
    mca.framework.block_registry.Registry.clear()


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
    mca.framework.block_registry.Registry.clear()


@pytest.fixture
def add_input_scenario(dynamic_input_block):
    a = dynamic_input_block()
    a.add_input(mca.framework.block_io.Input(a))
    a.add_input(mca.framework.block_io.Input(a))
    yield a
    mca.framework.block_registry.Registry.clear()


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


"""Block connecting, disconnecting, data availability tests."""


def test_connect(basic_scenario):
    a, b = basic_scenario
    assert [a.outputs[0], b.inputs[0]] in mca.framework.block_registry.Registry._graph.edges


def test_connect_2(one_input_block):
    a = one_input_block()
    b = one_input_block()
    print(a is b)
    with pytest.raises(exceptions.ConnectionsError):
        b.inputs[0].connect(a.inputs[0])
    mca.framework.block_registry.Registry.clear()


def test_connect_3(basic_scenario, one_output_block):
    a, b = basic_scenario
    c = one_output_block()
    with pytest.raises(exceptions.ConnectionsError):
        b.inputs[0].connect(c.outputs[0])


def test_disconnect_input(basic_scenario):
    a, b = basic_scenario
    b.inputs[0].disconnect()
    assert [
        a.outputs[0],
        b.inputs[0],
    ] not in mca.framework.block_registry.Registry._graph.edges
    b.inputs[0].disconnect()
    assert [
        a.outputs[0],
        b.inputs[0],
    ] not in mca.framework.block_registry.Registry._graph.edges


def test_disconnect_output(basic_scenario, one_input_block):
    a, b = basic_scenario
    c = one_input_block()
    c.inputs[0].connect(a.outputs[0])
    a.outputs[0].disconnect()
    assert [
        a.outputs[0],
        b.inputs[0],
    ] not in mca.framework.block_registry.Registry._graph.edges
    assert [
        a.outputs[0],
        c.inputs[0],
    ] not in mca.framework.block_registry.Registry._graph.edges
    a.outputs[0].disconnect()
    assert [
        a.outputs[0],
        c.inputs[0],
    ] not in mca.framework.block_registry.Registry._graph.edges


def test_get_output(basic_scenario):
    a, b = basic_scenario
    assert mca.framework.block_registry.Registry.get_output(b.inputs[0]) is a.outputs[0]
    b.inputs[0].disconnect()
    assert mca.framework.block_registry.Registry.get_output(b.inputs[0]) is None


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
    mca.framework.block_registry.Registry.clear()


"""Tests concerning the dynamic block."""


def test_add_input(add_input_scenario, dynamic_output_block):
    a = add_input_scenario
    assert len(a.inputs) == 3
    assert [a.inputs[1], a.outputs[0]] in mca.framework.block_registry.Registry._graph.edges
    with pytest.raises(exceptions.InputOutputError):
        a.add_input(mca.framework.block_io.Input(a))
    b = dynamic_output_block()
    with pytest.raises(exceptions.InputOutputError):
        b.add_input(mca.framework.block_io.Input(b))


def test_add_input_2(dynamic_input_block):
    a = dynamic_input_block()
    b = mca.framework.block_io.Input(a)
    a.add_input(b)
    with pytest.raises(exceptions.InputOutputError):
        a.add_input(b)


def test_delete_input(delete_input_scenario, dynamic_output_block):
    a = delete_input_scenario
    assert len(a.inputs) == 2
    assert all([x in mca.framework.block_registry.Registry._graph.nodes() for x in a.inputs])
    a.delete_input(1)
    with pytest.raises(exceptions.InputOutputError):
        a.delete_input(0)
    b = dynamic_output_block()
    with pytest.raises(exceptions.InputOutputError):
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


def test_dynamic_output_data(dynamic_output_block,
                             one_output_block, two_input_block):
    a = dynamic_output_block()
    b = one_output_block()
    c = two_input_block()
    d = two_input_block()
    b.trigger_update()
    a.inputs[0].connect(b.outputs[0])
    a.add_output(mca.framework.block_io.Output(a, None))
    a.add_output(mca.framework.block_io.Output(a, None))
    c.inputs[0].connect(a.outputs[0])
    c.inputs[1].connect(a.outputs[1])
    assert c.inputs[0].data == 1 and c.inputs[1].data == 1
    d.inputs[0].connect(a.outputs[2])
    d.inputs[1].connect(a.outputs[1])
    a.delete_output(1)
    assert d.inputs[1].data is None and d.inputs[0].data == 1
    mca.framework.block_registry.Registry.clear()


"""Tests for block convenience methods."""


def test_check_empty_inputs(two_input_one_output_block, two_output_block):
    a = two_input_one_output_block()
    a.outputs[0].data = 1
    assert a.check_empty_inputs() is True
    assert a.outputs[0].data is None
    b = two_output_block()
    b.outputs[0].data = 1
    a.inputs[0].connect(b.outputs[0])
    assert a.check_empty_inputs() is None


def test_read_kwargs(parameter_block):
    a = parameter_block(test_parameter=0.1, test_parameter1=1)
    assert a.parameters["test_parameter"].value == 0.1
    assert a.parameters["test_parameter1"].value == 1


def test_disconnect_all(seventh_scenario):
    a, b, c, d = seventh_scenario
    c.disconnect_all()
    assert [a.outputs[0],
            c.inputs[0]] not in mca.framework.block_registry.Registry._graph.edges
    assert [b.outputs[0],
            c.inputs[1]] not in mca.framework.block_registry.Registry._graph.edges
    assert [c.outputs[0],
            d.inputs[0]] not in mca.framework.block_registry.Registry._graph.edges


def test_save_output_data(sin_block, sin_signal):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sin_block.save_output_data(0, dir_path + "/sin.json")
    test_dict = {"data_type": "Signal",
                 "name": sin_signal.meta_data.name,
                 "quantity_a": sin_signal.meta_data.quantity_a,
                 "symbol_a": sin_signal.meta_data.symbol_a,
                 "unit_a": repr(sin_signal.meta_data.unit_a),
                 "quantity_o": sin_signal.meta_data.quantity_o,
                 "symbol_o": sin_signal.meta_data.symbol_o,
                 "unit_o": repr(sin_signal.meta_data.unit_o),
                 "abscissa_start": sin_signal.abscissa_start,
                 "values": sin_signal.values,
                 "increment": sin_signal.increment,
                 "ordinate": str(sin_signal.ordinate)}
    with open(dir_path + "/sin.json", "r") as save_file:
        test_dict_saved = json.load(save_file)
    assert test_dict == test_dict_saved

    file_list = [f for f in os.listdir(dir_path) if f.endswith(".json")]
    for f in file_list:
        os.remove(os.path.join(dir_path, f))


def test_get_meta_data(default_meta_data):
    output_meta_data = mca.framework.data_types.MetaData(name="test",
                                                         unit_a="W",
                                                         symbol_a="P",
                                                         unit_o="kg",
                                                         symbol_o="m")
    output = mca.framework.block_io.Output(meta_data=output_meta_data)
    result_meta_data = output.get_meta_data(default_meta_data)
    assert result_meta_data == default_meta_data
    assert result_meta_data.name == output_meta_data.name
    output.abscissa_meta_data = True
    output.ordinate_meta_data = False
    result_meta_data = output.get_meta_data(default_meta_data)
    assert result_meta_data.unit_a == output_meta_data.unit_a
    assert result_meta_data.symbol_a == output_meta_data.symbol_a
    assert result_meta_data.quantity_a == output_meta_data.quantity_a
    assert result_meta_data.unit_o == default_meta_data.unit_o
    assert result_meta_data.symbol_o == default_meta_data.symbol_o
    assert result_meta_data.quantity_o == default_meta_data.quantity_o
    output.abscissa_meta_data = False
    output.ordinate_meta_data = True
    result_meta_data = output.get_meta_data(default_meta_data)
    assert result_meta_data.unit_a == default_meta_data.unit_a
    assert result_meta_data.symbol_a == default_meta_data.symbol_a
    assert result_meta_data.quantity_a == default_meta_data.quantity_a
    assert result_meta_data.unit_o == output_meta_data.unit_o
    assert result_meta_data.symbol_o == output_meta_data.symbol_o
    assert result_meta_data.quantity_o == output_meta_data.quantity_o
    output.abscissa_meta_data = True
    output.ordinate_meta_data = True
    result_meta_data = output.get_meta_data(default_meta_data)
    assert result_meta_data == output_meta_data

