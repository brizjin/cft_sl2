import ply.lex as lex
import ply.yacc as yacc
from ply.lex import TOKEN

class Parser(object):
    tokens = ()
    precedence = ()
    stack = ['ROOT']

    def __init__(self,debug = 0):
        self.debug = debug
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[1] + "_" + self.__class__.__name__
        except:
            modname = "parser"+"_"+self.__class__.__name__
        debugfile = modname + ".dbg"
        tabmodule = modname + "_" + "parsetab"
        
        self.lexer = lex.lex(module = self,
                             debug  = debug,
                             #optimize=1
                             )

        self.yacc = yacc.yacc(module    = self,
                              debug     = debug,
                              debugfile = debugfile,
                              tabmodule = tabmodule,
                              #optimize=1
                              )
        
    #def t_error(self,t):
    #    print "Illegal character '%s'" % t.value[0]
    #    t.lexer.skip(1)
    def t_error(self,t):
        print "Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)

    def parse(self,text,show_tokens = True):
        #self.text = text
        if show_tokens:
           self.lexer.input(text)
           for tok in self.lexer:
               print tok

        return self.yacc.parse(text,lexer=self.lexer)

import sublime, sublime_plugin
class test3Command(sublime_plugin.TextCommand):
    def run(self, edit):
      pass