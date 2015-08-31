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

If you have SCons installed you may simply run SCons from the root
directory and either the Windows or Linux installation program will
be built in the ./dist directory.

If you do not have SCons installed then you must do a manual build of
the installers. To do this follow the instructions below:

1) The Cheetah template files must be compiled into Python files before
   running the code generator or building the installers.

   To build the Python files from the Cheetah .TMPL files run the following
   command from the src directory:

        cheetah.py compile tl/*.tmpl Android/*.tmpl 

2) To build the Windows installer:

        python setup.py bdist_wininst
OR

        python setup.py bdist_msi

OR

2) To build the Linux installer:

        python setup.py bdist_rpm

    This will produce two .rpm files:
        AllJoynCodeGeSetup-X.X.X-X.noarch.rpm
        AllJoynCodeGeSetup-X.X.X-X.src.rpm

    The noarch version will install the code generator runtime.

    Under Ubuntu you will probably need to use alien to convert the .rpm
    to a .deb package. Details on how to do that are here:
    http://www.howtogeek.com/howto/ubuntu/install-an-rpm-package-on-ubuntu-linux/

In any case the installer(s) will be in the 'dist' directory.

After installing you must run the script /usr/local/bin/ajcodegen-compile.py
before invoking the code generator. This only need be done once. Under Linux
you may be required to run this as superuser. After that you may simply run
ajcodegen.py.
