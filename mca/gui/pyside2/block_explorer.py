from PySide2 import QtWidgets, QtCore, QtGui
import os

import mca
from mca.language import _
from mca import blocks


class BlockExplorer(QtWidgets.QWidget):
    """Widget that holds and arranges the search bar,
     the button filter and the block list.

     Attributes
         search_bar: Matches the strings the tags and block classes within
                     the block list.
         button_filter: Group of buttons which can only be pressed exclusively
                        and sort the list by tags or by blocks.
        block_list: Contains blocks and tags al items.
     """

    def __init__(self, scene):
        """Initialize BlockExplorer widget.

        Args:
            scene: Reference of the block scene.
        """
        QtWidgets.QWidget.__init__(self)

        self.setMinimumSize(200, 0)
        self.setLayout(QtWidgets.QVBoxLayout())

        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.setPlaceholderText(_("Search..."))

        self.button_filter = ButtonFilter()
        self.block_list = BlockList(scene)
        self.block_list.button_group = self.button_filter.button_group

        self.button_filter.tag_button.pressed.connect(self.block_list.show_all)
        self.button_filter.block_button.pressed.connect(self.block_list.show_blocks)

        self.block_list.search_bar = self.search_bar
        self.search_bar.textChanged.connect(self.block_list.show_items)

        self.layout().addWidget(self.search_bar)
        self.layout().addWidget(self.button_filter)
        self.layout().addWidget(self.block_list)

        self.block_list.show_all()


class BlockList(QtWidgets.QListWidget):
    """BlockList widget holding tags and drag-able blocks. Allows creating
    block items in the :class:`.BlockScene` with the drag-able block list
    items.
    """
    def __init__(self, scene):
        """Initialize BlockList widget.

        Args:
            scene: Reference of the :class:`.BlockScene` .
        """
        QtWidgets.QListWidget.__init__(self)

        self.scene = scene
        self.search_bar = None
        self.button_group = None

        self.setDragEnabled(True)

        self.menu = QtWidgets.QMenu()
        self.new_block_action = QtWidgets.QAction(_("New block"))
        self.new_block_action.triggered.connect(
            lambda: self.scene.create_block_item(self.currentItem().data(3)(),
                                                 self.width(), 10)
        )
        self.menu.addAction(self.new_block_action)

        for block_class in blocks.block_classes:
            self.add_block(block_class)
        for tag in blocks.tag_dict.keys():
            self.add_tag(tag)

    def mouseMoveEvent(self, event):
        """Method invoked when the mouse grabs an item from the list. Allows
        dragging the blocks into the :class:`.BlockScene`.
        """
        mime_data = QtCore.QMimeData()
        drag = QtGui.QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction,
                   QtCore.Qt.CopyAction)

    def mouseDoubleClickEvent(self, event):
        """Method invoked when an item in the list gets double-clicked.
        If a block gets clicked, it will get initialized in the
        :class:`.BlockScene`. If a tag gets clicked the string will appear in
         the search_bar.
        """
        item = self.currentItem()
        if item is None:
            return
        if item.data(4) == "block":
            selected_block_class = item.data(3)
            self.scene.create_block_item(selected_block_class(), 0, 0,
                                         open_edit_window=True, find_free_space=True)
        elif item.data(4) == "tag":
            self.search_bar.setText(item.data(5))

    def contextMenuEvent(self, event):
        """Method invoked when right-clicking with the mouse. Opens
        the menu.
        """
        self.menu.exec_(event.globalPos())

    def show_items(self):
        """Shows and hides certain list items depending on the
        search_bar string.
        """
        if self.button_group.button(1).isChecked():
            self.show_all()
        else:
            self.show_only_blocks()

    def hide_all_items(self):
        """Hide all items in the BlockList."""
        all_items = self.findItems("", QtCore.Qt.MatchStartsWith)
        for item in all_items:
            self.setItemHidden(item, True)

    def show_blocks(self):
        """Show all block items matching the search string in the search bar."""
        self.hide_all_items()
        search_string = self.search_bar.text()
        matching_items = self.findItems(search_string, QtCore.Qt.MatchContains)
        for item in matching_items:
            if item.data(4) == "block" and item.data(5) is False:
                item.setHidden(False)

    def show_all(self):
        """Show blocks and tags with their related blocks matching the
        search string in the search bar. Blocks which already appear as
        related blocks under a tag get hidden.
        """
        self.hide_all_items()
        search_string = self.search_bar.text()
        matching_items = self.findItems(search_string, QtCore.Qt.MatchContains)
        matching_tags = filter(lambda x: x.data(4) == "tag", matching_items)
        related_blocks = []
        for tag in matching_tags:
            related_blocks += tag.related_blocks
        matching_blocks = list(map(lambda x: x.data(3), related_blocks))
        for item in matching_items:
            if search_string and item.data(5) is False and matching_blocks.count(item.data(3)) == 0:
                item.setHidden(False)
            elif item.data(4) == "tag":
                item.setHidden(False)

    def add_block(self, block, related_block=False):
        """Adds a block to the list.

        Args:
            block: Class of the block to add.
            related_block: Flag whether the block is related to a tag.
        """
        item = QtWidgets.QListWidgetItem()
        if block.icon_file:
            item.setIcon(QtGui.QIcon(os.path.dirname(
                mca.__file__) + "/blocks/icons/" + block.icon_file))
        item.setData(3, block)
        item.setData(4, "block")
        item.setData(5, related_block)
        item.setText(block.name)
        self.addItem(item)
        return item

    def add_tag(self, tag_name):
        """Adds a tag and its related blocks to the list.

        Args:
            tag_name (str): Name of the tag.
        """
        tag_item = TagListItem(tag_name=tag_name)
        self.addItem(tag_item)
        for block_class in blocks.tag_dict[tag_name]:
            block_item = self.add_block(block_class, related_block=True)
            tag_item.related_blocks.append(block_item)
        return tag_item


class TagListItem(QtWidgets.QListWidgetItem):
    """Custom list widget item for tags. Setting the hidden status
    of the tag item also sets the status for the related blocks.

    Attributes:
        related_blocks(list): List of all block list items related to this tag.
    """
    def __init__(self, tag_name):
        """Initialize TagListItem.

        Args:
            tag_name: Name of the tag.
        """
        QtWidgets.QListWidgetItem.__init__(self)

        self.setData(4, "tag")
        self.setData(5, tag_name)

        font = self.font()
        font.setBold(True)
        font.setPointSize(13)
        self.setFont(font)
        self.setText(tag_name)

        self.related_blocks = []

    def setHidden(self, hide):
        """Sets the hidden status for itself and the related blocks.

        Args:
            hide: True to set the tag and the related blocks hidden.
        """
        for block in self.related_blocks:
            block.setHidden(hide)
        super().setHidden(hide)


class ButtonFilter(QtWidgets.QWidget):
    """Widget for managing and arranging a group of buttons for filtering
    the block list.

    Attributes:
        button_group: Abstract widget managing the behaviour of a
                      group of buttons.
        tag_button: Button to filter the :class:`.BlockList` for tags and
                    their related blocks.
        block_button: Button to filter only for block list items which are
                      not related to a tag.
    """
    def __init__(self):
        """Initialize ButtonFilter widget."""
        QtWidgets.QWidget.__init__(self)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().setAlignment(QtCore.Qt.AlignLeft)
        self.button_group = QtWidgets.QButtonGroup()
        self.button_group.setExclusive(True)

        self.tag_button = QtWidgets.QPushButton("T")
        self.tag_button.setToolTip("Show blocks associated with tags")
        self.tag_button.setCheckable(True)
        self.tag_button.setChecked(True)
        self.tag_button.setMaximumWidth(30)

        self.block_button = QtWidgets.QPushButton("B")
        self.block_button.setToolTip("Search only for blocks")
        self.block_button.setCheckable(True)
        self.block_button.setMaximumWidth(30)

        self.layout().addWidget(self.tag_button)
        self.layout().addWidget(self.block_button)

        self.button_group.addButton(self.tag_button, 1)
        self.button_group.addButton(self.block_button, 2)
