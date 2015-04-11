# Copyright AllSeen Alliance. All rights reserved.
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

import validate
import common

class MemberDef:
    """Common base class for field and argument definitions."""

    def __init__(self, name = None, arg_type = None):
        """Initialize an instance of the MemberDef class."""
        self.name = name
        self.arg_type = arg_type
        # This is initialized in Interface.parse()
        self.interface = None

        return

    def get_flattened_signature(self):
        """Flatten the signature by replacing all [NamedTypes] with their expanded signature."""
        basesig = self.get_base_signature()
        if basesig[0] != '[':
            return self.arg_type
        prefix = 'a'*(len(self.arg_type)-len(basesig))
        basetype = self.get_named_type().get_flattened_signature()
        return prefix+basetype

    def get_flattened_base_signature(self):
        """Return the flattened base signature."""
        return get_base_signature(self.get_flattened_signature())

    def get_base_signature(self):
        """Return the base signature i.e. 'i', 'ai', and 'aai' all return 'i'."""
        return get_base_signature(self.arg_type)

    def get_named_type(self):
        """Returns the named type definition this argument refers to, or None."""
        if self.interface is None:
            return None
        basesig = self.get_base_signature()
        if basesig[0] == '[':
            return self.interface.get_named_type(basesig[1:-1])
        return None

    def references_named_type(self):
        """Returns true if arg_type contains a [NamedType] reference."""
        basesig = self.get_base_signature()
        return basesig[0] == '['

    def is_basic_type(self):
        """Return True if this argument is a basic type."""
        return (not self.references_named_type()) and is_basic_type(self.arg_type)

    def is_array(self):
        """Return True if this argument is an array. A dictionary is considered an array."""
        return is_array(self.get_flattened_signature())

    def is_structure(self):
        """Return True if the base argument type is a structure."""
        return is_structure(self.get_flattened_signature())

    def is_dictionary(self):
        """Return True if the base argument type is a dictionary."""
        return is_dictionary(self.get_flattened_signature())

    def is_dictionary_array(self):
        """Return True if the base argument type is an array of dictionaries."""
        return is_dictionary_array(self.get_flattened_signature())

    def get_indirection_level(self):
        """Get the number of dimensions in the array or 0 if not an array."""
        return get_indirection_level(self.get_flattened_signature())

    def get_max_array_dimension(self):
        """Gets the number of array dimensions in this signature."""
        return get_max_array_dimension(self.get_flattened_signature())

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
        return get_max_structure_depth(self.get_flattened_signature())

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
        return get_max_dictionary_depth(self.get_flattened_signature())

    def __str__(self):
        return "{0} : {1}".format(self.name, self.arg_type)

    def __eq__(self, other):
        """Compares this member definition to another and returns true if equal."""
        return self.name == other.name and self.arg_type == other.arg_type

    def __ne__(self, other):
        """Implements the '!=' operator."""
        if self == other:
            return False
        return True

def get_indirection_level(signature):
    """Get the number of dimensions in the array or 0 if not an array."""
    return len(signature) - len(signature.lstrip('a'))

def get_base_signature(signature, index = 0):
    """Return the base signature i.e. 'i', 'ai', and 'aai' all return 'i'."""
    return signature[index:len(signature)].lstrip('a')

def is_array(signature):
    """Return True if this argument is an array. A dictionary is considered an array."""
    return signature[0] == "a"

def is_structure(signature):
    """Return True if the base argument type is a structure."""
    sig = get_base_signature(signature)
    return sig[0] == '('

def is_dictionary(signature):
    """Return True if the base argument type is a dictionary."""
    sig = get_base_signature(signature)
    return signature[0] == 'a' and sig[0] == '{'

def is_dictionary_array(signature):
    """Return True if the base argument type is an array of dictionaries."""
    return is_dictionary(signature) and get_indirection_level(signature) > 1

def __find_end_of_type(signature, index = 0):
    """Returns the index of the start of the next type starting at 'index'.

If there are no more types then return the end of the type signature.

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
    assert(index < len(signature))
    c = signature[index]

    if c == '(':
        end_index = __find_container_end(signature, index, ')')
    elif c == '{':
        end_index = __find_container_end(signature, index, '}')
    elif c == 'a':
        base = get_base_signature(signature, index)
        end_index = __find_end_of_type(base)
        end_index += index + get_indirection_level(signature, index)
    else:
        end_index = index + 1

    return end_index

def is_basic_type(signature):
    """Returns True if the signature is a basic type

'a', '(', '{', and 'v' are not considered basic types because they usually
cannot be handled the same as other types."""

    basic_types = ('b','d', 'g', 'i','n','o','q','s','t','u','x','y')
    return signature in basic_types

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

def split_signature(sig):
    """splits a container signature into individual fields."""
    components = []
    index = 1
    while index < len(sig)-1:
        part = sig[index:]

        startindex = get_indirection_level(part)
        endindex = __find_end_of_type(part, startindex)

        components.append(part[:endindex])
        index = index + endindex
    return components

def make_clean_name(signature):
    clean_name = signature.replace("(", "_")
    clean_name = clean_name.replace(")", "")
    clean_name = clean_name.replace("{", "_")
    clean_name = clean_name.replace("}", "")
    clean_name = clean_name.replace("[", "_")
    clean_name = clean_name.replace("]", "")

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
