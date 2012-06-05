#!/usr/bin/env python2.7

if __name__ == '__main__':
    print >> sys.stderr, 'Not supposed to run as itself (yet).'
    sys.exit (-1)

import sys
import ply.yacc, ply.lex

t_ignore = ' \t'

literals = ['{', '}', ';', '=']

types = ('string', 'int32')

class Field:
    def __init__ (self, name):
        self.name = name

necessity_types = ('required', 'optional')

def t_Sname (t):
    r'[a-zA-Z][a-zA-Z0-9]*'
    if t.value in necessity_types:
        t.type = 'NECESSITY'
    elif t.value in types:
        t.type = 'Tcons'
    else:
        t.type = reserved.get (t.value, 'Sname')
    return t

t_IDX = '[0-9]+'

tokens = ('MESSAGE', 'NECESSITY', 'Tcons', 'Sname', 'IDX')
reserved = {
    'message': 'MESSAGE'
}

def p_FieldsDecl (p):
    """FieldsDecl : FieldDecl ';' FieldsDecl
            | FieldDecl ';'
            | """
    print 'Fields', [i for i in p]

def p_FieldNameDecl (p):
    """FieldNameDecl : Tcons Sname '=' IDX"""
    print 'FieldNameDecl', [i for i in p]

def p_FieldDecl (p):
    """FieldDecl : NECESSITY FieldNameDecl """
    print 'Field', [i for i  in p]
    p [0] = Field (p[1])

def p_MessageDecl (p):
    """MessageDecl : MESSAGE '{' FieldsDecl '}'"""
    print 'Message', [i for i in p]
    if p[2] is None:
        return

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error (t):
    print 'error', t
    t.lexer.skip (1)

start = 'MessageDecl'

def parse (body):
    print 'parsing', body
    lexer = ply.lex.lex ()
    yacc = ply.yacc.yacc ()

    print yacc.parse (body, debug=True)
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
    
