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
import fielddef

class StructDef:
    """Contains the description of a declared structure"""

    def __init__(self):
        """Initialize an instance of the StructDef class"""
        self.name = ""
        self.fields = []

        return

    def parse(self, xml, lax_naming):
        """Parse the given struct xml element"""
        #print("Parsing Struct '{0}'".format(xml.get('name')))
        self.name = xml.get('name')
        validate.type_name(self.name)

        for fieldnode in xml.findall('field'):
            f = fielddef.FieldDef()
            f.parse(fieldnode, lax_naming)
            self.add_field(fieldnode, f)

        return

    def add_field(self, xml, field):
        for f in self.fields:
            if f.name == field.name:
                validate.raise_exception(xml,
                        "Duplicate field name '{0}' not allowed.".format(f.name))

        self.fields.append(field)
        return

    def get_flattened_signature(self):
        sig = "("
        for field in self.fields:
            sig += field.get_flattened_signature()
        sig += ")"
        return sig

    def get_order(self):
        return len(self.get_flattened_signature())

    def get_field_list(self):
        return self.fields

    def __str__(self):
        description = "      Name: {0}:\n".format(self.name)
        for field in self.fields:
            description += "        {0}\n".format(str(field))
        return description

    def __eq__(self, other):
        """Compares this struct definition to another and returns true if equal."""
        if not isinstance(other, StructDef):
            return False
        if other.name != self.name or len(other.fields) != len(self.fields):
            return False

        for index in range(len(self.fields)):
            f = self.fields[index]
            other_f = other.fields[index]
            if other_f != f:
                return False

        return True

    def __ne__(self, other):
        """Implements the '!=' operator."""
        if self == other:
            return False
        return True
