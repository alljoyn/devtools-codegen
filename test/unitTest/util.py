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

import AllJoynCodeGen.config as config

def validate_cmdline(cmdline):
    pass # no checks performed

def validate_cmdline_wkn_required(cmdline):
    if cmdline.well_known_name is None:
        raise config.ConfigException("Well-known name is required.")

def get_config():
    c = config.Config()
    c.register_target('tl', { 'validate_cmdline' : validate_cmdline_wkn_required })
    c.register_target('ddcpp', { 'validate_cmdline' : validate_cmdline })
    c.parse()
    return c
