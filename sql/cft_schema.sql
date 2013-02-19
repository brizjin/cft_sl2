select xmlelement("classes",xmlagg(xmlelement("class",XMLAttributes(cl.id as id,cl.name as name,rpad(cl.name,40,' ') || lpad(cl.id,30,' ')as text)
                                              ,xmlelement("meths",(select xmlagg(xmlelement("method",xmlattributes(m.id as id,m.short_name as short_name,m.name as name,rpad(m.name,40,' ') || lpad(m.short_name,30,' ')as text)) order by m.name) from methods m where m.class_id = cl.id))
                                              ,xmlelement("views",(select xmlagg(xmlelement("view",xmlattributes(cr.id as id,cr.short_name as short_name,cr.name as name))) from criteria cr where cr.class_id = cl.id))
                                              )
                                  )
                 ).getclobval() classes  
from classes cl
where (select count(1) from methods m where m.class_id = cl.id) > 0
  or (select count(1) from criteria cr where cr.class_id = cl.id) > 0
