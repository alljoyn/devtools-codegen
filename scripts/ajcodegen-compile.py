#!/usr/bin/env python
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

# Python script for invoking the Cheetah compiler for the .tmpl files.

import os
import sys
import fnmatch
import subprocess
import platform
import distutils.spawn

import AllJoynCodeGen.CheetahCompileExcept as cce

cheetah_command = []

def __get_cheetah_command():
    global cheetah_command

    if cheetah_command:
        return cheetah_command

    cheetah_py = None
    system_type = platform.system()

    if system_type == "Linux" or system_type == "Darwin":
        cheetah_py = distutils.spawn.find_executable("cheetah")
    elif system_type == "Windows":
        scripts_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        cheetah_py = os.path.join(scripts_dir, "cheetah.py")
        cheetah_command.append("python.exe")
    else:
        print("Unrecognized system type '{0}'".format(system_type))
        return []

    if cheetah_py:
        cheetah_command.extend([cheetah_py, "compile"]);
    else:
        print("Cheetah compiler was not found.")
        cheetah_command = []

    return cheetah_command

def __cheetah_compile(filename):
    path = os.path.dirname(filename)

    if not os.path.isdir(path):
        print("Template directory '{0}' was not found!".format(path))
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

    if src_files:
        cheetah_command = __get_cheetah_command()

        if cheetah_command:
            cheetah_command.extend(src_files)
            try:
                subprocess.check_output(cheetah_command)
            except subprocess.CalledProcessError as e:
                print("Unable to compile Cheetah .tmpl files.")
                print("Command was '{0}'.".format(cheetah_command))
                return

            print("Successfully compiled .tmpl files in '{0}'".format(path))

##############
# All modules that contain Cheetah templates must be placed within a try such as this.
##############
try:
    import AllJoynCodeGen.tl.GenTL
except cce.CheetahCompilationException as e:
    # The message is the complete filename of the module for which the import was attempted.
    __cheetah_compile(e.message)
