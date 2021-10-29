import pytest
import os

from mca import blocks, exceptions
from mca.framework import save, load, io_registry, block_io


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


def test_load_block_structure(adder_signal_generator):
    adder_signal_generator
    save.save_block_structure(file_path)
    io_registry.Registry.clear()
    saved_blocks = load.load_block_structure(file_path)
    for block in saved_blocks:
        if isinstance(block, blocks.Adder):
            assert len(block.inputs) == 3
            assert block.inputs[2].connected_output is not None
            assert block.outputs[0].abscissa_metadata is True
        if isinstance(block, blocks.SignalGeneratorPeriodic):
            assert block.parameters["name"].value == "test"
            assert block.parameters["amp"].value == 3
            assert block.parameters["abscissa"].parameters["start"].value == 1
            assert block.parameters["abscissa"].parameters["values"].value == 100
            assert block.outputs[0].metadata.name == "test1"
    with pytest.raises(exceptions.DataLoadingError):
        load.load_block_structure(file_path)
