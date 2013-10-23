from Parser import Parser

import ply.lex  as lex
import ply.yacc as yacc
from ply.lex import TOKEN


class PlPlusMacro(Parser):
    def __init__(self,debug = 0):
        super(PlPlusMacro,self).__init__(debug)
        
    tokens = ('PRAGMA','MACRO','LPAREN','RPAREN','SEMI','COMMA','STRING','SUBSTITUTE')
    t_ignore    = ' \n\t'
    t_LPAREN    = r'\('
    t_RPAREN    = r'\)'
    t_COMMA     = r','
    t_SEMI      = r';'

    def t_COMMENT(self,t):
        r'--.*|\/\*(.|\n)*?\*\/'

    def t_STRING(self,t):
        r'''
        \'(.|\n)*?(?<!\')\'(?!\')
        '''
        t.value = t.value[1:-1]
        return t

    def t_ID(self,t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        state = t.lexer.current_state()
        value = t.value.upper()
        stack = self.stack
        if value in ['PRAGMA','MACRO','SUBSTITUTE']:           
            t.type = value
            return t

    def p_expr(self,p):
        'expression : pragmas'
        p[0] = p[1]

    # def p_strings_string(self,p):
    #     '''
    #     strings : STRING
    #     '''
    #     p[0] = p[1]

    # def p_strings(self,p):
    #     '''
    #     strings : strings STRING
    #     '''
    #     p[0] = p[1] + p[2]

    def p_options(self,p):
        '''
        pragmas :
        '''
    def p_pragmas_element(self,p):
        'pragmas : pragma'
        p[0] = [p[1]]

    def p_pragmas_loop(self,p):
        'pragmas : pragmas pragma'
        #p[1].append(p[2])
        p[0] = p[1] + [p[2]]

    def p_pragma(self,p):
        'pragma : PRAGMA MACRO LPAREN STRING COMMA STRING COMMA SUBSTITUTE RPAREN SEMI'
        class pragma:
            def __repr__(self):
                return self.type + ":" + self.name + "=" + self.text
        pr = pragma()
        pr.name = p[4]
        pr.text = p[6]
        pr.type = p[8]
        p[0] = pr


