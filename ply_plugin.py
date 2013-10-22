# -*- coding: utf-8 -*-
import sublime, sublime_plugin


import ply.lex as lex
import ply.yacc as yacc
from ply.lex import TOKEN
import os

keywords = (
    'FUNCTION',
    'PROCEDURE',
    'RETURN',
    'BEGIN',
    'END',
    'IS',
    'BODY',
    'IN',
    'OUT',
    'REF',
    'DEFAULT',
    'NULL',

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
    'LPAREN', 'RPAREN',
    'LBRACKET', 'RBRACKET',
    'COMMA', 'PERIOD', 'SEMI', 'COLON',
    'DIGIT',
    'COMMENT',
    'INLINE_STRING',

    #'TEXT',
)

#t_PLUS      = r'\+'
#t_MINUS     = r'-'
t_DIGIT     = r'\d+'
t_ignore    = r' '
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'
t_COMMA     = r','
t_PERIOD    = r'\.'
t_SEMI      = r';'
t_COLON     = r':'
#t_COMMENT   = r''
#t_comment   = r'--.*'

def t_ANY_COMMENT(t):
    r'--.*|\/\*(.|\n)*?\*\/'
    #return t
    #pass


states = (
    ('body','exclusive'),
    ('is','exclusive'),
)
def t_body_INLINE_STRING(t):
    r'\'.*?\''
def t_is_INLINE_STRING(t):
    r'\'.*?\''

# def t_body_begin(t):     
#     r'(?i)begin'
#     t.lexer.level +=1

# def t_body_end(t):
#     r'(?i)end;'
#     t.lexer.level -=1

#     # If closing brace, return the code fragment
#     if t.lexer.level == 0:
#         t.value = t.lexer.lexdata[t.lexer.code_start:t.lexer.lexpos-4]
#         t.type = "BODY"
#         #t.type = t.type.upper()
#         t.lexer.lineno += t.value.count('\n')
#         t.lexer.begin('INITIAL')
#         t.lexer.lexpos -= 4           
#         return t
# Ignored characters (whitespace)
t_body_ignore = " \t\n"


def t_body_error(t):    # For bad characters, we just skip over it
    t.lexer.skip(1)

t_is_ignore = " \t\n"
def t_is_error(t):
    t.lexer.skip(1)

#def t_is_is(t):
#    r'(?i)is'
    

# def t_is_begin(t):
#     r'(?i)begin'

#def t_body_end(t):
#    r'(?i)end\s*;'
#    return next_state(t,'INITIAL','BODY')

# def t_is_end(t):
#     r'(?i)end\s*;'
    
#     t.lexer.level  -=1
#     if t.lexer.level == 1:
#         t.lexer.flevel -=1

def begin_state(t,name):
    #print "begin state",name
    t.lexer.code_start = t.lexer.lexpos        # Record the starting position
    t.lexer.level = 1                          # Initial brace level
    t.lexer.begin(name)                        # Enter 'ccode' state
    #t.lexer.stack = []
    return t

def next_state(t,state_name,type_name):
    #print "end state",state_name
    t.lexer.level -=1
    #print "!!!!!level=",t.lexer.level
    if t.lexer.level == 0:
        t.value = t.lexer.lexdata[t.lexer.code_start:t.lexer.lexpos-5]
        t.type = type_name
        t.lexer.lineno += t.value.count('\n')
        t.lexer.begin(state_name)
        t.lexer.lexpos -= 5
        #t.value = ''
        return t

#stack = []

def t_ANY_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    state = t.lexer.current_state()
    value = t.value.upper()
    stack = t.lexer.stack

    if state in ['is','body']:
        if not value in ['FUNCTION','PROCEDURE','BEGIN','END','CASE','LOOP','IF' ]:
            return


    if value in keywords or value in oracle_types:
        t.type = value
    #print 'TYPE=',value,state
    #print 'TYPE1=',t.type,value,state
    if state == 'INITIAL':
        if value == 'IS':
            #print "1"
            
            begin_state(t,'is')
            #t.lexer.flevel = 0
            #t.lexer.level = 0
            return 
        elif value == 'BEGIN':
            #print 'BEGIN BODY'
            begin_state(t,'body')
            #return

    elif state == 'body':
        #if value == 'BEGIN':
        #    t.lexer.level +=1
        #    return
        if value == 'BEGIN':
            if stack[-1] in ['FUNCTION','PROCEDURE']:
                #print 'FUNC'
                return
            #elif stack[-1] == 'ROOT':
                #print 'ROOT'
                #return next_state(t,'INITIAL','IS')
            else:
                #print "ANON"
                stack.append('ANANYMUS_BLOCK')
                return
        elif value in ['CASE']:
            stack.append(value)
            return
        elif value in ['LOOP','IF']:
            if stack[-1] == 'END':
                stack.pop()
                stack.pop()
            else:
                stack.append(value)
            return
        elif value in ['FUNCTION','PROCEDURE']:
            stack.append(value)
            return
        elif value =='END':
            #print " ",value,stack
            if stack[-1] in ['CASE','FUNCTION','PROCEDURE','ANANYMUS_BLOCK']:
                stack.pop()
            elif stack[-1] == 'ROOT':
                #return
                return next_state(t,'INITIAL','BODY')
            else:
                #print "ADD END"
                stack.append(value)
            #print "2",value,stack
            return
        # elif value == 'END':
            
        #     t.lexer.level -= 1
        #     if t.lexer.level == 0:
        #         #print "LEXER 0"
        #         t.lexer.level += 1
        #         return next_state(t,'INITIAL','BODY')
        #     return
    elif state == 'is':
        
        if value == 'BEGIN':
            if stack[-1] in ['FUNCTION','PROCEDURE']:
                #print 'FUNC'
                return
            elif stack[-1] == 'ROOT':
                #print 'ROOT'
                return next_state(t,'INITIAL','IS')
            else:
                #print "ANON"
                stack.append('ANANYMUS_BLOCK')
                return
        elif value in ['CASE']:
            stack.append(value)
            return
        elif value in ['LOOP','IF']:
            if stack[-1] == 'END':
                stack.pop()
                stack.pop()
            else:
                stack.append(value)
            return
        elif value in ['FUNCTION','PROCEDURE']:
            stack.append(value)
            return
        elif value =='END':
            #print " ",value,stack
            if stack[-1] in ['CASE','FUNCTION','PROCEDURE','ANANYMUS_BLOCK']:
                stack.pop()
            elif stack[-1] == 'ROOT':
                return
            else:
                #print "ADD END"
                stack.append(value)
            #print "2",value,stack
            return

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
        self.return_type = ''
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
    default_section :
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
                    | declare_procedure
    '''
    #exprs.append(p[1])
    p[0] = p[1]

def p_f(p):
    '''
    declare_function : FUNCTION ID param_list_paren RETURN datatype IS declarations BEGIN BODY END SEMI
                     | FUNCTION ID param_list_paren RETURN datatype SEMI
    '''
    #print 'FUNC %s'%p[2]
    f = declare_function()
    f.name = p[2]
    f.params = p[3]
    f.return_type = p[5]
    #p[0] = 'FUNCTION %s return %s is %s'%(p[2],p[4],p[6])
    p[0] = f

def p_proc(p):
    '''
    declare_procedure : PROCEDURE ID param_list_paren IS declarations BEGIN BODY END SEMI
                      | PROCEDURE ID param_list_paren SEMI
    '''
    #print 'FUNC %s'%p[2]
    f = declare_function()
    f.name = p[2]
    f.params = p[3]
    #f.return_type = p[5]
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
def p_default_section(p):
    'default_section : DEFAULT NULL'


def p_param(p):
    'param : ID param_type datatype default_section'
    
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
             | NULL
    '''
    p[0] = p[1]

def p_user_data_type(p):
    'datatype : LBRACKET ID RBRACKET'
    p[0] = p[2]
def p_user_data_type_ref(p):
    'datatype : REF LBRACKET ID RBRACKET'
    p[0] = "ref " + p[3]
def p_user_data_type_variable(p):
    'datatype : variable'
    p[0] = 'VAR:' + p[1]
def p_variable(p):
    'variable : ID'
    p[0] = p[1]
    


def p_variable_defination(p):
    'variable_def : ID datatype SEMI'
    p[0] = 'variable %s of %s'%(p[1],p[2])

def p_error(p):
    print "Syntax error in input!"

#def t_comment(t):
    #r'(?<=begin)((.|\n)*?)(?=end)'
#    r'begin(.|\n)*?end'
#    pass

# Declare the state




class test2Command(sublime_plugin.TextCommand):
    def run(self, edit):
        from oracle import timer
        t = timer()

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
        debug = 0
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
        lexer.stack = ['ROOT']


        #lexer = lex.lex()
        data = '''  function new_func1(
                        tag_name varchar2
                        ,a in integer
                        ,b out integer ,d number(10)
                        ,c in out varchar2
                        ,e number(10,10)
                        ,h [PRCRED]
                        ,g ref [AC_FIN] default null
                        ,i hello
                        ,k      test
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
                            for j in 1..p_property.count
                            loop    
                                if p_property(j).[PROPERTY_TYPE].[CODE] like '%SERVICE_CODE%' then
                                    service_code_ref := p_property(j).[REF_VALUE];
                                    &debug('Ссылка на сервис (service_code_ref) = ' || service_code_ref, 0)
                                end if;
                            end loop;
                        hello end;
                    begin
                    end;

                    function new_func2 return varchar2 is
                    begin
                        --tag_value := DBMS_XMLGEN.convert(tag_value,0); --преобразуем ESC символы                        
                        --res_out := case when res_out is not null then res_out || chr(10) else res_out end || chr(9) ||'<'||tag_name||'>'||tag_value||'</'||tag_name||'>';
                        one more line
                        'Выполняется процедура CheckProp'
                        'end;'
                        &debug('Выполняется процедура CheckProp', 0)
                    end;

                    function new_func3 return varchar2;

                    function add_service    
                    /*Добавление сервиса*/
                    (   p_object_srv        reference
                        /*Ссылка на объект для подключения дополнительного сервиса*/
                        ,p_obj_class        ref [METACLASS]
                        /*Класс объекта для подключения дополнительного сервиса*/
                        ,p_info_obj         info_obj
                        /*Информация об объетке*/
                        ,p_service_type ref [SERVICE_DICT]
                        /*Вид услуги*/
                        ,p_property         tab_type
                        /*Параметры сервиса*/
                        ,p_take_tarif       boolean default null
                        /*Брать тариф*/
                        ,p_service      ref [CARD_SERVICES] default null
                        /*Ссылка на сервис*/
                        ,p_add_card_appl    ref [VZ_ISS_APPL] default null
                        /*Ссылка на запрос*/
                        ,p_add_par          varchar2(2000) default null
                        /*Дополнительные параметры*/
                        ,p_Date             DATE default null
                        /*Дата*/
                        ,p_Mess             out varchar2
                        /*Информационное сообщение*/
                    )
                    return ref [VZ_ISS_APPL];

                    procedure GetInfoObj
                    /*Получение информации об объекте*/
                    (   p_obj           in reference
                        /*ссылка на объект*/    
                        ,p_obj_class    in  ref[METACLASS]
                        /*класс обекта*/
                        ,p_info_obj     out info_obj
                        /*информация об объекте*/
                    );
                    procedure CheckProp
                    /* Процедура осуществляет проверку значений параметров*/
                    (
                        p_property      tab_type,
                        p_object_srv    reference,
                        p_service_type  ref [SERVICE_DICT],
                        p_card_serv     ref [CARD_SERVICES] default null
                    ) is
                        --isServCodePropsEq   boolean default false;
                        tempPropRef         ref [PROPERTY]; 
                        service_code_ref ref [UD_CODE_NAME];    
                    begin

                        &debug('Выполняется процедура CheckProp', 0)
                        for i in 1..p_property.count
                        loop
                            if p_property(i).[PROPERTY_TYPE].[CODE] = 'UCS_ADDR_TYPE' then
                                &debug('Передано свойство с кодом вида свойства "UCS_ADDR_TYPE"', 0)
                                begin
                                    -- Поиск ссылки на тип сервиса
                                    &debug('Производится выборка переданной ссылки на сервис', 0)
                                    for j in 1..p_property.count
                                    loop    
                                        if p_property(j).[PROPERTY_TYPE].[CODE] like '%SERVICE_CODE%' then
                                            service_code_ref := p_property(j).[REF_VALUE];
                                            &debug('Ссылка на сервис (service_code_ref) = ' || service_code_ref, 0)
                                        end if;
                                    end loop;
                                end;
                            end if;
                        end loop;
                    end;
        '''


        data = '''
            function EDIT_AUTO(
        P_NUM_DOG       IN      PRODUCT_NUM,            --1  Номер договора
        P_DATE_BEGIN    IN      DATE,                   --2  Дата создания договора
        P_DATE_BEGINING IN      DATE,                   --3  Дата начала действия договора
        P_DATE_CLOSE    IN      DATE,                   --4  Дата закрытия договора
        P_DATE_ENDING   IN      DATE,                   --5  Дата окончания действия договора
        P_CREATE_USER   IN      USER_REF,               --6  Создано пользователем
        P_NOTES         IN      MEMO,                   --7  Примечания
        P_COM_STATUS    IN      COM_STATUS_P_REF,       --8  Обобщенный статус продукта
        P_ARRAY_SUM_DOG IN      SUM_DOG_ARR,            --9  Суммы договора
        P_ARRAY_DOG_ACC IN      HOZ_OP_ACC_ARR,         --10 Счета договора
        P_FILIAL        IN      BRANCH_REF,             --11 Филиал
        P_ARRAY_OPER_DOG IN      DOC_COM_JOUR_ARR,      --12 Операции договора
        P_DEPART        IN      DEPART_REF,             --13 Подразделение
        P_NUM_DOG_CLIENT IN      SHORT3,                --14 Порядковый номер договора клиента
        P_PROD_INS_HISTORY IN      LOAN_INSPECT_ARR,    --15 История смены куратора договора
        P_USER_TYPE     IN      USER_TYPE_RE_ARR,       --16 Пользовательский тип
        P_INTERNAL_CODE IN      STRING_25,              --17 Внутренний код для импорта (служебный)
        P_PER_COMISSIONS IN      PERIOD_COM_ARR,        --18 Периодические комиссии
        P_REPS_PRZ      IN      REPS_PRZ_HIS_ARR,       --19 Признаки для отчётности
        P_RES_OTHER_FIL IN      RES_OTHER_FI_ARR,       --20 Формировать доходы/расходы при урегулировании резерва в другом филиале
        P_ADD_AGR_ARR   IN      ADD_AGR_ARR,            --21 Массив Дополнительных соглашений
        P_CLIENT        IN      CL_PRIV_REF,            --22 Клиент
        P_CARD          IN      VZ_CARDS_REF,           --23 Основная карта
        P_DEPN_CARD     IN      DEPOSIT_PRIV_REF,       --24 Депозит карточный
        P_DEPN_NAKOP    IN      DEPOSIT_PRIV_REF,       --25 Депозит до востребования (накопительный)
        P_DEPN_SROCH    IN      DEPOSIT_PRIV_REF        --26 Депозит срочный
    )return null
    is
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
        -- Установка значения реквизита "Примечания"
        [NOTES] := P_NOTES;
        -- Установка значения реквизита "Обобщенный статус продукта"
        [COM_STATUS] := P_COM_STATUS;
        -- Установка значения реквизита "Филиал"
        [FILIAL] := P_FILIAL;
        -- Установка значения реквизита "Подразделение"
        [DEPART] := P_DEPART;
        -- Установка значения реквизита "Порядковый номер договора клиента"
        [NUM_DOG_CLIENT] := P_NUM_DOG_CLIENT;
        -- Установка значения реквизита "Внутренний код для импорта (служебный)"
        [INTERNAL_CODE] := P_INTERNAL_CODE;
        -- Установка значения реквизита "Клиент"
        [CLIENT] := P_CLIENT;
        -- Установка значения реквизита "Основная карта"
        [CARD] := P_CARD;
        -- Установка значения реквизита "Депозит карточный"
        [DEPN_CARD] := P_DEPN_CARD;
        -- Установка значения реквизита "Депозит до востребования (накопительный)"
        [DEPN_NAKOP] := P_DEPN_NAKOP;
        -- Установка значения реквизита "Депозит срочный"
        [DEPN_SROCH] := P_DEPN_SROCH;
    end;
        '''
        #data = ''
        
        #data = text
        # from oracle import dataView
        # v = dataView(self.view)
        # text = v.sections['EXECUTE'].body.text
        # import re
        # text = re.sub(r'\n\t',r'\n',text).lstrip('\t')  #Удалим служебный таб в начале каждой строки
        # text = re.sub(r'\t',r'',text)                   #Удалим служебный таб в начале каждой строки
        # text = re.sub(r' +$','',text,re.MULTILINE)      #Удаляем все пробелы в конце строк, потому что цфт тоже их удаляет
        #print 'DATA=',text

        text = data

        lexer.input(text)
        #for tok in lexer:
        #    print tok

        p = yacc.yacc(debug=debug,
                  debugfile=debugfile,
                  tabmodule=tabmodule).parse(text)
        #print "p=",p
        #print 'STACK=',lexer.stack
        print "#"
        for a in p:
            print a
        print "#"

        print t.print_time('Разбор функций за')

        #print exprs
