# Copyright (c) 2013-2014 AllSeen Alliance. All rights reserved.
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
import memberdef

class ArgDef(memberdef.MemberDef):
    """Contains the description of a argument."""
    def __init__(self, xml = None, name = None, arg_type = None,
                 direction = None, variant_type = None):
        """Initialize an instance of the ArgDef class."""
        memberdef.MemberDef.__init__(self, name, arg_type)
        self.direction = direction
        self.variant_type = variant_type

        if xml is not None and (
                name is not None or arg_type is not None or direction is not None):
            self.__validate(xml)

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
            name_type = memberdef.make_clean_name(self.arg_type)
            self.name = "{0}{1}Arg{2}_{3}".format(parent.name,
                                                  parent_type,
                                                  arg_num,
                                                  name_type)
        self.__validate(xml)

        return


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
