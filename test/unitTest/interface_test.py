# Copyright (c) 2013, AllSeen Alliance. All rights reserved.
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

import AllJoynCodeGen.interface as interface
import AllJoynCodeGen.propertydef as propertydef
import AllJoynCodeGen.methoddef as methoddef
import AllJoynCodeGen.signaldef as signaldef
import AllJoynCodeGen.ajobject as ajobject

class TestInterface(unittest.TestCase):
    """Tests the Interface class."""

    def test_set_name(self):
        """Tests setting the name."""
        i = interface.Interface()
        name = "Foo.Bar.Test"
        i.set_name(name)
        self.assertEqual(i.interface_full_name, name)
        self.assertEqual(i.interface_name, 'Test')
        return

    def test_add_parent(self):
        """Tests adding parents."""
        i = interface.Interface()
        self.assertEqual(len(i.parents), 0)

        o = ajobject.AllJoynObject("/Foo/Zoo/Moo")
        i.add_parent(o)
        self.assertEqual(len(i.parents), 1)

        o = ajobject.AllJoynObject("/Foo/Zoo/Moo2")
        i.add_parent(o)
        self.assertEqual(len(i.parents), 2)
        return

    def test_add_method(self):
        """Tests adding methods."""
        i = interface.Interface()
        self.assertEqual(len(i.methods), 0)

        m = methoddef.MethodDef()
        i.add_method(None, m)
        self.assertEqual(len(i.methods), 1)

        m = methoddef.MethodDef()
        m.name = "NewName"
        i.add_method(None, m)
        self.assertEqual(len(i.methods), 2)
        return

    def test_add_signal(self):
        """Tests adding signals."""
        i = interface.Interface()
        self.assertEqual(len(i.signals), 0)

        s = signaldef.SignalDef()
        i.add_signal(None, s)
        self.assertEqual(len(i.signals), 1)

        s = signaldef.SignalDef()
        s.name = "NewName"
        i.add_signal(None, s)
        self.assertEqual(len(i.signals), 2)
        return

    def test_add_property(self):
        """Tests adding signals."""
        i = interface.Interface()
        self.assertEqual(len(i.signals), 0)

        p = propertydef.PropertyDef()
        i.add_property(None, p)
        self.assertEqual(len(i.properties), 1)

        p = propertydef.PropertyDef()
        p.name = "NewName"
        i.add_property(None, p)
        self.assertEqual(len(i.properties), 2)
        return

    def test_eq(self):
        """Tests the == operator."""
        self.__do_name_eq_test()
        self.__do_prop_eq_test()
        self.__do_method_eq_test()
        self.__do_signal_eq_test()
        self.__do_parent_test()
        return

    def test_str(self):
        """Tests the generation of the string representation of an
        interface."""
        i = interface.Interface()

        name = "Foo.Bar.Test"
        i.set_name(name)
        toString = i.__str__()
        self.assertTrue(str.find(toString, "Full: " + name) != -1)
        return

    def __do_name_eq_test(self):
        """Tests the two interfaces for (in)equality with various names."""
        i1 = interface.Interface()
        i2 = interface.Interface()
        self.assertEqual(i1, i2)

        i1_name = "Foo.Bar"
        i1.set_name(i1_name)
        self.assertNotEqual(i1, i2)

        i2.set_name("Foo.Bat")
        self.assertNotEqual(i1, i2)

        i2.set_name(i1_name)
        self.assertEqual(i1, i2)
        return

    def __do_prop_eq_test(self):
        """Tests the two interfaces for (in)equality with properties."""
        i1 = interface.Interface()
        i2 = interface.Interface()
        self.assertEqual(i1, i2)

        p1 = propertydef.PropertyDef()

        i1.add_property(None, p1)
        self.assertNotEqual(i1, i2)

        p2 = propertydef.PropertyDef()
        i2.add_property(None, p2)
        self.assertEqual(i1, i2)

        p1.name = "PropName"
        self.assertNotEqual(i1, i2,
                         "Should detect that property names are different.")

        p2.name = "propName"
        self.assertNotEqual(i1, i2)

        p2.name = p1.name
        self.assertEqual(i1, i2)
        return

    def __do_method_eq_test(self):
        """Tests the two interfaces for (in)equality with methods."""
        i1 = interface.Interface()
        i2 = interface.Interface()
        self.assertEqual(i1, i2)

        m1 = methoddef.MethodDef()

        i1.add_method(None, m1)
        self.assertNotEqual(i1, i2)

        m2 = methoddef.MethodDef()
        i2.add_method(None, m2)
        self.assertEqual(i1, i2)

        m1.name = "MethodName"
        self.assertNotEqual(i1, i2,
                         "Should detect that method names are different.")

        m2.name = "methodName"
        self.assertNotEqual(i1, i2)

        m2.name = m1.name
        self.assertEqual(i1, i2)
        return

    def __do_signal_eq_test(self):
        """Tests the two interfaces for (in)equality with signals."""
        i1 = interface.Interface()
        i2 = interface.Interface()
        self.assertEqual(i1, i2)

        s1 = signaldef.SignalDef()

        i1.add_signal(None, s1)
        self.assertNotEqual(i1, i2)

        s2 = signaldef.SignalDef()
        i2.add_signal(None, s2)
        self.assertEqual(i1, i2)

        s1.name = "SignalName"
        self.assertNotEqual(i1, i2,
                         "Should detect that signal names are different.")

        s2.name = "signalName"
        self.assertNotEqual(i1, i2)

        s2.name = s1.name
        self.assertEqual(i1, i2)
        return

    def __do_parent_test(self):
        """Tests the two interfaces for equality regardless of the parents."""
        i1 = interface.Interface()
        i2 = interface.Interface()
        self.assertEqual(i1, i2)

        p1 = ajobject.AllJoynObject("/P1")
        i1.add_parent(p1)
        self.assertEqual(i1, i2)

        i2.add_parent(p1)
        self.assertEqual(i1, i2)

        p2 = ajobject.AllJoynObject("/P2")
        i1.add_parent(p2)
        self.assertEqual(i1, i2)

        i2.add_parent(p2)
        self.assertEqual(i1, i2)

        return

if __name__ == '__main__':
    unittest.main()


