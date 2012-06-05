#!/usr/bin/env python2.7

import unittest
import pb2py
import os

class ProtoBufferParserTest (unittest.TestCase):
    def setUp (self):
        pass

    def tearDown (self):
        print '-------------------------------------------------------'


    def testParseMessageError1 (self):
        m = """message"""
        parser = pb2py.PB2PyParser (m)
        d = parser.toDict()
        self.assertTrue (len (d) == 0)


    def testParseMessage (self):
        m = """message { }"""
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
        self.assertTrue ('foo' in d)

    def testParseMessageWithTwoFields (self):
        m = """message {
    required string foo = 1;
    required int32 bar = 2;
}"""
        parser = pb2py.PB2PyParser (m)
        d = parser.toDict()
        self.assertTrue (len (d) == 2)
        self.assertTrue ('foo' in d)
        self.assertTrue ('bar' in d)

    def testParseMessageWithManyFields (self):
        m = """message {
    required string foo = 1;
    required int32 bar = 2;
    required int32 yui = 3;

}"""
        parser = pb2py.PB2PyParser (m)
        d = parser.toDict()
        self.assertTrue (len (d) == 3)
        self.assertTrue ('foo' in d)
        self.assertTrue ('bar' in d)
        self.assertTrue ('yui' in d)


    def testParseMessageWithOneFieldOneLine (self):
        m = """message { required string foo = 1; }"""
        parser = pb2py.PB2PyParser (m)
        d = parser.toDict()
        self.assertTrue (len (d) == 1)
        self.assertTrue ('foo' in d)

