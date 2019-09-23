import networkx as nx

from . import output_base, input_base
from .. import exceptions


class IORegistry:
    """Class which registers all :class:`.Input` s and :class:`.Output` s 
    created and also handles connections  between Outputs and Inputs and the 
    consistency of the data through updates.
    
    Attributes:
        _graph: :ref:`Networkx Graph <networkx:DiGraph>` which is base of 
            IORegistry. 
    """

    def __init__(self):
        """Initializes the IORegistry."""
        self._graph = nx.DiGraph()

    def _invalidate_descendants(self, output):
        """Sets a flag of the output itself and all decendants to indicate
        their data may be invalid.
        
        Args:
            output: Output from which the invalidation starts.
        """
        output.up_to_date = False
        for descendant in nx.descendants(self._graph, output):
            descendant.up_to_date = False

    def _update_descendants(self, output):
        """Goes threw all decendants and updates the flags and tries to update 
        the block of the descendants. For example if an output is updated
        all connected inputs will be updated and the outputs of the same Block 
        as the inputs and so on.
        
        Note:
            A block will only update itself if all inputs are up to date.
        Args:
            output: Output from which the update process starts.
        """
        for edge in nx.bfs_edges(self._graph, output):
            if isinstance(edge[0], output_base.Output) and isinstance(
                edge[1], input_base.Input
            ):
                edge[1].up_to_date = edge[0].up_to_date
                edge[1].block.update_my_block()

    def invalidate_and_update(self, block):
        """Method which is called when a change (connect, disconnect,
        delete etc.) in the IO structure occurs
        which may cause data inconsistency. This method flags and updates
        blocks with an algorithm that ensures every Block updates itself
        only once in the process.
        
        Args:
            block (:class:`.Block`): Block in which the change occured.
        """
        for output in block.outputs:
            self._invalidate_descendants(output)
        block.update_my_block()
        for output in block.outputs:
            self._update_descendants(output)

    def add_node(self, node):
        """Adds an Input or Output to the registry.
        
        Args:
            node: Input or Output which should be added to the registry.
        
        Returns:
            The node which has been added to the structure.
        """
        self._graph.add_node(node)
        if isinstance(node, output_base.Output):
            for input_ in node.block.inputs:
                self._graph.add_edge(input_, node)
            return node
        if isinstance(node, input_base.Input):
            for output in node.block.outputs:
                self._graph.add_edge(node, output)
            return node

    def remove_input(self, input_):
        """Disconnects and removes an Input from the registry.
        
        Args:
            input_: Input which gets removed.
        """
        self.disconnect_input(input_)
        self._graph.remove_node(input_)

    def remove_output(self, output):
        """Disconnects and removes an Output from the registry.
        
        Args:
            output: Output which gets removed.
        """
        self.disconnect_output(output)
        self._graph.remove_node(output)

    def connect(self, output, input_):
        """Connects an Output to an Input.
        
        Args:
            output: Output which gets connected to the Input.
            input_: Input which gets connected to Output.
        
        Raises:
            exceptions.BlockCircleError: When connecting two nodes leads to
                a circle in the structure.
        """
        if not isinstance(output, output_base.Output) or not isinstance(
            input_, input_base.Input
        ):
            message = "{} is not instance of {} or {} is not instance of {}".format(
                output, output_base.Output, input_, input_base.Input
            )
            raise exceptions.ConnectionsError(message)
        if list(self._graph.predecessors(input_)):
            raise exceptions.ConnectionsError("Input already connected")
        self._graph.add_edge(output, input_)
        if not nx.is_directed_acyclic_graph(self._graph):
            self._graph.remove_edge(output, input_)
            raise exceptions.BlockCircleError(input_.block)
        self.invalidate_and_update(input_.block)

    def disconnect_input(self, input_):
        """Disconnects an Input from an Output if connected.
        
        Args:
            input_: Input which gets disconnected.
        """
        output = list(self._graph.predecessors(input_))
        if output:    
            self._graph.remove_edge(output[0], input_)
            self.invalidate_and_update(input_.block)

    def disconnect_output(self, output):
        """Disconnects an Output from all its Inputs.
        
        Args:
            output: Output which gets disconnected.            
        """
        inputs = [x for x in self._graph.neighbors(output)]
        for input_ in inputs:
            self._graph.remove_edge(output, input_)
        for input_ in inputs:
            for output in input_.block.outputs:
                self._invalidate_descendants(output)
        for block in set([x.block for x in inputs]):
            block.update_my_block()
        for input_ in inputs:
            for output in input_.block.outputs:
                self._update_descendants(output)

    def get_output(self, input_):
        """Returns the connected Output from an Input.
        
        Args:
            input_: Input to which the Output is connected to.
        """
        if list(self._graph.predecessors(input_)):
            return list(self._graph.predecessors(input_))[0]
        
    def clear(self):
        """Removes all Inputs and Outputs from the IORegistry."""
        self._graph.clear()

Registry = IORegistry()
