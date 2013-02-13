PL/SQL Developer Test script 3.0
28
declare 
  xml_clob clob;
begin  
  select xmlagg( xmlelement("CLASS",xmlelement("CLASS_BODY",'&'|| cl.id ||'&:{&NAME&:&' || cl.name || '&,').extract('//CLASS_BODY/text()')
                                   ,xmlelement("METHS",(select xmlagg(xmlelement("METHOD",'&'||m.short_name||'&:{&NAME&:&'||m.name||'&},')).extract('METHOD/text()')
                                                        from methods m where m.class_id = cl.id))
                                   ,xmlelement("CLASS_BODY_END",'},').extract('//CLASS_BODY_END/text()')
                            ).extract('//CLASS/*|//CLASS/text()')

  
  ).getclobval()
  into xml_clob
  from classes cl
  where (select count(1) from methods m where m.class_id = cl.id)>0
  --  and cl.id in ('CL_GROUP','SERVICE_QUAL')
  ;
  xml_clob := '{"classes":{'||xml_clob;
  xml_clob := replace(xml_clob,'&amp;','"');
  xml_clob := replace(xml_clob,'\','');
  xml_clob := replace(xml_clob,chr(10),'');
  xml_clob := replace(xml_clob,'<METHS>','"METHS":{');
  xml_clob := replace(xml_clob,',</METHS>','}');
  xml_clob := rtrim(xml_clob,',');
  xml_clob := replace(xml_clob,',<METHS/>','');  
  xml_clob := xml_clob || '}}';  
  --:i := length(xml_clob)/1000000;
  :out_clob := xml_clob;
end;
2
out_clob
1
<CLOB>
112
i
1
2.352273
-4
0
