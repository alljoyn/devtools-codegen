# Copyright (c) 2013, AllSeen Alliance. All rights reserved.
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

import unittest
import fnmatch
import os
import sys

sys.path.append("../../src")
import AllJoynCodeGen.parseajxml as parseajxml
import AllJoynCodeGen.validate as validate
import AllJoynCodeGen.config as config

file_dictionary = {}
interface_count = 0

def tearDownModule():
    global file_dictionary, interface_count

    print("\nFiles read: {0}.".format(len(file_dictionary)))
    f = "Interfaces successfully parsed: {0}."
    print(f.format(interface_count))
    return

class TestParse(unittest.TestCase):
    """Tests the parsing of XML files."""

    def test_invalid_filename(self):
        """Tests the invalid file name handling."""

        full_filename = "DoesNotExist.foo"
        with self.assertRaises(parseajxml.ParseException) as cm:
            self.__do_the_parse(full_filename)

        message = cm.exception.message
        self.assertTrue(str.find(message, full_filename) != -1)
        self.assertTrue(str.find(message, "No such file or directory") != -1)
        return

    def test_xml_testcases(self):
        """Tests files in xml_testcases directory."""
        files = self.__directory_xml_files("../xml_testcases")
        file_report_format = "Parsing '{0}'."

        for f in files:
            if str.find(f, "arg_with_no_name.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message
                e = "argument name is required or the use of the '-l' option"
                self.assertTrue(str.find(message, e) != -1)

                self.__do_the_parse(f, ("-l",))
            elif str.find(f, "empty_interface.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f, ("-b/org/freedesktop/bob",))
                    print(file_report_format.format(f))

                message = cm.exception.message
                e = "Incompletely specified interface"
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "empty_nested_node.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f, ("-b/org/freedesktop/fred",))
                    print(file_report_format.format(f))

                message = cm.exception.message
                e = "Child interfaces and/or nodes expected."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "empty_node.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message
                e = "Child interfaces and/or nodes expected."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "invalid_access_value.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message
                e = "is invalid. It must be 'read', 'write' or 'readwrite'."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "interface_with_only_annotation.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message
                e = "Incompletely specified interface"
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "excessive_arg_type_length.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message

                e = "Overlength signature"
                self.assertTrue(str.find(message, e) != -1)
                e = "It is 256 characters long. The max is 255."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "invalid_arg_type.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message
                e = "'c' is an invalid AllJoyn data type in 'c'."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "invalid_nested_class_collision.xml") != -1 or\
                 str.find(f, "invalid_same_level_class_collision.xml") != -1 or\
                 str.find(f, "invalid_deep_nested_class_collision.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message
                e = "has multiple definitions with different signatures."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "invalid_multiple_root_nodes.xml") != -1:
                with self.assertRaises(parseajxml.ParseException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message

                e = "Exception parsing"
                self.assertTrue(str.find(message, e) != -1)
                e = "junk after document element:"
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "method_same_arg_names.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message

                e = "Duplicate argument name"
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "nested_node_with_no_name.xml") != -1 or\
                 str.find(f, "invalid_nested_noname.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f, ("-b/Root",))
                    print(file_report_format.format(f))

                message = cm.exception.message
                e = "Attribute 'name' required for <node>."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "invalid_nested_objpath.xml") != -1 or\
                 str.find(f, "nested_node.xml") != -1 or\
                 str.find(f, "valid_sample_1.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message

                e = "Nested nodes cannot specify object paths."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "invalid_nested_same_name.xml") != -1 or\
                 str.find(f, "invalid_node_collision.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message
                e = "Duplicate node name "
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "invalid_node_no_path.xml") != -1 or\
                 str.find(f, "node_name_not_specified.xml") != -1 or\
                 str.find(f, "org.ayatana.indicator.session.xml") != -1 or\
                 str.find(f, "org.freedesktop.hal.xml") != -1 or\
                 str.find(f, "org.freedesktop.modemmanager.xml") != -1 or\
                 str.find(f, "org.gnome.bluetooth.applet.xml") != -1 or\
                 str.find(f, "org.gnome.nautilus.xml") != -1 or\
                 str.find(f, "test_org_gnome_bluetooth.xml") != -1:
                with self.assertRaises(parseajxml.ParseException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message

                e = "Bus object path not specified in XML or on command line."
                self.assertTrue(str.find(message, e) != -1)

                # Make sure it does work if the object path IS specified.
                # Some files require lax naming too.
                if str.find(f, "modemmanager") != -1 or\
                   str.find(f, "applet") != -1:
                    self.__do_the_parse(f, ("-b/Root", "-l"))
                else:
                    self.__do_the_parse(f, ("-b/Root",))
            elif str.find(f, "method_arg_with_dir_attr.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message

                e = "Argument direction 'bob' is invalid."
                self.assertTrue(str.find(message, e) != -1)
                e = "It must be 'in' or 'out'."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "method_multidimensional_array.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message

                e = "code generator does not support multidimensional arrays."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "signal_arg_with_dir_attr.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message

                e = "Signal arguments must have a direction of 'out'."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "node_name_ends_with_slash.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message

                e = "Bus object names must not end in a '/'."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "node_name_ends_with_slash.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message

                e = "Bus object names must not end in a '/'."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "node_objpath_not_specified.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message

                e = "Bus object names require '/' as the first character."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "annotation_missing_IsSecure_Value.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message

                e = "Annotation 'org.alljoyn.Bus.Item.IsSecure' is required"
                self.assertTrue(str.find(message, e) != -1)
                e = "to have an attribute of 'value'."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "annotation_missing_NoReply_Value.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message

                e = "Annotation 'org.freedesktop.DBus.Method.NoReply' is"
                self.assertTrue(str.find(message, e) != -1)
                e = " required to have an attribute of 'value'."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "annotation_missing_VariantTypes_Value.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message

                e = "Annotation 'org.alljoyn.Bus.Arg.VariantTypes' is"
                self.assertTrue(str.find(message, e) != -1)
                e = " required to have an attribute of 'value'."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "annotation_bad_NoReply_Value.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message

                e = "Unexpected annotation value 'False' for"
                self.assertTrue(str.find(message, e) != -1)
                e = " org.freedesktop.DBus.Method.NoReply."
                self.assertTrue(str.find(message, e) != -1)
                e = "Expected values are 'true' and 'false'."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "annotation_bad_IsSecure_Value.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message

                e = "Unexpected annotation value 'True' for"
                self.assertTrue(str.find(message, e) != -1)
                e = " org.alljoyn.Bus.Item.IsSecure."
                self.assertTrue(str.find(message, e) != -1)
                e = "Expected values are 'true' and 'false'."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "annotation_bad_VariantTypes_Value.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message

                e = "'B' is an invalid AllJoyn data type in 'B'."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "annotation_valid.xml") != -1:
                service = self.__do_the_parse(f)

                # Check on the default cases.
                i_default = service.get_interface("example.InterfaceDefault")
                explain_ns_interface = "Secure interface NOT expected."
                self.assertFalse(i_default.is_secure, explain_ns_interface)

                p_default = i_default.get_property("PropertyDefault")
                explain_ns_property = "Secure property NOT expected."
                self.assertFalse(p_default.is_secure, explain_ns_property)
                self.assertTrue(p_default.variant_type is None)

                m_default = i_default.get_method("MethodDefault")
                explain_ns_method = "Secure method NOT expected."
                self.assertFalse(m_default.is_secure, explain_ns_method)

                a_default = m_default.get_arg("argv")
                self.assertTrue(a_default is not None, "Expected an arg.")
                self.assertTrue(a_default.variant_type is None)

                s_default = i_default.get_signal("SignalDefault")
                explain_ns_signal = "Secure signal NOT expected."
                self.assertFalse(s_default.is_secure, explain_ns_signal)

                a_default = s_default.get_arg("arg")
                explain_expect_arg = "Expected an arg."
                self.assertTrue(a_default is not None, explain_expect_arg)
                self.assertTrue(a_default.variant_type is None)

                # Check on the secure cases.
                i_secure = service.get_interface("example.InterfaceSecure")
                explain_s_interface = "Secure interface expected."
                self.assertTrue(i_secure.is_secure, explain_s_interface)

                p_secure = i_secure.get_property("PropertySecure")
                explain_s_property = "Secure property expected."
                self.assertTrue(p_secure.is_secure, explain_s_property)
                variant_type = "n"
                self.assertEqual(p_secure.variant_type, variant_type)

                explain_s_method = "Secure method expected."
                m_secure_reply = i_secure.get_method("MethodReply")
                self.assertTrue(m_secure_reply.is_secure, explain_s_method)

                explain_r_method = "No reply method NOT expected."
                self.assertFalse(m_secure_reply.no_reply, explain_r_method)

                m_secure_no_reply = i_secure.get_method("MethodNoReply")
                self.assertTrue(m_secure_no_reply.is_secure, explain_s_method)

                a_secure = m_secure_no_reply.get_arg("argv")
                self.assertTrue(a_secure is not None, explain_expect_arg)
                self.assertEqual(a_secure.variant_type, variant_type)

                explain_nr_method = "No reply method expected."
                self.assertTrue(m_secure_no_reply.no_reply, explain_nr_method)

                s_secure = i_secure.get_signal("SignalSecure")
                explain_s_signal = "Secure signal expected."
                self.assertTrue(s_secure.is_secure, explain_s_signal)

                a_secure = s_secure.get_arg("arg")
                self.assertTrue(a_secure is not None, explain_expect_arg)
                self.assertEqual(a_secure.variant_type, variant_type)

                # Check on the explicitly not secure cases.
                i_insecure = service.get_interface("example.InterfaceNotSecure")
                self.assertFalse(i_insecure.is_secure, explain_ns_interface)

                p_insecure = i_insecure.get_property("PropertyNotSecure")
                self.assertFalse(p_insecure.is_secure, explain_ns_property)

                m_insecure = i_insecure.get_method("MethodReply")
                self.assertFalse(m_insecure.is_secure, explain_ns_interface)
                self.assertFalse(m_insecure.no_reply, explain_nr_method)

                a_insecure = m_insecure.get_arg("arg")
                self.assertTrue(a_insecure is not None, explain_expect_arg)
                self.assertTrue(a_insecure.variant_type is None)

                s_insecure = i_insecure.get_signal("SignalNotSecure")
                self.assertFalse(s_default.is_secure, explain_ns_signal)

                a_insecure = s_insecure.get_arg("arg")
                self.assertTrue(a_insecure is not None, explain_expect_arg)
                self.assertTrue(a_insecure.variant_type is None)
            else:
                self.__do_the_parse(f)
        return

    def test_b_tests(self):
        """Tests files in xml_testcases/b_tests directory."""
        files = self.__directory_xml_files("../xml_testcases/b_tests")
        file_report_format = "Parsing '{0}'."

        for f in files:
            if str.find(f, "instance_name_base.xml") != -1:
                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message

                e = "Bus object names require '/' as the first character."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "iop_base_node.xml") != -1:
                with self.assertRaises(parseajxml.ParseException) as cm:
                    self.__do_the_parse(f, ("-b/com/example", ))
                    print(file_report_format.format(f))

                message = cm.exception.message

                e = "Command line object path: '/com/example'"
                self.assertTrue(str.find(message, e) != -1)

                e = "does not match Xml object path: '/com/example/BaseOne'."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "sop_base_node.xml") != -1 or\
                 str.find(f, "sop_base_node_with_child.xml") != -1:
                with self.assertRaises(parseajxml.ParseException) as cm:
                    self.__do_the_parse(f, ("-b/com/example", ))
                    print(file_report_format.format(f))

                message = cm.exception.message

                e = "Command line object path: '/com/example'"
                self.assertTrue(str.find(message, e) != -1)

                e = "does not match Xml object path: '/com/example/'."
                self.assertTrue(str.find(message, e) != -1)

                with self.assertRaises(validate.ValidateException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message

                e = "'/com/example/' is an invalid bus object name."
                self.assertTrue(str.find(message, e) != -1)

                e = "Bus object names must not end in a '/'."
                self.assertTrue(str.find(message, e) != -1)
            elif str.find(f, "unnamed_base.xml") != -1 or\
                 str.find(f, "unnamed_base_with_child.xml") != -1:
                with self.assertRaises(parseajxml.ParseException) as cm:
                    self.__do_the_parse(f)
                    print(file_report_format.format(f))

                message = cm.exception.message

                e = "Bus object path not specified in XML or on command line."
                self.assertTrue(str.find(message, e) != -1)

                self.__do_the_parse(f, ("-b/com/example",))
            else:
                self.__do_the_parse(f)
        return

    def test_classes_and_instances(self):
        """Tests files in classes_and_instances directory."""
        files = self.__directory_xml_files("classes_and_instances")

        for f in files:
            self.__do_the_parse(f)

        return

    def test_unnamed(self):
        """Tests files in unnamed directory."""
        files = self.__directory_xml_files("unnamed")

        for f in files:
            self.__do_the_parse(f, ("-b/com/example",))

        return

    def test_arrays(self):
        """Tests files in arrays directory."""
        files = self.__directory_xml_files("arrays")

        for f in files:
            self.__do_the_parse(f)

        return

    def test_structs(self):
        """Tests files in structs directory."""
        files = self.__directory_xml_files("structs")

        for f in files:
            self.__do_the_parse(f)

        return

    def test_methods(self):
        """Tests files in methods directory."""
        files = self.__directory_xml_files("methods")

        for f in files:
            self.__do_the_parse(f)

        return

    def test_properties(self):
        """Tests files in properties directory."""
        files = self.__directory_xml_files("properties")

        for f in files:
            self.__do_the_parse(f)
        return

    def test_samples(self):
        """Tests files in samples directory."""
        files = self.__directory_xml_files("samples")

        for f in files:
            self.__do_the_parse(f)

        return

    def test_signals(self):
        """Tests files in signals directory."""
        files = self.__directory_xml_files("signals")

        for f in files:
            self.__do_the_parse(f)

        return

    def __directory_xml_files(self, path):
        """Traverses the entire directory path returns all XML files."""
        return_value = []

        for f in os.listdir(path):
            if fnmatch.fnmatch(f, "*.xml"):
                full_filename = "{0}/{1}".format(path, f)
                return_value.append(full_filename)

        return return_value

    def __valididate_parse_result(self,
                                  full_filename,
                                  additional_args = None):
        """Parse the given file and test for errors."""

        # All invalid XML has "invalid" in the filename. Test for that then
        # check to see if the parse result was as expected.
        if str.find(str.lower(full_filename), "invalid") != -1:
            exceptions = (parseajxml.ParseException, validate.ValidateException)
            with self.assertRaises(exceptions) as cm:
                self.__do_the_parse(full_filename, additional_args)

            # print(cm.exception.message)
        else:
            self.__do_the_parse(full_filename, additional_args)
        return

    def __do_the_parse(self,
                       filename,
                       additional_args = None):
        """Do the actual call to parse the file and do sanity checks."""
        global file_dictionary, interface_count

        if filename != "DoesNotExist.foo" and filename not in file_dictionary:
            file_dictionary[filename] = 0

        # print("\n####### {0} #######".format(filename))

        p = parseajxml.ParseAjXml(filename)
        node = p.tree.getroot()

        args = ["parse_test.py", "-ttc", "-wTest.Foo"]
        args.append(filename)

        if additional_args is not None:
            for a in additional_args:
                args.append(a)

        sys.argv = args
        c = config.Config()
        service = p.parse(c.command_line)
        interface_count += len(service.interfaces)

        # print(service)

        interfaces = self.__get_interfaces(node)
        for key, i in interfaces.items():
            i_name = i.get("name")
            service_interface = service.get_interface(key)

            if i_name == "org.freedesktop.DBus.Introspectable":
                mess_format = "From '{0}'.\nInterface '{1}' should be ignored."
                message = mess_format.format(filename, i_name)
                self.assertIsNone(service_interface, message)
            else:
                mess_format = "From '{0}'.\nExpected to find interface '{1}'."
                message = mess_format.format(filename, i_name)
                self.assertIsNotNone(service_interface, message)
                self.__compare_interfaces(i, service_interface, filename)

                # basic sanity check:
                #    all structures should have a signature starting with '('
                #    all dictionaries should have a signature starting with '{'
                # [checks for issue ASADT-3]
                for struct in service_interface.structures:
                    mess_format = "Container extraction gave malformed struct signature {0} in {1}."
                    message = mess_format.format(struct, filename)
                    self.assertTrue(struct[0] == "(" and struct[-1] == ")", message)
                for dict in service_interface.dictionaries:
                    mess_format = "Container extraction gave malformed dict signature {0} in {1}."
                    message = mess_format.format(dict, filename)
                    self.assertTrue(dict[0] == "{" and dict[-1] == "}", message)


        validate.alljoyn_data(service, "tc")

        return service

    def __get_interfaces(self, root):
        """Get the xml for all the interfaces in the xml file."""
        interfaces = {}
        for i in root.iter("interface"):
            i_name = i.get("name")
            interfaces[i_name] = i

        return interfaces

    def __compare_interfaces(self, xml, interface, filename):
        """Compare all the interface children in the xml to the AJ interface.

        assert if the names don't match."""

        children = list(xml)
        for c in children:
            name = c.get("name")
            m_format = "Expected interface '{0}' in '{1}' to have {2} '{3}'."
            mess = m_format.format(interface.interface_full_name,
                                   filename,
                                   c.tag,
                                   name)
            # print(mess)

            if c.tag == "signal":
                s = interface.get_signal(name)
                self.assertIsNotNone(s, mess)
            elif c.tag == "method":
                m = interface.get_method(name)
                self.assertIsNotNone(m, mess)
            elif c.tag == "property":
                p = interface.get_property(name)
                self.assertIsNotNone(p, mess)

        return


if __name__ == '__main__':
    unittest.main()

