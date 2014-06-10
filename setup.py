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

from distutils.core import setup
from src import config
import os
import fnmatch
import string

#######
# template_directories is the list of directories that contain .tmpl files to
# be compiled with Cheetah into .py files the first time the application is run.
# It is assumed that, by convention, each of these directories contains
# the Python file __init__.py and a file named GenXXX.py where 'XXX' is
# the last subdirectory of each of the template directories. Hence
# "src/android" contains a GenAndroid.py file and "src/tl" contains a GenTL.py file.
#
# All .tmpl files in the named directories will be part of the installation.
#
# All files in directories below these directories, not just .tmpl files,
# will be part of the installation.
#######
template_directories = ["src/android",
                        "src/tl"]

def __create_data_file_collection():
    return_value = []

    for path in template_directories:
        # Make sure this is a valid directory
        if not os.path.isdir(path):
            print("template directory '{0}' was not found!".format(path))
            continue

        print("Including template directory '{0}'".format(path))
        basename = os.path.basename(path)
        gen_file = "gen{0}.py".format(basename.lower())

        for dirpath, dirs, files in os.walk(path):
            # The "src" portion of the existing directory is not used in the destination path.
            base = dirpath.replace("src/", "", 1)
            dest = os.path.join("Lib/site-packages/AllJoynCodeGen", base)
            src_files = []

            for f in files:
                src = os.path.join(dirpath, f)
                # If this is the root of a template directory grab the GenXXX.py file.
                if dirpath == path:
                    if f.lower() == gen_file or f == "__init__.py":
                        src_files.append(src)
                    elif fnmatch.fnmatch(f, "*.tmpl"):
                        src_files.append(src)
                else:
                    src_files.append(src)

            dest_src = (dest, src_files)
            return_value.append(dest_src)

    return return_value

#####
# This is the collection of 'data' files to be added to the installation beyond
# those in the "src" directory.
#####
data_file_collection = __create_data_file_collection()

setup(name='AllJoynCodeGenSetup',
      version=config.get_version(),
      description='AllJoyn Code Generator',
      url='http://www.alljoyn.org/',
      package_dir={'AllJoynCodeGen': 'src'},
      packages=['AllJoynCodeGen'],
      scripts=['scripts/ajcodegen.py'],
      data_files=data_file_collection)
