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

import signaldef
import methoddef
import propertydef
import common
import validate
import container

class Interface:
    """Contains the description of a complete AllJoyn interface."""

    def __init__(self):
        """Initialize an instance of the Interface class."""
        self.interface_name = ""
        self.interface_full_name = ""
        self.is_secure = False
        self.is_derived = False
        self.methods = []
        self.signals = []
        self.properties = []
        self.parents = []
        self.structures = {}
        self.dictionaries = {}
        self.has_arrays = False
        self.has_arg_info = False

        return

    def parse(self, xml, lax_naming):
        """Parse the given interface xml element."""
        #print("Parsing Interface '{0}'".format(xml.get('name')))
        name = xml.get("name")
        self.set_name(name, xml)

        # Make a list of all the objects at this level.
        xml_root_objects = list(xml)

        child_count = 0

        for o in xml_root_objects:
            if o.tag == "signal":
                child_count += 1

                s = signaldef.SignalDef()
                s.parse(o, lax_naming)
                self.add_signal(o, s)
            elif o.tag == "method":
                child_count += 1

                new_method = methoddef.MethodDef()
                new_method.parse(o, lax_naming)
                self.add_method(o, new_method)
            elif o.tag == "property":
                child_count += 1

                new_property = propertydef.PropertyDef()
                new_property.parse(o)
                self.add_property(o, new_property)
            elif o.tag == "annotation":
                # Don't count this as a child for purposes of defining the
                # interface.
                common.get_annotations(xml, self)
            else:
                # Don't count this as a valid child.
                warn_format = "\nWarning! Ignoring interface xml object '{0}'."
                mess = warn_format.format(o.tag)
                mess = validate.get_xml_error(xml, mess)
                print(mess)

        if child_count <= 0:
            mess = "Incompletely specified interface '{0}'.".format(name)
            mess = validate.get_xml_error(xml, mess)
            raise validate.ValidateException(mess)

        self.__add_structs_dictionaries_arrays()

        return

    def set_name(self, name, xml = None):
        """Set the name of the interface.

        This is a bit more that a simple string assignment. interface_full_name
        is the full D-Bus interfacename with at least two elements (such as
        org.alljoyn, one.two, or test.foo). interfaceName is the last element
        of fullInterface name. In the examples above they would be "alljoyn",
        "two", or "foo".

        name: The full name of the interface the interfaceName is derived from
        this."""
        validate.interface_name(name, xml)
        self.interface_full_name = name
        s = name.split(".")
        self.interface_name = s[-1]
        return

    def get_full_coded_name(self, make_camel_cased = False):
        """Return the full interface name for use as an indentifier in c/c++ code.

Example: "/com/example/Demo" is returned as "_com_example_Demo" if make_camel_cased is False.
Example: "/com/example/Demo" is returned as "comExampleDemo" if make_camel_cased is True."""

        if make_camel_cased:
            return common.make_camel_case(self.interface_full_name, '.')

        return str.replace(self.interface_full_name, ".", "_")

    def get_name_components(self):
        """Return the interface full name as a list of components.

        Example: "com.example.Demo" is returned as ["com", "example", "Demo"]."""

        s = self.interface_full_name.split(".")
        return s

    def get_path(self):
        """Return portion of the interface full name prior to the interface_name.

        Example: "com.example.Demo" is returned as "com.example". """

        return ".".join(self.get_name_components()[0:-1])

    def add_parent(self, aj_parent):
        """Add a new parent to this interface.

        An interface can have many instances. The name of each instance
        is derived from the parent AllJoynObject."""
        self.parents.append(aj_parent)
        return

    def get_has_get_properties(self):
        """Return True if there is at least one property with read access."""
        return_value = False

        for p in self.properties:
            if p.no_reply:
                continue
            return_value = True
            break

        return return_value

    def add_method(self, xml, method):
        """Add a new method to this interface."""
        for m in self.methods:
            if m.name == method.name:
                mess = "Duplicate method name '{0}' not allowed.".format(m.name)
                mess = validate.get_xml_error(xml, mess)
                raise validate.ValidateException(mess)

        self.methods.append(method)
        return

    def get_method(self, name):
        """Get the existing method with this name."""
        for m in self.methods:
            if m.name == name:
                return m

        return None

    def add_signal(self, xml, signal):
        """Add a new signal to this interface."""
        for s in self.signals:
            if s.name == signal.name:
                mess = "Duplicate signal name '{0}' not allowed.".format(s.name)
                mess = validate.get_xml_error(xml, mess)
                raise validate.ValidateException(mess)

        self.signals.append(signal)
        return

    def get_signal(self, name):
        """Get the existing signal with this name."""
        for s in self.signals:
            if s.name == name:
                return s

        return None

    def add_property(self, xml, prop):
        """Add a new property to this interface."""
        for p in self.properties:
            if p.name == prop.name:
                mess = "Duplicate property name '{0}' not allowed.".format(p.name)
                mess = validate.get_xml_error(xml, mess)
                raise validate.ValidateException(mess)

        self.properties.append(prop)
        return

    def get_property(self, name):
        """Get the existing property with this name."""
        for p in self.properties:
            if p.name == name:
                return p

        return None

    def get_structs_in_struct_order(self):
        """Returns the structures in definition order for a header file.

This includes the dictionaries which are just a special case of a structure."""
        return_value = []

        unnamed = 0

        for k in sorted(self.structures):
            s = self.structures[k]
            if s.name is None:
                n = "{0}Unnamed{1}".format(self.interface_name, unnamed)
                s.set_name(n)
                unnamed += 1
            return_value.append(s)

        for k in sorted(self.dictionaries):
            d = self.dictionaries[k]
            if d.name is None:
                n = "{0}UnnamedDict{1}".format(self.interface_name, unnamed)
                d.set_name(n)
                unnamed += 1
            return_value.append(d)

        return_value.sort(key=container.Container.get_order)

        return return_value

    def __add_structs_dictionaries_arrays(self):
        for m in self.methods:
            self.__find_add_structs_dictionaries_arrays(m.args)

        for m in self.signals:
            self.__find_add_structs_dictionaries_arrays(m.args)

        for m in self.properties:
            self.__find_add_structs_dictionaries_arrays(m.args)

        return

    def __name_and_extract_to_list(self, arg, list):
        basesig = arg.get_base_signature()

        if basesig in list:
            # Already in the container list?
            # If so then check for a name, name it if needed, and we're done.
            c = list[basesig]
            if c.name is None:
                c.set_name(arg.name)
        else:
            # Add this container and extract all the subcontainers.
            c = container.Container(basesig, arg.name)
            list[basesig] = c
            c.extract_structures(self.structures)
            c.extract_dictionaries(self.dictionaries)

        return

    def __name_and_extract_struct(self, arg):
        self.__name_and_extract_to_list(arg, self.structures)
        return

    def __name_and_extract_dictionary(self, arg):
        self.__name_and_extract_to_list(arg, self.dictionaries)
        return

    def __find_add_structs_dictionaries_arrays(self, args):
        if args is not None:
            for a in args:
                a.interface = self
                if not self.has_arrays and str.find(a.arg_type, 'a'):
                    self.has_arrays = True

                if a.is_structure():
                    self.__name_and_extract_struct(a)
                elif a.is_dictionary():
                    self.__name_and_extract_dictionary(a)

        return

    def __add_container_type(self, container_list, arg):
        if arg.arg_type not in container_list:
            container_list[arg.arg_type] = arg.name

        return

    def __eq__(self, other):
        """Compares this interface to another and returns true if equal.

        This comparision includes the names, methods, signals, and properties
        but not the parents."""

        if (self is None and other is not None or
           self is not None and other is None or
           self.interface_full_name != other.interface_full_name):
            return False

        if (len(self.properties) != len(other.properties) or
           len(self.signals) != len(other.signals) or
           len(self.methods) != len(other.methods)):
            return False

        for m in self.methods:
            m_other = other.get_method(m.name)
            if m_other is None or m_other != m:
                return False

        for s in self.signals:
            s_other = other.get_signal(s.name)
            if s_other is None or s_other != s:
                return False

        for p in self.properties:
            p_other = other.get_property(p.name)
            if p_other is None or p_other != p:
                return False

        return True

    def __ne__(self, other):
        """Implements the '!=' operator."""
        if self == other:
            return False
        return True

    def __str__(self):
        """Create and return a string representation of this object."""
        f = "Name: {0}\nFull: {1}"
        return_value = f.format(self.interface_name, self.interface_full_name)

        if self.properties:
            return_value = "{0}\nProperties:".format(return_value)
            for p in self.properties :
                return_value = "{0}\n{1}".format(return_value, p)

        if self.methods:
            return_value = "{0}\nMethods:".format(return_value)
            for m in self.methods :
                return_value = "{0}\n{1}".format(return_value, m)

        if self.signals:
            return_value = "{0}\nSignals:".format(return_value)
            for s in self.signals :
                return_value = "{0}\n{1}".format(return_value, s)

        return return_value

