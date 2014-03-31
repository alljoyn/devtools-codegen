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

import AllJoynCodeGen.argdef as argdef

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

        self.assertTrue(argdef.is_structure("(bid)"))
        self.assertTrue(argdef.is_structure("a(bid)"))
        self.assertTrue(argdef.is_structure("aa(bid)"))
        self.assertTrue(argdef.is_structure("aaa(bid)"))
        self.assertFalse(argdef.is_structure("a{is}"))
        self.assertFalse(argdef.is_structure("a{i(sid)}"))
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

        self.assertTrue(argdef.is_dictionary("a{bid}"))
        self.assertTrue(argdef.is_dictionary("aa{bid}"))
        self.assertTrue(argdef.is_dictionary("aaa{bid}"))
        self.assertFalse(argdef.is_dictionary("a(is)"))
        self.assertFalse(argdef.is_dictionary("a(ia{is})"))
        return

    def test_get_indirection_level(self):
        """Tests the get_indirection_level() method."""
        a = argdef.ArgDef(None, "myArg", "a(bid)")
        self.assertEqual(a.get_indirection_level(), 1)

        a = argdef.ArgDef(None, "myArg", "aad")
        self.assertEqual(a.get_indirection_level(), 2)

        self.assertEqual(argdef.get_indirection_level("i"), 0)
        self.assertEqual(argdef.get_indirection_level("ai"), 1)
        self.assertEqual(argdef.get_indirection_level("aai"), 2)
        self.assertEqual(argdef.get_indirection_level("a{bid}"), 1)
        self.assertEqual(argdef.get_indirection_level("aa{bid}"), 2)
        self.assertEqual(argdef.get_indirection_level("aaa{bid}"), 3)
        self.assertEqual(argdef.get_indirection_level("a(is)"), 1)
        self.assertEqual(argdef.get_indirection_level("a(ia{is})"), 1)
        return

    def test_get_container(self):
        """Tests the get_container() method."""
        a = argdef.ArgDef(None, "myArg", "aad")
        self.assertEqual(a.get_container(), None)
        self.assertEqual(argdef.get_container("aad"), None)

        a = argdef.ArgDef(None, "myArg", "aa(dib)")
        self.assertEqual(a.get_container(2), "(dib)")
        self.assertEqual(argdef.get_container("aa(dib)", 2), "(dib)")

        a = argdef.ArgDef(None, "myArg", "aa(dib(bidu))")
        self.assertEqual(a.get_container(2), "(dib(bidu))")
        self.assertEqual(argdef.get_container("aa(dib(bidu))", 2), "(dib(bidu))")

        # If invoked in the middle of a signature get the sub container.
        a = argdef.ArgDef(None, "myArg", "(dib(bidu))bad(qun))")
        self.assertEqual(a.get_container(), "(dib(bidu))")
        self.assertEqual(argdef.get_container("(dib(bidu))bad(qun))"), "(dib(bidu))")

        a = argdef.ArgDef(None, "myArg", "aa{dib}")
        self.assertEqual(a.get_container(2), "{dib}")
        self.assertEqual(argdef.get_container("aa{dib}", 2), "{dib}")

        a = argdef.ArgDef(None, "myArg", "aa{d(ib)}")
        self.assertEqual(a.get_container(2), "{d(ib)}")
        self.assertEqual(argdef.get_container("aa{d(ib)}", 2), "{d(ib)}")

        return

    def test_get_max_structure_depth(self):
        """Tests the get_max_structure_depth() method."""
        sig = "bud"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_structure_depth(), 0)
        self.assertEqual(argdef.get_max_structure_depth(sig), 0)

        sig = "(bud)"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_structure_depth(), 1)
        self.assertEqual(argdef.get_max_structure_depth(sig), 1)

        sig = "(bud)(did)"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_structure_depth(), 1)
        self.assertEqual(argdef.get_max_structure_depth(sig), 1)

        sig = "(bud(did))"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_structure_depth(), 2)
        self.assertEqual(argdef.get_max_structure_depth(sig), 2)

        sig = "(q(bud)(did))"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_structure_depth(), 2)
        self.assertEqual(argdef.get_max_structure_depth(sig), 2)

        sig = "(i((bud(did))i))"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_structure_depth(), 4)
        self.assertEqual(argdef.get_max_structure_depth(sig), 4)

        sig = "(i((buda{did})i))"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_structure_depth(), 3)
        self.assertEqual(argdef.get_max_structure_depth(sig), 3)

        return

    def test_get_max_dictionary_depth(self):
        """Tests the get_max_dictionary_depth() method."""
        sig = "bud"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_dictionary_depth(), 0)
        self.assertEqual(argdef.get_max_dictionary_depth(sig), 0)

        sig = "a{bud}"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_dictionary_depth(), 1)
        self.assertEqual(argdef.get_max_dictionary_depth(sig), 1)

        sig = "a{bud}a{did}"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_dictionary_depth(), 1)
        self.assertEqual(argdef.get_max_dictionary_depth(sig), 1)

        sig = "a{buda{did}}"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_dictionary_depth(), 2)
        self.assertEqual(argdef.get_max_dictionary_depth(sig), 2)

        sig = "a{q{bud}a{did}}"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_dictionary_depth(), 2)
        self.assertEqual(argdef.get_max_dictionary_depth(sig), 2)

        sig = "a{ia{a{buda{did}}i}}"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_dictionary_depth(), 4)
        self.assertEqual(argdef.get_max_dictionary_depth(sig), 4)

        sig = "a{ia{a{buda(did)}i}}"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.get_max_dictionary_depth(), 3)
        self.assertEqual(argdef.get_max_dictionary_depth(sig), 3)

        return

    def test_find_end_of_basic_types(self):
        """Tests the find_end_of_basic_types() method."""

        sig = "i"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.find_end_of_basic_types(), 1)
        self.assertEqual(argdef.find_end_of_basic_types(sig), 1)

        sig = "b"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.find_end_of_basic_types(), 1)
        self.assertEqual(argdef.find_end_of_basic_types(sig), 1)

        sig = "bdinqstuvxy"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.find_end_of_basic_types(), 8)
        self.assertEqual(argdef.find_end_of_basic_types(sig), 8)

        sig = "bdinqstuoxy"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.find_end_of_basic_types(), 11)
        self.assertEqual(argdef.find_end_of_basic_types(sig), 11)

        sig = "bdinqstuoxy)"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.find_end_of_basic_types(), 11)
        self.assertEqual(argdef.find_end_of_basic_types(sig), 11)

        sig = "bdinqstuoxy}"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.find_end_of_basic_types(), 11)
        self.assertEqual(argdef.find_end_of_basic_types(sig), 11)

        sig = "bdinqstuoxya"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.find_end_of_basic_types(), 11)
        self.assertEqual(argdef.find_end_of_basic_types(sig), 11)

        sig = "bdinqstuoxya"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.find_end_of_basic_types(1), 11)
        self.assertEqual(argdef.find_end_of_basic_types(sig, 1), 11)

        sig = "bdinqstuoxya"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.find_end_of_basic_types(5), 11)
        self.assertEqual(argdef.find_end_of_basic_types(sig, 5), 11)

        sig = "bdinqstuoxya"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.find_end_of_basic_types(10), 11)
        self.assertEqual(argdef.find_end_of_basic_types(sig, 10), 11)

        sig = "bad"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.find_end_of_basic_types(), 1)
        self.assertEqual(argdef.find_end_of_basic_types(sig), 1)

        sig = "b(d"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.find_end_of_basic_types(), 1)
        self.assertEqual(argdef.find_end_of_basic_types(sig), 1)

        sig = "ba{d"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.find_end_of_basic_types(), 1)
        self.assertEqual(argdef.find_end_of_basic_types(sig), 1)

        sig = "b)d"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.find_end_of_basic_types(), 1)
        self.assertEqual(argdef.find_end_of_basic_types(sig), 1)

        sig = "b}d"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.find_end_of_basic_types(), 1)
        self.assertEqual(argdef.find_end_of_basic_types(sig), 1)

        sig = "(d"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.find_end_of_basic_types(), 0)
        self.assertEqual(argdef.find_end_of_basic_types(sig), 0)

        sig = "a{d"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.find_end_of_basic_types(), 0)
        self.assertEqual(argdef.find_end_of_basic_types(sig), 0)

        sig = ")d"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.find_end_of_basic_types(), 0)
        self.assertEqual(argdef.find_end_of_basic_types(sig), 0)

        sig = "}d"
        a = argdef.ArgDef(None, "myArg", sig)
        self.assertEqual(a.find_end_of_basic_types(), 0)
        self.assertEqual(argdef.find_end_of_basic_types(sig), 0)

        return

    def test_get_next_marshal_args_signature(self):
        """Tests the get_next_marshal_args_signature() method."""

        sig = "bid(ii)"
        a = argdef.ArgDef(None, "myArg", sig)

        answer = "bid"
        self.assertEqual(a.get_next_marshal_args_signature(), answer)
        self.assertEqual(argdef.get_next_marshal_args_signature(sig), answer)

        answer = "id"
        self.assertEqual(a.get_next_marshal_args_signature(1), answer)
        self.assertEqual(argdef.get_next_marshal_args_signature(sig, 1), answer)

        answer = "d"
        self.assertEqual(a.get_next_marshal_args_signature(2), answer)
        self.assertEqual(argdef.get_next_marshal_args_signature(sig, 2), answer)

        sig = "bidaii"
        a = argdef.ArgDef(None, "myArg", sig)

        answer = "bid"
        self.assertEqual(a.get_next_marshal_args_signature(), answer)
        self.assertEqual(argdef.get_next_marshal_args_signature(sig), answer)

        answer = "id"
        self.assertEqual(a.get_next_marshal_args_signature(1), answer)
        self.assertEqual(argdef.get_next_marshal_args_signature(sig, 1), answer)

        answer = "d"
        self.assertEqual(a.get_next_marshal_args_signature(2), answer)
        self.assertEqual(argdef.get_next_marshal_args_signature(sig, 2), answer)

        answer = "ai"
        self.assertEqual(a.get_next_marshal_args_signature(3), answer)
        self.assertEqual(argdef.get_next_marshal_args_signature(sig, 3), answer)

        sig = "a{uv}"
        a = argdef.ArgDef(None, "myArg", sig)

        answer = sig
        self.assertEqual(a.get_next_marshal_args_signature(), answer)
        self.assertEqual(argdef.get_next_marshal_args_signature(sig), answer)

        answer = "{uv}"
        self.assertEqual(a.get_next_marshal_args_signature(1), answer)
        self.assertEqual(argdef.get_next_marshal_args_signature(sig, 1), answer)

        answer = "u"
        self.assertEqual(a.get_next_marshal_args_signature(2), answer)
        self.assertEqual(argdef.get_next_marshal_args_signature(sig, 2), answer)

        answer = "v"
        self.assertEqual(a.get_next_marshal_args_signature(3), answer)
        self.assertEqual(argdef.get_next_marshal_args_signature(sig, 3), answer)

        sig = "(ba{da(ss)})"
        a = argdef.ArgDef(None, "myArg", sig)

        answer = sig
        self.assertEqual(a.get_next_marshal_args_signature(), answer)
        self.assertEqual(argdef.get_next_marshal_args_signature(sig), answer)

        answer = "b"
        self.assertEqual(a.get_next_marshal_args_signature(1), answer)
        self.assertEqual(argdef.get_next_marshal_args_signature(sig, 1), answer)

        answer = "a{da(ss)}"
        self.assertEqual(a.get_next_marshal_args_signature(2), answer)
        self.assertEqual(argdef.get_next_marshal_args_signature(sig, 2), answer)

        answer = "{da(ss)}"
        self.assertEqual(a.get_next_marshal_args_signature(3), answer)
        self.assertEqual(argdef.get_next_marshal_args_signature(sig, 3), answer)

        answer = "d"
        self.assertEqual(a.get_next_marshal_args_signature(4), answer)
        self.assertEqual(argdef.get_next_marshal_args_signature(sig, 4), answer)

        answer = "a(ss)"
        self.assertEqual(a.get_next_marshal_args_signature(5), answer)
        self.assertEqual(argdef.get_next_marshal_args_signature(sig, 5), answer)

        answer = "(ss)"
        self.assertEqual(a.get_next_marshal_args_signature(6), answer)
        self.assertEqual(argdef.get_next_marshal_args_signature(sig, 6), answer)

        answer = "ss"
        self.assertEqual(a.get_next_marshal_args_signature(7), answer)
        self.assertEqual(argdef.get_next_marshal_args_signature(sig, 7), answer)

        answer = "s"
        self.assertEqual(a.get_next_marshal_args_signature(8), answer)
        self.assertEqual(argdef.get_next_marshal_args_signature(sig, 8), answer)

        return
