#!/usr/bin/env python2.7

if __name__ == '__main__':
    print >> sys.stderr, 'Not supposed to run as itself (yet).'
    sys.exit (-1)

import sys
import ply.yacc, ply.lex
"""
t_MESSAGE = 'message'
"""
t_ignore = " \t\n"
t_OPEN = "{"
t_CLOSE = "}"
t_NECESSITY = r'(required|optional)'
t_EQUALS = '='

def t_Tcons (t):
    r'string'
    t.type = reserved.get (t.value, 'Tcons')
    return t

class Field:
    def __init__ (self, name):
        self.name = name

def t_Sname (t):
    r'[a-zA-Z][a-zA-Z0-9]*'
    t.type = reserved.get (t.value, 'Sname')
    return t

t_IDX = '[0-9]+'

tokens = ('MESSAGE', 'OPEN', 'CLOSE', 'NECESSITY', 'EQUALS', 'Tcons', 'Sname', 'IDX')
reserved = {
    'message': 'MESSAGE',
    'string': 'Tcons'
}

def p_FieldsDecl (p):
    """FieldsDecl : FieldDecl FieldsDecl
            | FieldDecl
            | """
    print 'Fields', [i for i in p]

def p_FieldDecl (p):
    """FieldDecl : NECESSITY Tcons Sname EQUALS IDX ';'"""
    print 'Field', [i for i  in p]
    p [0] = Field (p[1])

def p_MessageDecl (p):
    """MessageDecl : MESSAGE OPEN FieldsDecl CLOSE"""
    print 'Message', [i for i in p]
    if p[2] is None:
        return

def t_error (t):
    print 'error', t
    t.lexer.skip (1)

start = 'MessageDecl'

def parse (body):
    print 'parsing', body
    lexer = ply.lex.lex ()
    yacc = ply.yacc.yacc ()

    print yacc.parse (body)
    print 'parsed'

class PB2PyParser:

    __protBufDecl = None

    def __init__ (self, protBufDecl):
        self.__protBufDecl = protBufDecl
        self.__buildAST ()


    def __buildAST (self):
        parse(self.__protBufDecl)

    def toDict (self):
        pass


class Foo:
    bar = None
    baz = None
    
