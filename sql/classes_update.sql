select xmlelement("classes",xmlagg(xmlelement("class",XMLAttributes(cl.id   as id
                                                                   ,cl.name as name
                                                                   ,rpad(cl.name,40,' ') || lpad(cl.id,30,' ') as text)
                                              ,xmlelement("meths",(select xmlagg(xmlelement("method",xmlattributes(m.id          as id
                                                                                                                  ,m.short_name  as short_name
                                                                                                                  ,m.name        as name
                                                                                                                  ,rpad(m.name ,40,' ') || lpad(m.short_name ,30,' ') as text)
                                                                                                    ,xmlelement("params",(select xmlagg(xmlelement("param",xmlattributes(p.position   as position
                                                                                                                                                                        ,p.short_name as short_name
                                                                                                                                                                        ,p.name       as name
                                                                                                                                                                        ,p.class_id   as class_id
                                                                                                                                                                        ,decode(p.direction,'I','IN','O','OUT','B','IN_OUT','D','DEFAULT')  as direction
                                                                                                                                                                        )
                                                                                                                                                 )order by p.position
                                                                                                                                      )
                                                                                                                         from method_parameters p
                                                                                                                         where p.method_id = m.id
                                                                                                                         ) --select xmlagg attr
                                                                                                               ) 
                                                                                           ) order by m.name --method element
                                                                                )
                                                                   from methods m
                                                                   where m.class_id = cl.id
                                                                   )--select xmlagg method
                                                         )--meths element
                                              ,xmlelement("views",(select xmlagg(xmlelement("view"  ,xmlattributes(cr.id            as id
                                                                                                                  ,cr.short_name    as short_name
                                                                                                                  ,cr.name          as name
                                                                                                                  ,rpad(cr.name,40,' ') || lpad(cr.short_name,30,' ')as text)
                                                                                           ) order by cr.name
                                                                                 )
                                                                   from criteria cr
                                                                   where cr.class_id = cl.id
                                                                   )
                                                         )
                                              ,xmlelement("attrs",(select xmlagg(xmlelement("attr"  ,xmlattributes(ca.attr_id       as short_name
                                                                                                                  ,ca.self_class_id as self_class
                                                                                                                  ,ca.name          as name
                                                                                                                  ,ca.position      as position)
                                                                                           ) order by ca.position
                                                                                 )
                                                                   from class_attributes ca
                                                                   where ca.class_id = cl.id
                                                                   )
                                                         )
                                              )--element class
                                        )--xmlagg element
                 ).getclobval() classes  
from classes cl
where 1=1
  and cl.id = :class_id
  --and cl.id = 'EXT_DOCS_SVOD'
