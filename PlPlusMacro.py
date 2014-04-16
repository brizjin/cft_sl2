from Parser import Parser

import ply.lex  as lex
import ply.yacc as yacc
from ply.lex import TOKEN


class PlPlusMacro(Parser):
    def __init__(self,debug = 0):
        super(PlPlusMacro,self).__init__(debug)
        
    tokens = ('PRAGMA_MACRO','COMMENT','INLINE_STRING')
    t_ignore    = ' \n\t'

    def t_COMMENT(self,t):
        r'--.*|\/\*(.|\n)*?\*\/'
        #return t
    def t_INLINE_STRING(self,t):
        r'\'.*?\''
        return t    
    def t_PRAGMA_MACRO(self,t):
        r'(?i)PRAGMA\s+MACRO\((?P<name>[a-zA-Z_][a-zA-Z0-9_]*)'
            
        return t
    #def t_ALLSYM(self,t):
    #    r'.*+'
    #    return t
    def t_error(self,t):        
    #    print 'err'
        t.lexer.skip(1)
    

    def p_pragma(self,p):
        'pragma : PRAGMA_MACRO'
        print 'p_pragma'
        #p[0] = p[1]
    def p_error(self,p):
        print 'error',p




