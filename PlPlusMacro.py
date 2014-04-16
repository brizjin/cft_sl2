from Parser import Parser

import ply.lex  as lex
import ply.yacc as yacc
from ply.lex import TOKEN


class PlPlusMacro(Parser):
    def __init__(self,debug = 0):
        super(PlPlusMacro,self).__init__(debug)
    keywords = ('SUBSTITUTE','PRAGMA','MACRO')
    tokens = keywords + ('COMMENT','INLINE_STRING','ID','SEMI','COMMA','LPAREN','RPAREN','MACRO_EXEC')

    t_ignore    = ' \n\t'
    t_COMMA     = r','
    t_SEMI      = r';'
    t_LPAREN    = r'\('
    t_RPAREN    = r'\)'
    t_MACRO_EXEC= r'\&'

    def t_COMMENT(self,t):
        r'--.*|\/\*(.|\n)*?\*\/'
        #return t
    def t_INLINE_STRING(self,t):
        r'\'.*?\''
        return t    
    #def t_PRAGMA_MACRO(self,t):
    #    r'(?i)PRAGMA\s+MACRO\((?P<name>)'
    #        
    #    return t

    def t_error(self,t):        
    #    print 'err'
        t.lexer.skip(1)

    def t_ID(self,t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        value = t.value.upper()
        if value in self.keywords:
            t.type = value

        return t    

    def p_prog(self,p):
        'program : statements'
        print 'program'
    def p_optional(self,p):
        ''' program :
            statements :'''
        print optional
    def p_statements(self,p):
        '''statements : statements statement'''
        print 'statements'
    def p_statements2(self,p):
        '''statements : statement'''
        print "statements2"
    def p_statement(self,p):
        '''statement : pragma_macro_substitute
                     | pragma_use'''
        print "statement"
    def p_pragma(self,p):
        'pragma_macro_substitute : PRAGMA MACRO LPAREN ID COMMA INLINE_STRING COMMA SUBSTITUTE RPAREN SEMI'        
        print 'p_pragma'#,p.__dict__
        #line   = p.lineno(2)        # line number of the PLUS token
        #index  = p.lexpos(2)        # Position of the PLUS token
        #p.linespan(num). Return a tuple (startline,endline) with the starting and ending line number for symbol num.
        #p.lexspan(num). Return a tuple (start,end) with the starting and ending positions for symbol num.
        #p[0] = p[1]
    def p_pragma_use(self,p):
        'pragma_use : MACRO_EXEC ID LPAREN RPAREN'
        print 'pragma use'
    def p_error(self,p):
        #print 'error',p
        yacc.errok()
        #t = yacc.token()
        #return t
        #print "Whoa. You are seriously hosed."
        # Read ahead looking for a closing '}'
        #while 1:
        #    tok = yacc.token()             # Get the next token
        #    print 'TOK=',tok
        #    if not tok or tok.type == 'PRAGMA': break
        #yacc.restart()




