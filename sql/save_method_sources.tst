PL/SQL Developer Test script 3.0
179
declare 
  i integer;
  flag boolean := true; --правка диструбитива
   method_id varchar2(200);
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
  
   procedure set_source2(class_name varchar2,method_name varchar2,section_name varchar2,text clob)
  is
    i integer := 0;
    j integer := 0;
    --end_i integer := 1;
    tmp_str varchar2(32000) := '';
    sub_str varchar2(32000) := '';
    --method_id varchar2(200);
    method_id varchar2(200);
    line_str varchar2(32000);
    v_text clob;
    t timestamp;
    --cur_poss integer;
  begin
   -- stdio.put_line_pipe('1method_id='||method_id||',class='||class_name||',method_name='||method_name,'DEBUG_PIPE');
    
    select id
    into method_id
    from methods m
    where m.class_id = class_name
      and m.short_name = method_name
    ;    
    --stdio.put_line_pipe('2method_id='||method_id||',section_name='||section_name,'DEBUG_PIPE');
        
    DELETE
    FROM SOURCES
    where type = section_name
      and name = method_id;
      
    /*INSERT INTO SOURCES (name,type,line,text)
                VALUES  (method_id,section_name,1,'TEST');*/
    --returning name
                
    v_text := text;
    
    while v_text is not null and length(v_text)>0 --and i > 0
    loop
      i := instr(v_text,chr(10));
      --stdio.put_line_pipe('i1='||i,'DEBUG_PIPE');
      i := case when i = 0 then length(v_text) + 1 else i end;
      --stdio.put_line_pipe('i2='||i||'l='||length(v_text),'DEBUG_PIPE');
      j := j + 1;
      --stdio.put_line_pipe('i='||i,'DEBUG_PIPE');
      -- extract the token
      line_str := substr(v_text,1,i-1);
      v_text   := substr(v_text,i+1);
      
      INSERT INTO SOURCES (name,type,line,text)
                  VALUES  (method_id,section_name,j,line_str);
                  
      --stdio.put_line_pipe('line='||line_str,'DEBUG_PIPE');
      -- remove everything but letters (a-z)
      --v_token := regexp_replace(v_token, '\W');
      -- now do something with this token; I'll *display* it
      --dbms_output.put_line(v_token);
      -- chop off this token from the main string


      --exit when i = 0;
      --stdio.put_line_pipe('v_text='||v_text||'|','DEBUG_PIPE');
    end loop;
    --t = current_timestamp;
    --stdio.put_line_pipe('t='||||'|','DEBUG_PIPE');  
    
    --stdio.put_line_pipe('t2='||trim('0' from trim(':' from trim('0' from substr(current_timestamp - t,15,8)))) ||'|','DEBUG_PIPE');
    
    --Z$RUNTIME_PLP_TOOLS.Add_Method_Src(section_name,tmp_str);
    --stdio.put_line_pipe('END','DEBUG_PIPE');*/
  end;
  
  
  
begin
  if flag then
  --    set_source2();
    i := rtl.open;      
    set_source2(:class_name,:method_name,'EXECUTE' ,:b);
    set_source2(:class_name,:method_name,'VALIDATE',:v);
    set_source2(:class_name,:method_name,'PUBLIC'  ,:g);
    set_source2(:class_name,:method_name,'PRIVATE' ,:l);    
    set_source2(:class_name,:method_name,'VBSCRIPT',:s);
    
    select id
    into method_id
    from methods m
    where m.class_id = :class_name
      and m.short_name = :method_name
    ;
    --stdio.put_line_pipe('Перекомпиляция','DEBUG_PIPE'); 
    METHOD.recompile(method_id,true);
    --stdio.put_line_pipe('Откомпилировали','DEBUG_PIPE'); 
    rtl.close(i);
    
  else
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
    
 end if;
 
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
11
class_name
1
VZ_PAYMENTS
5
method_name
1
DEL_PAYMENT
5
out
1
<CLOB>
112
out_count
1
2
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
4208
s
1
<CLOB>
112
out_others
16
Ошибка сохранения методов
ORA-01017: неверно имя пользователя/пароль; вход в систему запрещается
ORA-06512: на  "IBS.RTL", line 6485
ORA-06512: на  "IBS.RTL", line 6495
ORA-06512: на  "IBS.RTL", line 1397
ORA-06512: на  "IBS.PLP2PLSQL", line 11555
ORA-06512: на  "IBS.PLP2PLSQL", line 5115
ORA-06512: на  "IBS.PLP2PLSQL", line 5682
ORA-06512: на  "IBS.PLP2PLSQL", line 13116
ORA-06512: на  "IBS.PLIB", line 16476
ORA-06512: на  "IBS.PLIB", line 17182
ORA-06512: на  "IBS.METHOD", line 3927
ORA-06512: на  "IBS.METHOD", line 4262
ORA-06512: на  "IBS.METHOD", line 4272
ORA-06512: на  line 116
ORA-06512: на  line 126
5
method_nam
0
-5
0
