# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import os
#from PragmaParser import PragmaParser
from oracle import db,timer
import re
sections_regex = re.compile(r'(?P<head>╒═+╕\n│ (?P<name>[A-Z]+) +│\n)(?P<body>.*?\n?)(?P<bottom>└─+┘\n)'.decode('utf-8'),re.S) #поиск секций


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
test3 = '''╒══════════════════════════════════════════════════════════════════════════════╕
│ EXECUTE                                                                      │
    function NEW_AUTO(
        P_XML_IN        IN      MEMO_BIG                --1  XML IN
    )return null
    is
    pragma macro(a,'stdio.put_line_pipe([1],''DEBUG_PIPEa'');',substitute);
    pragma macro(a2,'stdio.put_line_pipe');
    
    begin
        &a('TEST')
        &b('TEST')
        &c('TEST')
        &d('TEST')

        &a2('TEST','DEBUG_PIPE_TEST');
        -- Установка значения реквизита "Дата запроса"
        --[DATE_BEG] := P_DATE_BEG;
        -- Установка значения реквизита "Дата ответа"
        --[DATE_END] := P_DATE_END;
        -- Установка значения реквизита "XML IN"
        --[XML_IN] := P_XML_IN;
        -- Установка значения реквизита "XML OUT"
        --[XML_OUT] := P_XML_OUT;
        -- Установка значения реквизита "Пользователь"
        --[USER] := P_USER;
        
        ::[EPL_REQUESTS].[L].request(P_XML_IN);
    end;
└──────────────────────────────────────────────────────────────────────────────┘
╒══════════════════════════════════════════════════════════════════════════════╕
│ VALIDATE                                                                     │
    pragma macro(b,'stdio.put_line_pipe([1],''DEBUG_PIPEb'');',substitute);
    begin
        --if P_MESSAGE = 'DEFAULT' then
            --P_XML_IN  := [XML_IN];
            --P_XML_OUT := [XML_OUT];
            --P_DATE_BEG := sysdate;
        --end if;
        
        &b('TEST')  
        &c('TEST')
        &d('TEST')
        if P_MESSAGE = 'VALIDATE' then
            if P_INFO = 'FORMAT_XML_IN' then
                P_XML_IN := regexp_replace(P_XML_IN,'(<.*?>)','\1'||chr(10));
            end if;
        end if;
        
        --stdio.put_line_pipe('P_INFO='||P_INFO,'DEBUG_PIPE');
    end;
└──────────────────────────────────────────────────────────────────────────────┘
╒══════════════════════════════════════════════════════════════════════════════╕
│ PUBLIC                                                                       │
    pragma macro(c,'stdio.put_line_pipe([1],''DEBUG_PIPEc'');',substitute);
    
    function f(a integer)return boolean
    is
    begin
        
        &c('TEST')
        
    end;
└──────────────────────────────────────────────────────────────────────────────┘
╒══════════════════════════════════════════════════════════════════════════════╕
│ PRIVATE                                                                      │
    pragma macro(d,'stdio.put_line_pipe([1],''DEBUG_PIPEd'');',substitute);
    function f2(a integer)return boolean
    is
    begin
    
        &c('TEST')
        &d('TEST')
        
    end;
└──────────────────────────────────────────────────────────────────────────────┘
╒══════════════════════════════════════════════════════════════════════════════╕
│ VBSCRIPT                                                                     │
└──────────────────────────────────────────────────────────────────────────────┘
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
    #t_pragma_RPAREN     = r'\)'
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
        return

    def t_pragma_RPAREN(self,t):
        r'\)'
        if t.lexer.current_state() == 'pragma':
            t.lexer.begin('INITIAL')
        return t

    def t_ANY_ID(self,t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        value = t.value.upper()
        if t.lexer.current_state() == 'pragma':
            if t.value in self.pragmas:
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
        print "Pragmas=",self.pragmas

        if show_tokens:
           self.lexer.input(text)
           for tok in self.lexer:
               print tok

        return self.yacc.parse(text,lexer=self.lexer,tracking=True)

    def parse_sections(self,sections_text):
        def pragma_macro_replace(text,pragmas_call):
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
            return text_new

        pragmas_def = PragmaParser(debug=0).parse(sections_text,show_tokens=False)
        sections = {}
        heads    = {}
        bottoms  = {}
        for s in sections_regex.finditer(sections_text):            
            name = s.group('name')
            sections[name]  = s.group('body')
            heads[name]     = s.group('head')
            bottoms[name]   = s.group('bottom')

        def new_section_text(pragmas_def_add):
            section_name = pragmas_def_add[0]
            self.pragmas = {}
            for p in pragmas_def_add:
                print "DEF=",pragmas_def[p]
                self.pragmas.update(pragmas_def[p]) #добавляем определения из других секций
            section_text = sections[section_name]
            pragmas_call = self.yacc.parse(section_text,lexer=self.lexer,tracking=True)
            return heads[section_name] + pragma_macro_replace(section_text,pragmas_call) + bottoms[section_name]

        return new_section_text(['EXECUTE','VALIDATE','PUBLIC','PRIVATE']) \
             + new_section_text([          'VALIDATE','PUBLIC','PRIVATE']) \
             + new_section_text([                     'PUBLIC'          ]) \
             + new_section_text([          'PRIVATE', 'PUBLIC'          ]) \




class test3Command(sublime_plugin.TextCommand):    
   

    def run(self, edit):
        t    = timer()  
        #text = test3.decode('utf-8')
        # text = db["EPL_REQUESTS"].meths["NEW_AUTO"].get_sources()
        # print text
        # pragmas=PragmaParser(debug=0).parse(text,show_tokens=False)
        # print pragmas
        #print 't=',text
        #print text
        #pragmas=PragmaParser(debug=0).parse(text,show_tokens=False)
        #pragmas_call = PragmaCallParser(debug=0).parse(text,show_tokens=True)
        #print "PRAGMAS=",pragmas
        #new_text = PragmaCallParser(debug=0).parse_sections(text)
        #print "NEW_TEXT=",new_text
        #text    = db["DEBUG_TRIGGER"].meths["MACRO_LIB"].get_sources()
        #pragmas = PragmaParser(debug=0).parse(text)
        #print 'PR=',pragmas

        # text = db["EPL_HIST_SRV_D"].meths["FILL_HIST"].get_sources()
        # pragmas = PragmaParser(debug=0).parse(text)
        # print pragmas

        # import xmltodict
        # file_path = 'C:\\Users\\isb5\\AppData\\Roaming\\Sublime Text 2\\Packages\\CFT\\cache\\classes.xml'
        # f = open(file_path,"r")
        # text = f.read()
        # f.close()

        #o = xmltodict.parse(text.decode('1251'))
        # from bson import BSON
        # print 'TEXT=',o['CLASSES'].keys()
        # b = BSON.encode(o)
        # print "BSON=",len(b)

        #import pickle
        import cPickle as pickle
        import gzip

        #favorite_color = { "lion": "yellow", "kitty": "red" }
        fname = "C:\\Users\\isb5\\AppData\\Roaming\\Sublime Text 2\\Packages\\CFT\\cache\\save.p"
        #file = gzip.GzipFile(fname, 'wb')
        #file.write(pickle.dumps(o, 1))
        #file.close()

        def save(object, filename, bin = 1):
            file = gzip.GzipFile(filename, 'wb')
            file.write(pickle.dumps(object, bin))
            file.close()

        def load(filename):
            file = gzip.GzipFile(filename, 'rb')
            object = pickle.loads(file.read())
            file.close()
            return object

        o = load(fname)
        #print o
        #pickle.dump( o, open( fname,"wb"))
        #new_o = pickle.load( open( fname, "rb" ))

        #new_text = PragmaCallParser(debug=0).parse_sections(text)

            #sections_dict[s.group(1)] = section(self,s.start(2),s.end(2),s.group(1),text)


        # text_arr = []
        # prev_end = 0
        # text_len = len(text)
        # for v,(beg,end) in pragmas_call:
        #     text_arr.append(text[prev_end:beg])
        #     #text_arr.append(text[beg:end])
        #     text_arr.append(v[1:-1])
        #     prev_end = end
        # text_arr.append(text[prev_end:text_len])
        # text_new = "".join(text_arr)


        # print "TEXT=",text,"MACROTEXT=",text_new

        t.print_time('Разбор')
        # text2 = b.decode()
        # t.print_time('Декодирование')