PL/SQL Developer Test script 3.0
54
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
    return out_clob;
  end;
  
  /*function cpad(text varchar2,n integer,c char)return varchar2
  is
  begin
    return LPAD(RPAD(text,LENGTH(text) + (n - LENGTH(text)) / 2,c),n,c);
  end;*/
  
  /*function get_with_header(class_name varchar2,method_name varchar2,oper_type varchar2)return clob
  is
    --out_clob clob;
    d varchar2(2000);
  begin
    d := '';
    --d := d || chr(10) || cpad('-',50,'-');
    --d := d || chr(10) || '--' || cpad(oper_type,46,' ') || '--';
    --d := d || chr(10) || cpad('-',50,'-') || chr(10);
    d := d || chr(10) || '';
    d := d || chr(10) || '' || cpad(oper_type,48,' ') || '';
    d := d || chr(10) || '';
    d := d || chr(10) ||  rtrim(get_part(class_name,method_name,oper_type),chr(10));
    d := d || chr(10) || '';
    return d;
    --return rtrim(d || get_part(class_name,method_name,oper_type),chr(10));
  end;*/
  
  
begin
  class_name := :class_name;
  method_name := :method_name;
  :e := ltrim(get_part(class_name,method_name,'EXECUTE'),chr(10));
  :v := get_part(class_name,method_name,'VALIDATE');
  :g := get_part(class_name,method_name,'PUBLIC');
  :l := get_part(class_name,method_name,'PRIVATE');
  :s := get_part(class_name,method_name,'VBSCRIPT');

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
oper_type
1
EXECUTE
-5
out
1
<CLOB>
-112
e
1
<CLOB>
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
