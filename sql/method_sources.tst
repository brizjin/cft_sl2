PL/SQL Developer Test script 3.0
27
declare 
  c clob;
  class_name varchar2(200);
  method_name varchar2(200);

  function get_part(class_name varchar2,method_name varchar2,oper_type varchar2)return clob
  is
    out_clob clob;
  begin
    for r in (select text
              from sources 
              where name = (select m.id from METHODS m where m.class_id = class_name and m.short_name = method_name)
                and type = oper_type order by line)
    loop
      out_clob := out_clob || r.text || chr(10);
    end loop;
    return ltrim(out_clob,chr(10));
  end;
begin
  class_name  := :class_name;
  method_name := :method_name;
  :EXECUTE    := get_part(class_name,method_name,'EXECUTE');
  :VALIDATE   := get_part(class_name,method_name,'VALIDATE');
  :PUBLIC     := get_part(class_name,method_name,'PUBLIC');
  :PRIVATE    := get_part(class_name,method_name,'PRIVATE');
  :VBSCRIPT   := get_part(class_name,method_name,'VBSCRIPT');
end;
9
class_name
1
EPL_REQUESTS
5
method_name
1
NEW_AUTO
5
oper_type
1
EXECUTE
-5
out
1
<CLOB>
-112
EXECUTE
1
<CLOB>
112
VALIDATE
1
<CLOB>
112
PUBLIC
1
<CLOB>
112
PRIVATE
1
<CLOB>
112
VBSCRIPT
1
<CLOB>
112
0
