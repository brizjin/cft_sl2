# -*- coding: utf-8 -*-
from __future__ import with_statement
import sublime, sublime_plugin, sublime_plugin
import re
import json
import cx_Oracle
import os
import sublime
import threading,thread
import datetime,time
import xml.parsers.expat
import sys,traceback



plugin_name = "CFT"
plugin_path 			= os.path.join(sublime.packages_path(),plugin_name)
cache_path  			= os.path.join(plugin_path,"cache")
used_classes_file_path 	= os.path.join(plugin_path,"cache","cft_settings.json")

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
			try:
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
			except Exception,e:
				print "*** Ошибка асинхронного вызова:",e
				print "*** При вызове ",call_func.im_class if hasattr(call_func,"im_class") else "",call_func.__name__
				if sys != None:
					exc_type, exc_value, exc_traceback = sys.exc_info()
					
					traceback.print_exception(exc_type, exc_value, exc_traceback,
						                          limit=10, file=sys.stdout)
				
				
	RunInThread(on_complete).start()
def sub(p_str,from_str,to_str,p_start=0):
	"""
	Функция возвращает подстроку между двумя строками
	Включая эти строки
	Например sub(text,"declare","end;")
	"""
	begin = p_str.find(from_str,p_start)#-len(from_str)
	end = p_str.rfind(to_str,p_start)+len(to_str)
	return p_str[begin:end].strip()


class FileReader(object):
	def __init__(self):
		self.dir_path = os.path.join(sublime.packages_path(),plugin_name,"sql")
		self.load()
		#call_async(self.load)
	@staticmethod
	def read(file_path):
		if not os.path.exists(file_path):
			return ''
		f = open(file_path,"r")
		text = f.read()
		f.close()
		fileName, fileExtension = os.path.splitext(file_path)
		if fileExtension == '.tst':
			def sub(p_str,from_str,to_str,p_start=0):
				begin = p_str.find(from_str,p_start)#-len(from_str)
				end = p_str.rfind(to_str,p_start)+len(to_str)
				return p_str[begin:end].strip()
			text = sub(text,"declare","end;")
		return text

	@staticmethod
	def write(file_path,text):
		#file_path = os.path.join(sublime.packages_path(),plugin_name,file_path)
		f = open(file_path,"w")
		f.write(text)
		f.close()

	def substr(self,p_str,from_str,to_str,p_start=0):
		begin = p_str.find(from_str,p_start)+1
		end = p_str.find(to_str,p_start)
		return p_str[begin:end].strip()

	def load(self):
		self.cft_schema_sql 	 = self.read(os.path.join(plugin_path,"sql","cft_schema.sql"))
		self.method_sources 	 = self.read(os.path.join(plugin_path,"sql","method_sources.tst"))
		self.save_method_sources = self.read(os.path.join(plugin_path,"sql","save_method_sources.tst"))
		self.method_sources_json = self.read(os.path.join(plugin_path,"sql","method_sources_json.tst"))
		self.save_criteria_text  = self.read(os.path.join(plugin_path,"sql","save_criteria_text.tst"))
		self.classes_update		 = self.read(os.path.join(plugin_path,"sql","classes_update.sql"))
		

		
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
		r = FileReader.read(self.file_path)
		if len(r)>0:
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
		self.last  = datetime.datetime.now()
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

class cftDB(object):
	class db_row(object):
		def __init__(self,db,p_list):			
			self.db = db
			self.list = p_list
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
		
		def __repr__(self):
			try:
				#print self.list
				s = '('
				if self.list.__class__ == tuple:
					for r in self.list:
						if r[1].__class__== int:
							s += "%s : %-3i|" % (r[0],r[1])
						else:						
							s += "%s : %s|" % (r[0],r[1].encode('utf-8')) #ljust
				else:
					for r in self.list:
						s += "%10s:%-10s|" % (r,self.list[r][:20]) #ljust

				#r = re.compile(r' +') #Удаляем повторяющиеся пробелы
				#s = r.sub(' ',s.rstrip("|")) + ")"
				return s.encode('utf-8')
				#return self.list[5][1].encode('utf-8')
				
			except Exception,e:
				print "*** Ошибка repr:",e
		def __str__(self):
			return self.__repr__()# [r for r in self.dir()]				
	class class_row(db_row):
		def __init__(self, db, p_list):
			super(cftDB.class_row, self).__init__(db,p_list)
			self.meths = dict()
			self.views = dict()
			self.attrs = cftDB.class_attr_collection(self)
			self.is_updated = False
		def add_method(self,attrs):
			m = cftDB.method_row(self.db,self,attrs)
			self.meths[m.id] = m
			return m
		def add_view(self,attrs):
			v = cftDB.view_row(self.db,self,attrs)
			self.views[v.id] = v
			return v
		def add_attr(self,attrs):
			v = cftDB.attr_row(self.db,self,attrs)
			self.attrs[v.short_name] = v
			return v
		def get_objects(self):
			objs = []
			objs.extend([mv for mk,mv in self.meths.iteritems()])
			objs.extend([vv for vk,vv in self.views.iteritems()])
			return sorted(objs,key = lambda obj: obj.name)
		def update(self):
			if self.is_updated:
				return
			else:
				self.is_updated = True

			t = timer()
			sql = self.db.fr.classes_update
			xml_class = self.db.select(sql,self.id)
			
			self.meths = dict()
			self.views = dict()

			self.cur_method = None

			def start_element(name, attrs):
				#if name.lower() == 'class':
				#	self.cur_class = cftDB.class_row(db,attrs)
				#	self[self.cur_class.id] = self.cur_class
				if name == 'method':
					self.cur_method = self.add_method(attrs)
				elif name == 'view':
					self.add_view(attrs)
				elif name == 'param':
					self.cur_method.add_param(attrs)
				elif name == 'attr':
					a = self.add_attr(attrs)
					#print a

			def end_element(name):
				pass
			def char_data(data):
				pass

			parser = xml.parsers.expat.ParserCreate()
			parser.StartElementHandler  = start_element
			parser.EndElementHandler 	= end_element
			parser.CharacterDataHandler = char_data
			
			xml_class = '<?xml version="1.0" encoding="windows-1251"?>' + xml_class
			parser.Parse(xml_class, 1)

			t.print_time("%s update"%self.id)
		@property
		def target_class(self):
			if hasattr(self,"target_class_id"):
				cl = self.db.classes[self.target_class_id]
				cl.update()
				return cl
			else:
				return None;
		
		def autocomplete_list(self):
			self.update()

			a = [v for v in self.meths.values()] 				#методы
			#print "attrs=",db.classes[class_name].attrs
			a += [attr for attr in self.attrs.values()]		#аттрибуты класса
			a = sorted(a, key=lambda p: p.short_name)
			arr = []
			for m in a:
				if m.__class__ == cftDB.method_row:
					params_str = "\n"
					for param in sorted(m.params.values(),key=lambda p: int(p.position)):
						params_str += "\t%-15s \t=> ${%s:%-15s} \t--%-2s %-7s %-20s %s\n"%(param.short_name
																				,param.position
																				,param.short_name
																				,param.position
																				,param.direction
																				,param.class_id
																				,param.name)

					arr.append((u"M %s\t%s"%(m.short_name,m.name[:20]),"[%s](%s);\n"%(m.short_name,params_str)))
				elif m.__class__ == cftDB.attr_row:
					arr.append((u"A %s\t%s"%(m.short_name,m.name[:20]),"[%s]"%m.short_name))
			return arr
		
		@property
		def autocomplete(self):
			#print "autocomplete"
			arr = self.autocomplete_list()
			#print "self=",self.id
			if self.base_class_id == "COLLECTION" or self.base_class_id == "REFERENCE":			
				arr += self.target_class.autocomplete_list()
				#print "target=", self.target_class
			
			return arr
	class method_row(db_row):
		def __init__(self, db, p_class, p_list):
			super(cftDB.method_row, self).__init__(db,p_list)
			self.class_ref = p_class
			self.params = dict()
		def add_param(self,attrs):
			p = cftDB.param_row(self.db,attrs)
			self.params[p.position] = p
			return p
		def get_sources(self):
			conn = self.db.pool.acquire()
			cursor = conn.cursor()
			text_out = cursor.var(cx_Oracle.CLOB)
			cursor.execute(self.db.fr.method_sources,(self.class_ref.id, self.short_name.upper(),text_out))
			value = unicode(text_out.getvalue().read(),'1251')
			self.db.pool.release(conn)

			return value

		def get_sources_with_no_pool(self):
			t=timer()
			text_out = self.db.cursor.var(cx_Oracle.CLOB)
			self.db.cursor.execute(self.db.fr.method_sources,(self.class_ref.id, self.short_name.upper(),text_out))
			value = unicode(text_out.getvalue().read(),'1251')
			t.print_time("get_source")
			return value


		def set_sources(self,value):
			#print "set_sources_method",value
			try:
				t = timer()
				conn = self.db.pool.acquire()
				cursor = conn.cursor()
				cursor.setinputsizes(source_code=cx_Oracle.CLOB)
				err_clob = cursor.var(cx_Oracle.CLOB)
				err_num  = cursor.var(cx_Oracle.NUMBER)
				cursor.execute(self.db.fr.save_method_sources,class_name=self.class_ref.id, method_name=self.short_name.upper(),source_code=value,out=err_clob,out_count=err_num)				
				err_num = int(err_num.getvalue())
		

				if err_num == 0:					
					print u"Успешно откомпилированно за %s сек" % t.get_time()
				else:
					err_msg = unicode(err_clob.getvalue().read(),'1251').strip()
					#sublime.active_window().run_command('show_panel', {"panel": "console", "toggle": "true"})
					sublime.status_message(u"Ошибок компиляции %s за %s сек" % (err_num,t.get_time()))
					print "**********************************************"
					print "** Ошибки компиляции %s за %s"% (self.short_name.encode('1251'),t.get_now())
					print "**********************************************"
					print err_msg

				conn.commit()
				self.db.pool.release(conn)		
			except Exception,e:
				print "*** Ошибка выполнения method_row.set_sources:",e
				if sys != None:
					exc_type, exc_value, exc_traceback = sys.exc_info()
					traceback.print_exception(exc_type, exc_value, exc_traceback,
						                          limit=10, file=sys.stdout)
		def set_sources_with_no_pool(self,value):
			#print "set_sources_method",value
			try:
				t = timer()


				self.db.cursor.setinputsizes(source_code=cx_Oracle.CLOB)
				err_clob = self.db.cursor.var(cx_Oracle.CLOB)
				err_num  = self.db.cursor.var(cx_Oracle.NUMBER)
				self.db.cursor.execute(self.db.fr.save_method_sources,class_name=self.class_ref.id, method_name=self.short_name.upper(),source_code=value,out=err_clob,out_count=err_num)				
				err_num = int(err_num.getvalue())
		

				if err_num == 0:					
					print u"Успешно откомпилированно за %s сек" % t.get_time()
				else:
					err_msg = unicode(err_clob.getvalue().read(),'1251').strip()
					#sublime.active_window().run_command('show_panel', {"panel": "console", "toggle": "true"})
					sublime.status_message(u"Ошибок компиляции %s за %s сек" % (err_num,t.get_time()))
					print "**********************************************"
					print "** Ошибки компиляции %s за %s"% (self.short_name.encode('1251'),t.get_now())
					print "**********************************************"
					print err_msg

				self.db.connection.commit()	
			except Exception,e:
				print "*** Ошибка выполнения method_row.set_sources:",e
				if sys != None:
					exc_type, exc_value, exc_traceback = sys.exc_info()
					traceback.print_exception(exc_type, exc_value, exc_traceback,
						                          limit=10, file=sys.stdout)
			finally:
				t.print_time("set_sources")

		def errors(self):
			errors = self.db.select("select * from ERRORS t where t.method_id = :method_id order by class,type,sequence,line,position,text",self.id)
			if not errors:
				errors = list()
			return errors
			#self.errors_num = err_num

		def get_text(self):
			#return [self.text,u"Метод"]
			return u"Метод:         " + self.text
	class view_row(db_row):	
		def __init__(self, db, p_class, p_list):
			super(cftDB.view_row, self).__init__(db,p_list)
			self.class_ref = p_class
		def get_text(self):
			#return [self.text,u"Представление"]
			print self
			return u"Представление: " + self.text
		def get_sources(self):
			return self.db.select("select cr.condition from criteria cr where short_name = :view_short_name",self.short_name)
		def set_sources(self,value):
			try:
				t = timer()
				#save_criteria_text.tst
				#print "set_sourses_view",self.id,self.name,self.short_name,self.class_ref.id
				self.db.cursor.setinputsizes(view_src=cx_Oracle.CLOB)

				self.db.cursor.execute(self.db.fr.save_criteria_text,view_short_name=self.short_name,view_id=self.id,view_name=self.name,view_class=self.class_ref.id,view_src=value)				
				# err_num = int(err_num.getvalue())
				# if err_num == 0:
				# 	sublime.status_message(u"Успешно откомпилированно за %s сек" % t.get_time())
				print u"Успешно откомпилированно за %s сек" % t.get_time()
				# else:
				# 	err_msg = unicode(err_clob.getvalue().read(),'1251').strip()
				# 	sublime.active_window().run_command('show_panel', {"panel": "console", "toggle": "true"})
				# 	sublime.status_message(u"Ошибок компиляции %s за %s сек" % (err_num,t.get_time()))
				# 	print "**********************************************"
				# 	print "** %s" % t.get_now()
				# 	print err_msg
				self.db.connection.commit()
			except cx_Oracle.DatabaseError, e:
				print "ошибка"
				error, = e
				print error.code,error.message,error.context,error
	class param_row(db_row):	
		def __init__(self, db, p_list):
			super(cftDB.param_row, self).__init__(db,p_list)
	class attr_row(db_row):
		def __init__(self, db,p_class, p_list):
			super(cftDB.attr_row, self).__init__(db,p_list)
			self.class_ref = p_class

		@property
		def self_class(self):
			s_class = self.db[self.self_class_id]
			if s_class.base_class_id == "REFERENCE":
				return s_class.target_class
			else:
				return s_class
	class class_collection(dict):
		def __init__(self, db):
			super(cftDB.class_collection, self).__init__()
			self.db = db
			self.cur_class = None
		def parse(self,xml_text):
			
			def start_element(name, attrs):
				if name.lower() == 'class':
					self.cur_class = cftDB.class_row(db,attrs)
					self[self.cur_class.id] = self.cur_class
				if name == 'method':
					self.cur_class.add_method(attrs)
				if name == 'view':
					self.cur_class.add_view(attrs)
			def end_element(name):
				pass
			def char_data(data):
				pass

			parser = xml.parsers.expat.ParserCreate()
			parser.StartElementHandler  = start_element
			parser.EndElementHandler 	= end_element
			parser.CharacterDataHandler = char_data
			
			xml_text = '<?xml version="1.0" encoding="windows-1251"?>' + xml_text
			parser.Parse(xml_text, 1)
		@property
		def as_list(self):
			#t = timer()
			used_classes 	 = [db.classes[clk] for clk in cft_settings["used_classes"] if db.classes.has_key(clk)]
			not_used_classes = [clv for clk,clv in db.classes.iteritems() if clk not in cft_settings.get("used_classes")]
			used_classes.extend(not_used_classes)		
			#t.print_time("get_classes")
			return used_classes
		@property
		def used(self):
			#if not hasattr(self,"used_settings"):				
			#	self.used_settings = sublime.load_settings("used_classes.json")			
			
			if not hasattr(self,"used_classes"):
				text = FileReader.read(used_classes_file_path)
				if len(text)>0:
					self.json.loads(text)
				self.used_classes = self.used_settings.get("classes")
		@property
		def autocomplete(self):
			a = [v for v in self.values()]
			a = sorted(a, key=lambda p: p.id)
			a = [("%s\t%s"%(c.id,c.name[:20]),"[%s]"%c.id) for c in a]
			return a
	class class_attr_collection(dict):
		def __init__(self, db):
			super(cftDB.class_attr_collection, self).__init__()
			self.db = db
		@property
		def autocomplete(self):			
			a = [attr for attr in self.values()]		#аттрибуты класса
			a = sorted(a, key=lambda p: p.short_name)
			a = [(u"A %s\t%s"%(attr.short_name,attr.name[:20]),"[%s] = ${1:}"%attr.short_name) for attr in a]
			return a
	


	def __init__(self):
		self.on_classes_cache_loaded 	= EventHook()
		self.on_methods_cache_loaded 	= EventHook()
		self.is_methods_ready 			= False
		self.classes_lock 				= thread.allocate_lock()
		self.select_lock 				= thread.allocate_lock()
		self.connection_lock 			= thread.allocate_lock()
	def connect(self,connection_string):
		self.connection_string 	= connection_string

		user_ = str(connection_string[:connection_string.find('/')])
		pass_ = str(connection_string[connection_string.find('/')+1:connection_string.find('@')])
		dsn_  = str(connection_string[connection_string.find('@')+1:])

		self.pool = cx_Oracle.SessionPool(user 		= user_,
										  password 	= pass_,
										  dsn 		= dsn_,
										  min 		= 1,
										  max 		= 5,
										  increment = 1,
										  threaded  = True)
		call_async(self.load_classes)
		call_async(self.load)
		call_async(self.read_sql)
	def read_sql(self):

		self.fr = FileReader()
	def load(self):
		self.connection 				= cx_Oracle.connect(self.connection_string)		
		self.cursor 					= self.connection.cursor()
		#self.connection 	= cx_Oracle.connect(self.connection_string)		
		#self.cursor 		= self.connection.cursor()
		return 1
	def select_classes(self):
		sql = """select xmlelement(classes,xmlagg(xmlelement(class,XMLAttributes(cl.id as id
																				,cl.name as name
																				,cl.target_class_id as target_class_id
																				,cl.base_class_id as base_class_id
																				,rpad(cl.name,40,' ') || lpad(cl.id,30,' ')as text)))).getclobval() c from classes cl
				 """

		#value = self.select_in_tmp_connection(sql)
		value = self.select(sql)
		return value
	def load_classes(self):
		call_async(lambda:(FileReader.read(os.path.join(cache_path,"classes.xml")),"class_cache"),self.parse,async_callback=True)
		call_async(self.select_classes,lambda txt:self.save_and_parse(os.path.join(cache_path,"classes.xml"),txt,"class_select"),"Загрузка списка классов",async_callback=True)
		
		#call_async(lambda:(FileReader.read(os.path.join(cache_path,"methods.xml")),"methods_cache"),self.parse,async_callback=True)
		#call_async(lambda:self.select_in_tmp_connection(FileReader.read(os.path.join(plugin_path,"sql","cft_schema.sql"))),
		#		   lambda txt:self.save_and_parse(os.path.join(cache_path,"methods.xml"),txt,"method_select"),async_callback=True)
	def is_connected(self):
		#return hasattr(self,"cursor") and hasattr(self,"connection") and self.select("select * from dual")[0][0] == 'X'
		try:
			if hasattr(self,"pool"):
				return True
			return False
		except Exception:
			return False
	def select(self,sql,*args):
		value = None
		try:			
			conn = self.pool.acquire()
			cursor = conn.cursor()
			cursor.arraysize = 50
			#t = timer()
			value = self.select_cursor(cursor, sql, *args)
			#t.print_time("Select")
			self.pool.release(conn)
		except Exception,e:
			print "*** Ошибка выполнения select:",e
			if sys != None:
				exc_type, exc_value, exc_traceback = sys.exc_info()
				traceback.print_exception(exc_type, exc_value, exc_traceback,
					                          limit=10, file=sys.stdout)

		return value
	def select_cursor(self,cursor,sql,*args):
		try:
			#print "3",re.sub("\s+"," ",sql)
			cursor.execute(sql,args)			
			desc  = [d[0].lower() for d in cursor.description]						
			table = [[(lambda: unicode(t,'1251') if t.__class__ == str else t)() for t in row] for row in cursor]#Конвертнем все строковые значения в юникод				
			table = [[(lambda: "" if not t else t)() for t in row] for row in table] #Заменяем все значение None на пустую строку

			#print "desc_len=",len(desc),"table_len",len(table)
			#value = None
			if len(desc)==1 and len(table)==1:
				if t.__class__.__name__ == 'LOB':
					return table[0][0].read()
				else:
					return table[0][0]
			else:
				return [cftDB.db_row(self,zip(desc,row)) for row in table]
			
		except Exception,e:
			error, = e.args
			if error.__class__.__name__ == 'str':
				print "error",error
			elif error.code == 28:#ошибка нет подключения
				return []
			else:
				print "db.select_cursor.EXCEPTION:",error.code,error.message,error.context,e,sql
				if sys != None:
					exc_type, exc_value, exc_traceback = sys.exc_info()
					traceback.print_exception(exc_type, exc_value, exc_traceback,
						                          limit=10, file=sys.stdout)
			#return []
	def get_sid(self):

		return self.select("select sys_context('userenv','sid') sid, sid from v$mystat where rownum=1")[0]["sid"]
	def save_and_parse(self,file_name,txt,type=None):
		FileReader.write(file_name,txt)
		self.parse(txt,type)
	def parse(self,txt,type=None):
		try:
			#self.classes = ParseXml(txt).classes
			#print "before assign classes",type
			self.classes_lock.acquire()
			new_classes = cftDB.class_collection(self)			
			#print "after assign classes",type
			new_classes.parse(txt)
			self.classes = new_classes
			#print "after parse classes",type

			if type == "class_cache":
				self.on_classes_cache_loaded.fire()
			elif type == 'methods_cache':
				self.is_methods_ready = True
				self.on_methods_cache_loaded.fire()
			
			self.classes_lock.release()
		except Exception,e:
			print "*** Ошибка загрузки классов:",e
			if sys != None:
				exc_type, exc_value, exc_traceback = sys.exc_info()
				traceback.print_exception(exc_type, exc_value, exc_traceback,
					                          limit=10, file=sys.stdout)
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
	def __getitem__(self, key):
		cl = self.classes[key]
		cl.update()
		return cl

db = cftDB()

class connectCommand(sublime_plugin.WindowCommand):
	def run(self):
		print "CONNECT"
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
		print "OPEN MEHTODS"
		if not db.is_connected():
			db.on_classes_cache_loaded += lambda:sublime.set_timeout(self.open_classes,0)
			sublime.active_window().run_command('connect',{})
		else:
			self.open_classes()

	def open_classes(self):
		self.classes = db.get_classes()
		self.window.show_quick_panel([clv.text for clv in self.classes],self.open_methods,sublime.MONOSPACE_FONT)

	#def is_methods_ready(self,selected_class):
		
	 	#if not db.is_methods_ready:
	 	#	db.on_methods_cache_loaded += lambda:sublime.set_timeout(lambda:self.open_methods(selected_class),0)
	 	#else:
	 	#self.open_methods(selected_class)

	def open_methods(self, selected_class):
		try:
			if selected_class >= 0:

				self.current_class = self.classes[selected_class]
				
				#if db.get_classes() != self.classes and db.classes.has_key(self.current_class.id): #Если за время выбора класса, список классов обновился. 
					#print "Загрузка была из кэша обновим из базы"
					#self.current_class = db.classes[self.current_class.id]						   #Перезагрузим текущий класс
				self.current_class.update()

				#meths = [mv.text for mk,mv in self.current_class.meths.iteritems()]
				#self.window.show_quick_panel(meths,self.method_on_done,sublime.MONOSPACE_FONT)
				self.list_objs = self.current_class.get_objects()
				self.window.show_quick_panel([obj.get_text() for obj in self.list_objs],self.method_on_done,sublime.MONOSPACE_FONT)
				
				cft_settings.update_used_class(self.current_class.id)
		except Exception,e:
			print "Ошибка при вызове open_methods",e
			if sys != None:
				exc_type, exc_value, exc_traceback = sys.exc_info()
				traceback.print_exception(exc_type, exc_value, exc_traceback,
					                          limit=10, file=sys.stdout)


	def method_on_done(self,input):

		def write(string):			
			edit = view.begin_edit()
			view.insert(edit, view.size(), string)
			view.end_edit(edit)
		if input >= 0:
			if len(self.current_class.meths.values()) > 0:
				#m = self.current_class.meths.values()[input]
				#obj = self.current_class.get_objects()[input]
				obj = self.list_objs[input]
				#view = sublime.active_window().new_file()
				view = dataView()
				view.set_name(obj.name)
				view.set_scratch(True)
				view.set_syntax_file("Packages/CFT/PL_SQL (Oracle).tmLanguage")

				#view.settings().set("cft_object",{"id": obj.id,"class" : obj.class_ref.id, "type": obj.__class__.__name__})
				view.data = obj
				
				
				text = obj.get_sources()

				write(text)

				view.focus()
				

			else:
				sublime.status_message(u"У класса нет методов для открытия")
			#pass

	def on_change(self, input):
		pass		

	def on_cancel(self):
		pass
class MarkErrors(sublime_plugin.TextCommand):
	def run(self,edit):



		if err_num == 0:
			sublime.status_message(u"Успешно откомпилированно за %s сек" % t.get_time())
			print u"Успешно откомпилированно за %s сек" % t.get_time()

			view.erase_regions('cft-errors')
			view.settings().set("cft-errors",dict())
		else:
			err_msg = unicode(err_clob.getvalue().read(),'1251').strip()
			#sublime.active_window().run_command('show_panel', {"panel": "console", "toggle": "true"})
			sublime.status_message(u"Ошибок компиляции %s за %s сек" % (err_num,t.get_time()))
			print "**********************************************"
			print "** %s" % t.get_now()
			print err_msg

			regions = []
			regions_dict = dict()

			for err in regions_dict:
				lineno = err.line
				text_point = view.text_point(lineno - 1, 0)
				l = view.text_point(lineno, 0) - text_point - 1
				regions.append(sublime.Region(text_point, text_point + l))
				regions_dict[str(err.line)] = err.text

			view.settings().set("cft-errors",regions_dict)
			view.add_regions(
							'cft-errors',
							regions,
							'keyword', 'dot', 4 | 32)

			#view.fold(sublime.Region(10,15))
			#view.sel().add(cur_sel)
class save_methodCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		
		#import cProfile
		#self.profiler = cProfile.Profile()

		if not db.is_connected():
			db.on_classes_cache_loaded += lambda:sublime.set_timeout(self.save,0)
			#db.on_classes_cache_loaded += lambda:self.profiler.runcall(lambda:sublime.set_timeout(self.save,0))
			sublime.active_window().run_command('connect',{})
		else:
			self.save()
			#self.profiler.runcall(self.save)


	def save(self):
		try:
			
			#profiler.runcall(self.save)
			#profiler.print_stats()
			self.t = timer()


			view = dataView(sublime.active_window().active_view())
			obj = view.data
			sublime_src_text = view.substr(sublime.Region(0,view.size()))
			db_src_text = obj.get_sources()

			r = re.compile(r' +$', re.MULTILINE) #Удаляем все пробелы в конце строк, потому что цфт тоже их удаляет
			sublime_src_text = r.sub('',sublime_src_text)

			#print sublime_src_text
			if sublime_src_text != db_src_text:
				obj.set_sources(sublime_src_text)
			else:
				print "Текст операции не изменился"

			view.mark_errors()




		except Exception,e:
			print "*** Ошибка сохранения исходников:",e
			if sys != None:
				exc_type, exc_value, exc_traceback = sys.exc_info()
				
				traceback.print_exception(exc_type, exc_value, exc_traceback,
					                          limit=10, file=sys.stdout)
		finally:
			self.t.print_time("Сохранение текста операции")
			sublime.status_message(u"Компиляция завершена за " + self.t.get_time())

		#self.profiler.print_stats()
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
		import re, fileinput
		import pyPEG
		from pyPEG import parse,parseLine
		from pyPEG import keyword, _and, _not, ignore

		# pyPEG:
		#
		#   basestring:     terminal symbol (characters)
		#   keyword:        terminal symbol (keyword)
		#   matchobj:       terminal symbols (regex, use for scanning symbols)
		#   function:       named non-terminal symbol, recursive definition
		#                   if you don't want naming in output, precede name with an underscore
		#   tuple:          production sequence
		#   integer:        count in production sequence:
		#                    0: following element is optional
		#                   -1: following element can be omitted or repeated endless
		#                   -2: following element is required and can be repeated endless
		#   list:           options, choose one of them
		#   _not:           next element in production sequence is matched only if this would not
		#   _and:           next element in production sequence is matched only if this would, too

		# comment <- r"//.*" | r"/\*.**?\*/";
		# def comment():          return [re.compile(r"//.*"), re.compile("/\*.*?\*/", re.S)]
		# # literal <- r'\d*\.\d*|\d+|".*?"';
		# def literal():          return re.compile(r'\d*\.\d*|\d+|".*?"')
		# # symbol <- r"\w+"
		# def symbol():           return re.compile(r"\w+")
		# # operator <- r"\+|\-|\*|\/|\=\=";
		# def operator():         return re.compile(r"\+|\-|\*|\/|\=\=")
		# # operation <- symbol operator (literal | functioncall);
		# def operation():        return symbol, operator, [literal, functioncall]
		# # expression <- literal | operation | functioncall;
		# def expression():       return [literal, operation, functioncall]
		# # expressionlist <- expression ("," expression)*;
		# def expressionlist():   return expression, -1, (",", expression)
		# # returnstatement <- k"return" expression;
		# def returnstatement():  return keyword("return"), expression
		# # ifstatement <- k"if" "(" expression ")" block k"else" block;
		# def ifstatement():      return keyword("if"), "(", expression, ")", block, keyword("else"), block
		# # statement <- (ifstatement | returnstatement) ";";
		# def statement():        return [ifstatement, returnstatement], ";"
		# # block <- "{" statement+ "}";
		# def block():            return "{", -2, statement, "}"
		# # parameterlist <- "(" symbol ("," symbol)* ")";
		# def parameterlist():    return "(", symbol, -1, (",", symbol), ")"
		# # functioncall <- symbol "(" expressionlist ")";
		# def functioncall():     return symbol, "(", expressionlist, ")"
		# # function <- k"function" symbol parameterlist block;
		# def function():         return keyword("function"), symbol, parameterlist, block
		# # simpleLanguage <- function;
		# def simpleLanguage():   return function

		pyPEG.print_trace = True

		from xml.sax.saxutils import escape
		from pyPEG import Symbol

		def pyAST2XML(pyAST):
		    if isinstance(pyAST, unicode) or isinstance(pyAST, str):
		        return escape(pyAST)
		    if type(pyAST) is Symbol:
		        result = u"<" + pyAST[0].replace("_", "-") + u">"
		        for e in pyAST[1:]:
		            result += pyAST2XML(e)
		        result += u"</" + pyAST[0].replace("_", "-") + u">"
		    else:
		        result = u""
		        for e in pyAST:
		            result += pyAST2XML(e)
		    return result

		#files = fileinput.input(os.path.join(plugin_path,"pypeg_input.txt"))
		#result = parse(simpleLanguage(), files, True, comment)
		text = """function fak(n) { // ignore
    if (n==0) { // 0! is 1 by definition
        return 1;
    } else {
        return n * fak(n - 1);
    };
}"""
		#result = parseLine(text,simpleLanguage(), [], True, comment)
		#print result
		#print pyAST2XML(result)


		plplus_text = """
			a integer;
			b varchar2(2000);
			c varchar2;
			acc_ref ref [AC_FIN];
			n number;
		begin
			null;
			acc_ref := 'hello';
			n := 10.1;
			acc_ref := ::[AC_FIN]([CODE] = '001'
								or [FILIAL] > '002'
								and [BRANCH] is null
								or [BRANCH] = ::[BRANCHES]([CODE] = '001'));
		end;
		"""
		def comment():			return [re.compile(r"--.*"), re.compile("/\*.*?\*/", re.S)]
		def symbol():           return re.compile(r"\w+")
		
		def null():				return "null"#re.compile(r"null")
		def string():			return "'",re.compile(r"(.+?)(?=')"),"'"
		def number():			return re.compile(r"\d+(\.\d+)?")
		#def string():			return re.compile(r"\'.*\'")
		def basetype():			return [re.compile(r"integer"),
										re.compile(r"varchar2(\(\d+\))?"),
										re.compile(r"boolean"),
										re.compile(r"number(\(\d+\))?"),
									   ]
		def cfttype():			return -1,"ref","[",symbol,"]"
		def datatype():			return [basetype,cfttype]
		#def null():				return "null"
		#def variable():			return [null,symbol]
		def var_define():		return symbol,datatype,";"				
		def null_statement():	return null
		#def undefined_statement(): return re.compile(r".*"),";"
		def cft_attr():			return "[",symbol,"]"
		def condition():		return [(expression,re.compile(r"=|!=|>|>=|<|<="),expression),
										 (expression,re.compile(r"is null|is not null"))]
		def where():			return condition,-1,(["and","or"],condition)
		def short_locate():		return "::",cfttype,"(",where,")"
		
		def expression():		return [null,string,number,cft_attr,short_locate]
		def asign_statement():	return symbol,":=", expression
		def statement():		return [asign_statement,null_statement],";"
		def define_block():		return -2,var_define
		def exec_block():		return keyword("begin"),-2,statement,keyword("end"),";"
		def block():			return define_block,exec_block		
		def plplus_language():  return block

		plplus_result = parseLine(plplus_text,plplus_language,[],True,comment)
		print pyAST2XML(plplus_result)











class dataView(object):
	def __init__(self,view=None):
		if view:
			#print view
			self.view = view
		else:
			self.view = sublime.active_window().new_file()
	@property
	def data(self):
		try:
			#if self.view.settings().has("cft_object"):
			if hasattr(self,"_data"):
				return self._data
			else:
				value = self.view.settings().get("cft_object")
				#db.classes[value["class"]].update()
				if value["type"] == "method_row":
					cl = db.classes[value["class"]]
					if len(cl.meths)==0:
						cl.update()
					value = cl.meths[value["id"]]
				self._data = value
				return value
		except Exception,e:
			print "*** Ошибка настроек представления:",e
			if sys != None:
				exc_type, exc_value, exc_traceback = sys.exc_info()
				traceback.print_exception(exc_type, exc_value, exc_traceback,
													limit=10, file=sys.stdout)
	@data.setter
	def data(self,value):
		if value.__class__.__name__ == "method_row":
			self.view.settings().set("cft_object",{"id": value.id,"class" : value.class_ref.id, "type": value.__class__.__name__})
			self._data = value
	def focus(self):

		sublime.active_window().focus_view(self.view)
	def __getattr__(self, name):

		return getattr(self.view,name)
	def get_method_section(self,name):
		src_text = sublime.Region(0,self.view.size())
		src_text = self.view.substr(src_text)
		
		regexp = r'-+\n-+(.)*-+\n-+'
		p = re.compile(regexp)
		arr = p.split(src_text)

		# B = arr[2].strip('\n')
		# V = arr[4].strip('\n')
		# G = arr[6].strip('\n')
		# L = arr[8].strip('\n')
		# S = arr[10].strip('\n')

		t = {'EXECUTE'   : 0,
			 'VALIDATE'  : 2,
			 'PUBLIC'    : 4,
			 'PRIVATE'   : 6,
			 'VBSCRIPT'  : 8}

		return arr[t[name]]#.strip('\n')
	def get_view_line_by_section_line(self,section_line,section_name):
		if section_name == 'EXECUTE':
			#print 'EXECUTE'
			return section_line
		elif section_name == 'VALIDATE':
			value = self.view.rowcol(len(self.get_method_section('EXECUTE')))[0]   + 3 + section_line
			#print value,section_line,section_name
			return value
		elif section_name == 'PUBLIC':
			value = self.view.rowcol(len(self.get_method_section('EXECUTE')))[0]   + 3 + \
				    self.view.rowcol(len(self.get_method_section('VALIDATE')))[0]  + 3 + section_line
			#print value,section_line,section_name
			return value
		elif section_name == 'PRIVATE':
			value = self.view.rowcol(len(self.get_method_section('EXECUTE')))[0]  + 3 + \
					self.view.rowcol(len(self.get_method_section('VALIDATE')))[0] + 3 + \
					self.view.rowcol(len(self.get_method_section('PUBLIC')))[0]   + 3 + 8 + section_line
			#print value,section_line,section_name
			return value
		elif section_name == 'VALIDSYS':
			return 0
	def mark_errors(self):
		#print "errors:",self.data.errors()
		#print "line 7 is ",self.get_view_line_by_section_line(3,"PRIVATE")
		self.view.erase_regions('cft-errors')
		self.view.settings().set("cft-errors",dict())

		warnings = []
		errors = []
		regions_dict = dict()

		#print self.data.errors()

		for row in self.data.errors():
			lineno = self.get_view_line_by_section_line(row.line,row.type)
			text_point = self.view.text_point(lineno - 1, 0)
			l = self.view.text_point(lineno, 0) - text_point - 1
			if row.list[6][1] == 'W': #6,1 это поле class
				warnings.append(sublime.Region(text_point, text_point + l))
			elif row.list[6][1] == 'E':
				errors.append(sublime.Region(text_point, text_point + l))
			regions_dict[str(self.get_view_line_by_section_line(row.line,row.type))] = row.text

		self.view.settings().set("cft-errors",regions_dict)
		self.view.add_regions(
						'cft-warnings',
						warnings,
						'comment', 'dot', 4 | 32)
		self.view.add_regions(
						'cft-errors',
						errors,
						'keyword', 'dot', 4 | 32)
	#def mark_errors_async(self):
	#	call_async(lambda:sublime.set_timeout(self.mark_errors,0))

	@property
	def until_caret_row_text(self):
		cursor_position = self.view.sel()[0].a
		row_num,col_num = self.view.rowcol(cursor_position)
		start_row_position = self.view.text_point(row_num,0)
		row_text = self.view.substr(sublime.Region(start_row_position,cursor_position))
		return row_text
	def selection_row_sub(self,begin_str,end_str):
		from_str = self.until_caret_row_text
		begin 	 = from_str.rfind(begin_str)+len(begin_str)
		end 	 = from_str.rfind(end_str)#-len(end_str)
		return from_str[begin:end].strip()
		#class_name = row_text[row_text.rfind("::[")+3:len(row_text)-2]


#Класс для обработки событий
#например события открытия выпадающего списка
class el(sublime_plugin.EventListener):
	def on_load(self,view):
		#print "on_load_"
		pass
	def on_pre_save(self,view):
		print "on_pre_save_"
	def on_modified(self,view):
		view = dataView(view)
		# cursor_position = view.sel()[0].a
		# row_num,col_num = view.rowcol(cursor_position)
		# start_row_position = view.text_point(row_num,0)
		# last_simbol = view.substr(sublime.Region(cursor_position-1,cursor_position))

		#print "modified",last_simbol
		last_text = view.until_caret_row_text
		if last_text[-2:] == '::' or last_text[-2:] == "]("	or last_text[-1:] == '.' or last_text[-4:] == "and ":
			view.run_command('my_auto_complete',{})
	def on_query_completions(self,view,prefix,locations):
		return
		#print "1:%s,2:%s,3:%s,4:%s" % (self,view,prefix,locations)
		view = dataView(view)
		#completion_flags = sublime.INHIBIT_WORD_COMPLETIONS #Только то что в списке
		completion_flags = sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS #Список и автоподсказки
		
		a = []
		last_text = view.until_caret_row_text
		if not hasattr(db,"classes"):
			a = [(u"нет подключения к базе",u"text_to_paste")]
			completion_flags = sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS #Список и автоподсказки
		elif last_text[-2:] == "](" or last_text[-4:] == "and ": #Конструкция поиска
			#class_name = view.selection_row_sub("::[","](")
			for m in re.finditer(r"((::)*\[[a-zA-Z_#0-9]+\])(?!\(\[)",view.until_caret_row_text):
				name = m.group(1)
				print name
				if name[0:2] == "::":
					current_class = db[name[3:-1]]
				elif current_class.attrs.has_key(name[1:-1]):
					current_class = current_class.attrs[name[1:-1]].self_class					
					if current_class.base_class_id == 'COLLECTION':
						current_class = current_class.target_class
					if current_class.base_class_id == 'REFERENCE':
						current_class = current_class.target_class
				#::[EXT_DOCS_SVOD]()
			#a = db[class_name].attrs.autocomplete
			#print current_class.id
			a = current_class.attrs.autocomplete
		elif last_text[-1:] == '.':
			#for m in reversed(list(re.finditer(r"(::)*\[[a-zA-Z_#]+\]",text))):
			current_class = None
			for m in re.finditer(r"((::)*\[[a-zA-Z_#0-9]+\])",view.until_caret_row_text):
				#name = text[m.start():m.end()]
				name = m.group(1)
				if name[0:2] == "::":
					current_class = db[name[3:-1]]
					a = current_class.autocomplete
				elif current_class.attrs.has_key(name[1:-1]):
					current_class = current_class.attrs[name[1:-1]].self_class					
					a = current_class.autocomplete			
				else:
					print "else_name=",name
		elif last_text[-2:] == "::": #Вводим класс
			a = db.classes.autocomplete

		completion_flags = sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS
		return (a,completion_flags)
	def on_selection_modified(self, view):
		row, col = view.rowcol(view.sel()[0].a)
		row = row + 1 
		cft_errors = view.settings().get("cft-errors")

		if cft_errors != None:
			if cft_errors.has_key(str(row)):
				view.set_status('cft-errors',cft_errors[str(row)])
			else:
				view.set_status('cft-errors',"")
class my_auto_completeCommand(sublime_plugin.TextCommand):
    '''Used to request a full autocompletion when
    complete_as_you_type is turned off'''
    def run(self, edit, block=False):
    	#print "hello" 
        self.view.run_command('hide_auto_complete')
        sublime.set_timeout(self.show_auto_complete, 50)

    def show_auto_complete(self):
    	#print "second"
        self.view.run_command(
            'auto_complete', {
                'disable_auto_insert': True,
                'api_completions_only': True,
                'next_completion_if_showing': False
            }
        )
