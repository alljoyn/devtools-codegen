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

import argparse
import os
import validate

class ConfigException(Exception):
    """Configuration exceptions"""

def get_version():
    return "0.0.1"

class Config:
    """Contains the configuration obtained from the command line.

    This class defines, parses, and validates the command line arguments.
    The configuration values are accessable via the member 'command_line'.
    command_line has the following members and values:

        xml_input_file (string)
        object_path (None or string)
        client_only (None or True)
        lax_naming (None or True)
        overwrite (None or True)
        output_path (string)
        runnable (None or True)
        target_language (string)
        well_known_name (None or string)
    """
    def __init__(self):
        """Initialize an instance of the Config class."""
        self.targets = {}

    def register_target(self, target, hooks):
        """Register hooks for a supported target.

        The hooks should be a dictionary with two functions:

            { 'validate_cmdline' : validate_cmdline_function,
              'generate_code'    : generate_code_function }
        """
        self.targets[target] = hooks

    def parse(self):
        """Parse and validate the command-line arguments."""
        ver = get_version()
        descrip = "Generate AllJoyn code from XML source. Version {0}.".format(ver)
        parser = argparse.ArgumentParser(description=descrip)

        help_text = """The file containing the xml definition of an object's
            interface(s)."""
        parser.add_argument("xml_input_file", help=help_text)

        help_text = """The object path (including name) of the object being
            defined in the xml input file. If the xml file contains the object
            path it does not match OBJECT_PATH, this tool will exit with an
            error. If the name is not defined either in the XML or using
            this flag, this tool will also exit with an error."""
        parser.add_argument("-b", "--object-path", help=help_text)

        help_text = """Only generate the client side code; if not specified,
            both the client and service code are generated."""
        parser.add_argument("-c", "--client-only", help=help_text,
                            action="store_true")

        help_text = """Relaxes the requirement that all method and signal
            arguments be named. If specified, default names will be generated
            for arguments."""
        parser.add_argument("-l", "--lax-naming", help=help_text,
                            action="store_true")

        help_text = """Overwrite non-developer files if they exist in the
            output directory. If specified, the codegen tool will overwrite
            existing files except for files that may contain developer code.
            The tool will create a copy of those files instead. Copies that
            already exist will be overwritten."""
        parser.add_argument("-o", "--overwrite", help=help_text,
                            action="store_true")

        help_text = """The path where the generated C++ files will be placed.
            If not specified, they will be output in the current working
            directory."""
        parser.add_argument("-p", "--output-path", help=help_text)

        help_text = """The generated client executable will make method calls
            with default values and the service method handlers will reply
            with default values. This option requires a valid object path to
            be specified (i.e. -b)."""
        parser.add_argument("-R", "--runnable", help=help_text,
                            action="store_true")

        help_text = """The target language. 'android' is for Java code on
            the Android platform. 'c' is for the AllJoyn 'C' binding
            to AllJoyn Standard Client (not implemented). 'cpp' is C++ code
            for AllJoyn Standard Client (not implemented). 'o' is for
            Objective C for Apple Targets (not implemented). 'tl' is C code
            for AllJoyn Thin Library. 'ddcpp' is C++ code for the Data-driven
            API."""
        parser.add_argument("-t", "--target-language", required=True,
                            choices=self.targets.keys(),
                            help=help_text)

        ver_text = "Version {0}.".format(ver)
        parser.add_argument("-v", '--version', action='version', version=ver_text)

        help_text = """The well-known name that the interface will use when
            requesting a bus name or advertising a name."""
        parser.add_argument("-w", "--well-known-name", help=help_text)

        help_text = """Output verbose information about the XML during
             parsing."""
        parser.add_argument("-x", "--xml", help=help_text, action="store_true")

        self.command_line = parser.parse_args()
        self.__validate()

    def target_hook(self, name):
        """Return the hooks of the selected target."""
        return self.targets[self.command_line.target_language][name]

    def __validate(self):
        """Validates various command line arguments beyond simple syntax."""
        self.target_hook('validate_cmdline')(self.command_line)

        if self.command_line.object_path is not None:
            validate.bus_object_path(self.command_line.object_path)

        if self.command_line.well_known_name is not None:
            validate.well_known_name(self.command_line.well_known_name)

        if self.command_line.output_path is None:
            self.command_line.output_path = "."

        path = self.command_line.output_path

        if path is not None and not os.path.exists(path):
            raise ConfigException("Path '{0}' does not exist.".format(path))

        return
