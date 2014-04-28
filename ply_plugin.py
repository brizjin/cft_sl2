# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import os
#from PragmaParser import PragmaParser
from oracle import db,timer


test1 = '''
    pragma macro(stdio_print,'stdio.put_line_pipe([1]||[1],[2])', substitute);
    pragma macro(abc,'stdio.put_line_pipe');
    function FunctionName return ref [AC_FIN] is
    begin
        &stdio_print('hello','DEBUG_PIPE');
        &abc('test','world');
        &stdio_print('new','line');
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
test2 = '''
    pragma include(::[RUNTIME].[MACRO_LIB]);
    pragma include(::[DEBUG_TRIGGER].[MACRO_LIB]);
    pragma include(::[RUNTIME].[CSMD]);
    pragma include(::[DEPN].[LIB_MACRO]);

    OurBank  ref [CL_BANK_N] := ::[SYSTEM].[VARIABLES].OurBank; -- наш банк

    dep_client_num number;      -- порядковый номер клиента

    type debt_rec   is record ( debt            ref [VID_DEBT],
                                type_account    varchar2,
                                summ            [SUMMA],
                                code            ::[VID_DEBT].[CODE]%type
                                );
    type debt_type  is table of debt_rec;

    -- -------------------------------------------------------------------------------------
    -- Служебный макрос для определения реквизитов с типом AC_FIN_REF по указанному ТБП

    pragma macro(get_field0,
    'declare
        result VARCHAR2(32000);
        cursor attr_list is
            select ca.ATTR_ID ATTR_ID
            from VW_CLASS_ATTRIBUTES ca
            where ca.CLASS_ID      = upper([1])
              and ca.SELF_CLASS_ID = upper(''AC_FIN_REF'');
    begin
        result := null;
        for attr_rec in attr_list loop
            result := result || '',''||[2]||''.[''||attr_rec.ATTR_ID||'']'';
        end loop;
        if(result is null)then
            result := ''0'';
        else
            result := ltrim(result,'','');
        end if;
        [0] := result;
    end;'
    ,process);

    pragma macro(get_field,'&get_field0([1],[2])', substitute);

'''





        
from Parser import Parser
import ply.lex  as lex
import ply.yacc as yacc
#from ply.lex import TOKEN
from name_dict import name_dict
from PragmaParser import PragmaParser

class PragmaCallParser(Parser):
    def __init__(self,debug = 0):
        super(PragmaCallParser,self).__init__(debug)
    
    tokens = ('AMP',
        #'SEMI',
        'ID',"LPAREN","RPAREN","COMMA",'INLINE_STRING')
    t_pragma_COMMA      = r','
    t_pragma_LPAREN     = r'\('
    t_pragma_RPAREN     = r'\)'
    t_ANY_ignore            = ' \n\t'
    #t_AMP               = r'&'

    states = (
        ('pragma','exclusive'),
    )

    def t_ANY_error(self,t):
        t.lexer.skip(1)
    def t_error(self,t):
        t.lexer.skip(1)

    def t_ANY_COMMENT(self,t):
        r'--.*|\/\*(.|\n)*?\*\/'

    def t_ANY_INLINE_STRING(self,t):
        r'\'(.|\n|\'\')*?\''
        if t.lexer.current_state() == 'pragma':            
            return t

    def t_AMP(self,t):
        r'&'
        t.lexer.begin('pragma')
        return t

    def t_ANY_SEMI(self,t):
        r';'
        if t.lexer.current_state() == 'pragma':
            t.lexer.begin('INITIAL')
            #return t
        return

    def t_ANY_ID(self,t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        value = t.value.upper()
        if t.lexer.current_state() == 'pragma':
            if not "substitute" in self.pragmas[t.value].params:
                t.lexer.begin('INITIAL')
            #t.pragma_def = self.pragmas[t.value]
                #print "substitute=",self.pragmas[t.value].params
            return t

    def p_program(self,p):
        "program : statements"
        p[0] = p[1]

    def p_statements(self,p):
        "statements : statements statement"
        #p[0] = dict(p[1].items()+p[2].items())
        p[1].append(p[2])
        p[0] = p[1]

    def p_statements2(self,p):
        "statements : statement"
        p[0] = [p[1]]

    def p_statement(self,p):
        """ statement : pragma_macro_call_substitute
            statement : pragma_macro_call
        """
        #print "P2=",p.lexspan(1)
        #p[0] = {p[1].name:(p[1],p.lexspan(1))}
        #p[1]["position"] = p.lexspan(1)

        #print "LEXSPAN=",p.lexspan(1)#,p
        v,correction = p[1]
        beg,end = p.lexspan(1)
        p[0] = (v,(beg,end + correction))

    def p_pragma_macro_call_substitute(self,p):
        "pragma_macro_call_substitute : AMP ID LPAREN params RPAREN"
        
        name        = p[2]
        params      = p[4]
        pragma_def  = self.pragmas[name].value
        for i,param_value in enumerate(params): #Делаем подстановку параметров
            pragma_def = pragma_def.replace('[%i]'%(i+1),param_value)


        #print "SUBST=",pragma_def

        #p[0] = name_dict({"name":p[2],"params":p[4]}).set_repr(lambda s:u"MACRO_CALL_SUBSTITUTE %s%s"%(s.name,s.params))
        p[0] = (pragma_def,1)


    def p_pragma_macro_call(self,p):
        "pragma_macro_call : AMP ID"
        name = p[2]
        name_len = len(p.slice[2].value)
        p[0] = (self.pragmas[name].value,name_len)

        #p[0] = name_dict({"name":p[2]}).set_repr(lambda s:u"MACRO_CALL %s"%(s.name))

    def p_params(self,p):
        "params : params COMMA idorstring"
        p[1].append(p[3])
        p[0] = p[1]

    def p_params2(self,p):
        "params : idorstring"
        p[0] = [p[1]]

    def p_idorstring(self,p):
        '''idorstring : ID
           idorstring : INLINE_STRING'''        
        p[0] = p[1]

    def p_error(self,p):
        print "SYNTAX ERROR on ", p

    def parse(self,text,show_tokens = True):
        #self.text = text        
        self.pragmas=PragmaParser(debug=0).parse(text,show_tokens=False)
        #print "Pragmas=",pragmas

        if show_tokens:
           self.lexer.input(text)
           for tok in self.lexer:
               print tok

        return self.yacc.parse(text,lexer=self.lexer,tracking=True)

class test3Command(sublime_plugin.TextCommand):    
   

    def run(self, edit):
        t = timer()  
        #text = test1
        text = db["EPL_REQUESTS"].meths["NEW_AUTO"].get_sources()

        pragmas_call = PragmaCallParser(debug=0).parse(text,show_tokens=True)
        text_arr = []
        prev_end = 0
        text_len = len(text)
        for v,(beg,end) in pragmas_call:
            text_arr.append(text[prev_end:beg])
            #text_arr.append(text[beg:end])
            text_arr.append(v[1:-1])
            prev_end = end
        text_arr.append(text[prev_end:text_len])
        text_new = "".join(text_arr)
        print "TEXT=",text,"MACROTEXT=",text_new

        t.print_time('Разбор')