┌────────────────────────────────────────────────┐
│                    EXECUTE                     │
├────────────────────────────────────────────────┤
 begin
 	-- Установка значения реквизита "Код"
 	[CODE] := P_CODE;
 	
 	[DATE_CREATE] := sysdate;
 	-- Установка значения реквизита "Дата"
 	[DATE_REESTR] := P_DATE_REESTR;
 	-- Установка значения реквизита "Платежная система"
 	[EXT_SYS] := P_EXT_SYS;
 	-- Установка значения реквизита "Сводный документ"
 	[SVOD_DOC] := P_SVOD_DOC;
 	-- Установка значения реквизита "Валюта"
 	[VAL] := P_VAL;
 	-- Установка значения реквизита "Сумма в валюте"
 	[SUMMA] := P_SUMMA;
 	-- Установка значения реквизита "Сумма в нац. покрытии"
 	[SUMMA_NT] := P_SUMMA_NT;
 	-- Установка значения реквизита "Кол-во документов"
 	[DOCS_COUNT] := P_DOCS_COUNT;
 	-- Установка значения реквизита "Интегратор. Входящее сообщение"
 	[MSG_IN] := P_MSG_IN;
 end;
└────────────────────────────────────────────────┘
┌────────────────────────────────────────────────┐
│                    VALIDATE                    │
├────────────────────────────────────────────────┤
└────────────────────────────────────────────────┘
┌────────────────────────────────────────────────┐
│                     PUBLIC                     │
├────────────────────────────────────────────────┤
└────────────────────────────────────────────────┘
┌────────────────────────────────────────────────┐
│                    PRIVATE                     │
├────────────────────────────────────────────────┤
└────────────────────────────────────────────────┘
┌────────────────────────────────────────────────┐
│                    VBSCRIPT                    │
├────────────────────────────────────────────────┤
└────────────────────────────────────────────────┘