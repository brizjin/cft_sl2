# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import os

test1 = '''
    pragma macro(get_field,'stdio.put_line_pipe([1],[2])', substitute);
    function EDIT_AUTO(
        P_NUM_DOG       IN      PRODUCT_NUM,            --1  Номер договора
        P_DATE_ENDING   IN      DATE,                   --5  Дата окончания действия договора
        P_CREATE_USER   IN      USER_REF               --6  Создано пользователем
    )return integer
    is
        function FunctionName(params) return DataType is
        begin
            return null;
        exception when others then
            return null;
        end;
    begin
        -- Установка значения реквизита "Номер договора"
        [NUM_DOG] := P_NUM_DOG;
        -- Установка значения реквизита "Дата создания договора"
        [DATE_BEGIN] := P_DATE_BEGIN;
        -- Установка значения реквизита "Дата начала действия договора"
        [DATE_BEGINING] := P_DATE_BEGINING;
        -- Установка значения реквизита "Дата закрытия договора"
        [DATE_CLOSE] := P_DATE_CLOSE;
        -- Установка значения реквизита "Дата окончания действия договора"
        [DATE_ENDING] := P_DATE_ENDING;
        -- Установка значения реквизита "Создано пользователем"
        [CREATE_USER] := P_CREATE_USER;
    end;

    function FunctionName return ref [AC_FIN] is
    begin
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




class test2Command(sublime_plugin.TextCommand):
    def run(self, edit):
        from oracle import timer
        t = timer()
        
        print "test2 command is starting..."
        from PlPlus import PlPlus
        p = PlPlus(debug=1).parse(test1)
        #from PlPlusMacro import PlPlusMacro
        #p=PlPlusMacro(debug=1).parse(text)

        
        for a in p:
            print a
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