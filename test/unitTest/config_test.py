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

import unittest
import fnmatch
import os
import sys

import AllJoynCodeGen.config as config
import util

class TestConfig(unittest.TestCase):
    """Tests the Config class."""
    def test_no_args(self):
        """Test what happens when no arguments are given."""

        sys.argv = ["DummyArg0"]

        with self.assertRaises(SystemExit) as cm:
            c = util.get_config()

        self.assertTrue(sys.exc_info() is not None)
        return

    def test_object_path(self):
        """Test the object path (-b) flag."""
        args = ["arg0", "-b/TestFoo", "-ttl", "-wTest.Foo", "file.xml"]
        sys.argv = args
        c = util.get_config()
        self.assertTrue(c.command_line.xml_input_file == "file.xml")
        self.assertTrue(c.command_line.target_language == "tl")
        self.assertTrue(c.command_line.object_path == "/TestFoo")

        args = ["arg0", "-b", "/TestFoo", "-wTest.Foo", "-ttl", "file.xml"]
        sys.argv = args
        c = util.get_config()
        self.assertTrue(c.command_line.object_path == "/TestFoo")
        return

    def test_client_only(self):
        """Test the client only (-c) flag."""
        c = self.__one_arg_test("-b/TestFoo")
        self.assertFalse(c.command_line.client_only)

        c = self.__one_arg_test("-c")
        self.assertTrue(c.command_line.client_only)
        return

    def test_lax_naming(self):
        """Test the lax naming (-l) flag."""
        c = self.__one_arg_test("-b/TestFoo")
        self.assertFalse(c.command_line.lax_naming)

        c = self.__one_arg_test("-l")
        self.assertTrue(c.command_line.lax_naming)
        return

    def test_overwrite(self):
        """Test the overwrite (-o) flag."""
        c = self.__one_arg_test("-b/TestFoo")
        self.assertFalse(c.command_line.overwrite)

        c = self.__one_arg_test("-o")
        self.assertTrue(c.command_line.overwrite)
        return

    def test_runnable(self):
        """Test the runnable (-R) flag."""
        c = self.__one_arg_test("-b/TestFoo")
        self.assertFalse(c.command_line.runnable)

        c = self.__one_arg_test("-R")
        self.assertTrue(c.command_line.runnable)
        return

    def test_target_language(self):
        """Test the target language (-t) flag."""
        args = ["arg0", "-ttl", "-wTest.foo", "file.xml"]
        sys.argv = args

        c = util.get_config()
        self.assertTrue(c.command_line.xml_input_file == "file.xml")
        self.assertTrue(c.command_line.target_language == "tl")

        args[1] = "-tFoo"

        try:
            c.parse()
            self.assertTrue(False,
                    "Invalid target language should result in a SystemExit.")
        except SystemExit:
            self.assertTrue(sys.exc_info() is not None)
        return

    def test_well_known_name_optional(self):
        """Test the well known name flag."""
        args = ["arg0", "-ttl", "file.xml"]
        sys.argv = args
        # non-optional for 'tl'
        self.assertRaises(config.ConfigException, util.get_config)
        # optional for 'ddcpp'
        args[1] = "-tddcpp"
        c = util.get_config()
        self.assertTrue(c.command_line.well_known_name == None)
        return

    def test_well_known_name(self):
        """Test the well known name flag."""
        args = ["arg0", "-ttl", "-wTest.My.Foo", "file.xml"]
        sys.argv = args
        c = util.get_config()
        self.assertTrue(c.command_line.well_known_name == "Test.My.Foo")
        return

    def test_xml(self):
        """Test the -x (--xml) flag."""
        c = self.__one_arg_test("-b/TestFoo")
        self.assertFalse(c.command_line.xml)

        c = self.__one_arg_test("-x")
        self.assertTrue(c.command_line.xml)
        return

    def __one_arg_test(self, arg_to_test):
        """Test this one argument when creating a configuration."""
        args = ["arg0", arg_to_test, "-ttl", "-wTest.Foo", "file.xml"]
        sys.argv = args
        c = util.get_config()
        return c

if __name__ == '__main__':
    unittest.main()


