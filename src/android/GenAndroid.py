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

import sys
import shutil
import os
import glob

from .. import CheetahCompileExcept as cce

try:
    # These are all Android specific files built from templates (.tmpl).
    from AndroidLayoutMain import AndroidLayoutMain
    from AndroidManifest import AndroidManifest
    from AndroidStrings import AndroidStrings

    from classpath import classpath
    from ClientMain import ClientMain
    from ClientImplementation import ClientImplementation

    from Interface import Interface

    from project import project
    from properties import properties

    from ServiceMain import ServiceMain
    from ServiceImplementation import ServiceImplementation
except ImportError:
    # The exception message must be nothing but the file name.
    raise cce.CheetahCompilationException(__file__)

# These are native Python files
from .. import config
from .. import service
from .. import argdef
from .. import interface as iface
from .. import structdef
from .. import dictdef
from .. import memberdef
from .. import common

def hooks():
    """Return the hooks for the AllJoyn Android language binding."""

    hooks = {'validate_cmdline' : __validate_cmdline,
             'generate_code' : __generate_code }
    return hooks

def __generate_code(command_line, codegen_service):
    """Generate the AllJoyn Android Java code from the previously parsed XML."""

    assert(command_line.target_language == "android")

    __make_directories_copy_resource_files(command_line, codegen_service)

    # Make the interface files before the others because __make_interface_arg_info()
    # is called on each interface for initialization. This initialization is required
    # before some of the common files are built.
    __make_interface_files(command_line, codegen_service)
    __make_common_files(command_line, codegen_service)

    return

def __validate_cmdline(command_line):
    """Validate the command-line arguments.

    The Well-known name is required.

    Arguments:
    command_line -- the command-line arguments to be validated"""

    if command_line.well_known_name is None:
        raise config.ConfigException("Well-known name is required.")

class ArgInfo:
    """This is a container class for argument data."""

    def __init__(self, args, direction, interface = None, name = None):
        """Initialize a new instance of an ArgInfo class."""
        arg_list = []

        self.arg_declaration = self.__get_arg_declarations(args, direction)

        for a in args:
            if a.direction != direction:
                continue

            arg_list.append(a)

        if direction == "out" and name and len(arg_list) > 1:
            # Because a Java method can't return multiple values they were
            # combined them into a single structure. That structure has a name
            # with the suffix iface.return_suffix.
            name += iface.return_suffix
            assert(name in interface.structures)

            struct = interface.structures[name]
            output_arg = argdef.ArgDef(None, name, struct.signature, "out")
            output_arg.interface = interface
            self.args = [output_arg]
        else:
            self.args = arg_list

        return

    def max_number_of_array_dimensions(self):
        """Gets the maximum number of array dimensions in any of the arguments."""
        return_value = 0

        for a in self.args:
            dim = a.get_max_array_dimension()

            if dim > return_value:
                return_value = dim

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
            if a.arg_type.find('a') != -1:
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

    def __get_arg_declarations(self, args, direction):
        """This gets the argument declarations for a given method/signal."""
        return_value = None
        # {0} = previous set of arg declarations.
        # {1} = Java type.
        # {2} = '[]' if array, '' otherwise.
        # {3} = argument name.
        arg_format = "{0}{1}{2} {3}"
        is_first = True

        for a in args:
            if a.direction != direction:
                continue

            if is_first:
                is_first = False
                return_value = ""
            else:
                return_value = "{0}, ".format(return_value)

            sig = a.arg_type.lstrip('a')
            ptr = "[]" * (len(a.arg_type) - len(sig))
            j_type = get_java_type(a.interface, sig)

            return_value = arg_format.format(return_value, j_type, ptr, a.name)

        return return_value

def get_return_arg(member):
    """Get the return argument/structure for this member."""
    outputs = member.output_arg_info.args
    # This should be true even if there are multiple outputs.
    # The outputs are all combined into a single struture.
    assert(len(outputs) <= 1)
    arg = None

    if len(outputs) > 0:
        arg = outputs[0]

    return arg

def get_java_return_type(member):
    """Get the return type for this member."""
    arg = get_return_arg(member)

    if arg is None:
        return "void"

    t = get_java_type(arg.interface, arg.arg_type, member)

    return t

# This is a comment string used at the start of all "runnable" code.
comment_start_runnable ="""\
/* TODO: Start of generated code which should be replaced by user. */"""

# This is a comment string used at the end of all "runnable" code.
comment_end_runnable = """\
/* TODO: End of generated code which should be replaced by user. */"""

# This is a comment string used at the start of places where the user should
# deal with a error condition.
comment_handle_error = "/* TODO: Handle the error condition. */"

# This converts an AllJoyn data type into the Android Java printf format string .
printf_dictionary = {'b': "%b",
                     'd': "%g",
                     'g': "%s",
                     'i': "%d",
                     'n': "%d",
                     'o': "%s",
                     'q': "%d",
                     's': "%s",
                     't': "%d",
                     'u': "%d",
                     'v': "/* TODO: Figure out variant types. */",
                     'x': "%d",
                     'y': "%d",
                    }

# This converts an AllJoyn data type into the Android Java data type.
type_dictionary = {'b': "boolean",
                   'd': "double",
                   'g': "String",
                   'i': "int",
                   'n': "short",
                   'o': "String",
                   'q': "short",
                   's': "String",
                   't': "long",
                   'u': "int",
                   'v': "/* TODO: Figure out variant types. */",
                   'x': "long",
                   'y': "byte",
                  }

def get_base_java_type(interface, signature, member = None):
    """Get the non-array type of this signature"""
    return get_java_type(interface, signature.lstrip('a'), member)

def get_java_type(interface, signature, member = None):
    """Get the Java type corresponding to this AllJoyn signature. Or if not found from the signature
    see if it is a return structure which has a signature based upon the member name."""
    t = None
    return_struct_key = None

    if member:
        return_struct_key = member.name + iface.return_suffix

    base_signature = memberdef.get_base_signature(signature)

    if base_signature in type_dictionary:
        tbase = type_dictionary[base_signature]
    elif return_struct_key in interface.structures:
        s = interface.structures[return_struct_key]
        tbase = __make_structure_type_name(interface, s)
    else:
        assert(base_signature[0] == '[')
        named_type = interface.get_named_type(base_signature[1:-1])
        if isinstance(named_type, structdef.StructDef) or isinstance(named_type, dictdef.DictDef):
            tbase = __make_structure_type_name(interface, named_type)

    if memberdef.is_array(signature):
        t = "{0}[]".format(tbase)
    else:
        t = tbase

    assert(t)

    return t

def get_initialization(arg, member = None):
    """Get the initialization string to use for this argument."""
    t = get_base_java_type(arg.interface, arg.arg_type, member)

    if arg.is_array():
        if t == "String":
            init = ' = {"String 0", "String 1", "String 2"}'
        elif arg.is_structure() or arg.is_dictionary():
            init = " = {{ new {0}(), new {0}(), new {0}() }}".format(t)
        else:
            b = arg.get_base_signature()
            if b[0] == 'b':
                init = " = { false, false, false, false, false, false, false, false, false, false }"
            else:
                init = " = { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 }"
    else:
        if arg.arg_type == "b":
            init = " = false"
        elif arg.arg_type == "d":
            init = " = 0.0"
        elif t == "String":
            init = ' = ""'
        elif arg.is_structure() or arg.is_dictionary():
            init = " = new {0}()".format(t)
        else:
            init = " = 0"

    return init

def get_complete_name(object_name, interface_name, component):
    return_value = "{0}/{1}::{2}()".format(object_name, interface_name, component.name)
    return return_value

def has_persistent_args(service, is_client):
    """Return True if any components have arguments that need to be persistent."""
    for key in sorted(service.interfaces):
        i = service.interfaces[key]

        if interface_needs_persistent_data(i, is_client):
            return True

    return False

def interface_needs_persistent_data(interface, is_client):
    """Returns True if this Interface needs persisent data for Runnable code.

    The test returns true if any method has arguments which match the direction
    or it has a writable property. Or if direction is "out" then if there are
    any signals with arguments."""

    # The server must have persistent data for signal arguments.
    if not is_client:
        for s in interface.signals:
            if s.args:
                return True

    # In the more general case the client needs persistent data for inputs.
    # The server needs persistent data for outputs.
    if is_client:
        direction = "in"
    else:
        direction = "out"

    for m in interface.methods:
        for a in m.args:
            if a.direction == direction:
                return True

    for p in interface.properties:
        if (p.is_writeable() and direction == "in") or (
            p.is_readable() and direction == "out"):
            return True

    return False

def get_well_known_name_path(configuration):
    return __get_well_known_name_path(configuration.command_line)

def make_members_from_structure(interface, struct):
    """Return the member types, names, and initialization from the structure."""
    return_value = []

    for f in struct.fields:
        java_type = get_java_type(interface, f.arg_type)
        init = get_initialization(f)
        m = [java_type, f.name, init]

        return_value.append(m)

    return return_value

def __make_structure_type_name(interface, structure):
    return "{0}.{1}".format(interface.interface_name, structure.name)

def __get_well_known_name_path(command_line):
    """Get the subdirectory the Android user inteface should reside in."""
    sub_path = ""
    directories = command_line.well_known_name.split(".")

    for d in directories:
        sub_path = os.path.join(sub_path, d)

    return sub_path

def __get_interface_subdirectory(interface):
    """Get the subdirectory the files for this interface should reside in."""
    sub_path = ""
    directories = interface.get_name_components()[0:-1]

    for d in directories:
        sub_path = os.path.join(sub_path, d)

    return sub_path

def __make_interface_files(command_line, codegen_service):
    sub_path0 = "src"

    # For each interface generate service and client .java Interface files.
    for key in sorted(codegen_service.interfaces):
        i = codegen_service.interfaces[key]
        __make_interface_arg_info(i)

        sub_path1 = __get_interface_subdirectory(i)

        # If client only don't generate the service files.
        if not command_line.client_only:
            temp = Interface()
            temp.interface = i

            service_path = os.path.join("Service", sub_path0, sub_path1)
            filename = "{0}.java".format(i.interface_name)

            full_filename = os.path.join(service_path, filename)
            __make_target_file(temp, full_filename, command_line, codegen_service)

            temp = ServiceImplementation()
            temp.interface = i

            service_path = os.path.join("Service", sub_path0, sub_path1)
            filename = "{0}Impl.java".format(i.interface_name)

            full_filename = os.path.join(service_path, filename)
            __make_target_file(temp, full_filename, command_line, codegen_service)

        temp = Interface()
        temp.interface = i

        client_path = os.path.join("Client", sub_path0, sub_path1)
        filename = "{0}.java".format(i.interface_name)

        full_filename = os.path.join(client_path, filename)
        __make_target_file(temp, full_filename, command_line, codegen_service)

        if i.signals:
            temp = ClientImplementation()
            temp.interface = i

            service_path = os.path.join("Client", sub_path0, sub_path1)
            filename = "{0}Impl.java".format(i.interface_name)

            full_filename = os.path.join(client_path, filename)
            __make_target_file(temp, full_filename, command_line, codegen_service)

    return

def __make_common_files(command_line, codegen_service):
    """Generate the files that are common to both the client and server."""
    # The first entry is the template.
    # The second entry is the name of the file being created.
    common_files = [[project(),           ".project"],
                    [properties(),        "project.properties"],
                    [AndroidManifest(),   "AndroidManifest.xml"],
                    [AndroidStrings(),    os.path.normpath("res/values/strings.xml")],
                    [AndroidLayoutMain(), os.path.normpath("res/layout/main.xml")],
                    [classpath(),         ".classpath"]
                   ]

    projects = ["Client"]

    if not command_line.client_only:
        projects.append("Service")

    for client_or_service_string in projects:
        for template, subfilename in common_files:
            template.client_or_service = client_or_service_string
            filename = os.path.join(client_or_service_string, subfilename)
            __make_target_file(template, filename, command_line, codegen_service)

    temp = ServiceMain()
    sub_path0 = "src"
    sub_path1 = __get_well_known_name_path(command_line)
    filename = os.path.join("Service", sub_path0, sub_path1, "ServiceMain.java")
    __make_target_file(temp, filename, command_line, codegen_service)

    temp = ClientMain()
    filename = os.path.join("Client", sub_path0, sub_path1, "ClientMain.java")
    __make_target_file(temp, filename, command_line, codegen_service)

    return

def __copy_subdirectory(dest_path):
    """Copy a directory, in a sub dir from this file, to the dest_path directory."""

    # copytree() requires a non-existent destination.
    # If the path exists assume the contents are correct.
    if os.path.exists(dest_path):
        print("Path '{0}' exists and will not be updated.".format(dest_path))
        return

    # The source subdirectory is a subdirectory of this file.
    source_subdir = os.path.basename(dest_path)
    source = os.path.join(os.path.split(__file__)[0:-1][0], source_subdir)
    shutil.copytree(source, dest_path)

def __make_directories_copy_resource_files(command_line, codegen_service):
    projects = ["Client"]

    # Get the source directory for the resource files.
    # This is in a subdirectory just below the location of this file.
    android_res = os.path.join(os.path.split(__file__)[0:-1][0], "res")

    if not command_line.client_only:
        projects.append("Service")

    libs = __get_alljoyn_libs()

    for p in projects:
        sub_path0 = os.path.join(command_line.output_path, p)

        # Each "main()" requires a ".settings" directory.
        full_path = os.path.join(sub_path0, ".settings")
        __copy_subdirectory(full_path)

        # Each "main()" requires a "res" directory.
        full_path = os.path.join(sub_path0, "res")
        __copy_subdirectory(full_path)

        # Make the values res/values directory which contains the strings file.
        values_dir = os.path.join(full_path, "values")
        if not os.path.exists(values_dir):
            os.makedirs(values_dir)

        libs_dir = os.path.join(sub_path0, "libs")

        if not os.path.exists(libs_dir):
            os.makedirs(libs_dir)

        if len(libs) > 0:
            shutil.copy2(libs[0], libs_dir)

        arm_dir = os.path.join(libs_dir, "armeabi")

        if not os.path.exists(arm_dir):
            os.makedirs(arm_dir)

        if len(libs) > 1:
            shutil.copy2(libs[1], arm_dir)

        # The "main()" part of the code goes into the Well-Known name directory.
        sub_path0 = os.path.join(sub_path0, "src")
        sub_path1 = __get_well_known_name_path(command_line)
        full_path = os.path.join(sub_path0, sub_path1)

        if not os.path.exists(full_path):
            os.makedirs(full_path)

        # Each interface goes into it's own directory.
        for key in sorted(codegen_service.interfaces):
            i = codegen_service.interfaces[key]
            sub_path1 = __get_interface_subdirectory(i)
            full_path = os.path.join(sub_path0, sub_path1)

            if not os.path.exists(full_path):
                os.makedirs(full_path)

    return

def __get_alljoyn_libs():
    """Gets the complete path to files liballjoyn_java.so and alljoyn.jar.

They are returned as [jar_lib, so_lib] or a warning message is printed
and the return value is []."""
    return_value = []

    # The source of the libraries is found via an environment variable.
    alljoyn_sdk_home_environment_variable = "ALLJOYN_SDK_HOME"

    if alljoyn_sdk_home_environment_variable not in os.environ:
        print("WARNING! '{0}' environment variable is not set.".format(alljoyn_sdk_home_environment_variable))
    else:
        sdk_home = os.environ[alljoyn_sdk_home_environment_variable]
        sdk_lib_wild_path = os.path.join(sdk_home, "alljoyn-android", "core", "alljoyn-*",
                                         "java")
        sdk_lib_path = glob.glob(sdk_lib_wild_path)

        if len(sdk_lib_path) < 1 or not os.path.exists(sdk_lib_path[0]):
            print("WARNING! Path '{0}' does not exist.".format(sdk_lib_wild_path))
        else:
            so_lib = os.path.join(sdk_lib_path[0], "lib", "liballjoyn_java.so")
            jar_lib = os.path.join(sdk_lib_path[0], "jar", "alljoyn.jar")

            found = True

            if not os.path.isfile(so_lib):
                found = False
                print("WARNING! File '{0}' does not exist.".format(so_lib))

            if not os.path.isfile(jar_lib):
                found = False
                print("WARNING! File '{0}' does not exist.".format(jar_lib))

            if found:
                return_value = [jar_lib, so_lib]

    if len(return_value) < 1:
        print("WARNING! No AllJoyn libraries copied to the project.")

    return return_value

def __make_target_file(template, filename, command_line, codegen_service):
    """Make this one file, filename, from the given template."""
    template.command_line = command_line
    template.service = codegen_service

    path = command_line.output_path
    out_file = os.path.join(path, filename)
    subdir = os.path.split(out_file)[0]

    if not os.path.exists(subdir):
        os.makedirs(subdir)

    with open(out_file, 'w') as f:
        f.write("{0}".format(template))

    return

def __make_interface_arg_info(interface):
    """Make the arg info for all methods, signals, and properties."""
    if interface.has_arg_info == False:
        for m in interface.methods:
            m.input_arg_info = ArgInfo(m.args, "in")
            m.output_arg_info = ArgInfo(m.args, "out", interface, m.name)

        for s in interface.signals:
            s.input_arg_info = None
            s.output_arg_info = ArgInfo(s.args, "out")

        for p in interface.properties:
            p.input_arg_info = ArgInfo(p.args, "in")
            p.output_arg_info = ArgInfo(p.args, "out", interface, p.name)

        interface.has_arg_info = True

    return
