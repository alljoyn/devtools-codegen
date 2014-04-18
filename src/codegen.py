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

import sys
import parseajxml
import config
import validate
import service
import tl.GenTL

##################################
# This is the start of execution.
##################################
def main():
    """The entry point for AllJoyn Code Generator."""
    error_format = "\nERROR! {0}"

    try:
        configuration = config.Config()
        report_config(configuration)
        parser = parseajxml.ParseAjXml(configuration.command_line.xml_input_file)
        service = parser.parse(configuration.command_line)

        target = configuration.command_line.target_language

        validate.alljoyn_data(service, target)

        if configuration.command_line.xml:
            print(service)

        if target == "tl":
            tl.GenTL.generate_code(configuration.command_line, service)
        elif target == 'c':
            # Also must enable this option in config.__validate()
            pass # The 'C' generator has not been implemented.
        elif target == 'cpp':
            # Also must enable this option in config.__validate()
            pass # The 'C++' generator has not been implemented.
        elif target == 'o':
            # Also must enable this option in config.__validate()
            pass # The Objective C generator has not been implemented.
        else:
            print("Unexpected target language option. No code generated.")


    except config.ConfigException as e:
        print(error_format.format(e.message))
        sys.exit(1)

    except validate.ValidateException as e:
        print(error_format.format(e.message))
        sys.exit(1)

    except parseajxml.ParseException as e:
        print(error_format.format(e.message))
        sys.exit(1)

    print("Done.")
    return

def report_config(c):
    """Print the configuration options."""
    input_file = c.command_line.xml_input_file
    print("Input XML file = '{0}'.".format(input_file))

    if c.command_line.object_path is not None:
        path = c.command_line.object_path
        print("Object path = '{0}'.".format(path))

    if c.command_line.lax_naming:
        print("Lax naming enabled.")

    if c.command_line.overwrite:
        print("Overwrite is enabled.")

    if c.command_line.output_path is not None:
        path = c.command_line.output_path
        print("Output path is '{0}'.".format(path))

    if c.command_line.runnable:
        print("Runnable code will be generated.")

    target = c.command_line.target_language
    print("Target language option is '{0}'.".format(target))

    if c.command_line.well_known_name is not None:
        name = c.command_line.well_known_name
        print("Well known name = '{0}'.".format(name))

    return

if __name__=="__main__":
   main()
