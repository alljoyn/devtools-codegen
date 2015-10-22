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

import sys
import os

from .. import CheetahCompileExcept as cce

try:
    from SConstruct import SConstruct
    from CommonClientService import CommonClientService
    from CommonClientService_H import CommonClientService_H

    from ServiceMain import ServiceMain
    from ServiceDoWork import ServiceDoWork
    from Service_H import Service_H
    from ServiceIface import ServiceIface
    from ServiceIface_H import ServiceIface_H

    from ClientMain import ClientMain
    from ClientDoWork import ClientDoWork
    from Client_H import Client_H
    from ClientIface import ClientIface
    from ClientIface_H import ClientIface_H

    from ReadMe import ReadMe
except ImportError:
    # The exception message must be nothing but the file name.
    raise cce.CheetahCompilationException(__file__)

from .. import config
from .. import service
from .. import memberdef
from .. import structdef
from .. import dictdef

AJ_PropertiesIface = "AJ_PropertiesIface"

class Executable:
    """This is a container class for passing build instructions to scons."""

    def __init__(self, name, sources):
        """Initialize an instance of the Executable class.

        'name' is the root name of the target executable.
        'sources' is the list of sources used to build the executable."""

        self.name = name
        self.sources = sources

        return

def hooks():
    """Return the hooks for the AllJoyn Thin Library language binding."""

    hooks = {'validate_cmdline' : __validate_cmdline,
             'generate_code' : __generate_code }
    return hooks

def __validate_cmdline(command_line):
    """Validate the command-line arguments.

    The Well-known name is required.

    Arguments:
    command_line -- the command-line arguments to be validated"""

    if command_line.well_known_name is None:
        raise config.ConfigException("Well-known name is required.")

def __generate_code(command_line, service):
    """Generate the AllJoyn Thin Library code."""

    assert(command_line.target_language == "tl")

    temp = CommonClientService_H()
    make_target_file(temp, "CommonClientService.h", command_line, service)

    temp = CommonClientService()
    source = "CommonClientService.c"
    make_target_file(temp, source, command_line, service)

    client_sources = [source]

    if not command_line.client_only:
        service_sources = [source]

        temp = Service_H()
        source = "Service.h"
        make_target_file(temp, source, command_line, service)

        temp = ServiceMain()
        source = "ServiceMain.c"
        make_target_file(temp, source, command_line, service)
        service_sources.append(source)

        temp = ServiceDoWork()
        source = "ServiceDoWork.c"
        make_target_file(temp, source, command_line, service)
        service_sources.append(source)

    temp = Client_H()
    source = "Client.h"
    make_target_file(temp, source, command_line, service)

    temp = ClientMain()
    source = "ClientMain.c"
    make_target_file(temp, source, command_line, service)
    client_sources.append(source)

    temp = ClientDoWork()
    source = "ClientDoWork.c"
    make_target_file(temp, source, command_line, service)
    client_sources.append(source)

    temp = ReadMe()
    source = "ReadMe.txt"
    make_target_file(temp, source, command_line, service)

    # For each interface generate service and client .c and .h Interface files.
    for key in sorted(service.interfaces):
        i = service.interfaces[key]

        # If client only don't generate the service files.
        if not command_line.client_only:
            temp = ServiceIface_H()
            temp.interface = i
            source = "Service{0}.h".format(i.interface_full_name)
            make_target_file(temp, source, command_line, service)

            temp = ServiceIface()
            temp.interface = i
            source = "Service{0}.c".format(i.interface_full_name)
            make_target_file(temp, source, command_line, service)
            service_sources.append(source)

        temp = ClientIface_H()
        temp.interface = i
        source = "Client{0}.h".format(i.interface_full_name)
        make_target_file(temp, source, command_line, service)

        temp = ClientIface()
        temp.interface = i
        source = "Client{0}.c".format(i.interface_full_name)
        make_target_file(temp, source, command_line, service)
        client_sources.append(source)

    client_exe = Executable("ClientMain", client_sources)
    temp = SConstruct()

    if command_line.client_only:
        temp.executables = [client_exe]
    else:
        service_exe = Executable("ServiceMain", service_sources)
        temp.executables = [service_exe, client_exe]

    make_target_file(temp, "SConstruct", command_line)

    return

def make_target_file(template, filename, command_line, service = None):
    """Make this one file, filename, from the given template."""
    template.command_line = command_line
    template.service = service

    path = command_line.output_path

    out_file = os.path.join(path, filename)

    with open(out_file, 'w') as f:
        f.write("{0}".format(template))

    return

# This is a comment string used at the start of all "runnable" code.
comment_start_runnable ="""\
/* TODO: Start of generated code which should be replaced by user. */"""

# This is a comment string used at the end of all "runnable" code.
comment_end_runnable = """\
/* TODO: End of generated code which should be replaced by user. */"""

# This is a comment string used at the start of places where the user should
# deal with a error condition.
comment_handle_error = "/* TODO: Handle the error condition. */"

# This converts an AllJoyn data type signature into the AllJoyn define of that sig.
arg_define_dictionary = {'a': "AJ_ARG_ARRAY",
                         'b': "AJ_ARG_BOOLEAN",
                         'd': "AJ_ARG_DOUBLE",
                         'g': "AJ_ARG_SIGNATURE",
                         'i': "AJ_ARG_INT32",
                         'n': "AJ_ARG_INT16",
                         'o': "AJ_ARG_OBJ_PATH",
                         'q': "AJ_ARG_UINT16",
                         's': "AJ_ARG_STRING",
                         't': "AJ_ARG_UINT64",
                         'u': "AJ_ARG_UINT32",
                         'v': "AJ_ARG_VARIANT",
                         'x': "AJ_ARG_INT64",
                         'y': "AJ_ARG_BYTE",
                         '(': "AJ_ARG_STRUCT",
                         '{': "AJ_ARG_DICT_ENTRY",
                        }

# This converts an AllJoyn data type into the name of the val in an _AJ_Arg struct.
val_dictionary = {'b': "v_bool",
                  'd': "v_double",
                  'g': "v_signature",
                  'i': "v_int32",
                  'n': "v_int16",
                  'o': "v_objPath",
                  'q': "v_uint16",
                  's': "v_string",
                  't': "v_uint64",
                  'u': "v_uint32",
                  'v': "v_data",
                  'x': "v_int64",
                  'y': "v_byte",
                 }

# This converts an AllJoyn data type into the Thin Library 'C' data type.
type_dictionary = {'a': "AJ_Arg",
                   'b': "uint32_t",
                   'd': "double",
                   'g': "char*",
                   'i': "int32_t",
                   'n': "int16_t",
                   'o': "char*",
                   'q': "uint16_t",
                   's': "char*",
                   't': "uint64_t",
                   'u': "uint32_t",
                   'v': "AJ_Arg",
                   'x': "int64_t",
                   'y': "uint8_t",
                  }

# This converts an AllJoyn data type into the Thin Library 'C' printf data type.
printf_dictionary = {'b': "%d",
                     'd': "%g",
                     'g': "%s",
                     'i': "%d",
                     'n': "%d",
                     'o': "%s",
                     'q': "%u",
                     's': "%s",
                     't': "%llu",
                     'u': "%u",
                     'v': "v",
                     'x': "%lld",
                     'y': "%u",
                    }

class ArgInfo:
    """This is a container class for argument data."""

    def __init__(self, args, direction):
        """Initialize a new instance of an ArgInfo class."""
        self.args = []
        self.signature = ""

        arg_string = self.__get_marshal_args_string(args, direction)
        self.marshal_args_string = arg_string
        self.arg_declaration = self.__get_arg_declarations(args, direction)

        for a in args:
            if a.direction != direction:
                continue

            self.args.append(a)
            self.signature = "".join([self.signature, a.get_flattened_signature()])

        if len(self.args) == 0:
            self.marshal_args_string = None
            self.arg_declaration = None

        return

    def max_number_of_array_dimensions(self):
        """Gets the maximum number of array dimensions in any of the arguments."""
        return_value = 0

        for a in self.args:
            dim = a.get_max_array_dimension()

            if dim > return_value:
                return_value = dim

        return return_value

    def max_number_of_array_indices_needed(self, print_arrays):
        """Gets the maximum number of array indices needed.
        This is in part based on the max number of array dimensions in any of the arguments.
        It is also a function of the type of arrays being marshaled/unmarshalled. Basic
        types such as int, bools, doubles (but not string types) don't need to be
        marshaled/unmarshalled one element at a time. But strings, structures, and
        dictionaries (complex types) do.

        At this time multiple dimensions are not supported. But it is believed that an index
        will be needed for each dimension for everything except the most basic types which
        will need one minus the number of dimensions.

        However, when in runnable mode sometimes an index is needed to traverse through
        an array for display purposes for all data types. So when print_arrays is true
        there are additional considerations.

        The logic table is as follows:

        print_arrays | complex | dimensions | return value
        ----------------------------------------------
           0         0           0           0
           0         1           0           0
           1         0           0           0
           1         1           0           0
           1         0           1           1
           0         0           1           0
           0         0           n         n - 1
           1         0           n         n - 1
           1         1           1           1
           0         1           1           1
           0         1           n           n
           1         1           n           n
        """
        return_value = 0

        for a in self.args:
            dim = a.get_max_array_dimension()

            if dim == 0:
                continue

            base_sig = a.get_base_signature()
            complex_type = base_sig in ('s', 'o', 'g') or a.is_structure() or a.is_dictionary()

            if complex_type:
                if dim > return_value:
                    return_value = dim
                continue

            if (dim - 1) > return_value:
                return_value = dim - 1

            if print_arrays and return_value == 0:
                return_value = 1

        return return_value

    def get_max_structure_depth(self):
        """Gets the maximum structure depth in any of the arguments."""
        return_value = 0

        for a in self.args:
            dim = a.get_max_structure_depth()

            if dim > return_value:
                return_value = dim

        return return_value

    def get_max_dictionary_depth(self):
        """Gets the maximum dictionary depth in any of the arguments."""
        return_value = 0

        for a in self.args:
            dim = a.get_max_dictionary_depth()

            if dim > return_value:
                return_value = dim

        return return_value

    def has_array(self):
        return_value = False

        for a in self.args:
            if a.is_array():
                return_value = True
                break

        return return_value

    def is_basic_types(self):
        return_value = True

        for a in self.args:
            if a.arg_type == 'v' or a.arg_type not in val_dictionary:
                return_value = False
                break

        return return_value

    def __get_marshal_args_string(self, args, direction):
        return_value = None
        is_first = True

        for a in args:
            if a.direction != direction:
                continue

            if is_first:
                is_first = False
                return_value = ""

            return_value = "{0}, {1}".format(return_value, a.name)

        return return_value

    def __get_arg_declarations(self, args, direction):
        """This gets the argument declarations for a given method/signal."""
        return_value = None
        # {0} = previous set of arg declarations.
        # {1} = "const " if array, "" otherwise.
        # {2} = 'C' type.
        # {3} = '*' if array, '' otherwise.
        # {4} = argument name.
        arg_format = "{0}{1}{2}{3} {4}"
        is_first = True

        for a in args:
            if a.direction != direction:
                continue

            if is_first:
                is_first = False
                return_value = ""
            else:
                return_value = "{0}, ".format(return_value)

            ptr = "*" * a.get_indirection_level()
            c_type = get_base_c_type(a)

            if a.is_array():
                const = "const "
            else:
                const = ""

            return_value = arg_format.format(return_value, const,
                                             c_type, ptr, a.name)

            if a.is_array():
                # append element count argument
                return_value = "{0}, int {1}Elements".format(return_value, a.name)

        return return_value

class InterfaceComponent:
    """This is a container class for the interface component names.

    The interface component names are the names of the methods, signals, and
    properties. The comp_type is one of "meth", "sig", or "prop"."""
    def __init__(self, define, switch, name, comp_type, no_reply = False):
        self.define = define
        self.switch = switch
        self.name = name
        assert(comp_type == "meth" or comp_type == "sig" or comp_type == "prop")
        self.comp_type = comp_type
        self.no_reply = no_reply
        self.caller_args = None
        return

    def has_array(self, on_input):
        return_value = False

        args = None

        if on_input and self.input_arg_info is not None:
            args = self.input_arg_info.args
        elif not on_input and self.output_arg_info is not None:
            args = self.output_arg_info.args

        if args is not None:
            for a in args:
                if a.is_array():
                    return_value = True
                    break

        return return_value

    def max_input_output_arrays(self):
        if self.input_arg_info is not None:
            in_arrays = self.input_arg_info.max_number_of_array_dimensions()
        else:
            in_arrays = 0

        if self.output_arg_info is not None:
            out_arrays = self.output_arg_info.max_number_of_array_dimensions()
        else:
            out_arrays = 0

        return max(in_arrays, out_arrays)

# The format string for a name followed by a comma.
name_comma_format = "{0},"

# This is the format for the name of the app #define in the message identifers
# and the message handlers.
app_name_format = "APP_{0:_>2}_{1:_>2}_{2}"

# This is the format for the name of the proxy #define in the message identifers
# and the message handlers.
proxy_name_format = "PROXY_{0:_>2}_{1:_>2}_{2}"

def get_client_property_handlers_table(object_index, aj_object, interface):
    """Get all the client property handler strings for the table of handlers.

    This is a list of strings to be put directly in the ClientMain.c file."""
    return_value = []

    iface_index = aj_object.get_interface_index(interface)

    # The format for a property handler table entry.
    h_format = "0, {0:40} NULL"

    for p in interface.properties:
        if p.no_reply is True:
            continue

        h_name = __get_property_handler_name(object_index, interface, p)
        h = "{0}_GetHandler,".format(h_name)
        entry = h_format.format(h)
        return_value.append(entry)

    return return_value


def get_service_property_handlers_table(object_index, aj_object, interface):
    """Get all the service property handler strings for the table of handlers.

    This is a list of strings to be put directly in the ServiceMain.c file."""
    return_value = []

    iface_index = aj_object.get_interface_index(interface)

    # The format for a property handler table entry.
    h_format = "{0:40} {1} NULL"

    for p in interface.properties:
        name = app_name_format.format(object_index, iface_index, p.name)
        d = name_comma_format.format(name)
        h_name = __get_property_handler_name(object_index, interface, p)
        h = name_comma_format.format(h_name)
        entry = h_format.format(d, h)
        return_value.append(entry)

    return return_value

prop_handler_format = "(void*)PropHandlers{0}"

def get_service_property_get_set_entries(service):
    """Get the property get/set handler table entries for the service side.

    This is a list of strings to be put directly in the ServiceMain.c file."""
    return_value = []

    # The format for a get/set handler table entry.
    h_format = "{0} {1} {2}"

    object_paths = service.get_objects()

    for o in object_paths:
        if o.has_properties():
            iface_index = len(o.interfaces)
            name = app_name_format.format(o.index, iface_index, "AJ_PROP_GET")
            d = name_comma_format.format(name)
            h = name_comma_format.format("PropGetHandler")
            context = prop_handler_format.format(o.get_full_coded_name())
            entry = h_format.format(d, h, context)
            return_value.append(entry)

            name = app_name_format.format(o.index, iface_index, "AJ_PROP_SET")
            d = name_comma_format.format(name)
            h = name_comma_format.format("PropSetHandler")
            context = prop_handler_format.format(o.get_full_coded_name())
            entry = h_format.format(d, h, context)
            return_value.append(entry)

    return return_value

def get_client_property_get_entries(service):
    """Get the property get handler table entries for the client side.

    This is a list of strings to be put directly in the ClientMain.c file."""
    return_value = []

    # The format for a get/set handler table entry.
    h_format = "{0} {1} {2}"

    object_paths = service.get_objects()

    for o in object_paths:
        if o.has_properties():
            iface_index = len(o.interfaces)
            name = proxy_name_format.format(o.index, iface_index, "AJ_PROP_GET")
            d = name_comma_format.format(name)
            h = name_comma_format.format("PropGetHandler")
            context = prop_handler_format.format(o.get_full_coded_name())
            entry = h_format.format(d, h, context)
            return_value.append(entry)

    return return_value

def get_message_handlers_table(service):
    """Get all the message handler strings for the table of handlers.

    This is a list of strings to be put directly in the ServiceMain.c file."""
    return_value = []

    object_paths = service.get_objects()

    for o in object_paths:
        # The format for a message handler table entry.
        h_format = "{0:40} {1}"

        path_index = o.index
        iface_index = 0

        for i in o.interfaces:
            for m in i.methods:
                name = app_name_format.format(path_index, iface_index, m.name)
                d = name_comma_format.format(name)
                h_name = __get_method_handler_name(path_index, i, m)
                entry = h_format.format(d, h_name)
                return_value.append(entry)

            iface_index += 1

    return return_value

def get_interface_components(interface, aj_object, iface_index, client_side):
    return_value = []

    if client_side:
        d_format = proxy_name_format
    else:
        d_format = app_name_format

    path_index = aj_object.index

    r_format = "AJ_REPLY_ID({0})" # Some switch entries are wrapped in AJ_REPLY().
    define = None
    switch = None

    make_defines = path_index is not None and iface_index is not None

    for m in interface.methods:
        if make_defines:
            define = d_format.format(path_index, iface_index, m.name)
            switch = r_format.format(define)

        name = __get_method_handler_name(path_index, interface, m)

        comp = InterfaceComponent(define, switch, name, "meth", m.no_reply)
        comp.method = m
        comp.xml_name = m.name

        comp.input_arg_info = ArgInfo(m.args, "in")
        comp.output_arg_info = ArgInfo(m.args, "out")

        return_value.append(comp)

    for s in interface.signals:
        if make_defines:
            define = d_format.format(path_index, iface_index, s.name)

        name = __get_signal_handler_name(path_index, interface, s)

        # Signal defines are not wrapped in "AJ_REPLY_ID()".
        comp = InterfaceComponent(define, define, name, "sig")
        comp.signal = s
        comp.xml_name = s.name

        comp.input_arg_info = None
        comp.output_arg_info = ArgInfo(s.args, "out")
        return_value.append(comp)

    properties_iface_index = len(aj_object.interfaces)

    for p in interface.properties:
        if make_defines:
            define = d_format.format(path_index, iface_index, p.name)
            switch = r_format.format(define)

        name = __get_property_handler_name(path_index, interface, p)
        comp = InterfaceComponent(define, switch, name, "prop", p.no_reply)
        comp.prop = p
        comp.xml_name = p.name
        comp.prop_get_define = proxy_name_format.format(path_index,
                                                        properties_iface_index,
                                                        "AJ_PROP_GET")
        comp.prop_set_define = proxy_name_format.format(path_index,
                                                        properties_iface_index,
                                                        "AJ_PROP_SET")
        comp.input_arg_info = ArgInfo(p.args, "in")
        comp.output_arg_info = ArgInfo(p.args, "out")

        return_value.append(comp)

    return return_value

def get_message_defines_names(service):
    """Get all the defines and names for the objects, interfaces, methods, etc."""
    return_value = []
    object_paths = service.get_objects()

    for o in object_paths:
        iface_index = 0
        need_prop_define = True

        for i in o.interfaces:
            return_value += __get_client_switch_entries(i, o, iface_index,
                                                        need_prop_define)
            iface_index += 1

            # There must only be one define for each object that has
            # readable properties in one or more of it's interfaces. So don't
            # request property defines if we already have one for this object.
            if i.has_read_properties():
                need_prop_define = False

    return return_value

def get_defines(interface, client_side):
    """Get all the message identifier defines for this interface.

    These are a set of #defines that map indices in tables into an 32-bit int.
    If client_side == True then these are the defines used on the client side
    of things. If False then the service sided.
    These strings include the appropriate comments."""
    return_value = []

    if client_side:
        name_format = proxy_name_format
    else:
        name_format = app_name_format

    has_properties = False

    # This is the general format of the #define.
    d_format = "#define {0:38} {1}({2}, {3}, {4})"

    if len(interface.properties) > 0:
        has_properties = True

    for o in interface.parents:
        return_value.append("/*****")
        return_value.append(" * Path (node): \"{0}\"".format(o.get_full_name()))
        return_value.append(" */")

        path_index = o.index
        iface_index = o.get_interface_index(interface)

        if client_side:
            id_type = "AJ_PRX_MESSAGE_ID"
        else:
            id_type = "AJ_APP_MESSAGE_ID"

        member_index = 0
        for m in interface.methods:
            name = name_format.format(path_index, iface_index, m.name)
            mess = d_format.format(name, id_type, path_index,
                                iface_index, member_index)
            return_value.append(mess)
            member_index += 1

        for s in interface.signals:
            name = name_format.format(path_index, iface_index, s.name)
            mess = d_format.format(name, id_type, path_index,
                                iface_index, member_index)
            return_value.append(mess)
            member_index += 1

        if client_side:
            id_type = "AJ_PRX_PROPERTY_ID"
        else:
            id_type = "AJ_APP_PROPERTY_ID"

        for p in interface.properties:
            name = name_format.format(path_index, iface_index, p.name)
            mess = d_format.format(name, id_type, path_index,
                                iface_index, member_index)
            return_value.append(mess)
            member_index += 1

        if client_side:
            id_type = "AJ_PRX_MESSAGE_ID"
        else:
            id_type = "AJ_APP_MESSAGE_ID"

        if has_properties:
            # The entry in the table for AJ_PropertiesIface is added to the end.
            iface_index = len(o.interfaces)
            prop_comment = "/* All objects that use properties need these. */"
            return_value.append(prop_comment)
            get_name = "AJ_PROP_GET"
            name = name_format.format(path_index, iface_index, get_name)
            mess = d_format.format(name, id_type, path_index, iface_index, get_name)
            return_value.append(mess)

            set_name = "AJ_PROP_SET"
            name = name_format.format(path_index, iface_index, set_name)
            mess = d_format.format(name, id_type, path_index, iface_index, set_name)
            return_value.append(mess)
            return_value.append("")

    return return_value

def get_all_interface_coded_names(aj_object):
    """Get all the interface names for this object.

    All interface names coded such they are 'c' compatiable."""
    return_value = []
    has_properties = False

    for i in aj_object.interfaces:
        if len(i.properties) > 0:
            has_properties = True

        return_value.append("g_{0}".format(get_interface_coded_name(i)))

    if has_properties:
        return_value.append(AJ_PropertiesIface)

    return return_value

def get_interface_coded_name(interface):
    return "Iface{0}".format(interface.get_full_coded_name())

def get_interface_set_name(aj_object):
    name = "g_IfaceSet{0}".format(aj_object.get_full_name())
    return str.replace(name, "/", "_")

def get_complete_name(aj_object, interface, component):
    if component.input_arg_info is not None and\
       len(component.input_arg_info.args) > 0:
        input_args = component.input_arg_info.arg_declaration
    else:
        input_args = ""

    return_value = "{0}/{1}::{2}({3})".format(aj_object.get_full_name(),
                          interface.interface_full_name,
                          component.xml_name,
                          input_args)
    return return_value

def get_base_c_type(member):
    """Get the base (non-array) type of this member."""
    return __get_c_type(member.interface, member.get_base_signature())

def __get_c_type(interface, signature):
    """Get the 'C' type corresponding to this signature or None if not found."""
    t = None
    if signature in type_dictionary:
        t = type_dictionary[signature]
    elif signature[0] == '[':
        named_type = interface.get_named_type(signature[1:-1])
        if isinstance(named_type, structdef.StructDef) or \
           isinstance(named_type, dictdef.DictDef):
            t = "struct {0}".format(named_type.name)
    return t

def get_scaler_member(argdef):
    """Return first member name that is a scaler in this structure signature."""

    reject_types = ['(', '{', 'v', 'g', 'o', 's', 'x', 't', 'b', 'd']
    return_value = None

    # The reject type list gets smaller as we get more desperate. We never
    # return a structure, dictionary, variant, object, signature, or string.
    while return_value is None and len(reject_types) > 6:
        return_value = __do_get_scaler_member_search(argdef, reject_types)
        reject_types.pop() # If not found relax the requirements.

    return return_value

def make_member_from_memberdef(interface, member):
    """transform a single member definition into it's C declaration equivalent"""
    indirection_level = member.get_indirection_level()
    c_type = get_base_c_type(member)
    # some arcane manipulations are needed to patch this up
    basesig = member.get_base_signature()
    if basesig == 'b':
        comment = "/*bool*/ "
    elif member.is_dictionary():
        comment = "/*dictionary*/"
    else:
        comment = ""

    if indirection_level > 0:
        if basesig == 'b':
            c_type = "bool"
        comment = "/*'{0}{1}'*/ ".format(c_type, "*"*indirection_level)
        c_type = __get_c_type(interface, 'a')

    return "{0} {1}{2}".format(c_type, comment, member.name)

def get_array_container_variant_data(arg):
    """Get the initialization strings to use for variants found in arrays of containers.

    This is very closely related to get_initialization(). The naming and arrays size
    here must match the naming and arra size in get_initialization()."""
    return_value = []

    if arg.is_array():
        if arg.is_structure() or arg.is_dictionary():
            container = arg.get_named_type()
            for field in container.get_field_list():
                if field.arg_type == 'v':
                    data = "static uint8_t {0}{1}_uint8V[3];".format(arg.name, field.name.capitalize())
                    return_value.append(data)

    return return_value

def get_initialization(arg, indent_count):
    """Get the initialization string to use for this argument."""
    t = get_base_c_type(arg)

    if arg.is_array():
        if t == "char*":
            init = '[] = { "String 1", "String 2", "String 0" }'
        else:
            if arg.is_dictionary() or arg.is_structure():
                indent = indent_count * " "
                si0 = __make_structure_init_string(arg, 0)
                si1 = __make_structure_init_string(arg, 1)
                si2 = __make_structure_init_string(arg, 2)
                f = "[3] =\n{0}{{ {1},\n{0}  {2},\n{0}  {3} }}"
                init = f.format(indent, si0, si1, si2)
            else:
                init = "[10] = { 0 }"
    else:
        if arg.arg_type == "b":
            init = " = FALSE"
        elif arg.arg_type == "d":
            init = " = 0.0"
        elif arg.is_structure():
            init = " = {0}".format(__make_structure_init_string(arg))
        else:
            init = " = 0"

    return init

def __make_structure_init_string(arg, array_index = -1):
    """Return a structure initialization string for each structure member.

Each member will be set to zero except those which are pointers or variants in arrays.
If this arg is an array of structures then the index will be >= 0 and indicate which
element of the array being initialized."""
    assert(arg.is_structure() or arg.is_dictionary())
    member_num = 0
    index = 1
    init_values = []
    for field in arg.get_named_type().get_field_list():
        if field.arg_type == 's':
            if array_index >= 0:
                value = '"Hello world from initial {0}[{1}] {2}!"'.format(arg.name,
                                                                       array_index,
                                                                       field.name)
            else:
                value = '"Hello world from {0} {1}!"'.format(arg.name, field.name)
        elif field.arg_type == 'o':
            value = '"/test/foo"'
        elif field.arg_type == 'g':
            value = '"(sig)"'
        elif field.arg_type == 'd':
            value = "0.0"
        elif field.arg_type == 'b':
            value = "FALSE"
        elif field.arg_type == 'v' and index >= 0:
            variant_init = "{0}{1}_uint8V[{2}]".format(arg.name,
                                                       field.name.capitalize(),
                                                       array_index)
            value = '{{ AJ_ARG_BYTE, 1, 0, {{ &{0} }}, "y", 0 }}'.format(variant_init)
        elif field.is_structure():
            value = __make_structure_init_string(field)
        elif field.is_dictionary():
            value = "{{ {0} , {1} , {2} }}".format(__make_structure_init_string(field, 0), __make_structure_init_string(field, 1), __make_structure_init_string(field, 2))
        else:
            value = "0"

        init_values.append(value)

        index += 1

    return "{{ {0} }}".format(", ".join(init_values))

def __get_method_handler_name(path_index, interface, m):
    f = "{0}{1:_>2}_Meth{2}"

    return f.format(get_interface_coded_name(interface), path_index, m.name)

def __get_signal_handler_name(path_index, interface, s):
    f = "{0}{1:_>2}_Sig{2}"

    return f.format(get_interface_coded_name(interface), path_index, s.name)

def __get_property_handler_name(path_index, interface, p):
    f = "{0}{1:_>2}_Prop{2}"

    return f.format(get_interface_coded_name(interface), path_index, p.name)

def __get_client_switch_entries(interface, aj_object, iface_index, include_prop):
    return_value = []

    d_format = proxy_name_format
    path_index = aj_object.index

    r_format = "AJ_REPLY_ID({0})" # Some switch entries are wrapped in AJ_REPLY().
    define = None
    switch = None

    for m in interface.methods:
        define = d_format.format(path_index, iface_index, m.name)
        switch = r_format.format(define)

        name = __get_method_handler_name(path_index, interface, m)

        comp = InterfaceComponent(define, switch, name, "meth", m.no_reply)
        comp.method = m
        comp.xml_name = m.name

        comp.input_arg_info = ArgInfo(m.args, "in")
        comp.output_arg_info = ArgInfo(m.args, "out")

        return_value.append(comp)

    for s in interface.signals:
        define = d_format.format(path_index, iface_index, s.name)

        name = __get_signal_handler_name(path_index, interface, s)

        # Signal defines are not wrapped in "AJ_REPLY_ID()".
        comp = InterfaceComponent(define, define, name, "sig")
        comp.signal = s
        comp.xml_name = s.name

        comp.input_arg_info = None
        comp.output_arg_info = ArgInfo(s.args, "out")
        return_value.append(comp)

    properties_iface_index = len(aj_object.interfaces)

    if include_prop and interface.has_read_properties():
        define = d_format.format(path_index, properties_iface_index, "AJ_PROP_GET")
        switch = r_format.format(define)

        name = "PropGetHandler"
        comp = InterfaceComponent(define, switch, name, "prop")
        comp.object_name = aj_object.get_full_coded_name()

        return_value.append(comp)

    return return_value

def __do_get_scaler_member_search(argdef, reject_types):
    assert(argdef.is_dictionary() or argdef.is_structure())
    fieldlist = argdef.get_named_type().get_field_list()

    for field in fieldlist:
        if len(field.arg_type) != 1: continue
        if field.arg_type in reject_types: continue
        return [field.name, field.arg_type]

    return None

