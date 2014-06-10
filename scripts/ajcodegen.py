#!/usr/bin/env python
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

#!Python script for invoking the AllJoyn code generator.
import os
import sys
import fnmatch
import subprocess
import platform

def __get_codegen_package_path():
    scripts_dir = os.path.dirname(sys.argv[0])
    base_dir = os.path.dirname(scripts_dir)
    codegen_sub_directory = "Lib\site-packages\AllJoynCodeGen"
    codegen_complete_directory = os.path.join(base_dir, codegen_sub_directory)

    return codegen_complete_directory

def __get_cheetah_command():
    scripts_dir = os.path.dirname(sys.argv[0])
    cheetah_py = os.path.join(scripts_dir, "cheetah.py")
    if not os.path.isfile(cheetah_py):
        print("'{0}' was not found.".format(cheetah_py))
        return []

    return_value = []

    system_type = platform.system()

    if system_type == "Linux" or system_type == "Darwin":
        return_value.append("python")
    elif system_type == "Windows":
        return_value.append("python.exe")
    else:
        print("Unrecognized system type '{0}'".format(system_type))
        return []

    return_value.extend([cheetah_py, "compile"]);

    return return_value

def __compile_template_files_if_needed():
    path = __get_codegen_package_path()

    # Make sure this is a valid directory
    if not os.path.isdir(path):
        print("Code generator directory '{0}' was not found!".format(path))
        return

    src_files = []

    for dirpath, dirs, files in os.walk(path):
        # The "src" portion of the existing directory is not used in the destination path.
        base = dirpath.replace("src/", "", 1)
        dest = os.path.join("Lib/site-packages/AllJoynCodeGen", base)

        for f in files:
            src = os.path.join(dirpath, f)
            if fnmatch.fnmatch(f, "*.tmpl"):
                python_file = "{0}.py".format(os.path.splitext(src)[0])
                already_compiled = os.path.exists(python_file)

                if already_compiled:
                    template_file_time = os.path.getmtime(src)
                    python_file_time = os.path.getmtime(python_file)

                    if template_file_time > python_file_time:
                        src_files.append(src)
                else:
                    src_files.append(src)

    if len(src_files) > 0:
        cheetah_command = __get_cheetah_command()

        if len(cheetah_command) > 0:
            cheetah_command.extend(src_files)
            subprocess.check_output(cheetah_command)

__compile_template_files_if_needed()

from AllJoynCodeGen.codegen import main

main()
