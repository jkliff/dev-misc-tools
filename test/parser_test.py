#!/usr/bin/env python2.7

import unittest
import pb2py
import os

class ProtoBufferParserTest (unittest.TestCase):
    def setUp (self):
        pass

    def tearDown (self):
        pass

    def testParseMessage (self):
        m = """message {}"""
        parser = pb2py.PB2PyParser (m)
        d = parser.toDict()
        self.assertTrue (len (d) == 0)

    def testParseMessageWithOneField (self):
        m = """message {
    required string foo = 1;
}"""
        parser = pb2py.PB2PyParser (m)
        d = parser.toDict()
        self.assertTrue (len (d) == 1)
        self.assertTrue ('foo' in d.keys())

