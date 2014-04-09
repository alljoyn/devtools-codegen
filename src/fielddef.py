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

import common
import validate
import memberdef

class FieldDef(memberdef.MemberDef):
    """Contains the description of a structure field"""

    def __init__(self, name = None, arg_type = None):
        """Initialize an instance of the FieldDef class"""
        memberdef.MemberDef.__init__(self, name, arg_type)
        return

    def parse(self, xml, lax_naming):
        """Parse the given field xml element"""
        #print("Parsing Field '{0}'".format(xml.get('name')))
        self.name = xml.get('name')
        self.arg_type = xml.get('type')
        validate.data_signature(self.arg_type, xml)

