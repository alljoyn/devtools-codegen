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
import string
import os
import sys

import AllJoynCodeGen.validate as validate

class TestValidate(unittest.TestCase):
    """Tests the Validate class.

    TODO: Exercise the alljoyn_data() method."""

    def test_bus_object_path(self):
        """Test validation for bus object names."""

        # Valid bus object names
        name = "/"
        validate.bus_object_path(name)

        name = "/test"
        validate.bus_object_path(name)

        name = "/t/f"
        validate.bus_object_path(name)

        name_formats = (
                        "/test/{0}/foo", "/test{0}foo", "/test/{0}foo",
                        "/test{0}/foo", "/test/foo{0}"
                        )

        valid_chars = "{0}{1}_".format(string.digits, string.ascii_letters)

        for c in valid_chars:
            for f in name_formats:
                name = f.format(c)
                validate.bus_object_path(name)

        # Mostly invalid bus object names.
        with self.assertRaises(validate.ValidateException) as cm:
            validate.bus_object_path(None)

        message = cm.exception.message
        self.assertTrue(string.find(message, "Bus object name is required.") != -1)

        name = "test/foo"
        with self.assertRaises(validate.ValidateException) as cm:
            validate.bus_object_path(name)

        message = cm.exception.message
        response = "Bus object names require '/' as the first character."
        self.assertTrue(string.find(message, response) != -1)
        self.assertTrue(string.find(message, name) != -1)

        name = "/test//foo"
        with self.assertRaises(validate.ValidateException) as cm:
            validate.bus_object_path(name)

        message = cm.exception.message
        response = "Zero length elements ('//') are not allowed."
        self.assertTrue(string.find(message, response) != -1)
        self.assertTrue(string.find(message, name) != -1)

        name = "/test/"
        with self.assertRaises(validate.ValidateException) as cm:
            validate.bus_object_path(name)

        message = cm.exception.message
        response = "Bus object names must not end in a '/'."
        self.assertTrue(string.find(message, response) != -1)
        self.assertTrue(string.find(message, name) != -1)

        invalid_chars = "".join([string.punctuation, string.whitespace])

        for c in invalid_chars:
            for f in name_formats:
                name = f.format(c)

                if c == '_':
                    validate.bus_object_path(name)
                elif c != '/':
                    self.__invalid_character_in_bus_object_test(name)

        # Any length greater than 0 is valid but we only test to 500 chars.
        nine = "abcdeghij"
        elems = (
                 nine, nine, nine, nine, nine, nine, nine, nine, nine, nine,
                 nine, nine, nine, nine, nine, nine, nine, nine, nine, nine,
                 nine, nine, nine, nine, nine, nine, nine, nine, nine, nine,
                 nine, nine, nine, nine, nine, nine, nine, nine, nine, nine,
                 nine, nine, nine, nine, nine, nine, nine, nine, nine, nine
                )
        valid_long_name = "/{0}".format("/".join(elems))
        validate.bus_object_path(valid_long_name)
        return

    def test_interface_name(self):
        """Test validation for interface names.

        Interface names not are allowed to have hyphens ('-'). Other than
        that they are the same as well-known names."""
        self.__common_name_test(validate.interface_name)

        # Hyphens, '-', are not allowed in interface names.
        name = "test-.obj"
        with self.assertRaises(validate.ValidateException) as cm:
            validate.interface_name(name)

        message = cm.exception.message
        self.assertTrue(string.find(message, "Hyphens, '-', are not allowed") != -1)
        self.assertTrue(string.find(message, name) != -1)
        return

    def test_well_known_name(self):
        """Test validation for well-known names (aka bus name).

        Well-known names are allowed to have hyphens ('-'). Other than that they
        are the same as interface names."""
        self.__common_name_test(validate.well_known_name)
        name = "test-.obj"
        e = validate.well_known_name(name)
        self.assertTrue(e is None)
        return

    def test_arg_name(self):
        """Test validation for argument names."""
        response = "An argument name is required or the use of the '-l' option."

        with self.assertRaises(validate.ValidateException) as cm:
            validate.arg_name(None)

        message = cm.exception.message
        self.assertTrue(string.find(message, response) != -1)

        with self.assertRaises(validate.ValidateException) as cm:
            validate.arg_name("")

        message = cm.exception.message
        self.assertTrue(string.find(message, response) != -1)

        return

    def test_member_name(self):
        """Test validation for member names."""
        response = "A member name is required."

        with self.assertRaises(validate.ValidateException) as cm:
            validate.member_name(None)

        message = cm.exception.message
        self.assertTrue(string.find(message, response) != -1)

        with self.assertRaises(validate.ValidateException) as cm:
            validate.member_name("")

        message = cm.exception.message
        self.assertTrue(string.find(message, response) != -1)

        response = "has an invalid character"
        name_format = "invalid{0}char"

        for c in string.punctuation:
            name = name_format.format(c)

            if c == '_':
                validate.member_name(name)
            else:
                with self.assertRaises(validate.ValidateException) as cm:
                    validate.member_name(name)

                message = cm.exception.message
                self.assertTrue(string.find(message, response) != -1)
                self.assertTrue(string.find(message, name) != -1)

        name_format = "{0}digit_start"

        for c in string.digits:
            name = name_format.format(c)

            with self.assertRaises(validate.ValidateException) as cm:
                validate.member_name(name)

            message = cm.exception.message
            self.assertTrue(string.find(message, response) != -1)
            self.assertTrue(string.find(message, name) != -1)
        return

    def test_flat_data_signature(self):
        """Test validation for flattened argument signatures."""
        self.__flat_data_signature_empty_tests()
        self.__flat_data_signature_valid_tests()
        self.__flat_data_signature_invalid_char_tests()
        self.__flat_data_signature_paren_tests()
        self.__flat_data_signature_dictionary_tests()
        self.__flat_data_signature_length_tests()
        return

    def test_nonflat_data_signature(self):
        """Test validation for non-flattened argument signatures."""
        self.__data_signature_empty_tests()
        self.__data_signature_valid_tests()
        self.__data_signature_invalid_tests()

    def test_arg_direction(self):
        """Argument directions are only allowed to be 'in' and 'out'."""
        validate.arg_direction("in")
        validate.arg_direction("out")

        self.__arg_direction_invalid_test(None)
        self.__arg_direction_invalid_test("")
        self.__arg_direction_invalid_test(" ")
        self.__arg_direction_invalid_test("i")
        self.__arg_direction_invalid_test("inout")
        self.__arg_direction_invalid_test("outin")
        self.__arg_direction_invalid_test("o")
        self.__arg_direction_invalid_test("In")
        self.__arg_direction_invalid_test("Out")
        self.__arg_direction_invalid_test("IN")
        self.__arg_direction_invalid_test("OUT")
        return

    def test_property_access(self):
        """Test the access values for success and failure."""
        validate.property_access("read")
        validate.property_access("write")
        validate.property_access("readwrite")
        self.__property_access_invalid_test(None)
        self.__property_access_invalid_test("")
        self.__property_access_invalid_test("bob")
        self.__property_access_invalid_test("Read")
        self.__property_access_invalid_test("Write")
        self.__property_access_invalid_test("Readwrite")
        self.__property_access_invalid_test("READ")
        self.__property_access_invalid_test("WRITE")
        self.__property_access_invalid_test("READWRITE")
        return

    def __property_access_invalid_test(self, access):
        """Test to make sure this type of access is flagged as invalid."""
        with self.assertRaises(validate.ValidateException) as cm:
            validate.property_access(access)

        message = cm.exception.message
        response = "Argument access '{0}' is invalid.".format(access)
        self.assertTrue(string.find(message, response) != -1)
        return

    def __arg_direction_invalid_test(self, direction):
        """Test to make sure this direction is flagged as invalid."""
        with self.assertRaises(validate.ValidateException) as cm:
            validate.arg_direction(direction)

        message = cm.exception.message
        response = "Argument direction '{0}' is invalid.".format(direction)
        self.assertTrue(string.find(message, response) != -1)
        return

    def __flat_data_signature_length_tests(self):
        """Signatures may be up to 255 characters long. No more."""
        # Create a signature 255 characters long.
        eight = "bdghiino"
        elems = (
                 "((bins",
                 eight, eight, eight, eight, eight, eight, eight, eight, eight, eight,
                 eight, eight, eight, eight, eight, eight, eight, eight, eight, eight,
                 eight, eight, eight, eight, "sinsb))"
                )
        valid_long_signature = ")(".join(elems)
        validate.flat_data_signature(valid_long_signature)

        # Expand it to 256 characters.
        invalid = string.replace(valid_long_signature, "sinsb)", "sinsbb)")

        with self.assertRaises(validate.ValidateException) as cm:
            validate.flat_data_signature(invalid)

        message = cm.exception.message
        response = "It is 256 characters long. The max is 255."
        self.assertTrue(string.find(message, response) != -1)
        self.assertTrue(string.find(message, invalid) != -1)

        return

    def __flat_data_signature_dictionary_tests(self):
        """Test validation for dictionary argument signatures."""
        with self.assertRaises(validate.ValidateException) as cm:
            validate.flat_data_signature("(a{id}uia{s(inu)in)")

        message = cm.exception.message
        response = "Unbalanced '{' in AllJoyn data signature '(a{id}uia{s(inu)in)'."
        self.assertTrue(string.find(message, response) != -1)

        with self.assertRaises(validate.ValidateException) as cm:
            validate.flat_data_signature("a}ib{")

        message = cm.exception.message
        response = "Unexpected '}' in 'a}ib{'."
        self.assertTrue(string.find(message, response) != -1)

        with self.assertRaises(validate.ValidateException) as cm:
            validate.flat_data_signature("{ib}")

        message = cm.exception.message
        response = "All dictionary signatures must have an 'a' before them."
        self.assertTrue(string.find(message, response) != -1)

        with self.assertRaises(validate.ValidateException) as cm:
            validate.flat_data_signature("u{ib}")

        message = cm.exception.message
        self.assertTrue(string.find(message, response) != -1)

        response = "Dictionaries must have a basic type for a key."
        with self.assertRaises(validate.ValidateException) as cm:
            validate.flat_data_signature("a{(ib)b}")

        message = cm.exception.message
        self.assertTrue(string.find(message, response) != -1)

        with self.assertRaises(validate.ValidateException) as cm:
            validate.flat_data_signature("a{")

        message = cm.exception.message
        self.assertTrue(string.find(message, response) != -1)
        return

    def __flat_data_signature_paren_tests(self):
        """Test for signatures that have paren (structures) in them."""
        with self.assertRaises(validate.ValidateException) as cm:
            validate.flat_data_signature("(ab(stu)hin")

        message = cm.exception.message
        response = "Unbalanced '(' in AllJoyn data signature '(ab(stu)hin'."
        self.assertTrue(string.find(message, response) != -1)

        with self.assertRaises(validate.ValidateException) as cm:
            validate.flat_data_signature(")abc(")

        message = cm.exception.message
        response = "Unexpected ')' in ')abc('."
        self.assertTrue(string.find(message, response) != -1)

        with self.assertRaises(validate.ValidateException) as cm:
            sig = \
            "(i(i(i(i(i(i(i(i(i(i(i(i(i(i(i(i(i(i(i(i(i(i(i(i(i(i(i(i(i(i(i(i("
            validate.flat_data_signature(sig)

        message = cm.exception.message
        response = "Max depth of '(' is 32 and was exceeded in "
        self.assertTrue(string.find(message, response) != -1)

        return

    def __flat_data_signature_invalid_char_tests(self):
        """Test to make sure all invalid characters are caught."""
        valid_chars = ('a', # AllJoyn array container type
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
                       'y', # AllJoyn 8-bit unsigned integer basic type
                       '(', # AllJoyn struct container type
                       ')', # End of AllJoyn struct container type
                       '{', # AllJoyn dictionary or map container type
                       '}'  # End of AllJoyn dictionary or map container type
                      )
        err_format = "'{0}' is an invalid AllJoyn data type in '{1}'."

        for c in string.printable:
            if c in valid_chars:
                continue

            sig = "{0}i".format(c)
            with self.assertRaises(validate.ValidateException) as cm:
                validate.flat_data_signature(sig)

            message = cm.exception.message
            response = err_format.format(c, sig)
            self.assertTrue(string.find(message, response) != -1)
        return

    def __data_signature_invalid_tests(self):
        """Do tests to make sure invalid signatures are caught."""
        invalid_patterns = [
            "[OpenButNotClosed",
            "(i[Mixed]s)",
            "[Multi][Named][Type]",
            "[[Nested]]",
            "[Invalid(In){Between}Brackets]",
            "[Some%Invalid|Characters]",
            "[0InvalidTypeName]"
        ]
        for sig in invalid_patterns:
            with self.assertRaises(validate.ValidateException) as cm:
                validate.data_signature(sig)
        return


    def __data_signature_valid_tests(self):
        """Do tests to make sure valid signatures are accepted."""
        validate.data_signature("ab")
        validate.data_signature("(yxvutsqonihgdb)")
        validate.data_signature("((abd(ghi(no)))qstuvxy)")
        validate.data_signature("a{ib}")
        validate.data_signature("[SomeType]")
        validate.data_signature("a[SomeType]")
        validate.data_signature("aa[SomeType]")
        validate.data_signature("aaa[SomeType]")
        return

    def __flat_data_signature_valid_tests(self):
        """Do tests to make sure valid signatures are accepted."""
        validate.flat_data_signature("ab")
        validate.flat_data_signature("(yxvutsqonihgdb)")
        validate.flat_data_signature("((abd(ghi(no)))qstuvxy)")
        validate.flat_data_signature("a{ib}")
        return

    def __data_signature_empty_tests(self):
        """Do tests to make sure empty signatures are detected."""
        with self.assertRaises(validate.ValidateException) as cm:
            validate.data_signature(None)

        message = cm.exception.message
        response = "'NULL' is an invalid AllJoyn data type."
        self.assertTrue(string.find(message, response) != -1)

        with self.assertRaises(validate.ValidateException) as cm:
            validate.data_signature("")

        message = cm.exception.message
        response = "'NULL' is an invalid AllJoyn data type."
        self.assertTrue(string.find(message, response) != -1)
        return

    def __flat_data_signature_empty_tests(self):
        """Do tests to make sure empty signatures are detected."""
        with self.assertRaises(validate.ValidateException) as cm:
            validate.flat_data_signature(None)

        message = cm.exception.message
        response = "'NULL' is an invalid AllJoyn data type."
        self.assertTrue(string.find(message, response) != -1)

        with self.assertRaises(validate.ValidateException) as cm:
            validate.flat_data_signature("")

        message = cm.exception.message
        response = "'NULL' is an invalid AllJoyn data type."
        self.assertTrue(string.find(message, response) != -1)
        return

    def __invalid_character_in_bus_object_test(self, name):
        """Expect an invalid character in a bus object test."""
        with self.assertRaises(validate.ValidateException) as cm:
            validate.bus_object_path(name)

        message = cm.exception.message
        response = "' is an invalid character."
        self.assertTrue(string.find(message, response) != -1)
        self.assertTrue(string.find(message, name) != -1)
        return

    def __common_name_test(self, validator):
        """Do tests common to many names."""
        self.__no_name_test(validator)
        self.__long_name_test(validator)
        self.__no_first_character_period_test(validator)
        self.__elements_test(validator)
        self.__character_tests(validator)
        return

    def __long_name_test(self, validator):
        """Names may be up to 255 characters long. No more."""
        # Create a name 255 characters long.
        nine = "abcdeghij"
        elems = (
                 nine, nine, nine, nine, nine, nine, nine, nine, nine, nine,
                 nine, nine, nine, nine, nine, nine, nine, nine, nine, nine,
                 nine, nine, nine, nine, nine, "vwxyz"
                )
        valid_long_name = ".".join(elems)
        validator(valid_long_name)

        invalid = string.replace(valid_long_name, "vwxyz", "uvwxyz")

        with self.assertRaises(validate.ValidateException) as cm:
            validator(invalid)

        message = cm.exception.message
        response = "256 characters long. The max is 255."
        self.assertTrue(string.find(message, response) != -1)
        self.assertTrue(string.find(message, invalid) != -1)
        return

    def __no_name_test(self, validator):
        """The name is required. The exception should report this."""

        with self.assertRaises(validate.ValidateException) as cm:
            validator(None)

        message = cm.exception.message
        self.assertTrue(string.find(message, "is required") != -1)
        return

    def __no_first_character_period_test(self, validator):
        """The first character of a name is not allowed to be a period."""
        name = ".Test.Foo"
        with self.assertRaises(validate.ValidateException) as cm:
            validator(name)

        message = cm.exception.message
        expected_response = "The first character must not be a period."
        self.assertTrue(string.find(message, expected_response) != -1)
        self.assertTrue(string.find(message, name) != -1)
        return

    def __elements_test(self, validator):
        """Do the tests for conformation of the elements.

            Names are composed of 2 or more elements separated by a
            period ('.') character. All elements must contain at least
            one character."""

        name = "TestFoo"
        with self.assertRaises(validate.ValidateException) as cm:
            validator(name)

        message = cm.exception.message
        expected_response = "Names are composed of 2 or more elements"
        self.assertTrue(string.find(message, expected_response) != -1)
        self.assertTrue(string.find(message, name) != -1)

        # The two periods creates a zero length element.
        name = "test..foo"
        with self.assertRaises(validate.ValidateException) as cm:
            validator(name)

        message = cm.exception.message
        expected_response = "' has a zero length element."
        self.assertTrue(string.find(message, expected_response) != -1)
        self.assertTrue(string.find(message, name) != -1)

        # The trailing period creates a zero length element.
        name = "test.foo."
        with self.assertRaises(validate.ValidateException) as cm:
            validator(name)

        message = cm.exception.message
        self.assertTrue(string.find(message, expected_response) != -1)
        self.assertTrue(string.find(message, name) != -1)

        # Test a very short name. It should pass.
        validator("t.f")
        return

    def __character_tests(self, validator):
        """Test to make sure only valid characters are used in the name."""
        name_format = "test{0}char.foo"

        for c in string.ascii_letters:
            validator(name_format.format(c))

        for c in string.digits:
            validator(name_format.format(c))

        for c in string.punctuation:
            name = name_format.format(c)

            # Hyphens are handled elsewhere and some periods are valid.
            if c == '-' or c == '.':
                continue

            # All punctuation except '_' are forbidden.
            if c == '_':
                validator(name)
            else:
                with self.assertRaises(validate.ValidateException) as cm:
                    validator(name)

                expected_response = "Each element must only contain"
                message = cm.exception.message
                self.assertTrue(string.find(message, expected_response) != -1)

                invalid_element = string.split(name, '.')[0]
                self.assertTrue(string.find(message, invalid_element) != -1)

        # All white space is forbidden.
        for c in string.whitespace:
            name = name_format.format(c)
            with self.assertRaises(validate.ValidateException) as cm:
                validator(name)

            expected_response = "Each element must only contain"
            message = cm.exception.message
            self.assertTrue(string.find(message, expected_response) != -1)

            invalid_element = string.split(name, '.')[0]
            self.assertTrue(string.find(message, invalid_element) != -1)
        return

if __name__ == '__main__':
    unittest.main()
