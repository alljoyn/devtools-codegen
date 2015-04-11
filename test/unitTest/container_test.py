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

import unittest

import AllJoynCodeGen.container as container

########
# Each entry is ("number of unique structures", "signature").
########
structure_test_cases = ( (0, "b"),
                         (1, "(b)"),
                         (1, "(bad)"),
                         (2, "(bad(bad))"),
                         (4, "(bad(bad(dad))(bad))"),
                         (4, "((((bad)(bad)(bad)))(bad)bad)"),
                         (9, "((((bid)(bud)(bad(bad(bad)))))(dad)qub)")
                       )

########
# Each entry is ("number of unique dictionaries", "signature").
########
dictionary_test_cases = ( (0, "b"),
                          (1, "a{ib}"),
                          (1, "a{iu}"),
                          (2, "a{ia{is}}"),
                        )

########
# Each entry is ("number of unique containers", "signature").
########
mixed_test_cases = ( (0, "b"),
                     (3, "a{i(bib(bad)nib)}"),
                     (6, "(((ba{us})(ba{us}(bad)))(bad)bad)"),
                   )

class TestInterface(unittest.TestCase):
    """Tests the Interface class."""

    def test_structs(self):
        last_order = 0
        for case in structure_test_cases:
            c = container.Container(case[1])
            mess = "Case '{0}'.".format(case[1])
            self.assertTrue(c.get_order() >= last_order, mess)
            last_order = c.get_order()

            structs = {}
            c.extract_structures(structs)
            self.assertEqual(len(structs), case[0], mess)

        return

    def test_dictionaries(self):
        last_order = 0
        for case in dictionary_test_cases:
            c = container.Container(case[1])
            mess = "Case '{0}'.".format(case[1])
            self.assertTrue(c.get_order() >= last_order, mess)
            last_order = c.get_order()

            dicts = {}
            c.extract_dictionaries(dicts)
            self.assertEqual(len(dicts), case[0], mess)

        return

    def test_mixed(self):
        last_order = 0
        for case in mixed_test_cases:
            c = container.Container(case[1])
            mess = "Case '{0}'.".format(case[1])
            self.assertTrue(c.get_order() >= last_order, mess)
            last_order = c.get_order()

            dicts = {}
            structs = {}
            c.extract_dictionaries(dicts)
            c.extract_structures(structs)

            self.assertEqual(len(dicts) + len(structs), case[0], mess)

        return

