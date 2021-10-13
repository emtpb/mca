import pytest
import os

from mca.framework import io_registry, block_io
from mca import blocks


def test_clear(one_input_one_output_block):
    one_input_one_output_block()
    assert io_registry.Registry._graph.nodes
    io_registry.Registry.clear()
    assert not io_registry.Registry._graph.nodes


def test_get_all_blocks(one_input_block, one_output_block):
    io_registry.Registry.clear()
    a = one_input_block()
    assert len(io_registry.Registry.get_all_blocks()) == 1
    assert io_registry.Registry.get_all_blocks()[0] == a
    b = one_output_block()
    assert len(io_registry.Registry.get_all_blocks()) == 2
    assert b in io_registry.Registry.get_all_blocks()
    io_registry.Registry.clear()
    assert len(io_registry.Registry.get_all_blocks()) == 0


def test_remove_block(one_input_block, one_input_one_output_block):
    io_registry.Registry.clear()
    a = one_input_block()
    b = one_input_one_output_block()
    a.inputs[0].connect(b.outputs[0])
    io_registry.Registry.remove_block(b)
    assert a.inputs[0].connected_output is None
    assert b.inputs[0] not in io_registry.Registry._graph.nodes
    assert b.outputs[0] not in io_registry.Registry._graph.nodes
    assert b not in io_registry.Registry.get_all_blocks()
