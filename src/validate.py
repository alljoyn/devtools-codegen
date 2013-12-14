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

from xml.etree import ElementTree
import string

class ValidateException(Exception):
    """Validation exceptions."""

max_name_length = 255

# Validator methods for many objects.
#
# The following validators are implemented:
#
#   alljoyn_data(service)
#   arg_direction(string)
#   arg_name(string)
#   bus_object_path(string)
#   data_signature(string)
#   interface_name(string)
#   property_access(string)
#   member_name(string)
#   well_known_name(string)

def alljoyn_data(service, target):
    """Validates the AllJoyn service data.

    Throws a ValidateException on an error."""

    if service.alljoyn_object is None:
        raise ValidateException("No root node found.")

    __validate_aj_object(service.alljoyn_object)

    if target == "tc":
        __thin_client_service(service)
    else:
        # TODO: Validation for other target types.
        assert(target == "tc")

    return

def property_access(access, xml = None):
    """Validates a property access value as being read/write/readwrite."""
    valid_access = ("read", "write", "readwrite")

    if access not in valid_access:
        error1 = "Argument access '{0}' is invalid.".format(access)
        error2 = "It must be 'read', 'write' or 'readwrite'."
        error = " ".join([error1, error2])
        error = get_xml_error(xml, error)
        raise ValidateException(error)
    return

def arg_direction(direction, xml = None):
    """Validates an argument direction 'in' or 'out'."""
    valid_direction = ("in", "out")

    if direction not in valid_direction:
        d_format =\
            "Argument direction '{0}' is invalid. It must be 'in' or 'out'."
        error = d_format.format(direction)
        error = get_xml_error(xml, error)
        raise ValidateException(error)
    return

def data_signature(signature, xml = None):
    """Validates a data signature used for a method or signal argument."""
    error_format = "'{0}' is an invalid AllJoyn data type."

    if signature is None or len(signature) == 0:
        error = error_format.format("NULL")
        error = get_xml_error(xml, error)
        raise ValidateException(error)

    if len(signature) > 255:
        max_format1 = "Overlength signature '{0}'."
        max_format2 = "It is {0} characters long. The max is 255."
        err_mess1 = max_format1.format(signature)
        err_mess2 = max_format2.format(len(signature))

        error = "{0}\n{1}".format(err_mess1, err_mess2)
        error = get_xml_error(xml, error)
        raise ValidateException(error)

    valid_types = ('a', # AllJoyn array container type
                    'b', # AllJoyn boolean basic type
                    'd', # AllJoyn IEEE 754 double basic type
                    'g', # AllJoyn signature basic type
                    'h', # AllJoyn socket handle basic type
                    'i', # AllJoyn 32-bit signed integer basic type
                    'n', # AllJoyn 16-bit signed integer basic type
                    'o', # AllJoyn Name of an AllJoyn object instance
                    'q', # AllJoyn 16-bit unsigned integer basic type
                    's', # AllJoyn UTF-8 NULL terminated string basic type
                    't', # AllJoyn 64-bit unsigned integer basic type
                    'u', # AllJoyn 32-bit unsigned integer basic type
                    'v', # AllJoyn variant container type
                    'x', # AllJoyn 64-bit signed integer basic type
                    'y'  # AllJoyn 8-bit unsigned integer basic type
                    )
    valid_cont = (
                    '(', # AllJoyn struct container type
                    ')', # End of AllJoyn struct container type
                    '{', # AllJoyn dictionary or map container type
                    '}'  # End of AllJoyn dictionary or map container type
                    )

    error_format = "'{0}' is an invalid AllJoyn data type in '{1}'."
    unexp_format = "Unexpected '{0}' in '{1}'."
    paren_count = 0
    dict_count = 0

    max_index = len(signature)
    index = 0
    types = 0
    while index < max_index:
        c = signature[index]

        if c not in valid_types and c not in valid_cont:
            error = error_format.format(c, signature)
            error = get_xml_error(xml, error)
            raise ValidateException(error)

        if paren_count <= 0 and dict_count <= 0 and c is not 'a':
            types += 1

        if c == '(':
            paren_count += 1
        elif c == ')':
            paren_count -= 1

        if paren_count < 0:
            error = unexp_format.format(')', signature)
            error = get_xml_error(xml, error)
            raise ValidateException(error)

        if paren_count > 32:
            max_format = "Max depth of '(' is 32 and was exceeded in '{0}'."
            error = max_format.format(signature)
            error = get_xml_error(xml, error)
            raise ValidateException(error)

        if c == '{':
            dict_count += 1
            if index == 0 or signature[index - 1] != 'a':
                dict_error1 = \
                "All dictionary signatures must have an 'a' before them."
                dict_error2 = "'{0}' does not.".format(signature)
                error = " ".join([dict_error1, dict_error2])
                error = get_xml_error(xml, error)
                raise ValidateException(error)

            if (index + 1 >= max_index or
                signature[index + 1] not in valid_types):

                key_error1 = "Dictionaries must have a basic type for a key."
                key_error2 =\
                    "A dictionary in '{0}' does not.".format(signature)
                error = " ".join([key_error1, key_error2])
                error = get_xml_error(xml, error)
                raise ValidateException(error)

        # TODO: More dictionary tests.
        elif c == '}':
            dict_count -= 1

        if dict_count < 0:
            error = unexp_format.format('}', signature)
            error = get_xml_error(xml, error)
            raise ValidateException(error)

        if types > 1:
            e1 = "Arg '{0}' is an invalid argument.".format(signature)
            e2 = "Only a single type, struct, or array is allowed per arg."
            error = "{0}\n{1}".format(e1, e2)
            error = get_xml_error(xml, error)
            raise ValidateException(error)

        index += 1

    error_format = "Unbalanced '{0}' in AllJoyn data signature '{1}'."
    if paren_count > 0:
        error = error_format.format('(', signature)
        error = get_xml_error(xml, error)
        raise ValidateException(error)
    elif paren_count < 0:
        error = error_format.format(')', signature)
        error = get_xml_error(xml, error)
        raise ValidateException(error)

    if dict_count > 0:
        error = error_format.format('{', signature)
        error = get_xml_error(xml, error)
        raise ValidateException(error)
    elif dict_count < 0:
        error = error_format.format('}', signature)
        error = get_xml_error(xml, error)
        raise ValidateException(error)

    return

def bus_object_path(name, xml = None):
    """Validates a bus object name.

    Throws a ValidateException on invalid name."""

    # From the D-bus spec:
    # The path may be of any length.
    # The path must begin with an ASCII '/' (integer 47) character, and
    # must consist of elements separated by slash characters.
    # Each element must only contain the ASCII characters
    # "[A-Z][a-z][0-9]_"
    # No element may be the empty string.
    # Multiple '/' characters cannot occur in sequence.
    # A trailing '/' character is not allowed unless the path is the root
    # path (a single '/' character).
    if name is None or len(name) == 0:
        error = "Bus object name is required."
        error = get_xml_error(xml, error)
        raise ValidateException(error)

    error_format = "'{0}' is an invalid bus object name.\n{1}"

    if name[0] != '/':
        explanation = "Bus object names require '/' as the first character."
        error = error_format.format(name, explanation)
        error = get_xml_error(xml, error)
        raise ValidateException(error)

    if len(name) == 1:
        return

    if name[len(name) - 1] == '/':
        explanation = "Bus object names must not end in a '/'."
        error = error_format.format(name, explanation)
        error = get_xml_error(xml, error)
        raise ValidateException(error)

    valid_chars = "{0}{1}_".format(string.digits, string.ascii_letters)
    ex_format = "'{0}' is an invalid character."
    elements = name.split('/')

    # The 0 element is empty because the name must start with '/'.
    for e in elements[1:]:
        if len(e) <= 0:
            explanation = "Zero length elements ('//') are not allowed."
            error = error_format.format(name, explanation)
            error = get_xml_error(xml, error)
            raise ValidateException(error)

        for c in e:
            if string.find(valid_chars, c) == -1:
                explanation = ex_format.format(c)
                error = error_format.format(name, explanation)
                error = get_xml_error(xml, error)
                raise ValidateException(error)

def well_known_name(name):
    """Validates a well-known name.

    Throws a ValidateException on invalid name."""
    if name is None:
        raise ValidateException("Well-known name is required.")

    __common_name_tests(name)

def interface_name(name, xml = None):
    """Validates an interface name.

    Throws a ValidateException on invalid name."""
    if name is None:
        error = "Interface name is required."
        error = get_xml_error(xml, error)
        raise ValidateException(error)

    if str.find(name, "-") != -1:
        error_format = """Invalid name '{0}'.
Hyphens, '-', are not allowed in interface names."""
        error = error_format.format(name)
        error = get_xml_error(xml, error)
        raise ValidateException(error)

    __common_name_tests(name, xml)

def arg_name(name, xml = None):
    """Validates an argument name.

    Argument name restrictions are the same as member names.
    Throws a ValidateException on invalid name."""
    if name is None or len(name) == 0:
        error = "An argument name is required or the use of the '-l' option."
        error = get_xml_error(xml, error)
        raise ValidateException(error)

    if str.find(name, "-") != -1:
        error_format = "The member '{0}' has an invalid character: '-'."
        error = error_format.format(name)
        error = get_xml_error(xml, error)
        raise ValidateException(error)

    __name_length_check(name, xml)

    # Argument name restrictions are essentially the same as an element name.
    __element_test(name, "argument", xml)
    return

def member_name(name, xml = None):
    """Validates a member (method or signal) name.

    Throws a ValidateException on invalid name."""
    if name is None or len(name) == 0:
        error = "A member name is required."
        error = get_xml_error(xml, error)
        raise ValidateException(error)

    if str.find(name, "-") != -1:
        error_format = "The member '{0}' has an invalid character: '-'."
        error = error_format.format(name)
        error = get_xml_error(xml, error)
        raise ValidateException(error)

    __name_length_check(name, xml)

    # Member name restrictions are essentially the same as an element name.
    __element_test(name, "member", xml)

def __common_name_tests(name, xml = None):
    """Do tests common to all names."""
    __name_length_check(name, xml)
    __first_character_period(name, xml)
    __elements_test(name, xml)

def get_xml_error(xml, message):
    """Returns a string for error reporting using the xml and a message.

    If xml is None then just returns message."""

    if xml is not None:
        s = ElementTree.tostring(xml)
        return_value = "{0}\nFound here:\n{1}".format(message, s)
    else:
        return_value = message

    return return_value

def __name_length_check(name, xml):
    """Test for maximum length."""
    length = len(name)
    if length > max_name_length:
        f = "The name '{0}'\nis {1} characters long. The max is {2}."
        error = f.format(name, length, max_name_length)
        error = get_xml_error(xml, error)
        raise ValidateException(error)

def __first_character_period(name, xml):
    """Test for the first character being a period ('.')."""
    if name[0] == '.':
        f = """The name '{0}' is invalid.
The first character must not be a period."""

        error = f.format(name)
        error = get_xml_error(xml, error)
        raise ValidateException(error)

def __elements_test(name, xml):
    elements = name.split('.')
    error_format = """The name '{0}' is invalid.
Names are composed of 2 or more elements separated by a period ('.')
character. All elements must contain at least one character."""

    if len(elements) <= 1:
        error = error_format.format(name)
        error = get_xml_error(xml, error)
        raise ValidateException(error)

    if name[0] == '.':
        error = error_format.format(name)
        error = get_xml_error(xml, error)
        raise ValidateException(error)

    for e in elements:
        if len(e) < 1:
            error = "The name '{0}' has a zero length element.".format(name)
            error = get_xml_error(xml, error)
            raise ValidateException(error)
        __element_test(e, 'element', xml)

def __element_test(e, name_type, xml):
    """Do tests on a single name element."""
    error_format = """The {0} '{1}' has an invalid character.
Each {0} must only contain the ASCII characters "[A-Z][a-z][0-9]_" and must
not begin with a digit."""

    for c in e:
        if string.find(string.digits, e[0]) != -1:
            error = error_format.format(name_type, e)
            error = get_xml_error(xml, error)
            raise ValidateException(error)

        # Underscores are valid and hyphens are handled elsewhere.
        if (c != '_' and c != '-' and
            string.find(string.ascii_letters, c) == -1 and
            string.find(string.digits, c) == -1):

            error = error_format.format(name_type, e)
            error = get_xml_error(xml, error)
            raise ValidateException(error)
    return

def __validate_aj_object(node):
    """Validates a AllJoyn node.

    Each node must contain either, or both, interfaces or other nodes.
    Each subnode is also checked for validity.
    Throws a ValidateException on an error."""

    if len(node.alljoyn_objects) == 0 and len(node.interfaces) == 0:
        mess = "Node '{0}' is empty.".format(node.name)
        raise ValidateException(mess)

    for key in sorted(node.alljoyn_objects):
        n = node.alljoyn_objects[key]
        __validate_aj_object(n)

    return

def __search_for_multidimension_array(args):
    mess = "Thin Client code generator does not support multidimensional arrays."

    for a in args:
        if a.arg_type.find("aa") != -1:
            raise ValidateException(mess)
    return

c_key_words = ("auto", "break", "case", "char", "const", "continue", "default",
               "do", "double", "else", "enum", "extern", "float", "for",
               "goto", "if", "int", "long", "register", "return", "short",
               "signed", "sizeof", "static", "struct", "switch", "typedef",
               "union", "unsigned", "void", "volatile", "while"
              )

windows_key_words = ("interface")

def __search_for_tc_arg_keywords(args):
    c_mess = "Thin Client code may not use the 'C' keyword '{0}' as an argument name."
    win_mess = "Thin Client code may not use the Windows 'C' language keyword '{0}' as an argument name."

    for a in args:
        if a.name in c_key_words:
            raise ValidateException(c_mess.format(a.name))

        if a.name in windows_key_words:
            raise ValidateException(win_mess.format(a.name))
    return

def __thin_client_service(service):
    """Thin Client applications have some limitations. Check for those limits

    There is a max of 256 objects (nodes) per application.
    There is a max of 256 interfaces (255 if any of the interfaces have
    properties) per object.
    There is a max of 256 signals + methods per interface.
    There is a max of 256 properties per interface."""

    mess = "Thin Client code may not use the 'C' keyword '{0}' as a {1} name."

    for k in sorted(service.interfaces):
        i = service.interfaces[k]

        for m in i.methods:
            __search_for_multidimension_array(m.args)
            __search_for_tc_arg_keywords(m.args)

            if m.name in c_key_words:
                raise ValidateException(mess.format(m.name, "method"))

        for p in i.properties:
            __search_for_multidimension_array(p.args)
            __search_for_tc_arg_keywords(p.args)

            if p.name in c_key_words:
                raise ValidateException(mess.format(m.name, "property"))

        for s in i.signals:
            __search_for_multidimension_array(s.args)
            __search_for_tc_arg_keywords(s.args)

            if s.name in c_key_words:
                raise ValidateException(mess.format(s.name, "signal"))

    objects = service.get_objects()

    if len(objects) >= 256:
        max_mess1 = "There is a max of 256 objects (nodes)"
        max_mess2 = "in Thin Client applications."
        mess_format = "{0} {1}\nThis one has {2} objects."
        mess = mess_format.format(max_mess1, max_mess2, len(objects))
        raise ValidateException(mess)

    for o in objects:
        has_properties = False

        for i in o.interfaces:
            if len(i.methods) + len(i.signals) > 256:
                max_mess1 = "There is a max of 256 methods + signals per"
                max_mess2 = "interface in Thin Client applications."
                f = "{0} has {1} methods and {2} signals (total = {3})."
                max_mess3 = f.format(i.interface_full_name,
                                        len(i.methods),
                                        len(i.signals),
                                        len(i.methods) + len(i.signals))
                mess_format = "{0} {1}\n{2}"
                mess = mess_format.format(max_mess1, max_mess2, max_mess3)
                raise ValidateException(mess)

            num_props = len(i.properties)

            if num_props > 0:
                has_properties = True

            if num_props > 256:
                max_mess1 = "There is a max of 256 properties per interface"
                max_mess2 = "in Thin Client applications."
                mess_format = "{0} {1}\n{2} has {3} properties."
                mess = mess_format.format(max_mess1,
                                            max_mess2,
                                            i.interface_full_name,
                                            len(o.properties))
                raise ValidateException(mess)

        num = len(o.interfaces)

        if num > 256 or (has_properties and num > 255):
            max_mess1 = "There is a max of 256 interfaces (255 if any of the"
            max_mess2 = "interfaces have properties) per object (node)"
            max_mess3 = "in Thin Client applications."
            mess_format = "{0} {1} {2}\nObject {3} has {4} interfaces."
            mess = mess_format.format(max_mess1,
                                      max_mess2,
                                      max_mess3,
                                      o.get_full_name(),
                                      num)
            raise ValidateException(mess)


    return
