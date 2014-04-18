# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import os

test1 = '''
    pragma macro(stdio_print,'stdio.put_line_pipe([1],[2])', substitute);
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




class test2Command(sublime_plugin.TextCommand):
    def run(self, edit):
        from oracle import timer
        t = timer()
        
        print "test2 command is starting..."
        #from PlPlus import PlPlus
        #p = PlPlus(debug=1).parse(test1)
        from PlPlusMacro import PlPlusMacro
        macro=PlPlusMacro(debug=1)        
        p=macro.parse(test1)
        # if macro.debug:
        #     print "!!!!!!!!!!"#,macro.lexer.token()
        #     for tok in macro.lexer.token():
        #        print tok
        # while True:
        #     print "&&&&&&&&&"
        #     tok = macro.lexer.token()
        #     if not tok: break
        #     print tok

        if p:
            print "Parser="
            for a in p:
                print a
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