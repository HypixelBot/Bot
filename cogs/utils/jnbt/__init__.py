"""
JNBT is a library for reading and writing Named Binary Tag (NBT) data for Python 3.
It features both DOM and SAX-style parsing and writing, as well as utilities to read world data (e.g. world save directories and Minecraft Anvil regions).
"""

#NBT Tag Types, Exceptions
from cogs.utils.jnbt.shared import (
    TAG_END, TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG, TAG_FLOAT, TAG_DOUBLE, TAG_BYTE_ARRAY, TAG_STRING, TAG_LIST, TAG_COMPOUND, TAG_INT_ARRAY,
    TAG_COUNT,
    NBTFormatError, WrongTagError, ConversionError, DuplicateNameError, UnknownTagTypeError, OutOfBoundsError
)

#read, NBTDocument and TAG_* Classes
from cogs.utils.jnbt.tag import read, NBTDocument, TAG_Byte, TAG_Short, TAG_Int, TAG_Long, TAG_Float, TAG_Double, TAG_Byte_Array, TAG_String, TAG_List, TAG_Compound, TAG_Int_Array

#NBT Parsers + Handlers
from cogs.utils.jnbt.parse import parse
from cogs.utils.jnbt.handler import NBTHandler, PrintNBTHandler

#NBT Writer
from cogs.utils.jnbt.writer import writer, NBTWriter

#Minecraft-related classes and utilities
from cogs.utils.jnbt.mc.util import setMinecraftDir, getMinecraftPath
from cogs.utils.jnbt.mc.player import Player

#Classes and functions to interact with Minecraft worlds
from cogs.utils.jnbt.mc.world import DIM_NETHER, DIM_OVERWORLD, DIM_END, getWorld, iterWorlds, World, Dimension, Region


#Export everything we imported above
__all__ = [
    "TAG_END", "TAG_BYTE", "TAG_SHORT", "TAG_INT", "TAG_LONG", "TAG_FLOAT", "TAG_DOUBLE", "TAG_BYTE_ARRAY", "TAG_STRING", "TAG_LIST", "TAG_COMPOUND", "TAG_INT_ARRAY",
    "TAG_COUNT",
    "NBTFormatError", "WrongTagError", "ConversionError", "DuplicateNameError", "UnknownTagTypeError", "OutOfBoundsError",
    "read", "NBTDocument", "TAG_Byte", "TAG_Short", "TAG_Int", "TAG_Long", "TAG_Float", "TAG_Double", "TAG_Byte_Array", "TAG_String", "TAG_List", "TAG_Compound", "TAG_Int_Array",
    "parse",
    "NBTHandler", "PrintNBTHandler",
    "writer", "NBTWriter",
    "setMinecraftDir", "getMinecraftPath",
    "DIM_NETHER", "DIM_OVERWORLD", "DIM_END", "getWorld", "iterWorlds", "World", "Dimension", "Region"
]
