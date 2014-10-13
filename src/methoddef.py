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
import argdef
import common

class MethodDef:
    """Contains the description of a AllJoyn Method."""
    def __init__(self):
        """Initialize an instance of the Interface class."""
        self.name = ""
        self.args = []
        self.no_reply = False
        self.is_secure = False

    def parse(self, xml, lax_naming):
        """Parse the given signal xml element."""
        assert(xml is not None)
        assert(xml.tag == "method")

        #print("Parsing method '{0}'".format(xml.get('name')))
        self.name = xml.get("name")
        validate.member_name(self.name, xml)

        # Make a list of all the objects at this level.
        xml_root_objects = list(xml)

        arg_num = 0

        common.get_annotations(xml, self)

        for o in xml_root_objects:
            if o.tag == "arg":
                a = argdef.ArgDef()

                a.parse(o, lax_naming, "Method", self, arg_num)
                arg_num += 1

                # The default direction is "in".
                if a.direction is None:
                    a.direction = "in"

                self.__add_arg(xml, a)
            elif o.tag != "annotation":
                # Just ignore annotations. We got them earlier.
                warn_format = "\nWarning! Ignoring method xml object '{0}'."
                mess = warn_format.format(o.tag)
                mess = validate.get_xml_error(xml, mess)
                print(mess)

        return

    def get_arg(self, name):
        """Get the argument with the name 'name' or None if not found."""
        return_value = None

        for a in self.args:
            if a.name == name:
                return_value = a
                break

        return return_value

    def __add_arg(self, xml, new_arg):
        for a in self.args:
            if a.name == new_arg.name:
                mess = "Duplicate argument name '{0}'.".format(a.name)
                mess = validate.get_xml_error(xml, mess)
                raise validate.ValidateException(mess)

        self.args.append(new_arg)
        return

    def __eq__(self, other):
        """Compares this method to another and returns true if equal."""
        if (self is None and other is not None or
           self is not None and other is None or
           self.name != other.name or
           len(self.args) != len(other.args) or
           self.no_reply != other.no_reply or
           self.is_secure != other.is_secure):
            return False

        # Compare the args in the same order.
        index = 0
        max_index = len(self.args)
        while index < max_index:
            if self.args[index] != other.args[index]:
                return False
            index += 1

        return True

    def __ne__(self, other):
        """Implements the '!=' operator."""
        if self == other:
            return False
        return True

    def __str__(self):
        """Create and return a string representation of this object."""
        return_value = "  Name: {0}\n".format(self.name)

        if len(self.args) > 0:
            f = "{0}    no_reply: {1}\n"
            return_value = f.format(return_value, self.no_reply)

            f = "{0}    is_secure: {1}\n"
            return_value = f.format(return_value, self.is_secure)

            f = "{0}    Args:\n"
            return_value = f.format(return_value)
            for a in self.args:
                return_value = "{0}{1}".format(return_value, a)

        return return_value

