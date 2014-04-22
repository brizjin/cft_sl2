# -*- coding: utf-8 -*-
from Parser import Parser

import ply.lex  as lex
import ply.yacc as yacc
from ply.lex import TOKEN
from name_dict import name_dict

class PragmaParser(Parser):
    def __init__(self,debug = 0):
        super(PragmaParser,self).__init__(debug)

    keywords = ("MACRO",
        "TRUE",
        "FALSE",
        #"SUBSTITUTE",
        #"PROCESS"
        )
    tokens = keywords + ('SEMI','PRAGMA','INLINE_STRING','ID',"LPAREN","RPAREN","COMMA")

    t_ANY_ignore    = ' \n\t'
    t_pragma_COMMA     = r','
    t_pragma_LPAREN    = r'\('
    t_pragma_RPAREN    = r'\)'

    states = (
        ('pragma','exclusive'),
    )


    def t_PRAGMA(self,t):
    	r'(?i)PRAGMA'
        lc = t.lexer.clone()

        lc.begin('pragma')        
        tc = lc.token()        
        if tc and tc.type not in ["MACRO"]: #Если не обрабатываемая прагма, то пропускаем
            #print "NOT PRAGMA MACRO",t,tc
            print 'SKIP PRAGMA',tc.value.upper()
            return

        t.lexer.begin('pragma')
    	return t

    def t_ANY_SEMI(self,t):
        r';'
        if t.lexer.current_state() == 'pragma':
            t.lexer.begin('INITIAL')
        #t.lexer.pop_state()
            return t
        return
    
    def t_ANY_ID(self,t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        value = t.value.upper()
        #if value in self.keywords:
        #    t.type = value
        if t.lexer.current_state() == 'pragma':
            if value in self.keywords:
                t.type = value
            #elif value not in ["MACRO"]: #Если не обрабатываемая прагма, то пропускаем
            #    t.lexer.begin('INITIAL')
            #    return


            return t
        #print 'SKIP ID =',t


    def t_error(self,t):
        #print "skip=",t    
        t.lexer.skip(1)


    def t_ANY_COMMENT(self,t):
        r'--.*|\/\*(.|\n)*?\*\/'

    def t_ANY_INLINE_STRING(self,t):
        r'\'(.|\n|\'\')*?\''
        if t.lexer.current_state() == 'pragma':            
            return t    

    def t_ANY_error(self,t):
        #print "T_skip=",t
        t.lexer.skip(1)

    # def p_semi(self,p):
    #     r'prog : SEMI'
    #     p[0] = p[1]
    def p_prog(self,p):
        'program : statements'
        #print 'program'
        p[0] = p[1]
    def p_optional(self,p):
        ''' program :
            pragma_params :
            '''
    def p_statements(self,p):
       '''statements : statements statement'''
       p[1].append(p[2])
       p[0] = p[1]
    def p_statements2(self,p):
        '''statements : statement'''
        p[0] = [p[1]]
    def p_statement(self,p):
        '''statement : pragma_macro_substitute'''
        p[0] = p[1]
    def p_idorstring(self,p):
        '''idorstring : ID
           idorstring : INLINE_STRING
        '''
        p[0] = p[1]
    def p_pragma(self,p):
        ''' pragma_macro_substitute : PRAGMA MACRO LPAREN idorstring COMMA string pragma_params RPAREN SEMI'''
        def repr(s):            
            return "@PRAGMA MACRO %s %s=%s"%(s.params,s.name,s.value)            
        p[0] = name_dict(p,["pragma","macro","lparen","name","comma","value","params"],repr)
    # def p_pragma(self,p):
    #     ''' pragma_macro_substitute : PRAGMA MACRO LPAREN idorstring COMMA string COMMA options RPAREN SEMI
    #         pragma_macro_substitute : PRAGMA MACRO LPAREN idorstring COMMA string COMMA options COMMA bool RPAREN SEMI
    #     '''
    #     def repr(s):            
    #         return "@%sPRAGMA MACRO %s %s=%s"%(s.flag,s.options,s.name,s.value)
            
    #     p[0] = name_dict(p,["pragma","macro","lparen","name","comma","value","comma2","options","comma3",'flag'],repr)
    #def p_pragma2(self,p):
    #    ''' pragma_macro_substitute : PRAGMA MACRO LPAREN idorstring COMMA string RPAREN SEMI
    #        pragma_macro_substitute : PRAGMA MACRO LPAREN idorstring COMMA string COMMA bool RPAREN SEMI
    #    '''
    #    def repr(s):
    #        return "#%sPRAGMA MACRO %s=%s"%(s.flag,s.name,s.value)
    #    p[0] = name_dict(p,["pragma","macro","lparen","name","comma","value",'comma2','flag'],repr)
    def p_pragma_params(self,p):
        '''pragma_params : COMMA options'''
        p[0] = p[2]
    def p_pragma_params2(self,p):
        '''pragma_params : COMMA options COMMA bool'''        
        p[0] = (p[2],p[4])
    def p_pragma_params3(self,p):
        '''pragma_params : COMMA bool'''
        p[0] = p[2]

    def p_strings(self,p):
        'string : string INLINE_STRING'        
        p[0] = p[1] + p[2]
    def p_string(self,p):
        'string : INLINE_STRING'
        p[0] = p[1]

    def p_bool(self,p):
        ''' bool : TRUE
            bool : FALSE
        '''
        p[0] = p[1]

    def p_opts(self,p):
        'options : options COMMA ID'
        p[1].append(p[3])
        p[0] = p[1]
    def p_opts2(self,p):
        'options : ID'
        p[0] = [p[1]]

    def p_error(self,p):
        print "SYNTAX ERROR on ", p
        #yacc.errok()
