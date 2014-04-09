# Copyright (c) 2013 AllSeen Alliance. All rights reserved.
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

import common
import validate
import memberdef

class DictDef:
    """Contains the description of a declared dictionary"""

    def __init__(self):
        """Initialize an instance of the DictDef class"""
        self.name = ""
        self.key = None
        self.value = None

        return

    def parse(self, xml, lax_naming):
        """Parse the given dict xml element"""
        #print("Parsing Dict '{0}'".format(xml.get('name')))
        self.name = xml.get('name')
        validate.type_name(self.name)
        for keynode in xml.findall('key'):
            if self.key is not None:
                validate.raise_exception(keynode, "Duplicate key definition not allowed.")
            validate.data_signature(keynode.get('type'), keynode)
            self.set_key_signature(keynode.get('type'), keynode)

        for valuenode in xml.findall('value'):
            if self.value is not None:
                validate.raise_exception(valuenode, "Duplicate value definition not allowed.")
            validate.data_signature(valuenode.get('type'), valuenode)
            self.set_value_signature(valuenode.get('type'), valuenode)

        if self.key is None:
            validate.raise_exception(xml,
                    "Dict {0} does not have a key definition.".format(self.name))
        if self.value is None:
            validate.raise_exception(xml,
                    "Dict {0} does not have a value definition.".format(self.name))

        return

    def set_key_signature(self, sig, xml = None):
        if not memberdef.is_basic_type(sig):
            validate.raise_exception(xml,
                "Dict {0} must have a basic type as key, not '{1}'.".format(self.name, sig))
        self.key = memberdef.MemberDef("key", sig)
        return

    def set_value_signature(self, sig, xml = None):
        self.value = memberdef.MemberDef("value", sig)

    def get_flattened_signature(self):
        sig = "a{"
        sig += self.key.get_flattened_signature()
        sig += self.value.get_flattened_signature()
        sig += "}"
        return sig

    def get_order(self):
        return len(self.get_flattened_signature())

    def get_field_list(self):
        return [self.key, self.value]

    def __str__(self):
        f = "      Name: {0}\n        Key: '{1}'\n        Value: '{2}'\n"
        return f.format(self.name, self.key.arg_type, self.value.arg_type)

    def __eq__(self, other):
        """Compares this dictionary definition to another and returns true if equal."""
        if not isinstance(other, DictDef):
            return False
        if other.name != self.name or other.key != self.key or other.value != self.value:
            return False

        return True

    def __ne__(self, other):
        """Implements the '!=' operator."""
        if self == other:
            return False
        return True

