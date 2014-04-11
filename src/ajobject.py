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
import interface
import common

class AllJoynObject:
    """This class contains the information in a <node ... > found an AllJoyn
    xml file.

    The public members are:

    interfaces = []        # Each <node ...> may have zero or more interfaces.
    alljoyn_objects = {}   # Each node may have zero or more other <node ...>s.
    name = string          # The name of this object as found in the xml.
    parent = AllJoynObject # The parent AllJoynObject (<node ...>) if it exists.
    indent = int           # The indent to use for __str__().
    """

    def __init__(self, object_name, our_parent=None):
        """Initializes an instance of the AllJoynObject class."""
        self.name = object_name
        self.parent = our_parent
        self.interfaces = []      # The interface instances at this node.
        self.alljoyn_objects = {} # The child objects.
        self.indent = 0

        self.__has_properties = None

        # The index in the service collection of objects.
        # This is set to the proper value in service::get_objects()
        self.index = -1
        return

    def parse(self, xml, service, lax_naming):
        """Parses the xml to acquire the interface."""

        # Since we are parsing a new object the service cache is now invalid.
        service.delete_object_cache()

        self.__validate_name(xml)
        # print("Parsing the AllJoynObject '{0}'.".format(self.name))

        # Make a list of all the objects at this level.
        xml_root_objects = list(xml)

        child_count = 0

        for o in xml_root_objects:
            if o.tag == "interface":
                child_count += 1

                i = interface.Interface()
                i.parse(o, lax_naming)

                # Ignore the built in interfaces.
                built_in = {"org.freedesktop.DBus.Peer",
                            "org.freedesktop.DBus.Introspectable",
                            "org.freedesktop.DBus.Properties",
                            "org.freedesktop.DBus.ObjectManager"}

                if i.interface_full_name in built_in:
                    print("Ignoring built in interface '{0}'".format(i.interface_full_name))
                    continue

                # If this is new interface it is added. If it is not a new
                # interface the existing one is returned.
                i = service.add_interface(i, o)
                self.interfaces.append(i)
                i.add_parent(self)
            elif o.tag == "node":
                child_count += 1

                new_node_name = o.get("name")

                if new_node_name in self.alljoyn_objects:
                    error_format = "Duplicate node name '{0}'."
                    error = error_format.format(new_node_name)
                    error = validate.get_xml_error(o, error)
                    raise validate.ValidateException(error)

                new_node = AllJoynObject(new_node_name, self)
                new_node.parse(o, service, lax_naming)
                self.alljoyn_objects[new_node_name] = new_node
            else:
                # Don't count this as a valid child.
                warn_format = "\nWarning! Ignoring xml object '{0}'."
                print(warn_format.format(o.tag))

        if child_count <= 0:
            mess = "Child interfaces and/or nodes expected."
            mess = validate.get_xml_error(xml, mess)
            raise validate.ValidateException(mess)

        return

    def get_full_name(self):
        """Get the full name of this object."""
        full_name = self.name
        p = self.parent

        while p is not None and p.name is not None:
            if ((len(full_name) > 0 and full_name[0] == '/') or
               (len(p.name) == 1 and p.name[0] == '/')):
                full_name = "".join([p.name, full_name])
            else:
                full_name = "/".join([p.name, full_name])
            p = p.parent

        return full_name

    def append_objects(self, object_list):
        """Append self and all child objects to object_list."""
        object_list.append(self)

        for key in sorted(self.alljoyn_objects):
            o = self.alljoyn_objects[key]
            o.append_objects(object_list)

        return

    def get_interface_index(self, interface):
        """Get the index of this interface in this objects collection.

        Returns None if not found."""
        return_value = None
        index = 0

        for i in self.interfaces:
            if i == interface:
                return_value = index
                break
            index += 1

        return return_value

    def has_properties(self):
        """Return true if any of the interfaces contain a property."""
        return_value = False

        if self.__has_properties is None:
            for i in self.interfaces:
                if len(i.properties) > 0:
                    return_value = True
                    break

            self.__has_properties = return_value
        else:
            return_value = self.__has_properties

        return return_value

    def get_full_coded_name(self):
        """Return the full interface name for use as an indentifier in c/c++ code.

        Example: "/com/example/Demo" is returned as "com_example_Demo". """
        return str.replace(self.get_full_name(), "/", "_")

    def __validate_name(self, xml):
        """Check for a valid name and throw an exception if not valid."""

        if self.name is None or len(self.name) <= 0:
            error = "Attribute 'name' required for <node>."
            error = validate.get_xml_error(xml, error)
            raise validate.ValidateException(error)

        # If we have a node with a full path make it has no parent.
        if self.name[0] == '/' and self.parent is not None:
            error = "Nested nodes cannot specify object paths."
            error = validate.get_xml_error(xml, error)
            raise validate.ValidateException(error)

        full_name = self.get_full_name()
        # print("obj:: {0}\nfull: {1}".format(self.name, full_name))
        validate.bus_object_path(full_name, xml)
        return

    def __str__(self):
        """Create and return a string representation of this object."""
        indent_str = " " * self.indent

        f = "{0}Obj name: '{1}'\n{0}Full name: '{2}'\n{0}Interfaces:\n"
        return_value = f.format(indent_str, self.name, self.get_full_name())

        for i in self.interfaces:
            return_value = "{0}{1}  {2}\n".format(return_value,
                                                  indent_str,
                                                  i.interface_full_name)

        if len(self.alljoyn_objects) > 0:
            return_value = "{0}\n{1}Child objects:\n".format(return_value, indent_str)

            for key in sorted(self.alljoyn_objects):
                o = self.alljoyn_objects[key]
                o.indent = self.indent + 2
                return_value = "{0}{1}\n".format(return_value, o)
                o.indent = 0

        return return_value
