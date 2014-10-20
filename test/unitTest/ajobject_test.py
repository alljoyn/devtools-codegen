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

from xml.etree import ElementTree
import unittest
import fnmatch
import os
import sys

import AllJoynCodeGen.ajobject as ajobject
import AllJoynCodeGen.service as service

class TestAjObject(unittest.TestCase):
    """Tests the AllJoynObject class."""

    def test_init(self):
        """Tests initializing."""
        name1 = "/com/qcom/sampleObject"
        o1 = ajobject.AllJoynObject(name1)

        self.assertEqual(o1.name, name1)
        self.assertEqual(o1.parent, None)
        self.assertFalse(o1.interfaces)
        self.assertFalse(o1.alljoyn_objects)
        self.assertEqual(o1.indent, 0)
        self.assertEqual(o1.index, -1)

        name2 = "SubObject"
        o2 = ajobject.AllJoynObject(name2, o1)

        self.assertEqual(o2.name, name2)
        self.assertEqual(o2.parent, o1)
        self.assertFalse(o2.interfaces)
        self.assertFalse(o2.alljoyn_objects)
        self.assertEqual(o2.indent, 0)
        self.assertEqual(o2.index, -1)

        return

    def test_get_full_name(self):
        """Tests get_full_name()."""
        test_xml = """
            <node name="/root">
                <node name="sub1">
                    <node name="sub2/sub3">
                        <interface name="i.i0">
                            <method name="m0" />
                        </interface>
                    </node>
                </node>
                <node name="sub4">
                    <interface name="i.i1">
                        <method name="m1" />
                    </interface>
                </node>
            </node>"""

        node = ElementTree.fromstring(test_xml)
        s = service.Service(node.get("name"))
        s.parse(node, False)

        found_nodes = 0

        for o in s.get_objects():
            if o.name == "sub2/sub3":
                self.assertEqual(o.get_full_name(), "/root/sub1/sub2/sub3")
                self.assertEqual(o.index, 0)

                p = o.parent
                self.assertEqual(p.get_full_name(), "/root/sub1")
                # Nodes that do not have directly contain interfaces do not have indices.
                self.assertEqual(p.index, -1)

                p = p.parent
                self.assertEqual(p.get_full_name(), "/root")
                self.assertEqual(p.index, -1)

                p = p.parent
                self.assertIsNone(p)

                found_nodes += 1
            elif o.name == "sub4":
                self.assertEqual(o.get_full_name(), "/root/sub4")
                self.assertEqual(o.index, 1)

                p = o.parent
                self.assertEqual(p.get_full_name(), "/root")
                self.assertEqual(p.index, -1)

                p = p.parent
                self.assertIsNone(p)

                found_nodes += 1

        self.assertEqual(found_nodes, 2)

    def test_get_interface_index(self):
        """Tests get_interface_index()."""
        test_xml = """
            <node name="/root">
                <interface name="i.i0">
                    <method name="m0" />
                </interface>
                <interface name="i.i1">
                    <method name="m1" />
                </interface>
                <node name="sub">
                    <interface name="i.i1">
                        <method name="m1" />
                    </interface>
                    <interface name="i.i0">
                        <method name="m0" />
                    </interface>
                    <interface name="i.i2">
                        <method name="m2" />
                    </interface>
                </node>
            </node>"""
        node = ElementTree.fromstring(test_xml)
        s = service.Service(node.get("name"))
        s.parse(node, False)

        for o in s.get_objects():
            index = 0
            for i in o.interfaces:
                self.assertEqual(o.get_interface_index(i), index)
                index += 1

    def test_has_properties(self):
        """Tests has_properties()."""

        test_xml = """
            <node name="/root">
                <interface name="i.i0">
                    <method name="m0" />
                    <signal name="s0" />
                </interface>
                <interface name="i.i1">
                    <signal name="s1" />
                </interface>
                <interface name="i.i2">
                    <signal name="s2" />
                    <method name="m2" />
                </interface>
                <interface name="i.i3">
                    <method name="m0" />
                    <method name="m1" />
                    <method name="m2" />
                    <method name="m3" />
                </interface>
                <interface name="i.i4">
                    <signal name="s0" />
                    <signal name="s1" />
                    <signal name="s2" />
                    <signal name="s3" />
                    <signal name="s4" />
                </interface>
            </node>"""

        node = ElementTree.fromstring(test_xml)
        s = service.Service(node.get("name"))
        s.parse(node, False)

        o = s.get_objects()[0]
        self.assertFalse(o.has_properties())

        test_xml = """
            <node name="/root">
                <interface name="i.i0">
                    <method name="m0" />
                    <signal name="s0" />
                </interface>
                <interface name="i.i1">
                    <signal name="s1" />
                </interface>
                <interface name="i.i2">
                    <signal name="s2" />
                    <method name="m2" />
                </interface>
                <interface name="i.i3">
                    <method name="m0" />
                    <method name="m1" />
                    <method name="m2" />
                    <property name="p0" type="b" access="readwrite" />
                </interface>
                <interface name="i.i4">
                    <signal name="s0" />
                    <signal name="s1" />
                    <signal name="s2" />
                    <signal name="s3" />
                    <signal name="s4" />
                </interface>
            </node>"""

        node = ElementTree.fromstring(test_xml)
        s = service.Service(node.get("name"))
        s.parse(node, False)

        o = s.get_objects()[0]
        self.assertTrue(o.has_properties())

    def test_get_full_coded_name(self):
        """Tests get_full_coded_name()."""

        test_xml = """
            <node name="/root/sub0/sub1">
                <interface name="i.i0">
                    <method name="m0" />
                </interface>
            </node>"""

        node = ElementTree.fromstring(test_xml)
        s = service.Service(node.get("name"))
        s.parse(node, False)

        o = s.get_objects()[0]
        self.assertEqual(o.get_full_coded_name(), "_root_sub0_sub1")
        self.assertEqual(o.get_full_coded_name(False), "_root_sub0_sub1")
        self.assertEqual(o.get_full_coded_name(True), "rootSub0Sub1")
