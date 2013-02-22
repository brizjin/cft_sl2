# -*- coding: utf-8 -*-
import sublime, sublime_plugin, sublime_plugin
import re
import json
import cx_Oracle
import os
import sublime
import threading,thread
import datetime,time
import xml.parsers.expat
plugin_name = "CFT"
plugin_path = os.path.join(sublime.packages_path(),plugin_name)
cache_path  = os.path.join(plugin_path,"cache")

TIMER_DEBUG = True
#import cftdb
#from cftdb import call_async

class Hello(object):
	"""docstring for Hello"""
	def __init__(self, arg):
		super(Hello, self).__init__()
		self.arg = arg
class PathHelper(object):
	"""docstring for PathHelper"""
	def __init__(self, file_name):
		super(PathHelper, self).__init__()
		#self.arg = arg

		types = {			
			'B' : 'EXECUTE',	#тело
			'V' : 'VALIDATE',	#проверка
			'G' : 'PUBLIC',		#глобальные описания
			'L' : 'PRIVATE',	#локальные описания
			'S' : 'VBSCRIPT',	#клиент-скрипт
			'IBSO_METHOD' : 'METHODS',
			'RUN_SQL' : 'RUN_SQL',
		}

		full_file_name = file_name
		path_parts = full_file_name.split('\\')
		count = len(path_parts)
		self.file_name = path_parts[count-1]
		self.oper_name = path_parts[count-1].split('.')[0].upper()
		self.extention = path_parts[count-1].split('.')[1].upper()
		self.class_name = path_parts[count-2].upper()
		self.type = types[self.extention]
class NewCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		p = PathHelper(self.view.file_name())
		method_id = self.Create_Method(p.class_name,p.oper_name,'HELLO!!!')
		self.view.insert(edit, self.view.size(),method_id )

	def Create_Method(self,class_name,oper_name,full_name):
		connection = cx_Oracle.connect('ibs/ibs@cfttest')
		cursor = connection.cursor()

		method_id = cursor.var(cx_Oracle.STRING)
		
		plsql = """
			BEGIN 
				:method_id := Z$RUNTIME_PLP_TOOLS.Create_Method(:p_Class, :p_Short_Name, :p_Full_Name);
			END;
		"""
		execute_proc = cursor.execute(plsql, (method_id,class_name, oper_name, full_name))

		cursor.close()
		connection.close()

		return method_id.getvalue();
class UpdateCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		p = PathHelper(self.view.file_name())
		print ''
		if p.extention == 'IBSO_METHOD':
			self.view.replace(edit,sublime.Region(0,self.view.size()),'')
			self.PrintSection(edit,p,'EXECUTE')
			self.PrintSection(edit,p,'VALIDATE')
			self.PrintSection(edit,p,'PUBLIC')
			self.PrintSection(edit,p,'PRIVATE')
			self.PrintSection(edit,p,'VBSCRIPT')
		else:
			method_text = self.Update_Method(p.class_name,p.oper_name,p.type)
			self.view.replace(edit,sublime.Region(0,self.view.size()),method_text)

	def PrintSection(self,edit,path_helper,type_str):
		if self.view.size()>0:
			self.view.insert(edit,self.view.size(),'\n')
		self.view.insert(edit,self.view.size(),'------------------------------------------------')
		self.view.insert(edit,self.view.size(),'\n--	             %s                     --' % (type_str))
		self.view.insert(edit,self.view.size(),'\n------------------------------------------------')
		method_text = self.Update_Method(path_helper.class_name,path_helper.oper_name,type_str)
		if len(method_text)>0:
			self.view.insert(edit,self.view.size(),'\n')
		self.view.insert(edit,self.view.size(),method_text)

	def Update_Method(self,class_name,oper_name,oper_type):
		

		cnn_str = 'ibs/ibs@cfttest'
		connection = cx_Oracle.connect(cnn_str)
		cursor = connection.cursor()

		sql = """select text from sources where name = (select m.id from METHODS m where m.class_id = :class_name and m.short_name = :oper_name) and type = :oper_type order by line"""
		#print sql
		cursor.execute(sql, (class_name, oper_name.upper(), oper_type))
		

		method_text = ''
		
		for text in cursor.fetchall():
			#sublime.status_message("text=" + text)
			for s in text:
				try:
					if s == None:
						method_text += u'\n'
					else:
						method_text += unicode(s,'1251')
				except:
					pass#self.view.insert(edit, self.view.size(), u'%%%%%%%%')
			method_text += u'\n'

		method_text = method_text.rstrip(u'\n')

		cursor.close()
		connection.close()
		
		
		#print u"Текст операции ::[%s].[%s] успешно загружен" % (class_name,oper_name)
		print u"%s Текст операции ::[%s].[%s]-%s успешно загружен" % (str(datetime.datetime.now()),class_name,oper_name,oper_type)
		sublime.status_message(u"\n%s Текст операции ::[%s].[%s]-%s успешно загружен" % (str(datetime.datetime.now()),class_name,oper_name,oper_type))
		return method_text
class uploadCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		#path = PathHelper(self.view.file_name())
		class obj(object):
			def __init__(self):
				self.class_name = 'EXT_DOCS_SVOD'
				self.oper_name  = 'NEW_AUTO'
				self.extention  = 'IBSO_METHOD'
				
		path = obj()
		
		err_msg = []
		#err_msg.append('')
		if path.extention == 'IBSO_METHOD':
			src_text = sublime.Region(0,self.view.size())
			src_text = self.view.substr(src_text)
			
			regexp = r'-+\n-+(.)*-+\n-+'
			#print regexp
			p = re.compile(regexp)
			arr = p.split(src_text)

			B = arr[2].strip('\n')
			V = arr[4].strip('\n')
			G = arr[6].strip('\n')
			L = arr[8].strip('\n')
			S = arr[10].strip('\n')
			#print 'B=' + B
			# print 'V=' + V
			# print 'G=' + G
			# print 'L=' + L
			# print 'S=' + S

			self.Upload(path.class_name,path.oper_name,err_msg,'B',B)
			self.Upload(path.class_name,path.oper_name,err_msg,'V',V)
			self.Upload(path.class_name,path.oper_name,err_msg,'G',G)
			self.Upload(path.class_name,path.oper_name,err_msg,'L',L)
			self.Upload(path.class_name,path.oper_name,err_msg,'S',S)
		else:
			self.Upload(path.class_name,path.oper_name,err_msg,path.extention,self.view.substr(src_text))
		#self.view.insert(edit, self.view.size(),method_id )
		d = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
		if len(err_msg)>0:
			print u"%s Ошибки при сохранении операции ::[%s].[%s]" % (d,path.class_name,path.oper_name)
			for s in err_msg:
				print s

		else:
			print u"%s Операция ::[%s].[%s] успешно скомпилирована" % (d,path.class_name,path.oper_name)
		

	def Upload(self,class_name,oper_name,err_msg,oper_type,src_text):
		print u"1[%s]" % (datetime.datetime.now())
		connection = cx_Oracle.connect('ibs/ibs@cfttest')
		cursor = connection.cursor()
		oper_type = str(oper_type)
		print u"2[%s]" % (datetime.datetime.now())

		cursor.setinputsizes(p_Src=cx_Oracle.CLOB)
		#str_sqlerrm = cursor.var(cx_Oracle.STRING)
		#src_text = cursor.var(cx_Oracle.CLOB)

		plsql = """
			BEGIN			
				Z$RUNTIME_PLP_TOOLS.Open_Method(:p_class_name,:p_oper);
				Z$RUNTIME_PLP_TOOLS.Add_Method_Src(:p_oper_type,:p_Src);
				Z$RUNTIME_PLP_TOOLS.Update_Method_Src;
				Z$RUNTIME_PLP_TOOLS.reset;
			END;"""

		try:
			execute_proc = cursor.execute(plsql
									 ,p_Src = src_text
									 ,p_class_name = class_name
									 ,p_oper = oper_name
									 ,p_oper_type = oper_type
									 )
		except cx_Oracle.DatabaseError as e:
			error, = e.args
			print 'Ошибка сохранения ORA-0' + str(error.code)
		print u"3[%s]" % (datetime.datetime.now())


		t = {
			'B' : 'EXECUTE',
			'V'	: 'VALIDATE',
			'G'	: 'PUBLIC',
			'L'	: 'LOCAL',
			'S' : 'SCRIPT',
			}

		sql = """
			select class || ' ' || type || '  line:' || line || ',position:'||position||' \t '||text from ERRORS t
			where t.method_id = (select id from METHODS m
								  where m.class_id = :p_class_name
								    and m.short_name = :p_oper_name)
			  and t.type = :error_block
			  and t.class != 'W'
			order by class,type,sequence,line,position,text
			"""
		cursor.execute(sql, p_class_name = class_name, p_oper_name = oper_name,error_block = t[oper_type])
		print u"4[%s]" % (datetime.datetime.now())
		#arr = cursor.fetchall()
		#if len(arr)>0:
			

		for text in cursor.fetchall():
			#d = datetime.datetime.now()
			#err_msg += u"%s ошибки при сохранении операции ::[%s].[%s]-%s\n" % (d,class_name,oper_name,oper_type)
			err_msg.append(u'*** %s *** %s' % (oper_type,unicode(text[0],'1251')))
			#print u'*** %s *** %s' % (oper_type,unicode(text[0],'1251'))
			#print unicode('*** ' + s,'1251')
		print u"5[%s]" % (datetime.datetime.now())
		cursor.close()
		connection.close()
		print u"6[%s]" % (datetime.datetime.now())
class runsqlCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		d1 = datetime.datetime.now()
		#print 'Hello'
		path = PathHelper(self.view.file_name())
		#print path.extention
		# #err_msg = []
		# #err_msg.append('')
		if path.extention == 'RUN_SQL':
		 	src_text = sublime.Region(0,self.view.size())
		 	src_text = self.view.substr(src_text)
			regexp = r'---------------------'
			p = re.compile(regexp)
			arr = p.split(src_text)
			#print arr[3]
		 	dic = json.loads(arr[0])

		 	cnn = dic['connection_string']
		 	sql = dic['sql']
		 	xml_file_name = dic['xml_file_name']
		 	xml_file_index = dic['xml_file_index']
		 	#arr[1].strip('\n')
		 	xslt = arr[2].strip('\n')
		 	xml_file_clob = arr[xml_file_index].strip('\n')
		 	#print cnn
		 	#print sql
		 	#print xml_file_clob
		 	#print xml_file_name


			connection = cx_Oracle.connect(cnn)
			cursor = connection.cursor()
			cursor.setinputsizes(xslt=cx_Oracle.CLOB)
			cursor.execute(sql, xslt = xslt)
			connection.commit()

			plsql = """
			BEGIN			
				Z$CIT_ABONENT_LIB_XML.CLOB_TO_FILE(:xml_file_clob,:xml_file_name);
			END;"""
			cursor.setinputsizes(xml_file_clob=cx_Oracle.CLOB)
			cursor.execute(plsql,xml_file_clob = xml_file_clob,xml_file_name = xml_file_name)
			cursor.close()
			connection.close()

		print ''
		print u"%s SQL выполнен за %sсек" % (datetime.datetime.now().strftime("%H:%M:%S"),datetime.datetime.now()-d1)
			


		# 	# regexp = r'-+\n-+(.)*-+\n-+'
		# 	# #print regexp
		# 	# p = re.compile(regexp)
		# 	# arr = p.split(src_text)

		# 	# B = arr[2].strip('\n')
		# 	# V = arr[4].strip('\n')
		# 	# print B
		# 	# print V
class inputCommand(sublime_plugin.WindowCommand):
	def run(self):
		#print self.window#.__class__.showQuickPanel("hello window","","content")
		#for m in dir(self.window):
		#	if callable(getattr(self.window,m)):
		#		print m
		
		#self.window.show_quick_panel(["hello window","2"],self.m)
	
		self.window.show_input_panel("s1","s2",
			self.on_done, self.on_change, self.on_cancel)

	def on_done(self, input):
		pass

	def on_change(self, input):
		pass

	def on_cancel(self):
		pass
class quickCommand(sublime_plugin.WindowCommand):

	def run(self):
		global a
		
		if a == []:
			cnn_str = 'ibs/ibs@cfttest'
			connection = cx_Oracle.connect(cnn_str)
			cursor = connection.cursor()

			#sql = """select m.class_id || '.' || m.short_name || '@' || c.name || '.' || m.name  from methods m,classes c where m.class_id = c.id order by nvl(m.modified,to_date('01.01.0001','dd.mm.yyyy')) desc"""
			sql = """select c.id || '@' || c.name from classes c 
					 order by nvl(c.modified,to_date('01.01.0001','dd.mm.yyyy')) desc"""
			cursor.execute(sql)

			a = [unicode(text[0],'1251') for text in cursor.fetchall()]

			#a = ["a","b"]
			#for text in cursor.fetchall():
			#	a.append(text)

		self.window.show_quick_panel(a,self.on_done,sublime.MONOSPACE_FONT)
		
		#print "show_quick_panel"

	def on_done(self, c):
		print c
def with_exec_time(callback):
	dbeg = datetime.datetime.now()
	r = None
	if callback:
		r = callback()
	delta = datetime.datetime.now() - dbeg
	delta_str = (datetime.datetime.min + delta).time().strftime("%H:%M:%S.%f").strip("0:")

	print callback.__name__ + ', выполнена за ' + delta_str
	return r
def call_async(call_func,on_complete=None,msg=None,async_callback=False):
	class ThreadProgress():
	    def __init__(self, thread, message):
	        self.thread = thread
	        self.message = message	        
	        self.addend = 1
	        self.size = 8
	        self.d_begin = datetime.datetime.now()
	        sublime.set_timeout(lambda: self.run(0), 100)

	    def run(self, i):
	        if not self.thread.is_alive():
	            if hasattr(self.thread, 'result') and not self.thread.result:
	                sublime.status_message('')
	                return
	            delta = datetime.datetime.now() - self.d_begin
	            delta_str = (datetime.datetime.min + delta).time().strftime("%H:%M:%S.%f").strip("0:")            
	            how_long = unicode("Выполненно за %s сек" % delta_str,'utf-8')
	            how_long = unicode(self.message + ". ",'utf-8') + how_long if self.message else how_long
	            sublime.status_message(how_long)
	            return

	        before = i % self.size
	        after = (self.size - 1) - before

	        sublime.status_message('%s [%s=%s]' % \
	            (unicode(self.message,'utf-8'), ' ' * before, ' ' * after))

	        if not after:
	            self.addend = -1
	        if not before:
	            self.addend = 1
	        i += self.addend

	        sublime.set_timeout(lambda: self.run(i), 100)
	class RunInThread(threading.Thread):
		def run(self):
			if msg:
				ThreadProgress(self,msg)
			#t = timer()
			self.result = call_func()
			#t.print_time(msg + ' ' if msg else '' + "call_async func:" + call_func.__name__)
			if on_complete:
				def on_done():
					#t = timer()
					if not self.result:
						on_complete()
					elif self.result.__class__ == tuple:
						on_complete(*self.result)
					else:
						on_complete(self.result)
					#t.print_time(msg + ' ' + "call_async on_complete:" + on_complete.__name__)
				if async_callback:
					on_done()
				else:
					sublime.set_timeout(on_done, 0)
				
	RunInThread(on_complete).start()

class cft_settings_class(dict):
	def __init__(self):
		super(cft_settings_class,self).__init__()
		self.file_path = os.path.join(plugin_path,"cache","cft_settings.json")
		self["used_classes"] = list()
		call_async(self.load)
	def save(self):
		f = open(self.file_path,"w")
		f.write(json.dumps(self))
		f.close()
	def load(self):
		r = file.read(self.file_path)
		if len(r)>0:
			a = json.loads(r)
			super(cft_settings_class,self).__init__(json.loads(r))
	def update_used_class(self,class_id):
		used_classes = cft_settings["used_classes"]
		if class_id in used_classes:
			used_classes.remove(class_id)				
		used_classes.insert(0,class_id)		
		cft_settings.save()

cft_settings = cft_settings_class()


class timer(object):
	def __init__(self):
		self.begin = datetime.datetime.now()
		self.last = datetime.datetime.now()
	def get_time_delta_str(self,begin,end):
		delta 		= end - begin
		delta_str 	= (datetime.datetime.min + delta).time().strftime("%H:%M:%S.%f").strip("0:") 
		return delta_str
	def get_time(self):
		#delta 		= datetime.datetime.now() - self.begin
		#delta_str 	= (datetime.datetime.min + delta).time().strftime("%H:%M:%S.%f").strip("0:") 
		#return delta_str
		return self.get_time_delta_str(self.begin,datetime.datetime.now())
	def get_now(self):
		return datetime.datetime.now().strftime("%H:%M:%S")
	def print_time(self,text):
		if TIMER_DEBUG:
			print text,"за",self.get_time(),"сек."
			self.last = datetime.datetime.now()	
	def print_interval(self,text):
		if TIMER_DEBUG:
			print "%-6s"%self.get_time(),"%-6s"%self.get_time_delta_str(self.last,datetime.datetime.now()),text
			self.last = datetime.datetime.now()
class EventHook(object):

    def __init__(self):
        self.__handlers = []

    def __iadd__(self, handler):
        self.__handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.__handlers.remove(handler)
        return self

    def fire(self, *args, **keywargs):
        for handler in self.__handlers:
            handler(*args, **keywargs)

    def clearObjectHandlers(self, inObject):
        for theHandler in self.__handlers:
            if theHandler.im_self == inObject:
                self -= theHandler

class FileReader(object):
	def __init__(self):
		self.dir_path = os.path.join(sublime.packages_path(),plugin_name,"sql")
		self.load()
		#call_async(self.load)
	
	def substr(self,p_str,from_str,to_str,p_start=0):
		begin = p_str.find(from_str,p_start)+1
		end = p_str.find(to_str,p_start)
		return p_str[begin:end].strip()

	def sub(self,p_str,from_str,to_str,p_start=0):
		begin = p_str.find(from_str,p_start)#-len(from_str)
		end = p_str.rfind(to_str,p_start)+len(to_str)
		return p_str[begin:end].strip()

	def read(self,file_path):
		f = open(os.path.join(self.dir_path,file_path),"r")
		text = f.read()
		f.close()

		fileName, fileExtension = os.path.splitext(file_path)
		if fileExtension == '.tst':
			text = self.sub(text,"declare","end;")
		return text

	def load(self):
		#t = timer()
		self.cft_schema_sql = self.read("cft_schema.sql")		
		self.method_sources = self.read("method_sources.tst")
		self.save_method_sources = self.read("save_method_sources.tst")
		self.method_sources_json = self.read("method_sources_json.tst")
		#t.print_time("Тексты sql загружены за")
		#print self.cft_schema
		#print "file_loading_completed"
class file(object):
	def sub(p_str,from_str,to_str,p_start=0):
		begin = p_str.find(from_str,p_start)#-len(from_str)
		end = p_str.rfind(to_str,p_start)+len(to_str)
		return p_str[begin:end].strip()
	@staticmethod
	def read(file_path):
		#file_path = os.path.join(sublime.packages_path(),plugin_name,file_path)
		#t = timer()
		if not os.path.exists(file_path):
			return ''

		f = open(file_path,"r")
		text = f.read()
		f.close()

		fileName, fileExtension = os.path.splitext(file_path)
		if fileExtension == '.tst':
			text = sub(text,"declare","end;")
		#t.print_time("file.read" + file_path)
		return text

	@staticmethod
	def write(file_path,text):
		#file_path = os.path.join(sublime.packages_path(),plugin_name,file_path)
		f = open(file_path,"w")
		f.write(text)
		f.close()


class cftDB(object):
	class db_row(object):
		def __init__(self,db,p_list):			
			self.db = db
			if p_list.__class__ == dict:
				#super(db_row,self).__init__(p_list.values())			
				for k,v in p_list.iteritems():
					setattr(self,k.lower(),v)
			else:
				#super(db_row,self).__init__(p_list)
				for d in p_list:
					setattr(self,d[0],d[1])
		def __getitem__(self,index):
			return self.dir()[index]
	class class_row(db_row):
		def __init__(self, db, p_list):
			super(cftDB.class_row, self).__init__(db,p_list)
			self.meths = dict()
			self.views = dict()
		def add_method(self,attrs):
			m = cftDB.method_row(self.db,self,attrs)
			self.meths[m.id] = m
		def add_view(self,attrs):
			v = cftDB.view_row(self.db,self,attrs)
			self.views[v.id] = v
		def get_objects(self):
			objs = []
			objs.extend([mv for mk,mv in self.meths.iteritems()])
			objs.extend([vv for vk,vv in self.views.iteritems()])
			objs.sort(lambda objs,: objs.name)
			return objs

	class method_row(db_row):
		def __init__(self, db, p_class, p_list):
			super(cftDB.method_row, self).__init__(db,p_list)
			self.class_ref = p_class
		def get_sources(self):
			text_out = self.db.cursor.var(cx_Oracle.CLOB)
			self.db.cursor.execute(self.db.fr.method_sources,(self.class_ref.id, self.short_name.upper(),text_out))
			return unicode(text_out.getvalue().read(),'1251')
		def set_sources(self,value):
			#print "set_sources_method",value
			try:
				t = timer()
				#print value

				self.db.cursor.setinputsizes(source_code=cx_Oracle.CLOB)
				err_clob = self.db.cursor.var(cx_Oracle.CLOB)
				err_num  = self.db.cursor.var(cx_Oracle.NUMBER)
				self.db.cursor.execute(self.db.fr.save_method_sources,class_name=self.class_ref.id, method_name=self.short_name.upper(),source_code=value,out=err_clob,out_count=err_num)				
				err_num = int(err_num.getvalue())
				if err_num == 0:
					sublime.status_message(u"Успешно откомпилированно за %s сек" % t.get_time())
					print u"Успешно откомпилированно за %s сек" % t.get_time()
				else:
					err_msg = unicode(err_clob.getvalue().read(),'1251').strip()
					sublime.active_window().run_command('show_panel', {"panel": "console", "toggle": "true"})
					sublime.status_message(u"Ошибок компиляции %s за %s сек" % (err_num,t.get_time()))
					print "**********************************************"
					print "** %s" % t.get_now()
					print err_msg
				self.db.connection.commit()
			except cx_Oracle.DatabaseError as e:
				error, = e.args
				if error.__class__.__name__ == 'str':
					print "error=",error
				else:
					print "cx_Oracle.DatabaseError во время вызова метода select. ",error.code,error.message,error.context,e
		def get_text(self):
			#return [self.text,u"Метод"]
			return u"Метод:         " + self.text

	class view_row(db_row):	
		def __init__(self, db, p_class, p_list):
			super(cftDB.view_row, self).__init__(db,p_list)
			self.class_ref = p_class
		def get_text(self):
			#return [self.text,u"Представление"]
			return u"Представление: " + self.text

	def __init__(self):
		self.on_classes_cache_loaded = EventHook()
		self.on_methods_cache_loaded = EventHook()
		self.is_methods_ready = False

	def connect(self,connection_string):
		self.connection_string 	= connection_string
		call_async(self.load_classes)
		call_async(self.load)
		call_async(self.read_sql)
	def read_sql(self):
		self.fr = FileReader()
	def load(self):
		self.connection 	= cx_Oracle.connect(self.connection_string)		
		self.cursor 		= self.connection.cursor()
		return 1
	def select_classes(self):
		sql = """select xmlelement(classes,xmlagg(xmlelement(class,XMLAttributes(cl.id as id,cl.name as name,rpad(cl.name,40,' ') || lpad(cl.id,30,' ')as text)))).getclobval() c from classes cl
				 where (select count(1) from methods m where m.class_id = cl.id) > 0
  				 	or (select count(1) from criteria cr where cr.class_id = cl.id) > 0"""

		value = self.select_in_tmp_connection(sql)
		return value
		
	def load_classes(self):
		call_async(lambda:(file.read(os.path.join(cache_path,"classes.xml")),"class_cache"),self.parse,async_callback=True)
		call_async(self.select_classes,lambda *args:self.save_and_parse(os.path.join(cache_path,"classes.xml"),*args),async_callback=True)
		
		call_async(lambda:(file.read(os.path.join(cache_path,"methods.xml")),"methods_cache"),self.parse,async_callback=True)
		call_async(lambda:self.select_in_tmp_connection(file.read(os.path.join(plugin_path,"sql","cft_schema.sql"))),
				   lambda *args:self.save_and_parse(os.path.join(cache_path,"methods.xml"),*args),async_callback=True)
	def is_connected(self):
		#return hasattr(self,"cursor") and hasattr(self,"connection") and self.select("select * from dual")[0][0] == 'X'
		try:
			if hasattr(self,"connection"):
				self.connection.ping()
				return True
			else:
				return False
		except Exception, e:
			return False
		

	def select(self,sql,*args):

		return self.select_cursor(self.cursor,sql,*args)
	def select_in_tmp_connection(self,sql,*args):
		connection 	= cx_Oracle.connect(self.connection_string)
		cursor 		= connection.cursor()
		value 		= self.select_cursor(cursor,sql,*args)
		cursor.close()
		connection.close()
		return value
	def select_cursor(self,cursor,sql,*args):
		try:			
			cursor.execute(sql,args)			
			desc  = [d[0].lower() for d in cursor.description]						
			table = [[(lambda: unicode(t,'1251') if t.__class__ == str else t)() for t in row] for row in cursor]#Конвертнем все строковые значения в юникод				
			table = [[(lambda: "" if not t else t)() for t in row] for row in table] #Заменяем все значение None на пустую строку
			
			#print "desc_len=",len(desc),"table_len",len(table)
			#value = None
			if len(desc)==1 and len(table)==1:
				if t.__class__.__name__ == 'LOB':
					lob_str = table[0][0].read()
					return lob_str
				else:
					return table[0][0]
			else:
				return [cftDB.db_row(self,zip(desc,row)) for row in table]
			
		except cx_Oracle.DatabaseError as e:
			error, = e.args
			if error.__class__.__name__ == 'str':
				print "error",error
			elif error.code == 28:#ошибка нет подключения
				return []
			else:
				print "cx_Oracle.DatabaseError во время вызова метода select. ",error.code,error.message,error.context,e
			#return []

	def get_sid(self):

		return self.select("select sys_context('userenv','sid') sid, sid from v$mystat where rownum=1")[0]["sid"]
	def save_and_parse(self,file_name,txt,type=None):
		file.write(file_name,txt)
		self.parse(txt,type)
	def parse(self,txt,type=None):
		class ParseXml(object):	
			def __init__(self,xml_text):
				self.xml_text = xml_text
				self.cur_class = None
				self.classes = dict()

				self.parser = xml.parsers.expat.ParserCreate()
				self.parser.StartElementHandler  = self.start_element
				self.parser.EndElementHandler 	 = self.end_element
				self.parser.CharacterDataHandler = self.char_data

				self.xml_text = '<?xml version="1.0" encoding="windows-1251"?>' + self.xml_text
				self.parser.Parse(self.xml_text, 1)

			def start_element(self,name, attrs):
				if name.lower() == 'class':
					self.cur_class = cftDB.class_row(db,attrs)
					self.classes[self.cur_class.id] = self.cur_class
				if name == 'method':					
					self.cur_class.add_method(attrs)
				if name == 'view':					
					self.cur_class.add_view(attrs)
			def end_element(self,name):
				pass
			def char_data(self,data):
				pass
		self.classes = ParseXml(txt).classes
		if type == "class_cache":
			self.on_classes_cache_loaded.fire()
		elif type == 'methods_cache':
			self.is_methods_ready = True
			self.on_methods_cache_loaded.fire()
	def parse_json(self):
		out_clob = self.cursor.var(cx_Oracle.CLOB)
		self.cursor.execute(self.fr.method_sources_json,out_clob=out_clob)				
		out_clob = unicode(out_clob.getvalue().read(),'1251')
		self.classes = json.loads(out_clob)["classes"]
		self.classes = json.loads(out_clob)["classes"]

	def get_classes(self):
		#t = timer()
		used_classes 	 = [db.classes[clk] for clk in cft_settings["used_classes"] if db.classes.has_key(clk)]
		not_used_classes = [clv for clk,clv in db.classes.iteritems() if clk not in cft_settings.get("used_classes")]
		used_classes.extend(not_used_classes)		
		#t.print_time("get_classes")
		return used_classes

	#def get_classes_text(self):
	#	return [clv.text for clv in self.get_classes()]

db = cftDB()

class connectCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.window.show_input_panel(u"Схема/Пользователь@База_данных:","ibs/ibs@cfttest", self.on_done, self.on_change, self.on_cancel)
	def on_done(self, input):
		self.window.run_command('show_panel', {"panel": "console", "toggle": "true"})
		db.connect(input)
	def on_change(self, input):
		pass		
	def on_cancel(self):
		pass

class cft_openCommand(sublime_plugin.WindowCommand):
	def run(self):
		if not db.is_connected():
			db.on_classes_cache_loaded += lambda:sublime.set_timeout(self.open_classes,0)
			sublime.active_window().run_command('connect',{})
		else:
			self.open_classes()

	def open_classes(self):
		self.classes = db.get_classes()
		self.window.show_quick_panel([clv.text for clv in self.classes],self.is_methods_ready,sublime.MONOSPACE_FONT)

	def is_methods_ready(self,selected_class):
		
	 	if not db.is_methods_ready:
	 		db.on_methods_cache_loaded += lambda:sublime.set_timeout(lambda:self.open_methods(selected_class),0)
	 	else:
	 		self.open_methods(selected_class)

	def open_methods(self, selected_class):
		if selected_class >= 0:

			self.current_class = self.classes[selected_class]
			
			if db.get_classes() != self.classes and db.classes.has_key(self.current_class.id): #Если за время выбора класса, список классов обновился. 
		 		self.current_class = db.classes[self.current_class.id]						   #Перезагрузим текущий класс
			

			#meths = [mv.text for mk,mv in self.current_class.meths.iteritems()]
			#self.window.show_quick_panel(meths,self.method_on_done,sublime.MONOSPACE_FONT)
			self.window.show_quick_panel(self.current_class.get_objects(),self.method_on_done,sublime.MONOSPACE_FONT)
			
			cft_settings.update_used_class(self.current_class.id)


	def method_on_done(self,input):

		def write(string):			
			edit = view.begin_edit()
			view.insert(edit, view.size(), string)
			view.end_edit(edit)
		if input >= 0:
			m = None
			if len(self.current_class.meths.values()) > 0:
				m = self.current_class.meths.values()[input]
				view = sublime.active_window().new_file()
				view.set_name(m.name)
				view.set_scratch(True)
				view.set_syntax_file("Packages/CFT/PL_SQL (Oracle).tmLanguage")
				view.settings().set("cft_method",{"cft_class":m.class_ref.id,"cft_method":m.id})
				
				text = m.get_sources()

				write(text)
				sublime.active_window().focus_view(view)

			else:
				sublime.status_message(u"У класса нет методов для открытия")
			#pass

	def on_change(self, input):
		pass		

	def on_cancel(self):
		pass
class save_methodCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		try:
			t = timer()

			aview = sublime.active_window().active_view()
			if aview.settings().has("cft_method"):
				m = aview.settings().get("cft_method")
				m = db.classes[m["cft_class"]].meths[m["cft_method"]]
				
				sublime_src_text = aview.substr(sublime.Region(0,aview.size()))
				db_src_text = m.get_sources()

				r = re.compile(r' +$', re.MULTILINE) #Удаляем все пробелы в конце строк, потому что цфт тоже их удаляет
				sublime_src_text = r.sub('',sublime_src_text)

				#print sublime_src_text
				if sublime_src_text != db_src_text:
					m.set_sources(sublime_src_text)
				else:
					print "Текст операции не изменился ", t.get_time()
		except Exception as e:
			print e
class close_methodCommand(sublime_plugin.TextCommand):
	def run(self, edit):

		aview = sublime.active_window().active_view()
		if aview.settings().has("cft_method"):
			m = aview.settings().get("cft_method")
			m = db.classes[m["cft_class"]].meths[m["cft_method"]]
			
			sublime_src_text = aview.substr(sublime.Region(0,aview.size()))
			db_src_text = m.get_sources()

			if sublime_src_text == db_src_text:
				aview

			#print self.view.id()
			#print 
			#views[self.view.id()].set_sources(src_text)
			#m = sublime.active_window().active_view().settings().get("cft_method")
			


class get_settingCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		#print "run"
		#sublime.run_command("insert_snippet", {"contents": "hello ($0)"})
		
		#sublime.active_window().run_command('insert_snippet', {"contents": "hello text ${1:ttext} second ${2:second}"})
		a = self.view.settings().get("a")
		print "get setting = ", a
		a = sublime.active_window().active_view().settings().get("a")
		print "get setting = ", a

class print_cmdCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		#print "run"
		#sublime.run_command("insert_snippet", {"contents": "hello ($0)"})
		
		#sublime.active_window().run_command('insert_snippet', {"contents": "hello text ${1:ttext} second ${2:second}"})
		#print "try set"

		self.view.settings().set("a","hello_world")
		print "setting is set"

#Класс для обработки событий
#например события открытия выпадающего списка
class el(sublime_plugin.EventListener):
	def on_load(self,view):
		#print "on_load_"
		pass
	def on_pre_save(self,view):
		print "on_pre_save_"
	def on_query_completions(self,view,prefix,locations):
		return
		#print "1:%s,2:%s,3:%s,4:%s" % (self,view,prefix,locations)
		print "on_query_completions"
		global a
		import os,sys
		SUBLIME_ROPE_PATH = os.path.dirname(os.path.normpath(os.path.abspath(__file__)))
		#print SUBLIME_ROPE_PATH
		sys.path.insert(0, SUBLIME_ROPE_PATH + "\\rope\\contrib\\")
		import rope
		from rope.contrib import codeassist
		#from rope.contrib.codeassist import CompletionPropasal

		if a == []:
			print "select from db"
			cnn_str = 'ibs/ibs@cfttest'
			connection = cx_Oracle.connect(cnn_str)
			cursor = connection.cursor()

			sql = """select c.id from classes c
					 --where rownum<10
						 order by nvl(c.modified,to_date('01.01.0001','dd.mm.yyyy')) desc"""
			cursor.execute(sql)

			#a = [rope.contrib.codeassist.CompletionProposal(unicode(text[0],'1251'),"imported",unicode(text[0],'1251'))
			a = [(u"{result}\t({scope},{type},{more})".format(
				result=unicode(text[0],'1251'),scope="imported",type="param",more="more2"),u"::[%s].[${1:hello}]"%text)
					for text in cursor.fetchall()]
			#a = [()for p in a]
		#print a
		#completion_flags = 2
		#if self.suppress_word_completions:
		completion_flags = sublime.INHIBIT_WORD_COMPLETIONS
		#if self.suppress_explicit_completions:
		#completion_flags = sublime.INHIBIT_EXPLICIT_COMPLETIONS
		#print len(a)
		#for l in locations:			
		#	print l
		


		return (a,completion_flags)
		#return a
