# -*- coding: utf-8 -*-
import sublime, sublime_plugin
#from Parser import Parser



import os







class test2Command(sublime_plugin.TextCommand):
    def run(self, edit):
        from oracle import timer
        t = timer()

        text = self.view.substr(sublime.Region(0, self.view.size()))        


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
                -- Установка значения реквизита "Депозит до востреб
                ования (накопительный)"
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
        text = '''
        pragma macro('loop_xml','
            var [3]s sys_refcursor;     
            var [3] xmltype;
            [3]s := ::[EPL_REQUESTS].[LIB_XML].xml_cursor([1],[2]);
            loop [3]s.fetch([3]); exit when [3]s%notfound;',substitute);

        pragma macro('add',
            'if obj.[1] is not null then
                if ret is null then
                    ret := obj.[1];
                else
                    ret := ret|| '', ''||obj.[1];
                end if;
            end if;
            ',
            substitute);
        '''

        
        #from PlPlus import PlPlus
        #p = PlPlus().parse(text)
        from PlPlusMacro import PlPlusMacro
        p=PlPlusMacro(debug=1).parse(text)

        print "#"
        for a in p:
            print a
        print "#"

        print t.print_time('Разбор функций за')

        #print exprs
