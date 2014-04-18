from Parser import Parser

import ply.lex  as lex
import ply.yacc as yacc
from ply.lex import TOKEN

class D(dict):
    def __init__(self,p,arr,repr):
        for i,a in enumerate(arr):
            self[arr[i]] = p[i+1]
        #self = self.append(zip(arr,p))
        self["repr"] = repr
    def __getattr__(self,name):
        return self[name] if self[name] is not None else ''
    def __repr__(self):
        return self["repr"] if not callable(self["repr"]) else self["repr"](self)

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

    def t_error(self,t):        
        t.lexer.skip(1)

    def t_ID(self,t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        value = t.value.upper()
        if value in self.keywords:
            t.type = value

        return t    

    def p_prog(self,p):
        'program : statements'
        #print 'program'
        p[0] = p[1]
    def p_optional(self,p):
        ''' program :
            statements :
            pragma_exec_params :
            '''
        #print "optional=",p.__dict__
        #p[0] = p[1]
        #print optional
    def p_statements(self,p):
        '''statements : statements statement'''
        #print 'statements'
        #if not p[1]:
        #    p[1] = []
        #p[0] = p[1].append(p[2])
        print "p1=",type(p[1]),p[1]
        print "p2=",type(p[2]),p[2]
        p[0] = (p[1],p[2])
    def p_statements2(self,p):
        '''statements : statement'''
        #print "statements2"
        p[0] = p[1]
    def p_statement(self,p):
        '''statement : pragma_macro_substitute
                     | pragma_use'''
        #print "statement"
        p[0] = p[1]
    def p_pragma(self,p):
        'pragma_macro_substitute : PRAGMA MACRO LPAREN ID COMMA INLINE_STRING COMMA SUBSTITUTE RPAREN SEMI'        
        #print 'p_pragma'#,p.__dict__
        def repr(s):
            return "macro_def=%s,%s"%(s.name,s.value)
        p[0] = D(p,["pragma","macro","lparen","name","comma","value","comma2","substitute"],repr)
        print p[0]
        #print 'D=',d
        #line   = p.lineno(2)        # line number of the PLUS token
        #index  = p.lexpos(2)        # Position of the PLUS token
        #p.linespan(num). Return a tuple (startline,endline) with the starting and ending line number for symbol num.
        #p.lexspan(num). Return a tuple (start,end) with the starting and ending positions for symbol num.
        #p[0] = p[1]
    def p_pragma_use(self,p):
        'pragma_use : MACRO_EXEC ID LPAREN pragma_exec_params RPAREN'
        def repr(s):
            return "macro_exec=%s(%s)"%(s.name,s.params)
        p[0] = D(p,["macro_exec","name","LP","params"],repr)
        print p[0]
    
    def p_gragma_exec_params(self,p):
        '''pragma_exec_params : pragma_exec_params COMMA pragma_exec_param'''
        p[0] = (p[1],p[3])
        print "pragma_exec_params2=",p[0]
    def p_gragma_exec_params(self,p):
        '''pragma_exec_params : pragma_exec_param'''
        p[0] = p[1]
        print "pragma_exec_params=",p[0]
    def p_pragma_exec_param(self,p):
        '''pragma_exec_param : INLINE_STRING'''
        p[0] = p[1]
        print "pragma_exec_param=",p[0]

    def p_error(self,p):
        print 'error',p
        yacc.errok()
        #print "syntax error...",p
        #t = yacc.token()
        #return t
        #print "Whoa. You are seriously hosed."
        # Read ahead looking for a closing '}'
        #while 1:
        #    tok = yacc.token()             # Get the next token
        #    print 'TOK=',tok
        #    if not tok or tok.type == 'PRAGMA': break
        #yacc.restart()




