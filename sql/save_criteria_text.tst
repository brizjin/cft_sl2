PL/SQL Developer Test script 3.0
90
-- Created on 21/02/2013 by ISB5 
declare 
  -- Local variables here
  i integer;
  list varchar2(32000);
  p_err_compile varchar2(32000);
  b boolean;
begin
  --IBS.storage_mgr.check_user;
  i := rtl.open;
  --IBS.rcs_lock.release('VW#70578076'); 
  --IBS.rcs_lock.request('VW#70578076');
  :RESULT:=IBS.EXECUTOR.LOCK_OPEN(NULL,'ДА');
  --IBS.EXECUTOR.lock_close;
  --i := rtl.open;

  
  ibs.data_views.Create_Vw_Crit('70578076');
  :RESULT := ibs.data_views.GetVersion;
  IBS.EXECUTOR.SET_IDS('CN=manager authority, OU=reserved_OU_for_5_class, O=CFT, L=Novosibirsk, C=RU',
                       'CN=Common 1 CA, O=Center of Financial Technologies, C=RU','');
  :RESULT :=IBS.inst_info.version; 
  :RESULT :=IBS.inst_info.build_no;
  :RESULT :=IBS.inst_info.revision(); 
  IBS.storage_mgr.check_user; 
  IBS.executor.set_debug(0,IBS.executor.DEBUG2BUF); COMMIT;
  :RESULT :=IBS.Nav.Get_SysInfo('CHECK_TEMPLATE_HASH');
  --:RESULT :=IBS.javac_mgr.get_version; 


  -- Test statements here
  :RESULT :=IBS.Nav.Get_SysInfo('CARD_CONDITION'); 
  
  i := rtl.open;
  --IBS.rcs_lock.release('VW#70578076'); 
  --IBS.rcs_lock.request('VW#70578076');
  
  IBS.sysinfo.init_option_context(true);
  IBS.Data_Views.Set_Debug('0');
  :RESULT:=IBS.EXECUTOR.GET_DEBUG_TEXT('B');
  IBS.sysinfo.check_options('',P_ERR_COMPILE, true);
  
  b := IBS.executor.option_enabled('ORM.ARC.PACK');    
  :RESULT:=IBS.EXECUTOR.LOCK_OPEN(NULL,'ДА');
  :RESULT := SYS_CONTEXT('IBS_USER', 'USER_CONTEXT');
  :RESULT := SYS_CONTEXT('IBS_USER', 'USER_LOCK_OPEN');
  --b := IBS.executor.option_enabled('ORM.ARC.PACK'); 
  --IBS.sysinfo.check_options('',P_ERR_COMPILE, true);
  --:RESULT:=IBS.EXECUTOR.LOCK_OPEN(NULL,'ДА');
  :RESULT := IBS.Executor.Get_System_Id; 
  :RESULT := Dbms_Session.Unique_Session_Id; 
  Dbms_Application_Info.Set_Module('Администратор словаря данных', NULL); 
  Dbms_Application_Info.Set_Client_Info(:RESULT);
  :RESULT := IBS.EXECUTOR.LOCK_OPEN(NULL,'ДА');
  IBS.sysinfo.init_option_context(true); 
  IBS.sysinfo.find_data(list,null,null,'VALID');
  :RESULT :=IBS.sysinfo.get_lic_version; 
  -- :res:= IBS.opt_mgr.open_data('155835723', dbms_lob.lob_readonly); 
  :RESULT :=IBS.executor.get_installation_id; 
  IBS.EXECUTOR.SET_IDS('CN=manager authority, OU=reserved_OU_for_5_class, O=CFT, L=Novosibirsk, C=RU',
                       'CN=Common 1 CA, O=Center of Financial Technologies, C=RU','');
  :RESULT :=IBS.sysinfo.calc_version('CFT_BANK_2MCA');
  :RESULT :=IBS.sysinfo.calc_version('CORE');  
  IBS.sysinfo.check_options('',:s, true); 
  b := IBS.executor.option_enabled('ORM.ARC.PACK');    
  IBS.EXECUTOR.SET_IDS('CN=manager authority, OU=reserved_OU_for_5_class, O=CFT, L=Novosibirsk, C=RU',
                       'CN=Common 1 CA, O=Center of Financial Technologies, C=RU','');
  :RESULT := SYS_CONTEXT('IBS_USER', 'USER_CONTEXT');
  :RESULT := SYS_CONTEXT('IBS_USER', 'USER_LOCK_OPEN');
  
  :RES := IBS.Data_Views.Create_Criterion3('70578076',
                                                'Полный список 1',
                                                'VW_CRIT_TEST',
                                                'EXT_DOCS_SVOD',
                                                'type main is ------h
  select a (a,''HELLO356'')
  in ::[EXT_DOCS_SVOD]
;',
                                                0,
                                                0,
                                                null,
                                                4,
                                                '|AllMethods Y|HasClass|NotObjects|USERCONTEXT 0||PlPlus',
                                                null,
                                                null,
                                                null,
                                                null);
                                                
  IBS.Data_Views.Create_Vw_Crit('70578076');
end;
3
RESULT
1
'PLACEHOLDER FOR USER FUNCTION'
5
RES
1
70578076
5
S
0
5
0
