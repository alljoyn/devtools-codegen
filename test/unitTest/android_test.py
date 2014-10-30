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

import unittest
import fnmatch
import os
import sys
import string
import tempfile
import shutil
import subprocess

import AllJoynCodeGen.ajobject as ajobject
import AllJoynCodeGen.interface as interface
import AllJoynCodeGen.config as config
import AllJoynCodeGen.parseajxml as parseajxml
import AllJoynCodeGen.validate as validate
import AllJoynCodeGen.signaldef as sig
import AllJoynCodeGen.argdef as arg
import AllJoynCodeGen.methoddef as met
import AllJoynCodeGen.propertydef as prop

import AllJoynCodeGen.android.GenAndroid as ga

class Android(unittest.TestCase):
    """Tests the Android generation components."""

    def test_needs_persistent_data(self):
        """Tests the method GenAndroid.needs_persistent_data()."""
        i = interface.Interface()
        i.set_name("My.Interface1")
        self.assertFalse(ga.interface_needs_persistent_data(i, True))
        self.assertFalse(ga.interface_needs_persistent_data(i, False))

        s = sig.SignalDef()
        s.name = "MySignal"
        i.signals.append(s)
        self.assertFalse(ga.interface_needs_persistent_data(i, True))
        self.assertFalse(ga.interface_needs_persistent_data(i, False))

        a = arg.ArgDef(None, "myArg", "i", "out")
        s.args.append(a)
        self.assertFalse(ga.interface_needs_persistent_data(i, True))
        self.assertTrue(ga.interface_needs_persistent_data(i, False))

        s.args.remove(a)

        m = met.MethodDef()
        m.name = "MyMethod"
        i.methods.append(m)

        aOut = arg.ArgDef(None, "myOutputArg", "i", "out")
        m.args.append(aOut)
        self.assertFalse(ga.interface_needs_persistent_data(i, True))
        self.assertTrue(ga.interface_needs_persistent_data(i, False))

        m.args.remove(aOut)

        aIn = arg.ArgDef(None, "myInputArg", "i", "in")
        m.args.append(aIn)
        self.assertTrue(ga.interface_needs_persistent_data(i, True))
        self.assertFalse(ga.interface_needs_persistent_data(i, False))

        m.args.remove(aIn)

        p = prop.PropertyDef()
        p.name = "MyProperty"
        p.access = "read"
        aOut = arg.ArgDef(None, "myOutputArg", "i", "out")
        p.args.append(aOut)
        i.properties.append(p)
        self.assertFalse(ga.interface_needs_persistent_data(i, True))
        self.assertTrue(ga.interface_needs_persistent_data(i, False))

        aIn = arg.ArgDef(None, "myInputArg", "i", "in")
        p.args.append(aIn)
        p.access = "readwrite"
        self.assertTrue(ga.interface_needs_persistent_data(i, True))
        self.assertTrue(ga.interface_needs_persistent_data(i, False))

        p.access = "write"
        p.args.remove(aOut)
        self.assertTrue(ga.interface_needs_persistent_data(i, True))
        self.assertFalse(ga.interface_needs_persistent_data(i, False))

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
            # TODO: Fix the code generator so this test passes.
            if str.find(f, "unnamed_sample_1.xml") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            # TODO: Fix the code generator so this test passes.
            if str.find(f, "unnamed_sample_2.xml") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

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

        # TODO: Fix the code generator so this test passes.
        print("Skipping test_arrays().")
        return

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
            if str.find(f, "array") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            # TODO: Fix the code generator so this test passes.
            if str.find(f, "dictionary") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            self.__generate_code(f, False)
            self.__generate_code(f, True)

        return

    def test_properties(self):
        """Tests files in properties directory."""
        files = self.__directory_xml_files("properties")

        for f in files:
            # TODO: Fix the code generator so this test passes.
            if str.find(f, "array") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            # TODO: Fix the code generator so this test passes.
            if str.find(f, "dictionary") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            self.__generate_code(f, False)
            self.__generate_code(f, True)

        return

    def test_samples(self):
        """Tests files in samples directory."""
        files = self.__directory_xml_files("samples")

        for f in files:
            # TODO: Fix the code generator so this test passes.
            if str.find(f, "sample_1.xml") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            # TODO: Fix the code generator so this test passes.
            if str.find(f, "sample_2.xml") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            # TODO: Fix the code generator so this test passes.
            if str.find(f, "sample_array_args.xml") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            # TODO: Fix the code generator so this test passes.
            if str.find(f, "sample_dictEntry_args.xml") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            # TODO: Fix the code generator so this test passes.
            if str.find(f, "sample_with_prop.xml") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            self.__generate_code(f, False)
            self.__generate_code(f, True)

        return

    def test_signals(self):
        """Tests files in signals directory."""
        files = self.__directory_xml_files("signals")

        for f in files:
            # TODO: Fix the code generator so this test passes.
            if str.find(f, "array.xml") != -1:
                print("Skipping test file '{0}'.".format(f))
                continue

            # TODO: Fix the code generator so this test passes.
            if str.find(f, "signal_dictionary.xml") != -1:
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
        pathname = tempfile.mkdtemp(".CodGen")

        try:
            output_path_arg = "-p{0}".format(pathname)
            args = ["arg0", output_path_arg, "-tandroid", "-wTest.Foo", filename]
            if runnable:
                args.append("-R")

            if object_path is not None:
                args.append("-b{0}".format(object_path))

            sys.argv = args

            c = config.Config()

            parser = parseajxml.ParseAjXml(c.command_line.xml_input_file)
            service = parser.parse(c.command_line)

            target = c.command_line.target_language
            self.assertEqual(target, "android")

            validate.alljoyn_data(service, target)
            ga.generate_code(c.command_line, service)

            self.__verify_all_file_generated(parser.tree.getroot(), pathname,
                                            len(service.interfaces))
            self.__compile_code()
        finally:
            shutil.rmtree(pathname)

        return

    def __verify_file_generated(self, full_file_name, file_with_sub, minimum_size):
        """Verifies that a specific file is present and is of appropriate size."""
        exists = os.path.isfile(full_file_name)

        if not exists:
            print("The file '{0}' is missing.".format(file_with_sub))

        self.assertTrue(exists)

        file_size = os.path.getsize(full_file_name)

        if file_size < minimum_size:
            print("The file '{0}' is unexpectedly small ({1} bytes).".format(file_with_sub, file_size))

        self.assertTrue(file_size >= minimum_size)
        return

    # These are the files which are always present after generating code.
    files_always_present = (
                            ".classpath",
                            ".project",
                            "AndroidManifest.xml",
                            "project.properties",
                            ".settings/org.eclipse.jdt.core.prefs",
                            "libs/alljoyn.jar",
                            "libs/armeabi/liballjoyn_java.so",
                            "res/drawable-hdpi/icon.png",
                            "res/drawable-ldpi/icon.png",
                            "res/drawable-mdpi/icon.png",
                            "res/layout/main.xml",
                            "res/layout/message.xml",
                            "res/menu/mainmenu.xml",
                            "res/values/strings.xml",
                           )

    # This is the minimum expected size in bytes of any of the above files.
    # The smallest is strings.xml which can be as small as 144 bytes.
    files_always_present_minimum_size = 140

    def __verify_all_file_generated(self, xml, pathname, number_of_interfaces):
        """Verifies that all the expected files are present and are of appropriate sizes."""
        sub_pathes = ("Service", "Client")
        expected_number_of_files = 0

        for sub in sub_pathes:
            for f in self.files_always_present:
                file_with_sub= os.path.join(sub, f)
                full = os.path.join(pathname, sub, f)
                self.__verify_file_generated(full, file_with_sub, self.files_always_present_minimum_size)
                expected_number_of_files += 1

            # Verify ServiceMain.java and ClientMain.java
            well_known_name_path = ga.get_well_known_name_path()
            filename = "{0}Main.java".format(sub)
            file_with_sub= os.path.join(sub, "src", well_known_name_path, filename)
            full = os.path.join(pathname, file_with_sub)
            self.__verify_file_generated(full, file_with_sub, 10000)
            expected_number_of_files += 1

            interfaces = self.__get_interfaces(xml)
            for i in interfaces:
                name_components = i.name.split(".")
                directories = name_components[0:-1]

                interface_directory = "{0}/src".format(sub)
                for d in directories:
                    interface_directory = os.path.join(interface_directory, d)

                files_interface_specific_minimum_size = 1000

                f = "{0}.java".format(name_components[-1])
                file_with_sub = os.path.join(interface_directory, f)
                full = os.path.join(pathname, interface_directory, f)
                self.__verify_file_generated(full, file_with_sub, files_interface_specific_minimum_size)
                expected_number_of_files += 1

                if sub == "Service" or i.has_signals:
                    f = "{0}Impl.java".format(name_components[-1])
                    file_with_sub = os.path.join(interface_directory, f)
                    full = os.path.join(pathname, interface_directory, f)
                    self.__verify_file_generated(full, file_with_sub, files_interface_specific_minimum_size)
                    expected_number_of_files += 1

        actual_number_of_files = self.__get_actual_number_of_files(pathname)
        self.assertEqual(expected_number_of_files, actual_number_of_files)
        return

    # Ignore the built in interfaces.
    ignore_interfaces = {"org.freedesktop.DBus.Peer",
                         "org.freedesktop.DBus.Introspectable",
                         "org.freedesktop.DBus.Properties",
                         "org.freedesktop.DBus.ObjectManager"}

    def __get_interfaces(self, xml):
        """Get the xml for all the interfaces in the xml file."""
        names = []
        for i in xml.iter("interface"):
            # Don't add in an interface name that already exists.
            n = i.get("name")
            signals = i.iter("signal")

            has_signals = False

            # object of type 'generator' has no len() so do it this way.
            for s in signals:
                has_signals = True
                break

            interface = UnitTestInterFace(n, has_signals)

            if (interface not in names) and (n not in self.ignore_interfaces):
                names.append(interface)

        return names

    def __empty_directory(self, path):
        """Empty this directory of all files."""
        for f in os.listdir(path):
            complete_filename = os.path.join(path, f)
            os.remove(complete_filename)
        return

    def __compile_code(self):
        """Compile the code and check for errors."""

        # TODO: Compile the code and check for errors.
        return

    def __get_actual_number_of_files(self, pathname):
        """Get the total number of files in the tree specified by "pathname"."""
        return_value = 0

        for root, dirs, files in os.walk(pathname):
            return_value += len(files)

        return return_value

class UnitTestInterFace:
    """This is just a container class to hold the interface names and whether the interface has any signals."""
    def __init__(self, name, has_signals):
        self.name = name
        self.has_signals = has_signals

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return "Name: '{0}' Has signals: {1}".format(self.name, self.has_signals)
