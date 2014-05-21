# Copyright (c) 2014 AllSeen Alliance. All rights reserved.
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
import os

from .. import propertydef as pd

from Interface_H import Interface_H
from Interface_CC import Interface_CC
from Provider_H import Provider_H
from Provider_CC import Provider_CC
from Consumer_H import Consumer_H
from Consumer_CC import Consumer_CC

class_suffixes = { 'intf' : 'TypeDescription', 'prov' : 'Interface', 'cons' : 'Proxy' }

def hooks():
    hooks = {'validate_cmdline' : __validate_cmdline,
             'generate_code' : __generate_code }
    return hooks

def __validate_cmdline(command_line):
    # object path is optional but XML parser needs it
    # insert dummy if not present
    if command_line.object_path is None:
        command_line.object_path = "/dummy"

def __generate_code(command_line, service):
    """Generate the AllJoyn C++ code."""

    assert(command_line.target_language == "ddcpp")

    intf_h = Interface_H()
    intf_cc = Interface_CC()
    prov_h = Provider_H()
    prov_cc = Provider_CC()
    cons_h = Consumer_H()
    cons_cc = Consumer_CC()

    for key in service.interfaces:
        intf = service.interfaces[key]
        intf.intf_class = intf.interface_name + class_suffixes['intf']
        intf.prov_class = intf.interface_name + class_suffixes['prov']
        intf.cons_class = intf.interface_name + class_suffixes['cons']
        # generate the files
        __make_target_file(intf_h, intf.intf_class + '.h', command_line, intf)
        __make_target_file(intf_cc, intf.intf_class + '.cc', command_line, intf)
        __make_target_file(prov_h, intf.prov_class + '.h', command_line, intf)
        __make_target_file(prov_cc, intf.prov_class + '.cc', command_line, intf)
        __make_target_file(cons_h, intf.cons_class + '.h', command_line, intf)
        __make_target_file(cons_cc, intf.cons_class + '.cc', command_line, intf)

    return

def __make_target_file(template, filename, command_line, interface = None):
    """Make this one file, filename, from the given template."""
    template.command_line = command_line
    template.interface = interface

    path = command_line.output_path

    out_file = os.path.join(path, filename)

    with open(out_file, 'w') as f:
        f.write("{0}".format(template))

    return

def names_csv(items, direction = None, initial = None):
    """Create a comma-separated list of the names of all items.

    If direction is provided then only items for the given direction are added.
    If initial is provided then this will be the starting CSV list instead of
    an empty one."""
    if initial:
        csv = initial
        first = False
    else:
        csv = ''
        first = True
    for item in items:
        if not direction or direction == item.direction:
            if not first:
                csv += ','
            else:
                first=False
            csv += item.name
    return csv

def get_arg(item):
    if isinstance(item, pd.PropertyDef):
        for arg in item.args:
            if 'out' == arg.direction:
                return arg
    else:
        return item
    raise Exception("Only read semantics is supported at '%s'" % item.name)

def sig_string(items, direction = None):
    """Create a DBus signature string for all items.

    If direction is provided then only items for the given direction are
    considered."""
    sig=''
    for item in items:
        arg = get_arg(item)
        if not direction or direction == arg.direction:
            sig += arg.get_flattened_signature()
    return '"' + sig + '"' if len(sig) > 0 else 'NULL'

def __reference_type(typestr, reference):
    if reference:
        typestr = 'const ' + typestr + '&'
    return typestr

def cpp_base_type(arg, reference = False, namespacing = True):
    if arg.references_named_type():
        # it is a named type because all compounds have been processed in cpp_type
        typestr = arg.get_named_type().name
        if namespacing:
            typestr = 'Type::' + typestr
        typestr = __reference_type(typestr, reference)
    else:
        basesig = arg.get_base_signature()
        typestr = cpp_type_dictionary[basesig]
        if 's' == basesig:
            typestr = __reference_type(typestr, reference)
    return typestr

def cpp_type(item, reference = False, namespacing = True):
    arg = get_arg(item)
    if arg.is_dictionary() and 1 == arg.get_indirection_level():
        typestr = cpp_base_type(arg, False, namespacing)
        typestr = __reference_type(typestr, reference)
    elif arg.is_array():
        basetypestr = cpp_base_type(arg, False, namespacing)
        depth = arg.get_indirection_level()
        if arg.is_dictionary():
            depth -= 1 # dictionaries are also arrays, so depth is one less
        for _ in xrange(depth):
            if ':' == basetypestr[0]:
                basetypestr = ' ' + basetypestr # C++ syntax fix
            if '>' == basetypestr[-1]:
                basetypestr = basetypestr + ' ' # C++ syntax fix
            basetypestr = 'std::vector<' + basetypestr + '>'
        typestr = __reference_type(basetypestr, reference)
    else:
        typestr = cpp_base_type(arg, reference, namespacing)
    return typestr

def args_string(items, direction = None, append = None):
    """Create a method arguments string for all items.

    If direction is provided then only items for the given direction are
    considered."""
    args = ''
    for item in items:
        if not direction or direction == item.direction:
            if args:
                args += ', '
            args += cpp_type(item, reference = True) + ' ' + item.name
    if append:
        if args:
            args += ', '
        args += append
    return args

# This converts an AllJoyn data type into a plain 'C++' data type.
cpp_type_dictionary = {'b': "bool",
                       'd': "double",
                       'g': "datadriven::Signature",
                       'i': "int32_t",
                       'n': "int16_t",
                       'o': "datadriven::ObjectPath",
                       'q': "uint16_t",
                       's': "qcc::String",
                       't': "uint64_t",
                       'u': "uint32_t",
                       'x': "int64_t",
                       'y': "uint8_t",
                       }

# TODO copied from TC, make generic?
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
