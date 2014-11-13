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
import argdef
import memberdef
import propertydef
import structdef
import fielddef
import dictdef
import common
import validate
import container

return_suffix = "_return_value"

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
        self.declared_names = []
        self.declared_structs = {}
        self.declared_dicts = {}

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
            elif o.tag == "struct":
                # Don't count this as a valid child.
                new_struct = structdef.StructDef()
                new_struct.parse(o, lax_naming)
                self.add_declared_struct(o, new_struct)
            elif o.tag == "dict":
                # Don't count this as a valid child.
                new_dict = dictdef.DictDef()
                new_dict.parse(o, lax_naming)
                self.add_declared_dict(o, new_dict)
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
        self.__declare_undeclared_types()
        self.__add_interface_to_all_members()

        validate.interface_completeness(self)

        return

    def set_name(self, name, xml = None):
        """Set the name of the interface.

        This is a bit more than a simple string assignment. interface_full_name
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

    def get_path(self, separator = "."):
        """Return portion of the interface full name prior to the interface_name.

        Example: "com.example.Demo" is returned as "com.example". """

        return separator.join(self.get_name_components()[0:-1])

    def get_full_coded_path(self):
        """Return portion of the interface full name prior to the interface_name for use as an identifier in c/c++ code.

        Example: "com.example.Demo" is returned as "com_example". """
        return self.get_path("_")

    def add_parent(self, aj_parent):
        """Add a new parent to this interface.

        An interface can have many instances. The name of each instance
        is derived from the parent AllJoynObject."""
        self.parents.append(aj_parent)
        return

    def has_read_properties(self):
        """Return True if there is at least one property with read access."""
        return_value = False

        for p in self.properties:
            if p.is_readable():
                return_value = True
                break

        return return_value

    def has_write_properties(self):
        """Return True if there is at least one property with write access."""
        return_value = False

        for p in self.properties:
            if p.is_writeable():
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

    def add_declared_struct(self, xml, struct):
        """Add a new declared struct to this interface."""
        if struct.name in self.declared_names:
            validate.raise_exception(xml, "Duplicate struct name '{0}' not allowed.".format(struct.name))
        self.declared_structs[struct.name] = struct
        self.declared_names.append(struct.name)
        return

    def add_declared_dict(self, xml, dict):
        """Add a new declared dict to this interface."""
        if dict.name in self.declared_names:
            validate.raise_exception(xml, "Duplicate dict name '{0}' not allowed.".format(dict.name))
        self.declared_dicts[dict.name] = dict
        self.declared_names.append(dict.name)
        return

    def get_named_type(self, typename):
        """Retrieve a named type (struct or dict)."""
        if typename in self.declared_structs:
            return self.declared_structs[typename]
        if typename in self.declared_dicts:
            return self.declared_dicts[typename]
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

    def __name_unnamed_containers(self):
        unnamed = 0

        for k in sorted(self.structures):
            s = self.structures[k]
            if s.name is None:
                n = "{0}Unnamed{1}".format(self.interface_name, unnamed)
                s.set_name(n)
                unnamed += 1

        for k in sorted(self.dictionaries):
            d = self.dictionaries[k]
            if d.name is None:
                n = "{0}UnnamedDict{1}".format(self.interface_name, unnamed)
                d.set_name(n)
                unnamed += 1

        return

    def get_containers_in_declaration_order(self):
        """Returns the declared containers in definition order for a header file"""
        return_value = []
        return_value += self.declared_structs.values()
        return_value += self.declared_dicts.values()
        return_value.sort(key = lambda x: x.get_order())
        return return_value

    def __add_structs_dictionaries_arrays(self):
        for m in self.methods:
            self.__find_add_structs_dictionaries_arrays(m.args, m.name)

        for s in self.signals:
            self.__find_add_structs_dictionaries_arrays(s.args, None)

        for p in self.properties:
            if p.is_readable:
                self.__find_add_structs_dictionaries_arrays(p.args, p.name)
            else:
                self.__find_add_structs_dictionaries_arrays(p.args, None)

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

    def __find_add_structs_dictionaries_arrays(self, args, multiple_return_name):
        """This is called for each method, signal, and property. With Android as
        the target readable properties and methods that have multiple return values
        a structure must be created that contains all of the return values. Hence
        if multiple_return_name is not None and the target is Android then find
        such arguments and if necessary create the structure and add it to the
        list of structures with that name."""

        out_args = []

        target_is_android = common.target_language == "android"

        if args is not None:
            for a in args:
                a.interface = self
                if a.references_named_type():
                    continue
                if a.is_structure():
                    self.__name_and_extract_struct(a)
                elif a.is_dictionary():
                    self.__name_and_extract_dictionary(a)

                if target_is_android and multiple_return_name and a.direction == "out":
                    out_args.append(a)

        if len(out_args) > 1:
            signature = "("

            for a in out_args:
                signature += a.arg_type

            signature += ")"

            return_structure_name = multiple_return_name + return_suffix
            c = container.Container(signature, return_structure_name)
            self.structures[return_structure_name] = c

        return

    def __resolve_contained_containers(self, fieldsig):
        baseidx = memberdef.get_indirection_level(fieldsig)
        basesig = memberdef.get_base_signature(fieldsig)
        if basesig[0] == '(':
            basesig = '[{0}]'.format(self.structures[basesig].name)
        elif basesig[0] == '{':
            basesig = '[{0}]'.format(self.dictionaries[basesig].name)
            baseidx = baseidx - 1 #the last 'a' is part of the dictionary definition
        return fieldsig[:baseidx] + basesig

    def __declare_undeclared_types(self):
        self.__name_unnamed_containers()

        for d in self.dictionaries.values():
            dict = dictdef.DictDef()
            dict.name = d.name
            fields = memberdef.split_signature(d.signature)
            dict.set_key_signature(self.__resolve_contained_containers(fields[0]))
            dict.set_value_signature(self.__resolve_contained_containers(fields[1]))
            self.add_declared_dict(None, dict)

        for s in self.structures.values():
            struct = structdef.StructDef()
            struct.name = s.name
            fields = memberdef.split_signature(s.signature)
            for index in range(len(fields)):
                structfield = fielddef.FieldDef("member{0}".format(index), \
                                                self.__resolve_contained_containers(fields[index]))
                struct.add_field(None, structfield)
            self.add_declared_struct(None, struct)

        # resolve unnamed types in the property/method/signal arguments as well
        for m in self.methods:
            if m.args is None: continue
            for arg in m.args:
                arg.arg_type = self.__resolve_contained_containers(arg.arg_type)

        for m in self.signals:
            if m.args is None: continue
            for arg in m.args:
                arg.arg_type = self.__resolve_contained_containers(arg.arg_type)

        for m in self.properties:
            if m.args is None: continue
            for arg in m.args:
                arg.arg_type = self.__resolve_contained_containers(arg.arg_type)

        return

    def __add_interface_to_all_members(self):
        for m in self.methods:
            if m.args is None: continue
            for arg in m.args:
                arg.interface = self
        for m in self.signals:
            if m.args is None: continue
            for arg in m.args:
                arg.interface = self
        for m in self.properties:
            if m.args is None: continue
            for arg in m.args:
                arg.interface = self

        for s in self.declared_structs.values():
            for f in s.fields:
                f.interface = self
        for d in self.declared_dicts.values():
            d.key.interface = self
            d.value.interface = self


    def __eq__(self, other):
        """Compares this interface to another and returns true if equal.

        This comparision includes the names, methods, signals, properties
        and declared types but not the parents."""

        if (self is None and other is not None or
           self is not None and other is None or
           self.interface_full_name != other.interface_full_name):
            return False

        if (len(self.properties) != len(other.properties) or
           len(self.signals) != len(other.signals) or
           len(self.methods) != len(other.methods) or
           len(self.declared_structs) != len(other.declared_structs) or
           len(self.declared_dicts) != len(other.declared_dicts)):
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

        for ds in self.declared_structs.values():
            ds_other = other.get_named_type(ds.name)
            if ds_other is None or ds_other != ds:
                return False

        for dd in self.declared_dicts.values():
            dd_other = other.get_named_type(dd.name)
            if dd_other is None or dd_other != dd:
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

