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

class PragmaCallParser(Parser):
    def __init__(self,debug = 0):
        super(PragmaCallParser,self).__init__(debug)

    tokens = ('AMP',)
    #t_pragma_COMMA      = r','
    #t_pragma_LPAREN     = r'\('
    #t_pragma_RPAREN     = r'\)'
    t_ignore            = ' \n\t'
    t_AMP               = r'&'

    def t_error(self,t):
        #print "skip=",t    
        t.lexer.skip(1)
    def p_amp(self,p):
        "amp : AMP"
        p[0] = p[1]
    def p_error(self,p):
        print "SYNTAX ERROR on ", p

class test3Command(sublime_plugin.TextCommand):    
   

    def run(self, edit):
        print "TEST3"
        text = test1
        p=PragmaCallParser(debug=0).parse(text,show_tokens=True)
        print "PARSER=",p