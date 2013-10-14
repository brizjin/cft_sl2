# -*- coding: utf-8 -*-
import sublime, sublime_plugin


import ply.lex as lex
import ply.yacc as yacc
from ply.lex import TOKEN
import os

keywords = (
    'FUNCTION',
    'RETURN',
    'BEGIN',
    'END',
    'IS',
    'BODY',
    'IN',
    'OUT',
)

oracle_types = (
    'NUMBER',
    'INTEGER',
    'DATE',
    'STRING',
    'VARCHAR2',
    'RAW',
    'BOOLEAN',
    'EXCEPTION',
    'INTERVAL',
    'TIMESTAMP',
    'BLOB',
    'CLOB',
    'BFILE',
    'LONG',
    'LONG_RAW',   
)

tokens = keywords + oracle_types + (
    #'NUMBER',
    #'PLUS',
    #'MINUS',
    'ID',
    'SEMICOLON',
    'LPAREN',
    'RPAREN',
    'COMMA',
    'DIGIT',
    'COMMENT',
    #'TEXT',
)

#t_PLUS      = r'\+'
#t_MINUS     = r'-'
t_DIGIT     = r'\d+'
t_ignore    = r' \t'
t_SEMICOLON = r';'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_COMMA     = r','
#t_COMMENT   = r''
#t_comment   = r'--.*'

def t_ANY_COMMENT(t):
    r'--.*|\/\*(.|\n)*\*\/'
    #return t
    #pass

# @TOKEN(r'(?i)' + '|'.join(keywords))
# def t_keyword(t):
#     t.type = t.value.upper()
#     if t.value.upper() == 'BEGIN':
#         t.lexer.code_start = t.lexer.lexpos        # Record the starting position
#         t.lexer.level = 1                          # Initial brace level
#         t.lexer.begin('body')                      # Enter 'ccode' state
#     return t

# @TOKEN(r'(?i)' + '|'.join(oracle_types))
# def t_oracle_types(t):
#     #t.type = 'ORACLE_TYPE'
#     t.type = t.value.upper()
#     return t

#def t_text(p):
#    r'([a-zA-Z_ ;]+)'
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    #print 'called ID'
    #print "ID=%s,%s"%(t.value,t.value.upper())
    if t.value.upper() in keywords or t.value.upper() in oracle_types:
        t.type = t.value.upper()
    if t.value.upper() == 'BEGIN':
        t.lexer.code_start = t.lexer.lexpos        # Record the starting position
        t.lexer.level = 1                          # Initial brace level
        t.lexer.begin('body')                      # Enter 'ccode' state
    return t

# def t_NUMBER(t):
#     r'\d+'
#     t.value = int(t.value)    
#     return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

class declare_function:
    def __init__(self):
        pass
    def __repr__(self):
        if self.params:
            return "%s%s return %s"%(self.name,self.params,self.return_type)
        else:
            return "%s return %s"%(self.name,self.return_type)
class param_class:
    def __repr__(self):
        if self.param_type:
            return "%s %s %s"%(self.name,self.param_type,self.data_type)
        else:
            return "%s %s"%(self.name,self.data_type)

#exprs = []
def p_expr(p):
    'expression : declarations'
    #print "EXPR=%s"%p[1]
    p[0]=p[1]
def p_optional(p):    
    '''
    declarations : 
    param_list :
    param_list_paren :
    param_type :
    two_digit_list :
    '''
def p_declarations_declare_element(p):
    '''
    declarations : declare_element
    param_list : param
    '''
    p[0] = [p[1]]
def p_declarations_declarations_declare_element(p):
    '''
    declarations : declarations declare_element    
    '''
    p[1].append(p[2])
    p[0] = p[1]

    #print "P!=%s"%p[0]
    #print "p0=%s"%(p.slice[1].__class__.__dict__)
    #if len(p)==3:
    #
        #print "p1=%s"%p[1].__class__
        
    #if str(p.slice[1]) == 'declare_element':
        #print "0"
        
#    else:
        #print "1"
#        p[1].append(p[2])
#        p[0] = p[1]
        

def p_declare_element(p):
    '''
    declare_element : declare_function
                    | variable_def
    '''
    #exprs.append(p[1])
    p[0] = p[1]

def p_f(p):
    '''
    declare_function : FUNCTION ID param_list_paren RETURN datatype IS declarations BEGIN BODY END SEMICOLON
    '''
    #print 'FUNC %s'%p[2]
    f = declare_function()
    f.name = p[2]
    f.params = p[3]
    f.return_type = p[5]
    #p[0] = 'FUNCTION %s return %s is %s'%(p[2],p[4],p[6])
    p[0] = f

def p_param_list_paren(p):
    'param_list_paren : LPAREN param_list RPAREN'
    #print "paren=%s"%p[2]
    p[0] = p[2]
#def p_param_list_param(p):
#    'param_list : param'
def p_param_list_param_list(p):
    'param_list : param_list COMMA param'
    p[1].append(p[3])
    p[0] = p[1]

def p_param_type_in_out(p):
    'param_type : IN OUT'
    p[0] = 'in out'

def p_param_type(p):
    '''param_type : IN
                  | OUT
    '''
    p[0] = p[1]


def p_param(p):
    'param : ID param_type datatype'
    
    param = param_class()
    param.name = p[1]
    param.data_type = p[3]
    param.param_type = p[2]
    p[0] = param

def p_one_digit_list(p):
    'one_digit_list : LPAREN DIGIT RPAREN'
    p[0] = '(' + p[2] + ')'

def p_two_digit_list_one(p):
    'two_digit_list : one_digit_list'
    p[0] = p[1]

def p_two_digit_list_two(p):
    'two_digit_list : LPAREN DIGIT COMMA DIGIT RPAREN'
    p[0] = '(' + p[2] + ',' + p[4] + ')'

def p_number_type(p):
    '''datatype : NUMBER two_digit_list
                | VARCHAR2 two_digit_list
                | STRING two_digit_list
                | RAW one_digit_list
                | INTERVAL two_digit_list
                | TIMESTAMP two_digit_list
    '''
    #p[0] = (p[1],p[2])
    if p[2]:
        p[0] = p[1]+p[2]
    else:
        p[0] = p[1]


def p_oracle_type(p):
    '''
    datatype : INTEGER
             | DATE
             | BOOLEAN
             | EXCEPTION
             | BLOB
             | CLOB
             | BFILE
             | LONG
             | LONG_RAW
    '''
    p[0] = p[1]


def p_variable_defination(p):
    'variable_def : ID datatype SEMICOLON'
    p[0] = 'variable %s of %s'%(p[1],p[2])

def p_error(p):
    print "Syntax error in input!"

#def t_comment(t):
    #r'(?<=begin)((.|\n)*?)(?=end)'
#    r'begin(.|\n)*?end'
#    pass

# Declare the state
states = (
    ('body','exclusive'),
)
#def t_body_COMMENT(t):
#    r'--.*|\/\*(.|\n)*\*\/'
#    return t
# Rules for the ccode state
def t_body_begin(t):     
    r'(?i)begin'
    t.lexer.level +=1

def t_body_end(t):
    r'(?i)end'
    t.lexer.level -=1

    # If closing brace, return the code fragment
    if t.lexer.level == 0:
        t.value = t.lexer.lexdata[t.lexer.code_start:t.lexer.lexpos-3]
        t.type = "BODY"
        #t.type = t.type.upper()
        t.lexer.lineno += t.value.count('\n')
        t.lexer.begin('INITIAL')
        t.lexer.lexpos -= 4           
        return t
# Ignored characters (whitespace)
t_body_ignore = " \t\n"

# For bad characters, we just skip over it
def t_body_error(t):
    t.lexer.skip(1)



class test2Command(sublime_plugin.TextCommand):
    def run(self, edit):
        text = self.view.substr(sublime.Region(0, self.view.size()))
        #print text
        #calc = Calc()
        #calc.parse(text)
        #calc.lexer.input(text)
        # Tokenize
        #for tok in calc.lexer:
        #    print tok

        #p = calc.parse(text)
        #print "p=",p

        #lexer = lex.lex(debug=1)
        debug = 1
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[1] + "_" + self.__class__.__name__
        except:
            modname = "parser"+"_"+self.__class__.__name__
        debugfile = modname + ".dbg"
        #tabmodule = "C:\Users\DK\Downloads\\" + modname + "_" + "parsetab"
        tabmodule = modname + "_" + "parsetab"
        #print "MOD:%s"%modname
        #print self.debugfile, self.tabmodule

        # Build the lexer and parser
        lexer = lex.lex(debug=debug)
        


        #lexer = lex.lex()
        data = '''  function new_func1(
                        tag_name varchar2
                        ,a in integer
                        ,b out integer ,d number(10)
                        ,c in out varchar2
                        ,e number(10,10)
                        /*
                        multiline
                        comment*/
                        ,f number
                        --test of comment
                        ) return integer is
                        a varchar2;
                        b integer;
                        c integer;
                        d integer;
                        function inner1 return varchar2 is
                        begin
                        end;
                    begin
                    end;
                    function new_func2 return varchar2 is
                    begin
                        --tag_value := DBMS_XMLGEN.convert(tag_value,0); --преобразуем ESC символы                        
                        --res_out := case when res_out is not null then res_out || chr(10) else res_out end || chr(9) ||'<'||tag_name||'>'||tag_value||'</'||tag_name||'>';
                        one more line
                    end;
                '''


        data2 = '''
        procedure add_out_tag(res_out in out clob,tag_name varchar2,tag_value clob)
        is
        begin
            --tag_value := DBMS_XMLGEN.convert(tag_value,0); --преобразуем ESC символы
            res_out := case when res_out is not null then res_out || chr(10) else res_out end || chr(9) ||'<'||tag_name||'>'||tag_value||'</'||tag_name||'>';
        end;
        '''
        #data = ''
        
        #data = text

        lexer.input(data)
        for tok in lexer:
            print tok

        p = yacc.yacc(debug=debug,
                  debugfile=debugfile,
                  tabmodule=tabmodule).parse(data)
        #print "p=",p
        for a in p:
            print a

        #print exprs
