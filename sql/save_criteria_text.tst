PL/SQL Developer Test script 3.0
31
declare 
  i integer;
  RESULT varchar2(32000);
  --IBS.rcs_lock.release('VW#70578076'); 
  --IBS.rcs_lock.request('VW#70578076');
  prop varchar2(2000);
begin
  --i := rtl.open;
  RESULT := IBS.EXECUTOR.LOCK_OPEN(NULL,'ДА');
  
  select cr.properties
  into prop
  from criteria cr where short_name = :view_short_name;
  
  RESULT := IBS.Data_Views.Create_Criterion3(:view_id,
                                             :view_name,
                                             :view_short_name,
                                             :view_class,
                                             :view_src,
                                                0,
                                                0,
                                                null,
                                                0,
                                                prop,
                                                null,
                                                null,
                                                null,
                                                null);
                                                
  IBS.Data_Views.Create_Vw_Crit(:view_id);
end;
5
view_id
1
42794440
3
view_name
1
Полный список
5
view_short_name
1
VW_CRIT_EXT_DOCS_SVOD
5
view_class
1
EXT_DOCS_SVOD
5
view_src
4
type main is ------hello
  select a (a,'HELLO356','second5')
  in ::[EXT_DOCS_SVOD]
;
5
0
