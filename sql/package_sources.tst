PL/SQL Developer Test script 3.0
44
-- Created on 04/09/2013 by ISB5 
declare 
  -- Local variables here
  i integer;
  class_name     varchar2(200);
  method_name    varchar2(200);
  package_type   varchar2(200);
  
  function get_part(class_name varchar2,method_name varchar2,oper_type varchar2)return clob
  is
    out_clob clob;
  begin
    /*for r in (select text
              --from user_source
              from dba_source
              where name = (select m.package_name from METHODS m where m.class_id = class_name and m.short_name = method_name)
                and type = oper_type
              order by line)*/
    for r in (select text
              from user_source s
                  ,methods m                               
              where s.name = m.package_name
                and s.type = oper_type
                and m.class_id = class_name
                and m.short_name = method_name
              order by line)
    loop
      out_clob := out_clob || r.text;-- || chr(10);
    end loop;
    return ltrim(out_clob,chr(10));
  end;
  
begin
  -- Test statements here
  class_name    := :class_name;
  method_name   := :method_name;
  package_type  := :package_type;
  
  --stdio.put_line_pipe('a='||class_name||',m='||method_name,'DEBUG_PIPE');
  :s := get_part(class_name,method_name,package_type);
  --stdio.put_line_pipe('S='||:s,'DEBUG_PIPE');
exception when others then
  stdio.put_line_pipe('e='||sqlerrm,'DEBUG_PIPE');          
end;
3
s
1
<CLOB>
112
class_name
1
PR_CRED
5
method_name
1
EPL_GASH_PRIORIT
5
0
