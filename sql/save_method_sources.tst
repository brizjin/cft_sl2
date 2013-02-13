PL/SQL Developer Test script 3.0
124
declare
   class_name varchar2(200);
   method_name varchar2(200);
   b clob;
   v clob;
   g clob;
   l clob;
   s clob;
   vsep varchar2(200) := '--------------------------------------------------
--                   VALIDATE                   --
--------------------------------------------------';
   gsep varchar2(200) := '--------------------------------------------------
--                    PUBLIC                    --
--------------------------------------------------';
   lsep varchar2(200) := '--------------------------------------------------
--                   PRIVATE                    --
--------------------------------------------------';
   ssep varchar2(200) := '--------------------------------------------------
--                   VBSCRIPT                   --
--------------------------------------------------';

   bend integer;
   vend integer;
   gend integer;
   lend integer;
   send integer;

   vstart integer;
   gstart integer;
   lstart integer;
   sstart integer;
   
   err_clob clob;
   src clob;
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
     return rtrim(out_clob,chr(10));
   end;
       
   procedure save_method(class_name varchar2,method_name varchar2,oper_type varchar2,src clob)
   is
     method_type varchar2(10);
     part clob;
     sources clob;
   begin
     --sources := regexp_replace(src,' +'||chr(10),chr(10));
     sources := src;
     part := get_part(class_name,method_name,oper_type);
          
     if part = sources or ((length(part)=0 or part is null) and (length(sources)=0 or sources is null)) then
       --STDIO.PUT_LINE_PIPE(oper_type || ' не изменился,' || length(part) || ',' || length(sources) ,'DEBUG_PIPE');
       return;
     end if;
     --STDIO.PUT_LINE_PIPE(oper_type || ',source=' || sources || ',' || length(sources) ,'DEBUG_PIPE');
     method_type := case oper_type
                    when 'EXECUTE'   then 'B'
                    when 'VALIDATE'  then 'V'
                    when 'PUBLIC'    then 'G'
                    when 'PRIVATE'   then 'L'
                    when 'VBSCRIPT'  then 'S'
                    end;

     
     Z$RUNTIME_PLP_TOOLS.Add_Method_Src(method_type,sources);
                    
   end;
begin   
  class_name    := :class_name;
  method_name   := :method_name;
  src           := :source_code;

  bend:= instr(src,vsep);
  b := substr(src,0,bend-2);

  
  vstart := bend+length(vsep)+1;
  vend:= instr(src,gsep);
  v := substr(src,vstart,vend-vstart-1);

  gstart := vend+length(gsep)+1;
  gend:= instr(src,lsep);
  g := substr(src,gstart,gend-gstart-1);
  
  lstart := gend+length(lsep)+1;
  lend:= instr(src,ssep);
  l := substr(src,lstart,lend-lstart-1);
  
  sstart := lend+length(ssep)+1;
  send:= length(src)+1;
  s := substr(src,sstart,send-sstart);
  
  Z$RUNTIME_PLP_TOOLS.Open_Method(class_name,method_name);
  
  save_method(class_name,method_name,'EXECUTE'   ,b);
  save_method(class_name,method_name,'VALIDATE'  ,v);
  save_method(class_name,method_name,'PUBLIC'    ,g);
  save_method(class_name,method_name,'PRIVATE'   ,l);
  save_method(class_name,method_name,'VBSCRIPT'  ,s);
  
  Z$RUNTIME_PLP_TOOLS.Update_Method_Src;
  --Z$RUNTIME_PLP_TOOLS.Compile_Method;
  Z$RUNTIME_PLP_TOOLS.reset;

  
  select listagg(class || ' ' || type || '  line:' || line || ',position:'||position||' \t '||text,chr(10))within group (order by line),count(1)
  into :out,:out_count
  from ERRORS t 
  where t.method_id = (select id from METHODS m
                        where m.class_id = class_name
                          and m.short_name = method_name)
    --and t.type = oper_type
    and t.class != 'W'
    order by class,type,sequence,line,position,text;

end;
5
out
1
<CLOB>
112
class_name
1
EXT_DOCS_SVOD
5
method_name
1
NEW_AUTO
5
source_code
1
<CLOB>
112
out_count
1
0
3
0
