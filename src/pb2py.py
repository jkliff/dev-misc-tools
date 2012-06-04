#!/usr/bin/env python2.7

if __name__ == '__main__':
    print >> sys.stderr, 'Not supposed to run as itself (yet).'
    sys.exit (-1)

import sys
import ply

def parse (body):
    print 'parsing', body

class PB2PyParser:

    __protBufDecl = None

    def __init__ (self, protBufDecl):
        self.__protBufDecl = protBufDecl
        self.__buildAST ()


    def __buildAST (self):
        parse(self.__protBufDecl)

    def toDict (self):
        pass
