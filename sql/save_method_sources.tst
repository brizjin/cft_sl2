PL/SQL Developer Test script 3.0
80
declare 
  i integer;
  
  /*procedure set_source(section_name varchar2,text clob)
  is
    i integer := 0;
  begin
    loop exit when i>length(text);
      Z$RUNTIME_PLP_TOOLS.Add_Method_Src(section_name,substr(text,i+1,i+32000));
      i := i + 32000;    
    end loop;
  end;*/
  /*procedure set_source(section_name varchar2,text clob)
  is
    i integer := 1;
    end_i integer := 1;
  begin
    loop exit when i>length(text);
      end_i := instr(text,chr(10),i);
      if end_i = 0 then
        end_i := length(text)+1;      
      end if;
      Z$RUNTIME_PLP_TOOLS.Add_Method_Src(section_name,substr(text,i,end_i-i));
      --stdio.put_line_pipe('i='||i||',end_i='||end_i||',text='||substr(text,i,end_i-i),'DEBUG_PIPE');
      i := end_i + 1;    
    end loop;
    stdio.put_line_pipe('END','DEBUG_PIPE');
  end;*/
  procedure set_source(section_name varchar2,text clob)
  is
    i integer := 1;
    end_i integer := 1;
    tmp_str varchar2(32000) := '';
    sub_str varchar2(32000) := '';
  begin
    loop exit when i>length(text);
      end_i := instr(text,chr(10),i);
      if end_i = 0 then
        end_i := length(text)+1;      
      end if;
      sub_str := substr(text,i,end_i-i+1);
      if length(tmp_str) + length(sub_str) > 32000 then        
        Z$RUNTIME_PLP_TOOLS.Add_Method_Src(section_name,tmp_str);
        --stdio.put_line_pipe('i='||length(tmp_str),'DEBUG_PIPE');
        tmp_str := sub_str;
      else
        tmp_str := tmp_str || sub_str;  
      end if;
      --stdio.put_line_pipe('i='||i||',end_i='||end_i||',text='||substr(text,i,end_i-i),'DEBUG_PIPE');
      i := end_i+1;    
    end loop;
    Z$RUNTIME_PLP_TOOLS.Add_Method_Src(section_name,tmp_str);
    --stdio.put_line_pipe('END','DEBUG_PIPE');
  end;
begin
  :out_count := 0;
  Z$RUNTIME_PLP_TOOLS.reset;
  Z$RUNTIME_PLP_TOOLS.Open_Method(:class_name,:method_name);
  set_source('B',:b);--'EXECUTE'
  set_source('V',:v);--'VALIDATE'
  set_source('G',:g);--'PUBLIC'
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
