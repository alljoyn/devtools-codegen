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

package_data_files = []

# All files needed for Thin Library support.
thin_library_package = ['tl/GenTL.py', 'tl/__init__.py', 'tl/*.tmpl']
package_data_files.extend(thin_library_package)

# All files needed for Android Java support.
android_package = ['android/GenAndroid.py', 'android/__init__.py', 'android/*.tmpl',
                   'android/.settings/*', 'android/res/*/*']
package_data_files.extend(android_package)

# All files needed for DataDriven C++ API support.
ddapi_cpp_package = ['ddcpp/GenCPP.py', 'ddcpp/__init__.py', 'ddcpp/*.tmpl']
package_data_files.extend(ddapi_cpp_package)

setup(name='AllJoynCodeGenSetup',
      version=config.get_version(),
      description='AllJoyn Code Generator',
      url='http://www.alljoyn.org/',
      package_dir={'AllJoynCodeGen': 'src'},
      package_data={'AllJoynCodeGen': package_data_files},
      packages=['AllJoynCodeGen'],
      scripts=['scripts/ajcodegen.py', 'scripts/ajcodegen-compile.py'])
