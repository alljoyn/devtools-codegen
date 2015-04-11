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

import unittest
import fnmatch
import os
import sys
import string
import tempfile
import shutil
import subprocess
import platform

import AllJoynCodeGen.ajobject as ajobject
import AllJoynCodeGen.interface as interface
import AllJoynCodeGen.config as config
import AllJoynCodeGen.parseajxml as parseajxml
import AllJoynCodeGen.validate as validate
import AllJoynCodeGen.CheetahCompileExcept as cce

try:
    # All modules that contain Cheetah templates must be placed within this try.
    import AllJoynCodeGen.tl.GenTL as tl
except cce.CheetahCompilationException:
    print("Unable to import compiled template modules.")
    print("Run ajcodegen-compile.py and try again.")
    sys.exit(1)

thin_client_home_environment_variable = "ALLJOYN_THINLIBRARY_HOME"
thin_client_home_environment_variable_warning = False

class ThinLibrary(unittest.TestCase):
    """Tests the Thin Library code generation components."""

    def test_interface_set_name(self):
        """Tests getting an interface set name from an AJ object."""

        r_name = "root"
        r = ajobject.AllJoynObject(r_name)

        set_name = tl.get_interface_set_name(r)
        self.assertTrue(str.find(set_name, r_name) != -1)
        self.assertTrue(str.find(set_name, '/') == -1)
        self.assertTrue(str.find(set_name, "IfaceSet") != -1)

        c_name = "child"
        c = ajobject.AllJoynObject(c_name, r)

        set_name = tl.get_interface_set_name(c)
        self.assertTrue(str.find(set_name, r_name) != -1)
        self.assertTrue(str.find(set_name, c_name) != -1)
        self.assertTrue(str.find(set_name, '/') == -1)
        self.assertTrue(str.find(set_name, "IfaceSet") != -1)

        g_name = "grandchild"
        g = ajobject.AllJoynObject(g_name, c)

        set_name = tl.get_interface_set_name(g)
        self.assertTrue(str.find(set_name, r_name) != -1)
        self.assertTrue(str.find(set_name, c_name) != -1)
        self.assertTrue(str.find(set_name, g_name) != -1)
        self.assertTrue(str.find(set_name, '/') == -1)
        self.assertTrue(str.find(set_name, "IfaceSet") != -1)

        return

    def test_interface_coded_name(self):
        """Tests getting an interface name coded such it can be compiled.

        The interface name must not be a 'c' key word or have punctuation
        characters other than '_' in it."""

        i = interface.Interface()
        i.set_name("Testing_3.AllSeen2_.MyInterface0")

        coded_name = tl.get_interface_coded_name(i)

        for c in string.punctuation:
            if c == '_':
                continue

            self.assertTrue(string.find(coded_name, c) == -1)

        return

    def test_classes_and_instances(self):
        """Tests files in classes_and_instances directory."""
        files = self.__directory_xml_files("classes_and_instances")

        for f in files:
            self.__generate_code(f, False)
            self.__generate_code(f, True)

        return

    def test_unnamed(self):
        """Tests files in unnamed directory."""
        files = self.__directory_xml_files("unnamed")

        for f in files:
            self.__generate_code(f, False, "/root")
            self.__generate_code(f, True, "/root")

        return

    def test_structs(self):
        """Tests files in structs directory."""
        files = self.__directory_xml_files("structs")

        for f in files:
            # TODO: Fix the code generator so this test passes.
            if str.find(f, "Complex.xml") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            self.__generate_code(f, False)
            self.__generate_code(f, True)

        return

    def test_arrays(self):
        """Tests files in arrays directory."""
        files = self.__directory_xml_files("arrays")

        for f in files:
            self.__generate_code(f, False)
            self.__generate_code(f, True)

        return

    def test_methods(self):
        """Tests files in methods directory."""
        files = self.__directory_xml_files("methods")

        for f in files:
            # TODO: Fix the code generator so this test passes.
            if str.find(f, "method_array_struct_array.xml") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            # TODO: Fix the code generator so this test passes.
            if str.find(f, "method_array_struct_array_struct.xml") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            # TODO: Fix the code generator so this test passes.
            if str.find(f, "method_array_struct_dictionary.xml") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            # TODO: Fix the code generator so this test passes.
            if str.find(f, "method_dictionary_of_arrays.xml") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            # TODO: Fix the code generator so this test passes.
            if str.find(f, "method_struct_contains_array.xml") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            # TODO: Fix the code generator so this test passes.
            if str.find(f, "method_struct_contains_array_of_struct.xml") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            # TODO: Fix the code generator so this test passes.
            if str.find(f, "method_struct_contains_dictionary.xml") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            # TODO: Fix the code generator so this test passes.
            if str.find(f, "method_struct_contains_variant.xml") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            # TODO: Fix the code generator so this test passes.
            if str.find(f, "method_variant_array.xml") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            # TODO: Fix the code generator so this test passes.
            if str.find(f, "method_array_struct_struct.xml") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            # TODO: Fix the code generator so this test passes.
            if str.find(f, "method_struct_contains_struct.xml") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            # TODO: Fix the code generator so this test passes.
            if str.find(f, "method_struct_contains_two_structs.xml") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            self.__generate_code(f, False)
            self.__generate_code(f, True)

        return

    def test_properties(self):
        """Tests files in properties directory."""
        files = self.__directory_xml_files("properties")

        for f in files:
            self.__generate_code(f, False)
            self.__generate_code(f, True)

        return

    def test_samples(self):
        """Tests files in samples directory."""
        files = self.__directory_xml_files("samples")

        for f in files:
            self.__generate_code(f, False)
            self.__generate_code(f, True)

        return

    def test_signals(self):
        """Tests files in signals directory."""
        files = self.__directory_xml_files("signals")

        for f in files:
            # TODO: Fix the code generator so this test passes.
            if str.find(f, "signal_variant_array.xml") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            self.__generate_code(f, False)
            self.__generate_code(f, True)

        return

    def __directory_xml_files(self, path):
        """Traverses the entire directory path returns all XML files."""
        return_value = []

        for f in os.listdir(path):
            if fnmatch.fnmatch(f, "*.xml"):
                full_filename = os.path.join(path, f)
                return_value.append(full_filename)

        return return_value

    def __generate_code(self, filename, runnable, object_path = None):
        print("Runnable: {0}, File: {1}".format(runnable, filename))
        global thin_client_home_environment_variable_warning

        if thin_client_home_environment_variable not in os.environ:

            if not thin_client_home_environment_variable_warning:

                print("'{0}' environment variable is not set.".format(thin_client_home_environment_variable))
                print("No compilation attempted.")
                thin_client_home_environment_variable_warning = True

            pathname = tempfile.mkdtemp(".CodGen")
        else:
            tl_home = os.environ[thin_client_home_environment_variable]
            pathname = os.path.join(tl_home, "codegen")

            # Check to see if the path exists. If it does then empty it.
            # If it doesn't exist then create it.
            if os.path.isdir(pathname):
                self.__empty_directory(pathname)
            else:
                os.makedirs(pathname)

        try:
            output_path_arg = "-p{0}".format(pathname)
            args = ["arg0", output_path_arg, "-ttl", "-wTest.Foo", filename]
            if runnable:
                args.append("-R")

            if object_path is not None:
                args.append("-b{0}".format(object_path))

            sys.argv = args

            c = config.Config()
            c.register_target('tl', tl.hooks())
            c.parse()

            parser = parseajxml.ParseAjXml(c.command_line.xml_input_file)
            service = parser.parse(c.command_line)

            target = c.command_line.target_language
            self.assertEqual(target, "tl")

            validate.alljoyn_data(service, target)
            c.target_hook('generate_code')(c.command_line, service)

            self.__verify_all_file_generated(parser.tree.getroot(), pathname,
                                            len(service.interfaces))
            if not thin_client_home_environment_variable_warning:
                self.__compile_code()
        finally:
            if thin_client_home_environment_variable_warning:
                shutil.rmtree(pathname)

        return

    # These are the files which are always present after generating code.
    files_always_present = (
                            "Client.h",
                            "ClientDoWork.c",
                            "ClientMain.c",
                            "CommonClientService.c",
                            "CommonClientService.h",
                            "ReadMe.txt",
                            "SConscript",
                            "Service.h",
                            "ServiceDoWork.c",
                            "ServiceMain.c",
                           )

    # These are the format strings to create the various files from
    # an interface name.
    files_interface_specific_formats = (
                                        "Client{0}.c",
                                        "Client{0}.h",
                                        "Service{0}.c",
                                        "Service{0}.h",
                                       )

    def __verify_all_file_generated(self, xml, pathname, number_of_interfaces):
        for f in self.files_always_present:
            full = os.path.join(pathname, f)
            self.assertTrue(os.path.getsize(full) > 260)

        interface_names = self.__get_interface_names(xml)

        for name in interface_names:
            for format_str in self.files_interface_specific_formats:
                f = format_str.format(name)
                full = os.path.join(pathname, f)
                self.assertTrue(os.path.getsize(full) > 350)

        expected_number_of_files = len(self.files_always_present)
        expected_number_of_files += len(interface_names) *\
                                    len(self.files_interface_specific_formats)

        actual_number_of_files = len(os.listdir(pathname))
        self.assertEqual(expected_number_of_files, actual_number_of_files)
        return

    # Ignore the built in interfaces.
    ignore_interfaces = {"org.freedesktop.DBus.Peer",
                         "org.freedesktop.DBus.Introspectable",
                         "org.freedesktop.DBus.Properties",
                         "org.freedesktop.DBus.ObjectManager"}

    def __get_interface_names(self, xml):
        """Get the xml for all the interfaces in the xml file."""
        names = []
        for i in xml.iter("interface"):
            # Don't add in an interface name that already exists.
            n = i.get("name")
            if (not n in names) and (n not in self.ignore_interfaces):
                names.append(n)

        return names

    def __empty_directory(self, path):
        for f in os.listdir(path):
            complete_filename = os.path.join(path, f)
            os.remove(complete_filename)
        return

    def __compile_code(self):
        cwd = os.getcwd()
        system_type = platform.system()

        if system_type == "Linux" or system_type == "Darwin":
            scons_command = "scons"
        elif system_type == "Windows":
            scons_command = "scons.bat"
        else:
            print("Unrecognized system type '{0}'".format(system_type))
            return

        try:
            thin_client_home = os.environ[thin_client_home_environment_variable]
            os.chdir(thin_client_home)
            subprocess.check_output([scons_command, "WS=detail"])
        finally:
            os.chdir(cwd)

        return
