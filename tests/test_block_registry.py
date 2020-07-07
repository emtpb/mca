import pytest
import os
import json

from mca.framework import block_registry, block_io
from mca import blocks


file_path = os.path.dirname(os.path.realpath(__file__)) + "/test.json"


def test_clear(one_input_one_output_block):
    one_input_one_output_block()
    assert block_registry.Registry._graph.nodes
    block_registry.Registry.clear()
    assert not block_registry.Registry._graph.nodes


def test_get_all_blocks(one_input_block, one_output_block):
    block_registry.Registry.clear()
    a = one_input_block()
    print(block_registry.Registry.get_all_blocks())
    assert len(block_registry.Registry.get_all_blocks()) == 1
    assert block_registry.Registry.get_all_blocks()[0] == a
    b = one_output_block()
    assert len(block_registry.Registry.get_all_blocks()) == 2
    assert b in block_registry.Registry.get_all_blocks()
    block_registry.Registry.clear()
    assert len(block_registry.Registry.get_all_blocks()) == 0


@pytest.fixture()
def adder_signal_generator():
    block_registry.Registry.clear()
    a = blocks.Adder()
    b = blocks.SignalGeneratorPeriodic(name="test", amp=3)
    b.outputs[0].meta_data.name = "test1"
    a.add_input(block_io.Input(a))
    a.inputs[2].connect(b.outputs[0])
    yield
    block_registry.Registry.clear()
    os.remove(file_path)


def test_save_block_structure(adder_signal_generator):
    adder_signal_generator
    block_registry.Registry.save_block_structure(file_path)
    block_registry.Registry.clear()
    with open(file_path, "r") as save_file:
        saved_structure = json.load(save_file)
    assert len(saved_structure["blocks"]) == 2
    for block_save in saved_structure["blocks"]:
        if block_save["class"] == str(type(blocks.Adder)):
            assert len(block_save["inputs"]) == 3
            assert block_save["inputs"][2].get("connected_output") is not None
        if block_save["class"] == str(type(blocks.SignalGeneratorPeriodic)):
            assert block_save["class"]["parameters"]["name"] == "test"
            assert block_save["class"]["parameters"]["amp"] == 3
            assert block_save["class"]["outputs"][0]["signal_name"] == "test1"


def test_load_block_structure(adder_signal_generator):
    adder_signal_generator
    block_registry.Registry.save_block_structure(file_path)
    block_registry.Registry.clear()
    saved_blocks = block_registry.Registry.load_block_structure(file_path)
    for block in saved_blocks:
        if isinstance(block, blocks.Adder):
            assert len(block.inputs) == 3
            assert block.inputs[2].connected_output is not None
        if isinstance(block, blocks.SignalGeneratorPeriodic):
            assert block.parameters["name"].value == "test"
            assert block.parameters["amp"].value == 3
            assert block.outputs[0].meta_data.name == "test1"


def test_remove_block(one_input_block, one_input_one_output_block):
    block_registry.Registry.clear()
    a = one_input_block()
    b = one_input_one_output_block()
    a.inputs[0].connect(b.outputs[0])
    block_registry.Registry.remove_block(b)
    assert a.inputs[0].connected_output is None
    assert b.inputs[0] not in block_registry.Registry._graph.nodes
    assert b.outputs[0] not in block_registry.Registry._graph.nodes
    assert b not in block_registry.Registry.get_all_blocks()
