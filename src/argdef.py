# Copyright (c) 2013, 2014 AllSeen Alliance. All rights reserved.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from xml.etree import ElementTree
import validate
import common

class ArgDef:
    """Contains the description of a argument."""
    def __init__(self, xml = None, name = None, arg_type = None,
                 direction = None, variant_type = None):
        """Initialize an instance of the ArgDef class."""
        self.name = name
        self.arg_type = arg_type
        self.direction = direction
        self.variant_type = variant_type

        if xml is not None and (
                name is not None or arg_type is not None or direction is not None):
            self.__validate(xml)

        # This is initialized in Interface.parse().
        self.interface = None
        return

    def parse(self, xml, lax_naming, parent_type, parent, arg_num):
        """Parse the given argument xml element."""
        assert(xml is not None)
        assert(xml.tag == "arg")

        self.arg_type = xml.get("type")
        common.get_annotations(xml, self)

        self.direction = xml.get("direction")
        self.name = xml.get("name")

        if (self.name is None or len(self.name) == 0) and lax_naming:
            name_type = make_clean_name(self.arg_type)
            self.name = "{0}{1}Arg{2}_{3}".format(parent.name,
                                                  parent_type,
                                                  arg_num,
                                                  name_type)
        self.__validate(xml)

        return

    def get_base_signature(self):
        """Return the base signature i.e. 'i', 'ai', and 'aai' all return 'i'."""
        return get_base_signature(self.arg_type)

    def is_array(self):
        """Return True if this argument is an array."""
        return is_array(self.arg_type)

    def is_structure(self):
        """Return True if the base argument type is a structure."""
        return is_structure(self.arg_type)

    def is_dictionary(self):
        """Return True if the base argument type is a dictionary."""
        return is_dictionary(self.arg_type)

    def get_container(self, index = 0):
        """Get container at this index or none if type is not a container."""
        return get_container(self.arg_type, index)

    def get_indirection_level(self):
        """Get the number of dimensions in the array or 0 if not an array."""
        return get_indirection_level(self.arg_type)

    def find_end_of_type(self, index = 0):
        """Returns the index of the start of the next type starting at 'index'.

If there are no more types then return of the type signature.

For example:
    ("ab", 0)  returns 1
    ("ab", 1)  returns 2
    ("aab", 0)  returns 1
    ("aab", 1)  returns 1
    ("aab", 2)  returns 3
    ("abb", 1)  returns 2
    ("abb", 2)  returns 3
    ("bqd", 0)  returns 1
    ("bqd", 1)  returns 2
    ("bqd", 2)  returns 3
    ("(bqd)", 0) returns 4
    ("(bqd)", 1) returns 2
    ("(bqd)", 2) returns 3
    ("(bqd)", 3) returns 4
    ("(bqd)", 4) returns 5
    ("(bqd(bad))", 0) returns 9
    ("(bqd(bad))", 1) returns 2
    ("(bqd(bad))", 2) returns 3
    ("(bqd(bad))", 3) returns 4
    ("(bqd(bad))", 4) returns 8
    ("(bqd(bad))", 5) returns 6"""
        return find_end_of_type(self.arg_type, index)

    def get_next_marshal_args_signature(self, index = 0):
        return get_next_marshal_args_signature(self.arg_type, index)

    def find_end_of_basic_types(self, index = 0):
        """Returns the index of the next non-basic type starting at 'index'.

'a', '(', '{', and 'v' are not considered basic types because they usually
cannot be handled the same as other types."""
        return find_end_of_basic_types(self.arg_type, index)

    def get_max_array_dimension(self):
        """Gets the number of array dimensions in this signature."""
        return get_max_array_dimension(self.arg_type)

    def __validate(self, xml):
        validate.arg_name(self.name, xml)
        validate.data_signature(self.arg_type, xml)

        if self.direction is not None:
            validate.arg_direction(self.direction, xml)

        return

    def __str__(self):
        """Create and return a string representation of this object."""
        f = "      Name: {0}\n        Type: '{1}'\n        Direction: '{2}'\n"
        return_value = f.format(self.name, self.arg_type, self.direction)

        return return_value

    def __eq__(self, other):
        """Compares this method to another and returns true if equal."""
        if (self is None and other is not None or
           self is not None and other is None or
           self.name != other.name or
           self.arg_type != other.arg_type or
           self.direction != other.direction):
            return False

        return True

    def __ne__(self, other):
        """Implements the '!=' operator."""
        if self == other:
            return False
        return True

    def get_max_structure_depth(self):
        """Return the maximum depth of structures in this type.
Examples:
    "bud" returns 0
    "(bud)" returns 1
    "(bud)(did)" returns 1
    "(bud(did))" returns 2
    "(q(bud)(did))" returns 2
    "(i((bud(did))i))" returns 4
"""
        return get_max_structure_depth(self.arg_type)

    def get_max_dictionary_depth(self):
        """Return the maximum depth of dictionaries in this type.
Examples:
    "bud" returns 0
    "a{bud}" returns 1
    "a{bud}a{did}" returns 1
    "a{buda{did}}" returns 2
    "a{qa{bud}a{did})" returns 2
    "a{ia{a{buda{did}}i}}" returns 4
"""
        return get_max_dictionary_depth(self.arg_type)

def get_indirection_level(signature, index = 0):
    """Get the number of dimensions in the array or 0 if not an array."""
    sig = signature[index:len(signature)]
    return len(sig) - len(sig.lstrip('a'))

def get_base_signature(signature, index = 0):
    """Return the base signature i.e. 'i', 'ai', and 'aai' all return 'i'."""
    return signature[index:len(signature)].lstrip('a')

def is_array(signature):
    """Return True if this argument is an array."""
    return signature[0] == "a"

def is_structure(signature):
    """Return True if the base argument type is a structure."""
    sig = get_base_signature(signature)
    return sig[0] == '('

def is_dictionary(signature):
    """Return True if the base argument type is a dictionary."""
    sig = get_base_signature(signature)
    return signature[0] == 'a' and sig[0] == '{'

def get_container(signature, index = 0):
    """Get container at this index or none if type is not a container."""
    return_value = None

    if signature[index] == '{' or signature[index] == '(':
        sig = signature[index:len(signature)]
        end_index = find_end_of_type(sig)
        return_value = sig[0:end_index]

    return return_value

def find_end_of_type(signature, index = 0):
    """Returns the index of the start of the next type starting at 'index'."""
    assert(index < len(signature))
    c = signature[index]

    if c == '(':
        end_index = __find_container_end(signature, index, ')')
    elif c == '{':
        end_index = __find_container_end(signature, index, '}')
    elif c == 'a':
        base = get_base_signature(signature, index)
        end_index = find_end_of_type(base)
        end_index += index + get_indirection_level(signature, index)
    else:
        end_index = index + 1

    return end_index

def find_end_of_basic_types(signature, index = 0):
    """Returns the index of the next non-basic type starting at 'index'.

'a', '(', '{', and 'v' are not considered basic types because they usually
cannot be handled the same as other types."""
    basic_types = ('b','d','i','n','o','q','s','t','u','x','y')

    while index < len(signature) and signature[index] in basic_types:
        index += 1

    return index

def get_next_marshal_args_signature(signature, index = 0):
    assert(index < len(signature))
    c = signature[index]

    if c == '(' or c == '{' or c == 'a' or c == 'v':
        end = find_end_of_type(signature, index)
    else:
        end = find_end_of_basic_types(signature, index)

    return signature[index:end]

def get_max_array_dimension(signature):
    """Gets the number of array dimensions in this signature."""
    return_value = 0
    while signature.find((return_value + 1) * 'a') != -1:
        return_value += 1

    return return_value

def get_max_structure_depth(signature):
    return get_max_container_depth(signature, '(', ')')

def get_max_dictionary_depth(signature):
    return get_max_container_depth(signature, '{', '}')

def get_max_container_depth(signature, start, stop):
    return_value = 0
    count = 0

    for c in signature:
        if c == start:
            count += 1
        elif c == stop:
            count -= 1

        if count > return_value:
            return_value += 1

    return return_value


def make_clean_name(signature):
    clean_name = signature.replace("(", "_")
    clean_name = clean_name.replace(")", "")
    clean_name = clean_name.replace("{", "_")
    clean_name = clean_name.replace("}", "")

    return clean_name

def __find_container_end(signature, index, end):
    start = signature[index]
    count = 0

    while index < len(signature):
        c = signature[index]

        if c == start:
            count += 1
        elif c == end:
            count -= 1

            if count == 0:
                index += 1
                break

        index += 1

    return index
