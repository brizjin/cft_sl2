PL/SQL Developer Test script 3.0
46
declare 
  i integer;
  
  procedure set_source(section_name varchar2,text clob)
  is
    i integer := 0;
  begin
    loop exit when i>length(text);
      Z$RUNTIME_PLP_TOOLS.Add_Method_Src(section_name,substr(text,i+1,i+32000));
      i := i + 32000;    
    end loop;
  end;
  
begin
  :out_count := 0;
  Z$RUNTIME_PLP_TOOLS.Open_Method(:class_name,:method_name);
  --Z$RUNTIME_PLP_TOOLS.Add_Method_Src('B',:b);--'EXECUTE'
  --Z$RUNTIME_PLP_TOOLS.Add_Method_Src('V',:v);--'VALIDATE'
  set_source('B',:b);--'EXECUTE'
  set_source('V',:v);--'VALIDATE'
--  Z$RUNTIME_PLP_TOOLS.Add_Method_Src('G',substr(:g,1,32000));--'PUBLIC'
--  if length(substr(:g,32001))>0 then
--    Z$RUNTIME_PLP_TOOLS.Add_Method_Src('G',substr(:g,32001));--'PUBLIC'
--  end if;
  set_source('G',:g);--'PUBLIC'
  --Z$RUNTIME_PLP_TOOLS.Add_Method_Src('L',:l);--'PRIVATE'
  --Z$RUNTIME_PLP_TOOLS.Add_Method_Src('S',:s);--'VBSCRIPT'
  set_source('L',:l);--'PRIVATE'
  set_source('S',:s);--'VBSCRIPT'
  Z$RUNTIME_PLP_TOOLS.Update_Method_Src;
  Z$RUNTIME_PLP_TOOLS.reset;
  
  --select listagg(class || ' ' || type || '  line:' || line || ',position:'||position||' \t '||text,chr(10))within group (order by line),count(1)
  select regexp_replace(xmlagg(xmlelement("ERROR",class || ' ' || type || '  line:' || line || ',position:'||position||' \t '||text,chr(10))).getclobval(),'<ERROR>|</ERROR>',''),count(1)
  into :out,:out_count
  from ERRORS t 
  where t.method_id = (select id from METHODS m
                        where m.class_id = :class_name
                          and m.short_name = :method_name)
    --and t.type = oper_type
    --and t.class != 'W'
    order by class,type,sequence,line,position,text;
exception when others then
  :out_others := :out || 'Ошибка сохранения методов' || chr(10) || sqlerrm || chr(10) || dbms_utility.format_error_backtrace;
  :out_count := 1;
end;
9
class_name
1
EXT_DOCS_SVOD
5
method_name
1
NEW_AUTO
5
out
1
<CLOB>
112
out_count
1
0
3
b
1
п»ї<CLOB>
112
v
1
<CLOB>
112
g
1
<CLOB>
112
l
1
<CLOB>
112
s
1
<CLOB>
112
0
