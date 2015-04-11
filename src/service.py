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

import ajobject
import validate

class Service:
    """Contains the description of a complete AllJoyn service.

    An AllJoyn service is composed of one AllJoynObjects and one or more
    Interfaces. There can be many instances of a single Interface if they are
    each contained within a different AllJoynObject. This gives each of them
    a different name and creates a different instance. The instance name is
    derived from the AllJoynObject parent and the specific Interface name."""

    def __init__(self, service_name):
        """Initializes an instance of the Service class."""

        # There is a single collection of interfaces which are shared with all
        # AllJoyObjects.
        self.interfaces = {}

        # There is a single AllJoynObject at the root level. It may contain
        # other AllJoynObjects and/or reference one of the Interfaces.
        self.alljoyn_object = ajobject.AllJoynObject(service_name)
        self.delete_object_cache()
        self.__has_read_properties = None
        self.__has_write_properties = None
        self.__number_of_signals = None
        self.__has_dictionaries = None
        return

    def parse(self, xml, lax_naming):
        """Parse the input xml into a better representation of the service."""
        self.alljoyn_object.parse(xml, self, lax_naming)
        return

    def add_interface(self, interface, xml):
        """Add this interface to the list of interfaces. Returns the interface.

        If the interface already exists then the existing interface is returned
        and the new interface is not added. If an interface with the same name
        but different signature exist then an exception is raised."""

        # First check to see if the interface already exists.
        i = self.get_interface(interface.interface_full_name)

        if i is None:
            self.interfaces[interface.interface_full_name] = interface
            i = interface

            # Because one or more of the following properties may have been set
            # to False and the addition of this interface may change that we now
            # set them to None so the previously cached value can be reevaluated
            # as needed in has_read_properties(), etc.
            self.__has_read_properties = None
            self.__has_write_properties = None
            self.__number_of_signals = None
            self.__has_dictionaries = None
        elif i != interface:
            error1_format = "Interface '{0}' has multiple definitions"
            error1 = error1_format.format(interface.interface_full_name)
            error2 = "with different signatures."
            error = " ".join([error1, error2])
            error = validate.get_xml_error(xml, error)
            raise validate.ValidateException(error)

        return i

    def get_interface(self, name):
        """Get the interface with this name (use full interface name)."""
        if name in self.interfaces:
            return self.interfaces[name]

        return None

    def get_objects(self):
        """Return a complete list of all objects."""

        if not self.objects and self.alljoyn_object is not None:
            self.alljoyn_object.append_objects(self.objects)
            index = 0
            for o in self.objects:
                # Only give index numbers to objects that have interfaces.
                if o.interfaces:
                    o.index = index
                    index += 1

        return self.objects

    def delete_object_cache(self):
        """Delete the cache of the objects but not the object themselves."""
        self.objects = []
        return

    def has_read_properties(self):
        """Return true if any of the interfaces contain a readable property."""
        return_value = False

        if self.__has_read_properties is None:
            for key in sorted(self.interfaces):
                i = self.interfaces[key]
                if i.has_read_properties():
                    return_value = True
                    break

            self.__has_read_properties = return_value
        else:
            return_value = self.__has_read_properties

        return return_value

    def has_write_properties(self):
        """Return true if any of the interfaces contain a writeable property."""
        return_value = False

        if self.__has_write_properties is None:
            for key in sorted(self.interfaces):
                i = self.interfaces[key]
                if i.has_write_properties():
                    return_value = True
                    break

            self.__has_write_properties = return_value
        else:
            return_value = self.__has_write_properties

        return return_value

    def has_properties(self):
        """Return true if any of the interfaces contain a property."""
        return self.has_read_properties() or self.has_write_properties()

    def has_signals(self):
        """Return true if any of the interfaces contain a signal."""
        return self.number_of_signals() > 0

    def number_of_signals(self):
        """Returns the number of signals in all instances of all interfaces."""
        return_value = 0

        if self.__number_of_signals is None:
            objects = self.get_objects()

            for o in objects:
                for i in o.interfaces:
                    return_value += len(i.signals)

            self.__number_of_signals = return_value
        else:
            return_value = self.__number_of_signals

        return return_value

    def has_dictionaries(self):
        """Return true if any of the interfaces contains a dictionary."""
        return_value = False

        if self.__has_dictionaries is None:
            for key in sorted(self.interfaces):
                i = self.interfaces[key]
                if i.dictionaries:
                    return_value = True
                    break

            self.__has_dictionaries = return_value
        else:
            return_value = self.__has_dictionaries

        return return_value

    def __str__(self):
        """Create and return a string representation of this object."""
        index = 0
        return_value = ""
        i_format = "{0}\n##### Interface[{1}] #####\n{2}"

        for key in sorted(self.interfaces):
            i = self.interfaces[key]
            return_value = i_format.format(return_value, index, i)
            index += 1

        if self.alljoyn_object is not None:
            self.alljoyn_object.indent = 0
            o_format = "{0}\n##### Objects #####\n{1}"
            return_value = o_format.format(return_value, self.alljoyn_object)

        return return_value
