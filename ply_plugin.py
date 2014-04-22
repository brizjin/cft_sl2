# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import os
from PragmaParser import PragmaParser
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



class test2Command(sublime_plugin.TextCommand):
    def run(self, edit):
        
        t = timer()        
        print "test2 command is starting..."
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
        text = db["EPL_REQUESTS"].meths["NEW_AUTO"].get_sources()
        #text = test1
        t.print_time('Получение текста')
        t=timer()
        p=PragmaParser(debug=1).parse(text,show_tokens=False)
        #p=PragmaParser(debug=1).parse(text,show_tokens=True)



        if p:
            print "Parser="
            for a in p:
                print unicode(a)
        else:
            print "Нет текста для анализа..."
        print "finished"

        t.print_time('Разбор')

        
        

class test3Command(sublime_plugin.TextCommand):
    pass
    #print exprs

    #text = self.view.substr(sublime.Region(0, self.view.size()))        
    
    #data = text
    # from oracle import dataView
    # v = dataView(self.view)
    # text = v.sections['EXECUTE'].body.text
    # import re
    # text = re.sub(r'\n\t',r'\n',text).lstrip('\t')  #Удалим служебный таб в начале каждой строки
    # text = re.sub(r'\t',r'',text)                   #Удалим служебный таб в начале каждой строки
    # text = re.sub(r' +$','',text,re.MULTILINE)      #Удаляем все пробелы в конце строк, потому что цфт тоже их удаляет
    #print 'DATA=',text