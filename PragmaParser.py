# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import os
#from PragmaParser import PragmaParser
from oracle import db,timer


test1 = '''
    pragma macro(stdio_print,'stdio.put_line_pipe([1],[2])', substitute);
    pragma macro(stdio_print2,'stdio.put_line_pipe([1],[2])');
    function FunctionName return ref [AC_FIN] is
    begin
        &stdio_print('hello','DEBUG_PIPE');
        return null;
    exception when others then
        return null;        
    end;

    procedure ProcName(a integer) is
    begin
        null;
    exception when others then null;
    end;
'''
from Parser import Parser

import ply.lex  as lex
import ply.yacc as yacc
from ply.lex import TOKEN
from name_dict import name_dict

class PragmaParser(Parser):
    def __init__(self,debug = 0):
        super(PragmaParser,self).__init__(debug)

    keywords = (
        "TRUE",
        "FALSE",
        #"SUBSTITUTE",
        #"PROCESS"
        )

    pragmas = ("MACRO","INCLUDE")

    tokens = keywords + pragmas + ('SEMI','PRAGMA',
        'INLINE_STRING','ID',
        "LPAREN","RPAREN",
        "COMMA","SECTION_BEGIN","SECTION_END",
        'COLON','LBRACKET', 'RBRACKET','PERIOD',)

    t_ANY_ignore      = ' \n\t'
    t_pragma_COMMA    = r','
    t_pragma_LPAREN   = r'\('
    t_pragma_RPAREN   = r'\)'
    t_pragma_COLON    = r':'
    t_pragma_LBRACKET = r'\['
    t_pragma_RBRACKET = r'\]'
    t_pragma_PERIOD   = r'\.'

    states = (
        ('pragma','exclusive'),
    )
    # def t_SECTION(self,t):
    #     ur'╒═+╕\n│ +\w+ +│\n└─+┘'
    #     return t
    def t_SECTION_BEGIN(self,t):
        ur'╒═+╕\n│\s(?P<section_name>\w+)\s+│\n'        
        t.value = t.lexer.lexmatch.group('section_name')
        return t
    def t_SECTION_END(self,t):
        ur'└─+┘'
        t.value = ''
        return t

    def t_PRAGMA(self,t):
    	r'(?i)PRAGMA'
        lc = t.lexer.clone()

        lc.begin('pragma')        
        tc = lc.token()
        #print 'TYPE=',tc.type
        if tc and tc.type not in ["MACRO","INCLUDE"]: #Если не обрабатываемая прагма, то пропускаем
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
            if value in self.keywords or value in self.pragmas:
                t.type = value
            #elif value not in ["MACRO"]: #Если не обрабатываемая прагма, то пропускаем
            #    t.lexer.begin('INITIAL')
            #    return


            return t
        #print 'SKIP ID =',t
    
        
    #def t_SKIP_SYMBOLS(self,t):
    #   ur'\[[a-zA-Z_][a-zA-Z0-9_]*\]|&|\(.*?\)|═|╒|│|╕|└|┘|─|\((.|\n)*?\)'
    #   #print "SKIP_SYMBOLS=",t


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
        p[0] = p[1]
    def p_prog2(self,p):
        'program : sections'
        p[0] = p[1]
    def p_sections(self,p):
        'sections : sections section'
        p[0] = dict(p[1].items()+p[2].items())
    def p_sections2(self,p):
        'sections : section'
        p[0] = p[1]
    def p_section(self,p):
        'section : SECTION_BEGIN statements SECTION_END'
        p[0] = {p[1]:p[2]}

    def p_optional(self,p):
        ''' program :
            pragma_params :
            statements :
            '''
    def p_statements(self,p):
        '''statements : statements statement'''
        p[1].update(p[2])        
        p[0] = p[1]
    def p_statements2(self,p):
        '''statements : statement'''
        p[0] = p[1]
    def p_statement(self,p):
        '''statement : pragma_macro_substitute
           statement : pragma_include
        '''
        p[0] = p[1]

    def p_idorstring(self,p):
        '''idorstring : ID
           idorstring : INLINE_STRING'''
        p[0] = p[1]
    def p_pragma(self,p):
        ''' pragma_macro_substitute : PRAGMA MACRO LPAREN idorstring COMMA string pragma_params RPAREN SEMI'''
        def repr(s):            
            #return (u"@PRAGMA MACRO %s %s=%s"%(s.params,s.name,s.value)).encode('utf8')
            return (u"MACRO %s"%s.name).encode('utf8')
        macro = name_dict({
            "name"  :p[4],
            "value" :p[6],
            "params":p[7]}).set_repr(repr)
        p[0] = {macro.name:macro}



    def p_pragma_include(self,p):
        ''' pragma_include : PRAGMA INCLUDE LPAREN method RPAREN SEMI'''
        def repr(s):            
            return (u"INCLUDE ::[%s].[%s]"%(s.class_name,s.name)).encode('utf8')
        include = name_dict({
            "class_name"  :p[4][0],
            "name" :p[4][1]}).set_repr(repr)
        text = db[include.class_name].meths[include.name].get_sources()
        pragmas=PragmaParser(debug=0).parse(text,show_tokens=False)
        p[0] = pragmas['PUBLIC']

    def p_pragma_method(self,p):
        ''' method : COLON COLON LBRACKET ID RBRACKET PERIOD LBRACKET ID RBRACKET'''
        p[0] = (p[4],p[8])

    def p_pragma_params(self,p):
        '''pragma_params : COMMA options'''
        p[0] = p[2]
    def p_pragma_params2(self,p):
        '''pragma_params : COMMA options COMMA bool'''
        p[0] = name_dict({"options" : p[2],
                          "flag"    : p[4]}).set_repr(lambda s: (u"Flag=%s Options=%s"%(s.flag,s.options)).encode('utf8') )
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
            bool : FALSE'''
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

class test2Command(sublime_plugin.TextCommand):
    def run(self, edit):
        
        t = timer()        
        #print "test2 command is starting..."
        #from PlPlus import PlPlus
        #p = PlPlus(debug=1).parse(test1)
        #from PlPlusMacro import PlPlusMacro
        #macro=PlPlusMacro(debug=1)        


        #text = db["LIABILITY_1417U"].meths["EPL_IMPORT"].get_sources()
        #text = db["INSIDER"].meths["Z3267103821"].get_sources()
        #text = db["PAYMENT"].meths["PROCESS#AUTO"].get_sources()
        #text = db["SCAN_STATION"].meths["BEGIN_WORK"].get_sources()
        #text = db["DEBT_PARAM"].meths["NEW#AUTO"].get_sources()
        #text = db["MON_EVENT"].meths["CLIENT_PRODUCTS"].get_sources()
        #text = db["MON_EVENT"].meths["L_CALL_METHODS"].get_sources()
        #text = db["RUNTIME"].meths["PROFILE_LIB"].get_sources()
        #text = db["RUNTIME"].meths["MACRO_LIB"].get_sources()
        #text = db["EPL_REQUESTS"].meths["L"].get_sources()
        #text = db["EPL_REQUESTS"].meths["NEW_AUTO"].get_sources()
        #text = test1
        #t.print_time('Получение текста')
        #t=timer()
        #print 'TEXT=',text
        #p=PragmaParser(debug=0).parse(text,show_tokens=False)
        #p=PragmaParser(debug=1).parse(text,show_tokens=True)
  
        #text = test3.decode('utf-8')
        text = db["EPL_REQUESTS"].meths["NEW_AUTO"].get_sources()
        print text
        pragmas=PragmaParser(debug=0).parse(text,show_tokens=False)
        print pragmas

        # if p:
        #     print "Parser="
        #     for a in p:
        #         print unicode(a)
        # else:
        #     print "Нет текста для анализа..."
        # print "finished"

        t.print_time('Разбор')