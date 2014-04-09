# Copyright (c) 2013, 2014 AllSeen Alliance. All rights reserved.
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

import unittest
import fnmatch
import os
import sys
import random

import AllJoynCodeGen.argdef as argdef
import AllJoynCodeGen.memberdef as memberdef

class TestArg(unittest.TestCase):
    """Tests the ArgDef class."""

    def test_init(self):
        """Tests initializing."""
        a = argdef.ArgDef()

        self.assertEqual(a.name, None)
        self.assertEqual(a.arg_type, None)
        self.assertEqual(a.direction, None)
        self.assertEqual(a.variant_type, None)
        self.assertEqual(a.interface, None)

        a = argdef.ArgDef(None, "myArg", "(bid)", "in", "")
        self.assertEqual(a.name, "myArg")
        self.assertEqual(a.arg_type, "(bid)")
        self.assertEqual(a.direction, "in")
        self.assertEqual(a.variant_type, "")
        self.assertEqual(a.interface, None)

        return

    def test_is_structure(self):
        """Tests the is_structure() method."""
        a = argdef.ArgDef(None, "myArg", "(bid)")
        self.assertTrue(a.is_structure())

        a = argdef.ArgDef(None, "myArg", "a(bid)")
        self.assertTrue(a.is_structure())

        self.assertTrue(memberdef.is_structure("(bid)"))
        self.assertTrue(memberdef.is_structure("a(bid)"))
        self.assertTrue(memberdef.is_structure("aa(bid)"))
        self.assertTrue(memberdef.is_structure("aaa(bid)"))
        self.assertFalse(memberdef.is_structure("a{is}"))
        self.assertFalse(memberdef.is_structure("a{i(sid)}"))
        return

    def test_is_dictionary(self):
        """Tests the is_dictionary() method."""
        a = argdef.ArgDef(None, "myArg", "a{bid}")
        self.assertTrue(a.is_dictionary())

        a = argdef.ArgDef(None, "myArg", "aa{bid}")
        self.assertTrue(a.is_dictionary())

        # This is actually an invalid arg type. Because the xml is None
        # no validation is done. If this test fails because of validation
        # just remove the test.
        a = argdef.ArgDef(None, "myArg", "{bid}")
        self.assertFalse(a.is_dictionary())

        self.assertTrue(memberdef.is_dictionary("a{bid}"))
        self.assertTrue(memberdef.is_dictionary("aa{bid}"))
        self.assertTrue(memberdef.is_dictionary("aaa{bid}"))
        self.assertFalse(memberdef.is_dictionary("a(is)"))
        self.assertFalse(memberdef.is_dictionary("a(ia{is})"))
        return

    def test_get_indirection_level(self):
        """Tests the get_indirection_level() method."""
        a = argdef.ArgDef(None, "myArg", "a(bid)")
        self.assertEqual(a.get_indirection_level(), 1)

        a = argdef.ArgDef(None, "myArg", "aad")
        self.assertEqual(a.get_indirection_level(), 2)

        self.assertEqual(memberdef.get_indirection_level("i"), 0)
        self.assertEqual(memberdef.get_indirection_level("ai"), 1)
        self.assertEqual(memberdef.get_indirection_level("aai"), 2)
        self.assertEqual(memberdef.get_indirection_level("a{bid}"), 1)
        self.assertEqual(memberdef.get_indirection_level("aa{bid}"), 2)
        self.assertEqual(memberdef.get_indirection_level("aaa{bid}"), 3)
        self.assertEqual(memberdef.get_indirection_level("a(is)"), 1)
        self.assertEqual(memberdef.get_indirection_level("a(ia{is})"), 1)
        return

    def test_get_max_structure_depth(self):
        """Tests the get_max_structure_depth() method."""
        sig = "bud"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_structure_depth(), 0)
        self.assertEqual(memberdef.get_max_structure_depth(sig), 0)

        sig = "(bud)"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_structure_depth(), 1)
        self.assertEqual(memberdef.get_max_structure_depth(sig), 1)

        sig = "(bud)(did)"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_structure_depth(), 1)
        self.assertEqual(memberdef.get_max_structure_depth(sig), 1)

        sig = "(bud(did))"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_structure_depth(), 2)
        self.assertEqual(memberdef.get_max_structure_depth(sig), 2)

        sig = "(q(bud)(did))"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_structure_depth(), 2)
        self.assertEqual(memberdef.get_max_structure_depth(sig), 2)

        sig = "(i((bud(did))i))"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_structure_depth(), 4)
        self.assertEqual(memberdef.get_max_structure_depth(sig), 4)

        sig = "(i((buda{did})i))"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_structure_depth(), 3)
        self.assertEqual(memberdef.get_max_structure_depth(sig), 3)

        return

    def test_get_max_dictionary_depth(self):
        """Tests the get_max_dictionary_depth() method."""
        sig = "bud"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_dictionary_depth(), 0)
        self.assertEqual(memberdef.get_max_dictionary_depth(sig), 0)

        sig = "a{bud}"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_dictionary_depth(), 1)
        self.assertEqual(memberdef.get_max_dictionary_depth(sig), 1)

        sig = "a{bud}a{did}"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_dictionary_depth(), 1)
        self.assertEqual(memberdef.get_max_dictionary_depth(sig), 1)

        sig = "a{buda{did}}"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_dictionary_depth(), 2)
        self.assertEqual(memberdef.get_max_dictionary_depth(sig), 2)

        sig = "a{q{bud}a{did}}"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_dictionary_depth(), 2)
        self.assertEqual(memberdef.get_max_dictionary_depth(sig), 2)

        sig = "a{ia{a{buda{did}}i}}"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_dictionary_depth(), 4)
        self.assertEqual(memberdef.get_max_dictionary_depth(sig), 4)

        sig = "a{ia{a{buda(did)}i}}"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_dictionary_depth(), 3)
        self.assertEqual(memberdef.get_max_dictionary_depth(sig), 3)

        return

    def test_split_signature(self):
        """Tests the split_signature() method."""
        fragments = ["b", "i", "d", "u", "x", "a{sv}", "(ii)", "(ia{sv})",
                     "a{i(ss)}", "(((yyy)))"]

        for i in range(5000):
            nfrags = random.randint(1, len(fragments)-1)
            frags = []
            for j in range(nfrags):
                frags.append(fragments[random.randint(0,len(fragments)-1)])
            sig = "(" + "".join(frags) + ")"
            fields = memberdef.split_signature(sig)
            self.assertEqual(len(fields), nfrags)
            for j in range(nfrags):
                self.assertEqual(fields[j], frags[j])

        return
