import os
import json
import pytest

from mca import blocks
from mca.framework import save, io_registry, block_io


file_path = os.path.dirname(os.path.realpath(__file__)) + "/test.json"


@pytest.fixture()
def adder_signal_generator():
    io_registry.Registry.clear()
    a = blocks.Adder()
    b = blocks.SignalGeneratorPeriodic(name="test", amp=3,
                                       abscissa={"values": 100, "start": 1})
    b.outputs[0].metadata.name = "test1"
    a.outputs[0].abscissa_metadata = True
    a.add_input(block_io.Input(a))
    a.inputs[2].connect(b.outputs[0])
    yield
    io_registry.Registry.clear()
    os.remove(file_path)


def test_save_block_structure(adder_signal_generator):
    adder_signal_generator
    save.save_block_structure(file_path)
    io_registry.Registry.clear()
    with open(file_path, "r") as save_file:
        saved_structure = json.load(save_file)
    assert len(saved_structure["blocks"]) == 2
    for block_save in saved_structure["blocks"]:
        if block_save["class"] == str(type(blocks.Adder)):
            assert len(block_save["inputs"]) == 3
            assert block_save["inputs"][2].get("connected_output") is not None
            assert block_save["outputs"][0].abscissa_metadata is True
        if block_save["class"] == str(type(blocks.SignalGeneratorPeriodic)):
            assert block_save["class"]["parameters"]["name"] == "test"
            assert block_save["class"]["parameters"]["amp"] == 3
            assert block_save["class"]["parameters"]["abscissa"]["start"] == 1
            assert block_save["class"]["parameters"]["abscissa"]["values"] == 100
            assert block_save["class"]["outputs"][0]["signal_name"] == "test1"