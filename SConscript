# Copyright AllSeen Alliance. All rights reserved.
#
#    Permission to use, copy, modify, and/or distribute this software for any
#    purpose with or without fee is hereby granted, provided that the above
#    copyright notice and this permission notice appear in all copies.
#
#    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
#    WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
#    MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
#    ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
#    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
#    ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
#    OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os
import shutil
import platform

import SCons.Action
import SCons.Builder
import SCons.Util

from src import config

def _generate(environment):
    """Add Builders and construction variables to the Environment."""
    environment['CHEETAH'] = _detect(environment)
    environment['BUILDERS']['CHEETAH'] = _cheetah_builder

_cheetah_builder = Builder(
                           action = 'cheetah compile $SOURCES',
                           suffix = '.py',
                           src_suffix = '.tmpl')

class ToolCheetahWarning(SCons.Warnings.Warning):
    pass

class CheetahCompilerNotFound(ToolCheetahWarning):
    pass

SCons.Warnings.enableWarningClass(ToolCheetahWarning)

def _detect(environment):
    """ Try to detect the Cheetah compiler """

    try:
        return environment['CHEETAH']
    except KeyError:
        pass

    cheetah = environment.WhereIs('cheetah') or environment.WhereIs('cheetah.py')

    if cheetah:
        return cheetah

    raise SCons.Errors.StopError(
        CheetahCompilerNotFound,
        "Could not find Cheetah compiler.")
    return None

################
# Start of execution.
################
env = Environment(ENV = os.environ, BUILDERS={'Cheetah' : _cheetah_builder})

Export('env')

# The version is used in the name of the target installation program.
version = config.get_version()

if platform.system() == "Linux":
    build_option = "bdist_rpm"
    build_target = "AllJoynCodeGenSetup-{0}.noarch.rpm".format(version)
elif platform.system() == "Windows":
    path_ext = env['ENV']['PATHEXT']
    env['ENV']['PATHEXT'] = "{0};.PY".format(path_ext)
    build_option = "bdist_msi"
    build_target = "AllJoynCodeGenSetup-{0}.win32.msi".format(version)

setup_action = "python2 setup.py {0}".format(build_option)

_generate(env)

# Add/remove projects in subdirectories for the build here.
env.SConscript('src/SConscript')

clean_target = env.Command(build_target, ['setup.py', 'src'], setup_action)
Clean(clean_target, Glob("build\*"))

Return('env')
