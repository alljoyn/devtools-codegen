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

import string
from xml.etree import ElementTree

import validate

target_language = None

def get_annotations(xml, aj_object):
    """Get the annotation value for the AllJoyn object from this xml."""
    annotations = xml.iterfind("annotation")

    for a in annotations:
        name = a.get("name")

        if name == "org.alljoyn.Bus.Item.IsSecure":
            value = __get_true_false_value(xml, a, name)
            aj_object.is_secure = value
        elif name == "org.freedesktop.DBus.Method.NoReply":
            value = __get_true_false_value(xml, a, name)
            aj_object.no_reply = value
        elif name == "org.alljoyn.Bus.Arg.VariantTypes":
            value = a.get("value")
            if value is None:
                __report_missing_value(xml, name)
            validate.data_signature(value)
            aj_object.variant_type = value
        else:
            f = "\nWarning! Ignoring interface annotation '{0}'."
            mess = f.format(name)
            mess = validate.get_xml_error(xml, mess)
            print(mess)

    return

def make_camel_case(object_name, separator = "/"):
    """Make an object name into a camel case string and delete the separator.

    If the separator is None this method just makes the first character lower
    case."""

    if separator:
        caps_value = string.capwords(object_name, separator)
        temp = caps_value.replace(separator, "")
    else:
        temp = object_name

    first_char_string = temp[0:1]
    return_value = first_char_string.lower() + temp[1:]

    return return_value

def get_arg_signature(component, direction):
    """Get the signature used to marshal the arguments when making a call."""
    return_value = ""

    for a in component.args:
        if a.direction == direction:
            return_value = "".join([return_value, a.arg_type])

    return return_value

def __get_true_false_value(xml, annotation, name):
    """Get a true or false value from the annotation xml.

    xml is the parent xml object to annotation xml.
    annotation is the xml object which should have a attribute of value
    containing the 'true' or 'false' value.
    name is the of the parent AllJoyn object."""
    value = annotation.get("value")

    if value is not None:
        if value == "true":
            value = True
        elif value == "false":
            value = False
        else:
            f = "Unexpected annotation value '{0}' for {1}."
            mess = f.format(value, name)
            f = "{0}\nExpected values are 'true' and 'false'."
            mess = f.format(mess)
            mess = validate.get_xml_error(xml, mess)
            raise validate.ValidateException(mess)
    else:
        __report_missing_value(xml, name)

    return value

def __report_missing_value(xml, name):
    f = "Annotation '{0}' is required to have an attribute of 'value'."
    mess = f.format(name)
    mess = validate.get_xml_error(xml, mess)
    raise validate.ValidateException(mess)
