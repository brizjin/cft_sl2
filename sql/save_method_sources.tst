PL/SQL Developer Test script 3.0
22
declare 
  i integer;
begin
  Z$RUNTIME_PLP_TOOLS.Open_Method(:class_name,:method_name);
  Z$RUNTIME_PLP_TOOLS.Add_Method_Src('B',:b);--'EXECUTE'
  Z$RUNTIME_PLP_TOOLS.Add_Method_Src('V',:v);--'VALIDATE'
  Z$RUNTIME_PLP_TOOLS.Add_Method_Src('G',:g);--'PUBLIC'
  Z$RUNTIME_PLP_TOOLS.Add_Method_Src('L',:l);--'PRIVATE'
  Z$RUNTIME_PLP_TOOLS.Add_Method_Src('S',:s);--'VBSCRIPT'
  Z$RUNTIME_PLP_TOOLS.Update_Method_Src;
  Z$RUNTIME_PLP_TOOLS.reset;
  
  select listagg(class || ' ' || type || '  line:' || line || ',position:'||position||' \t '||text,chr(10))within group (order by line),count(1)
  into :out,:out_count
  from ERRORS t 
  where t.method_id = (select id from METHODS m
                        where m.class_id = :class_name
                          and m.short_name = :method_name)
    --and t.type = oper_type
    --and t.class != 'W'
    order by class,type,sequence,line,position,text;  
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
