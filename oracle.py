# -*- coding: utf-8 -*-
from __future__ import with_statement
import sublime, sublime_plugin, sublime_plugin
import re,cx_Oracle,json,xml.parsers.expat
import os,sys,traceback,datetime,time,threading,thread
import pyPEG
from pyPEG import parse,parseLine,keyword, _and, _not, ignore,Symbol
from xml.sax.saxutils import escape


plugin_name = "CFT"
plugin_path 			= os.path.join(sublime.packages_path(),plugin_name)
cache_path  			= os.path.join(plugin_path,"cache")
used_classes_file_path 	= os.path.join(plugin_path,"cache","cft_settings.json")

TIMER_DEBUG = True
pyPEG.print_trace = True

beg_whites_regex  = re.compile(r'^\s*') #ищем начало строки без пробелов
end_whites_regex  = re.compile(r'\s*$') #ищем конец строки без пробелов
sections_regex    = re.compile(r'╒═+╕\n│ ([A-Z]+) +│\n(.*?)\n?└─+┘\n'.decode('utf-8'),re.S) #поиск секций

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
					#params_str = "\n"
					params_str = ""

					for param in sorted(m.params.values(),key=lambda p: int(p.position)):											
						#params_str += "\t,%-15s \t== ${%s:%-15s} \t--%-2s %-7s %-20s %s\n"%(param.short_name.replace('$','\$')
						params_str += "\t, %-15s \t== ${%s:null} \t--%-2s %-7s %-20s %s\n"%(param.short_name.replace('$','\$')
																				,param.position.replace('$','\$')
																				#,param.short_name.replace('$','\$')
																				,param.position.replace('$','\$')
																				,param.direction.replace('$','\$')
																				,param.class_id.replace('$','\$')
																				,param.name.replace('$','\$'))
					params_str = params_str.lstrip('\t,')
					params_str = "\n\t " + params_str

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
		def execute_header(self):
			params_str = ""
			for i,param in enumerate(sorted(self.params.values(),key=lambda p: int(p.position))):											
				#params_str += "\t,%-15s \t== ${%s:%-15s} \t--%-2s %-7s %-20s %s\n"%(param.short_name.replace('$','\$')
				if i<len(self.params)-1:	class_id = param.class_id + ","
				else:						class_id = param.class_id

				#if self.db.classes.has_key(class_id):	class_id = "::[%s]%stype"%(class_id,'%')
				
				params_str += "\t%-15s %-7s %-20s\t--%-2s %s\n"%(param.short_name
																#,param.position
																#,param.short_name
																,param.direction
																,class_id
																,param.position																				
																,param.name)
			params_str = params_str.lstrip('\t')#.rstrip(',')
			params_str = "\n\t" + params_str
			params_str = "function %s(%s)return null\nis\n"%(self.short_name,params_str)
			params_str = re.sub(r'\n',r'\n\t','\t' + params_str).rstrip('\t')
			return params_str

		def get_sources(self):
			

			def get_section_with_header(section_name,text):
				value  ='╒══════════════════════════════════════════════════════════════════════════════╕\n'.decode('utf-8')
				value +='│ '.decode('utf-8') + '%-10s' % section_name + '                                                                   │\n'.decode('utf-8')
				#value +='├──────────────────────────────────────────────────────────────────────────────┤\n'.decode('utf-8')

				if section_name == "EXECUTE":
					value += self.execute_header()

				value += re.sub(r'\n',r'\n\t','\t' + text).rstrip('\t') #добавим служебный таб в начало каждой строки
				value +='└──────────────────────────────────────────────────────────────────────────────┘\n'.decode('utf-8')
				return value
			def read_clob(clob_val):
				clob_val = clob_val.getvalue()
				if clob_val:	clob_val = clob_val.read().decode('1251')
				else:			clob_val = ""
				return clob_val

			conn = self.db.pool.acquire()
			cursor = conn.cursor()
			
			execute  = cursor.var(cx_Oracle.CLOB)
			validate = cursor.var(cx_Oracle.CLOB)
			public   = cursor.var(cx_Oracle.CLOB)
			private  = cursor.var(cx_Oracle.CLOB)
			vbscript = cursor.var(cx_Oracle.CLOB)

			cursor.execute(self.db.fr.method_sources,(self.class_ref.id, self.short_name.upper(),execute,validate,public,private,vbscript))

			self.execute  = read_clob(execute)
			self.validate = read_clob(validate)
			self.public   = read_clob(public)
			self.private  = read_clob(private)
			self.vbscript = read_clob(vbscript)

			value = ""
			

			value += get_section_with_header('EXECUTE'  ,self.execute)
			value += get_section_with_header('VALIDATE' ,self.validate)
			value += get_section_with_header('PUBLIC'   ,self.public)
			value += get_section_with_header('PRIVATE'  ,self.private)
			value += get_section_with_header('VBSCRIPT' ,self.vbscript)
			self.db.pool.release(conn)

			return value
		
		def set_sources(self,text):
			def execute_function(execute_text):
				def comment():		return [(re.compile(r"--.*")), re.compile("/\*.*?\*/", re.S)]
				def body():			return re.compile(r"is.*",re.S)
				def datatype():		return re.compile(r"\w+")
				def return_type():	return datatype		
				def begin_block():	return 0,keyword("declare"),0,any_text,keyword("begin"),-2,[any_text,begin_block],0,ignore(r"end;")
				def param_name():	return re.compile(r"\w+")
				def param_type():	return re.compile(r"(?i)in out|in|out")
				def param():		return param_name,0,param_type,datatype
				def params():		return param,-1,(',',param)
				def proc():			return
				def func_name():	return re.compile(r"\w+")
				def func():			return keyword('function'),func_name,"(",0,params,")",keyword('return'),return_type,body
				def exec_block():	return [func,proc]	

				self.result = parseLine(execute_text,exec_block,[],True,comment)
				class exe(object):
					func = self.result[0][0].what[0]
					#func_name = func.what[0].what
					#params_arr = func.what[1].what
					#params = dict([(p.what[0].what,{"type":p.what[1].what,"datatype":p.what[2].what})for p in params_arr])
					#return_type = func.what[2].what[0].what
					for w in func.what:
						if w[0] == "body":
							text = w.what
					#print "WHAT=", func.what
					#text = func.what[3].what
					text = text[text.find("\n")+1:]
				return exe()
			try:
				sections_dict = dict()
				for s in sections_regex.finditer(text):
					text = re.sub(r'\n\t',r'\n',s.group(2)).lstrip('\t')					#Удалим служебный таб в начале каждой строки
					text = re.sub(r' +$','',text,re.MULTILINE) 				#Удаляем все пробелы в конце строк, потому что цфт тоже их удаляет
					sections_dict[s.group(1)] = text

				#print "VALIDATE='%s'"%sections_dict["VALIDATE"],len(sections_dict["VALIDATE"])

				t = timer()
				conn = self.db.pool.acquire()
				cursor = conn.cursor()
				cursor.setinputsizes(
					b=cx_Oracle.CLOB,
					v=cx_Oracle.CLOB,
					g=cx_Oracle.CLOB,
					l=cx_Oracle.CLOB,
					s=cx_Oracle.CLOB
				)
				err_clob,err_num = cursor.var(cx_Oracle.CLOB),cursor.var(cx_Oracle.NUMBER)
				#print "TEXT=",execute_function(sections_dict["EXECUTE"]).text

				cursor.execute(
					self.db.fr.save_method_sources,
					class_name=self.class_ref.id,
					method_name=self.short_name.upper(),
					b=execute_function(sections_dict["EXECUTE"]).text,
					v=sections_dict["VALIDATE"],
					g=sections_dict["PUBLIC"],
					l=sections_dict["PRIVATE"],
					s=sections_dict["VBSCRIPT"],
					out=err_clob,
					out_count=err_num
				)				
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
				
				#print error.code,error.message,error.context,error
				if sys != None:
					exc_type, exc_value, exc_traceback = sys.exc_info()
					traceback.print_exception(exc_type, exc_value, exc_traceback,
						                          limit=10, file=sys.stdout)			
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
			#print self
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
			a = [(u"A %s\t%s"%(attr.short_name,attr.name[:20]),"[%s]"%attr.short_name) for attr in a]
			return a
	def __init__(self):
		self.on_classes_cache_loaded 	= EventHook()
		self.on_methods_cache_loaded 	= EventHook()
		self.is_methods_ready 			= False
		self.classes_lock 				= thread.allocate_lock()
		self.select_lock 				= thread.allocate_lock()
		self.connection_lock 			= thread.allocate_lock()

		self.connect("ibs/ibs@cfttest")
	def connect(self,connection_string):
		try:
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
		except Exception as e:
			print "e=",e
	def read_sql(self):
		try:
			self.fr = FileReader()
		except Exception as e:
			print "e=",e
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
#db = None

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
			#print view.encoding()
			#print "string=",string
			view.insert(edit, view.size(), string)
			view.end_edit(edit)
		if input >= 0:
			if len(self.current_class.meths.values()) > 0:
				#m = self.current_class.meths.values()[input]
				#obj = self.current_class.get_objects()[input]
				obj = self.list_objs[input]
				#view = sublime.active_window().new_file()
				view = dataView.new()
				view.set_name(obj.name)
				view.set_scratch(True)
				view.set_syntax_file("Packages/CFT/PL_SQL (Oracle).tmLanguage")
				view.set_encoding("utf-8")

				#view.settings().set("cft_object",{"id": obj.id,"class" : obj.class_ref.id, "type": obj.__class__.__name__})
				view.data = obj
				
				
				#text = obj.get_sources()
				text = obj.get_sources()
				#print "text",text

				write(text)

				view.focus()
				

			else:
				sublime.status_message(u"У класса нет методов для открытия")
			#pass
	def on_change(self, input):
		pass		
	def on_cancel(self):
		pass
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
			view = dataView.active()#(sublime.active_window().active_view())
			obj = view.data
			sublime_src_text = view.text#view.substr(sublime.Region(0,view.size()))
			db_src_text = obj.get_sources()
			#print sublime_src_text
			if sublime_src_text != db_src_text:
				obj.set_sources(view.text)
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

class dataView(object):
	def __init__(self,view):
		self.view = view
		#self.view = sublime.active_window().new_file()
		#self.view = sublime.active_window().active_view()

	@staticmethod
	def new():

		return dataView(sublime.active_window().new_file())
	@staticmethod
	def active():

		return dataView(sublime.active_window().active_view())

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
	
	@property
	def sections(self):
		class section(object):
			def __init__(self,view,begin,end,name,text):
				self.view  = view
				self.begin = begin				
				self.end   = end
				self.name  = name
				self.text  = text
				self.header_begin = self.begin
				if self.name == "EXECUTE":
					self.header_begin = self.begin
					self.begin = self.view.text_point(self.view.rowcol(self.begin)[0] + self.view.data.execute_header().count("\n"),0)

			@property
			def rows(self):
				if self.begin == self.end:
					return 0
				else:
					return len(self.view.lines(sublime.Region(self.begin,self.end)))
			def view_line_num(self,line_num):
				return self.view.rowcol(self.begin)[0] + line_num
			@property
			def lines(self):
				return self.view.lines(sublime.Region(self.begin,self.end))

		sections_dict = dict()
		for s in sections_regex.finditer(self.text):
			text = re.sub(r'\n\t',r'\n',s.group(2)).lstrip('\t')	#Удалим служебный таб в начале каждой строки
			text = re.sub(r' +$','',text,re.MULTILINE) 				#Удаляем все пробелы в конце строк, потому что цфт тоже их удаляет
			sections_dict[s.group(1)] = section(self,s.start(2),s.end(2),s.group(1),text)
		return sections_dict
	@property
	def current_section(self):
		
		def comment():			return [(re.compile(r"--.*")), re.compile("/\*.*?\*/", re.S)]
		#def blocks_text():		return re.compile(r".*?((?=└─)|$)".decode('utf-8'),re.S)
		#def blocks_text():		return ignore(r".*?((?=└─)|$)".decode('utf-8'),re.S)
		def blocks_section():	return ignore(r'╒═+╕\n│ +'.decode('utf-8')),re.compile(r'[A-Z]+') 	\
									  ,ignore(r' *│'.decode('utf-8')) \
									  ,ignore(r".*?((?=└─)|$)".decode('utf-8'),re.S) \
									  ,0,ignore(r'└─+┘\n'.decode('utf-8'))
		def blocks(): 			return -2,blocks_section
		
		old_trace = pyPEG.print_trace
		pyPEG.print_trace = False
		result = parseLine(self.text[:self.caret_position],blocks,[],True,comment)
		pyPEG.print_trace = old_trace
		#sections = dict([(s.what[0],s.what[1].what) for s in result[0][0].what])
		sections = [s.what[0] for s in result[0][0].what]
		#k,self.last_section = self.sections.items()[len(self.sections.items())-1]
		last_section = sections[len(sections)-1]

		return last_section

	def mark_errors(self):
		def RegionTrim(region):
			region_str = self.view.substr(region)
			match1 = beg_whites_regex.search(region_str)				
			match2 = end_whites_regex.search(region_str)
			return sublime.Region(region.begin()+match1.end(),region.end() - (match2.end() - match2.start()))
		#self.view.erase_regions('cft-errors')
		#self.view.settings().set("cft-errors",dict())
		warnings,errors,regions_dict = [],[],dict()		
		for row in self.data.errors():
			section = self.sections[row.type]

			line_num   = row.line-1
			line_count = len(section.lines)
			if line_count <= line_num:
				line_num = line_count-1
			#print "line_num=",line_num
			#print "line_count=",line_count

			line = RegionTrim(section.lines[line_num])
			if row.list[6][1] == 'W': #6,1 это поле class
				warnings.append(line)
			elif row.list[6][1] == 'E':
				errors.append(line)
			regions_dict[str(section.view_line_num(line_num + 1))] = row.text

		self.view.settings().set("cft-errors",regions_dict)
		self.view.add_regions('cft-warnings',warnings,'comment', 'dot', 4 | 32)
		self.view.add_regions('cft-errors'  ,errors  ,'keyword', 'dot', 4 | 32)
	#def mark_errors_async(self):
	#	call_async(lambda:sublime.set_timeout(self.mark_errors,0))

	@property
	def caret_position(self):
		return self.view.sel()[0].a

	@property
	def until_caret_row_text(self):
		cursor_position = self.view.sel()[0].a
		row_num,col_num = self.view.rowcol(cursor_position)
		start_row_position = self.view.text_point(row_num,0)
		row_text = self.view.substr(sublime.Region(start_row_position,cursor_position))
		return row_text
	@property
	def until_caret_text(self):
		cursor_position = self.view.sel()[0].a
		return self.view.substr(sublime.Region(0,cursor_position))


	@property
	def text(self):
		return self.view.substr(sublime.Region(0,self.view.size()))
	@property
	def current_text(self):
		sections = self.sections
		text = ""
		#print "CURRENT TEXT"
		try:
			for k,s in sections.items():
				if s.header_begin <= self.caret_position and self.caret_position <= s.end:
					#print s.name
					return self.view.substr(sublime.Region(s.header_begin,self.caret_position))
			return text
		except Exception as e:
			print e
			return ""

	def selection_row_sub(self,begin_str,end_str):
		from_str = self.until_caret_row_text
		begin 	 = from_str.rfind(begin_str)+len(begin_str)
		end 	 = from_str.rfind(end_str)#-len(end_str)
		return from_str[begin:end].strip()
		#class_name = row_text[row_text.rfind("::[")+3:len(row_text)-2]

	@property
	def block_autocomplete(self):
		try:
			def comment():		return [(re.compile(r"--.*")), re.compile("/\*.*?\*/", re.S)]
			def basetype():		return re.compile(r"integer|date|clob|blob|boolean|(varchar2|number)(\(\d+\))?")
			def cfttype():		return "[",re.compile(r"\w+"),"]"
			def cftref():		return "ref","[",re.compile(r"\w+"),"]"
			def undeftype():	return re.compile(r".*?(?=(,|\)| |\n))")
			def var_name():		return re.compile(r"\w+")
			def datatype():		return [basetype,cfttype,cftref,undeftype]
			#def vardef():		return var_name,datatype,0,(":=",ignore(r".*?(?=;)")),";"
			def vardef():		return var_name,datatype,";"
			# def begin_block():	return 0,keyword("declare"),0,any_text,keyword("begin"),-2,[any_text,begin_block],0,ignore(r"end;")
			def param_name():	return re.compile(r"\w+")
			def param_type():	return [re.compile(r"(?i)in out\b"),re.compile(r"(?i)in\b"),re.compile(r"(?i)out\b")]
			def param():		return param_name,0,param_type,datatype
			def params():		return param,-1,(',',param)
			def proc():			return
			def func_name():	return re.compile(r"\w+")
			def func():			return (keyword('function'),
										func_name,
										0,("(", params,")"),
										keyword('return'),
										datatype,
										keyword('is'),
										ignore(r".*?(?=end;)end;",re.S))

			def func_cur():		return (keyword('function'),
										func_name,
										0,("(", params,0,")"),
										keyword('return'),
										datatype,
										keyword('is'),
										#ignore(r".*",re.S)
										-1,vardef,
										keyword('begin'),
										ignore(r".*",re.S)
										)
			def block():		return -2,[func,proc,func_cur,vardef]	
			#print "TEXT=",view.sections[view.current_section].text[:view.caret_position]
			result = parseLine(self.current_text,block,[],True,comment)

			
			
			#print "SYM_TYPE",type(sym("hello"))

			block = sym(result).block
			block_autocomplete = list()
			block_dict = dict()
			for s in block.get_arr("vardef"):
				#print "varname=",s.var_name,s.datatype.name,s.datatype.value
				#print "DATA=",s.datatype
				block_autocomplete.append(("%s\t%s"%(s.var_name,s.datatype.value),s.var_name))
			

			for f in block.get_arr("func"):
				#print "f=",f.func_name,f.datatype.name,f.datatype.value
				#print "f=",f.func_name,dict([(p.param_name,{"kind":p.datatype.name,"type":p.datatype.value}) for p in f.params])

				#print "params=",f.params
				
				if len(f.params.as_arr())>0:
					p = max(f.params,key=lambda a:len(a.param_name))
					max_len=len(p.param_name)
					if max_len>15: max_len=15
				else: max_len = 15

				params_str = ""
				params_tmp = "\t, %-"+str(max_len)+"s == ${%s:null} \t--%-2s %-7s %-20s\n"

				#print "f.name=",f.func_name,len(f.params.as_arr())
				if len(f.params.as_arr())==0:
					f_snip  = "%s;"%f.func_name
				elif len(f.params.as_arr())==1:
					f_snip  = "%s(${1:null}); \t--%-7s %-20s\n"% \
						(f.func_name,
						 f.params.param.param_type.value,
						 f.params.param.datatype.value)
				elif len(f.params.as_arr())>1:

					for i,param in enumerate(f.params):
						#print param
						#params_str += "\t,%-15s \t== ${%s:%-15s} \t--%-2s %-7s %-20s %s\n"%(param.short_name.replace('$','\$')
						#params_str += "\t, %-15s \t== ${%s:null} \t--%-2s %-7s %-20s\n"% \
						params_str += params_tmp%\
							(param.param_name.replace('$','\$')
							,i+1,i+1,param.param_type.replace('$','\$')
							,param.datatype.value.replace('$','\$'))

					params_str = params_str.lstrip('\t,')
					params_str = "\n\t " + params_str
					f_snip  = "%s(%s);"%(f.func_name,params_str)
					#print "p=",p.param_name,p.datatype.name,p.datatype.value
				block_autocomplete.append(("%s()\t%s"%(f.func_name,f.datatype.value),f_snip))

			func_cur = block.func_cur
			#print "func_cur.name=",func_cur.func_name
			for p in func_cur.params:
				if db.classes.has_key(p.datatype.value):
					block_dict[p.param_name] = db.classes[p.datatype.value]

				block_autocomplete.append(("%s\t%s {f param}"%(p.param_name,p.datatype.value),p.param_name))
				#print "p=",p
			for v in func_cur.get_arr("vardef"):
				if db.classes.has_key(v.datatype.value):
					block_dict[v.var_name] = db.classes[v.datatype.value]
				block_autocomplete.append(("%s\t%s {var}"%(v.var_name,v.datatype.value),v.var_name))
			
			#print pyAST2XML(result)
			return block_autocomplete,block_dict
		except Exception as e:
			print "BLOCK AUTOCOMPLITE ERROR",e
			exc_type, exc_value, exc_traceback = sys.exc_info()					
			traceback.print_exception(exc_type, exc_value, exc_traceback, limit=10, file=sys.stdout)
			return []
class Dict(dict):
	def __init__(self,*args,**kwargs):
		super(Dict,self).__init__(*args,**kwargs)
	def __getattr__(self,name):
		return self[name]
		#print "ARGS=",args
class plplus(object):
	class sym(object):
		def __init__(self,s):
			self.s = s
		def get_arr(self,name):
			arr = list()
			for s in self.s:
				if type(s) is Symbol and s[0] == name:
					arr.append(plplus.sym(s.what))
			return arr
		@property
		def name(self):
			s = self.s
			if type(s) is list:		s = s[0]
			if type(s) is Symbol:	return s.__name__
			return ""

		@property
		def value(self):
			s = self.s
			if type(s) is list:	s = s[0]
			if type(s) is Symbol:	s = s.what
			if type(s) is Symbol: 	return plplus.sym(s)
			if isinstance(s, unicode) or isinstance(s, str): return s
			else: return plplus.sym(s).value
			
		def __iter__(self):		
			return iter(self.as_arr())
			#return iter(self.s)
		
		def as_arr(self):
			
			#print "TYPE=",type(self.s)
			if type(self.s) is list:
				arr = list()
				for s in self.s:
					if type(s) is Symbol:
						arr.append(plplus.sym(s.what))
				return arr
			else: return []

		def __getattr__(self,name):
			s = self.s
			if type(s) == tuple:
				s = s[0]
			if type(s) == list:
				for a in s:
					if type(a) == Symbol and a[0] == name:
						a = a.what
						#if type(a.what) is Symbol:
						#if type(a) is list and len(a) == 1:
						#	a = a[0]							
						if type(a) is Symbol or type(a) is list:	return plplus.sym(a)
						else:										return a
						#else:						return a.what
				try:
					return getattr(s[0],name)
				except AttributeError as e:
					return plplus.sym("")
			
			return getattr(self.s,name)
		def __repr__(self):
			return "sym(%s)"%self.s.__repr__()

	def __init__(self,text):
		try:
			def comment():		return [(re.compile(r"--.*")), re.compile("/\*.*?\*/", re.S)]
			def basetype():		return re.compile(r"integer|date|clob|blob|boolean|(varchar2|number)(\(\d+\))?")
			def cfttype():		return "[",re.compile(r"\w+"),"]"
			def cftref():		return "ref","[",re.compile(r"\w+"),"]"
			def undeftype():	return re.compile(r".*?(?=(,|\)| ))")
			def var_name():		return re.compile(r"\w+")
			def datatype():		return [basetype,cfttype,cftref,undeftype]
			#def vardef():		return var_name,datatype,0,(":=",ignore(r".*?(?=;)")),";"
			def vardef():		return var_name,datatype,";"
			# def begin_block():	return 0,keyword("declare"),0,any_text,keyword("begin"),-2,[any_text,begin_block],0,ignore(r"end;")
			def param_name():	return re.compile(r"\w+")
			def param_type():	return [re.compile(r"(?i)in out\b"),re.compile(r"(?i)in\b"),re.compile(r"(?i)out\b")]
			def param():		return param_name,0,param_type,datatype
			def params():		return param,-1,(',',param)
			def proc():			return
			def func_name():	return re.compile(r"\w+")
			def func():			return (keyword('function'),
										func_name,
										0,("(", params,")"),
										keyword('return'),
										datatype,
										keyword('is'),
										ignore(r".*?(?=end;)end;",re.S))

			def func_cur():		return (keyword('function'),
										func_name,
										0,("(", params,0,")"),
										keyword('return'),
										datatype,
										keyword('is'),
										#ignore(r".*",re.S)
										-1,vardef,
										keyword('begin'),
										ignore(r".*",re.S)
										)
			def block():		return -2,[func,proc,func_cur,vardef]	
			
			result = parseLine(text,block,[],True,comment)
			block = plplus.sym(result).block
			#print "TYPE=",type((s.var_name,s.datatype.value) for s in block.get_arr("vardef"))
			#try:
			
			self.vars = Dict((s.var_name,s.datatype.value) for s in block.get_arr("vardef"))
			#except Exception as e:
			#	print "E=",e
			
			self.funcs = Dict((f.func_name,	Dict({	"name"			: f.func_name,
											 		"return_type"	: f.datatype.value,
											 		"params"		: [Dict({"name"			: param.param_name,	
											 								 "param_type"	: param.param_type.value,
											 								 "datatype"		: param.datatype.value,
																		 	 "num"			: i+1
																			}) for i,param in enumerate(f.params)]
											})) for f in block.get_arr("func"))

			func_cur = block.func_cur
			self.func = Dict({	"name"			: func_cur.func_name,
						 		"return_type"	: func_cur.datatype.value,
						 		"params"		: Dict((p.param_name,Dict({	"name"		: p.param_name,
																 	  		"param_type": p.param_type.value,
															 		  		"datatype"	: p.datatype.value,
														 		  			"kind"		: p.datatype.name
														 	 				})) for p in func_cur.params),
								"vars"			: Dict((v.var_name,v.datatype.value) for v in func_cur.get_arr("vardef"))})
		except Exception as e:
			print "BLOCK AUTOCOMPLITE ERROR",e
			exc_type, exc_value, exc_traceback = sys.exc_info()					
			traceback.print_exception(exc_type, exc_value, exc_traceback, limit=10, file=sys.stdout)
			#return []
	@property
	def autocomplete(self):
		autocomplete  = list()
		autocomplete += [("%s\t%s"%(k,v),k) for k,v in self.vars.iteritems()] #Переменные определенные вне функции

		for k,f in self.funcs.items():
			#print "F=",f.params
			if len(f.params)>0:
				p = max(f.params,key=lambda a:len(a.name))
				max_len=len(p.name)
				if max_len>15: max_len=15
			else: max_len = 15

			params_str = ""
			params_tmp = "\t, %-"+str(max_len)+"s == ${%s:null} \t--%-2s %-7s %-20s\n"

			def string_table(*args):
				s = ""
				print args[0]

			if len(f.params)==0:
				f_snip  = "%s;"%f.func_name
			elif len(f.params)==1:				
				f_snip  = "%s(${1:%s});"% (f.name,f.params[0].name)
			elif len(f.params)>1:
				string_table("строка")
				for param in f.params:
					params_str += params_tmp%(param.name,param.num,param.num,param.param_type,param.datatype)
				f_snip  = "%s(%s);"%(f.name,"\n\t " + params_str.lstrip('\t,'))
				#print "p=",p.param_name,p.datatype.name,p.datatype.value
		autocomplete.append(("%s()\t%s"%(f.name,f.return_type),f_snip))

		return autocomplete

	def pyAST2XML(text):
		pyAST = text
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

class plplus_class(object):
	# class variable_class(object):
	# 	def __init__(self,var_define):
	# 		var_def 		= var_define[1]
	# 		self.name 		= var_def[0][1]		#name of var
	# 		self.type 		= var_def[1][0]		#базовый либо цфт тип
	# 		self.type_name 	= var_def[1][1][0]	#имя типа
	class variable_class(object):
		def __init__(self,var_define_symbol):
			try:
				s = var_define_symbol
				if s.__name__ != 'var_define':
					raise Exception ("Переменная должна быть символом var_define")

				self.name = s()[0]() # [1] или what или () синонимы
				self.kind = s.what[1].what[0].__name__
				if self.kind == 'cft':
					self.type = s.what[1].what[0].what[0]
				else:
					self.type = s.what[1].what[0].what
			except Exception as e:
				print e
		def __unicode__(self):

			return u'Variable(%s,%s,%s)'%(self.name,self.kind,self.type)
		def __repr__(self):

			return unicode(self)
	class section(object):
		def __init__(self,section_defenation):
			s = section_defenation
			#s[0] == "uncomplite_block_section"
			self.name = s.what[0]
			if s.what[1].what.__class__ == list:
				self.text = ""
			else:
				self.text = s.what[1].what
	class block_class(object):
		def __init__(self,block_define):			
			self.vars = dict()
			def_block = block_define[0][1]
			for var in def_block:
				v = plplus_class.variable_class(var)
				self.vars[v.name] = v
	class function_param_class(object):
		def __init__(self,param_def):
			#print "param_def",param_def
			self.in_out_type = "in"
			for attr in param_def():
				if attr.__name__ == "param_name":
					self.name = attr()
				elif attr.__name__ == "param_type":
					self.in_out_type = attr()
				elif attr.__name__ == "datatype":
					# self.kind = attr()[0].__name__
					# if self.kind == "cfttype":
					# 	self.type = attr()[0]()[0]
					# else:
					# 	self.type = attr()[0]()
					self.datatype = plplus_class.datatype_class(attr)
		def __unicode__(self):

			return u'Param(%s,%s,%s)'%(self.name,self.in_out_type,self.datatype)
		def __repr__(self):

			return unicode(self)

					#print "attr=",attr,"kind=",self.kind
			#print "self=",self.name,self.in_out_type,self.kind,self.type
	class datatype_class(object):
		def __init__(self,datatype_def):
			#print "data_type_def=",datatype_def
			#attr = datatype_def()[0]
			self.kind = datatype_def()[0].__name__
			if self.kind == "cfttype":
				self.type = datatype_def()[0]()[0]
			else:
				self.type = datatype_def()[0]()
		def __unicode__(self):

			return u'DataType(%s,%s)'%(self.kind,self.type)
		def __repr__(self):

			return unicode(self)

	class function_class(object):
		
		def __init__(self,func_def):
			#print "func=",func_def.what			
			self.name = func_def.what[0].what
			self.return_type = plplus_class.datatype_class(func_def.what[2]()[0]) #2 Это return_type
			self.params = dict()
			for p in func_def.what[1].what:
				param = plplus_class.function_param_class(p)
				self.params[param.name] = param
		def __unicode__(self):

			return u'Function(%s,%s)'%(self.name,self.params)
		def __repr__(self):

			return unicode(self)


	def __init__(self, plplus_text):
		#super(plplus_class, self).__init__(plplus_text)
		self.plplus_text = plplus_text
		#self.plplus_text = plplus_text
		# self.parse()
		# self.load()

	def parse(self,start = None):

		

		def comment():			return [(re.compile(r"--.*")), re.compile("/\*.*?\*/", re.S)]
		def symbol():           return re.compile(r"\w+")
		
		def null():				return "null"#re.compile(r"null")
		def string():			return "'",re.compile(r"(.+?)(?=')"),"'"
		def number():			return re.compile(r"\d+(\.\d+)?")
		#def string():			return re.compile(r"\'.*\'")
		def basetype():			return re.compile(r"integer|date|clob|blob|boolean|(varchar2|number)(\(\d+\))?")
		def cfttype():			return 0,"ref",0,"::","[",re.compile(r"\w+"),"]"
		def macro_type():		return re.compile(r"[&a-zA-Z_.0-9]+")
		def datatype():			return [basetype,cfttype,macro_type]
		#def null():			return "null"
		#def variable():		return symbol
		def var_define():		return symbol,datatype,";"				
		#def var_define():		return symbol,[basetype,cfttype,macro_type],";"
		#def null_statement():	return null
		def return_statement():	return keyword("return"),expression
		def pragma_statement():	return keyword("pragma"),symbol,";"
		#def undefined_statement(): return re.compile(r".*"),";"
		def attr_name():		return [("[",re.compile(r"\w+"),"]"),(re.compile(r"\w+"))]
		def meth_name():		return [("[",re.compile(r"\w+"),"]"),(re.compile(r"\w+"))]
		def cft_attr():			return [(cfttype,".",attr_name),attr_name],-1,(".",attr_name)
		#def cft_attr():			return 0,(cfttype,".",attr_name),-1,(".",attr_name)
		def cft_method():		return cfttype,-2,(".",attr_name)
		def condition():		return [(expression,re.compile(r"=|!=|>|>=|<|<="),expression),
										 (expression,re.compile(r"is null|is not null"))]
		def where():			return condition,-1,(["and","or"],condition)
		def condition_list():	return condition,-1,(["and","or"],condition)
		def short_locate():		return "::",cfttype,"(",where,-1,")"
		def cft_method_param():	return 0,(symbol,"=="),expression
		def cft_method_params():return cft_method_param,-1,(",",cft_method_param)
		def cft_method_call():	return cft_method,"(",-1,cft_method_params,")"
		def expression():		return [cft_attr,short_locate,symbol,string,number,null]
		def asign_statement():	return [symbol,cft_attr],":=", expression
		def if_statement():		return keyword("if"),condition_list,keyword("then"),-2,statement,ignore("end if")
		def statement():		return [if_statement,
										asign_statement,
										null,
										return_statement,
										pragma_statement,
										cft_method_call],";"
		def param_type():		return re.compile(r"in out|in|out")
		def param_name():		return re.compile(r"\w+")
		def func_param():		return param_name,0,param_type,datatype
		def func_params():		return func_param,-1,(',',func_param)
		def func_init():		return keyword('function'),symbol,"(",func_params,")",keyword('return'),datatype,keyword('is'),define_block,body_block
		def func_def():			return keyword('function'),symbol,"(",func_params,")",keyword('return'),datatype,";"
		def define_block():		return -2,[var_define,func_def,func_init,pragma_statement]
		def exception_when():	return keyword("when"),re.compile(r"(?i)others|no_data_found|too_many_rows"),keyword("then")#
		def exception_block():	return exception_when,-2,statement
		def exceptions_block():	return keyword("exception"),-2,exception_block
		def body_block():		return keyword("begin"),-2,statement,0,exceptions_block,keyword("end"),";"
		def block():			return 0,define_block,0,body_block
		def header():			return ignore(r'╒═+╕\n│ +'.decode('utf-8')),re.compile(r'[A-Z]+'),ignore(r' *│\n'.decode('utf-8'))
		def section():			return header,block,ignore(r'└─+┘\n'.decode('utf-8'))
		#def plplus_language():  return -2,block
		def plplus_language():  return -2,section
		########################
		#3 для секции exec поиск только переменных
		def exec_block():   	return -1,var_define,0,(keyword("begin"),-1,ignore(r".*?;",re.S),0,keyword("end"))
		########################
		#4 для private
		def private_pragma():				return keyword("pragma"),ignore(r".*?;")
		#def any_text(): 					return re.compile(r"(?!begin)(?!end;).*?((?=begin)|(?=end;))",re.S)
		def any_text(): 					return ignore(r"(?!begin)(?!end;).*?((?=begin)|(?=end;))",re.S)
		def begin_block():					return 0,keyword("declare"),0,any_text,keyword("begin"),-2,[any_text,begin_block],0,ignore(r"end;")
		def return_type():					return datatype
		def private_func_init_vars_only():	return keyword('function'),symbol,"(",func_params,")",keyword('return'),return_type,keyword('is'),begin_block
		def private_block(): 				return -1,[func_def,private_func_init_vars_only,var_define,private_pragma]
		
		
		start_lambda = plplus_language
		if start:
			if start == "private":
				self.result = parseLine(self.plplus_text,private_block,[],True,comment)

				lang = self.result[0][0].what
				self.variables = dict()
				self.funcs = dict()
				for s in lang:
					if s.__name__ == "var_define":
						v = plplus_class.variable_class(s) 
						self.variables[v.name] = v
					elif s.__name__ == "private_func_init_vars_only":
						v = plplus_class.function_class(s)
						self.funcs[v.name] = v
						#print "v=",v.__name__
			elif start == "exec_block":
				self.result = parseLine(self.plplus_text,exec_block,[],True,comment)
				lang = self.result[0][0].what 	#plplus-language
				self.variables = dict()
				for s in lang:
					v = plplus_class.variable_class(s) 
					self.variables[v.name] = v
		else:
			self.result = parseLine(self.plplus_text,plplus_language,[],True,comment)
		
		return self
	
	def exec_block_parser(self):
		return self.parse("exec_block")
	def private_parser(self):
		return self.parse("private")

	def load(self):
		lang = self.result[0][0][1] 	#plplus-language
		self.last 	= self.result[1]
		self.block 	= plplus_class.block_class(lang[0][1])
		for vk,vv in self.block.vars.iteritems():
			print vk,vv.type,vv.type_name
	def pyAST2XML(self,text):
		pyAST = text
		if isinstance(pyAST, unicode) or isinstance(pyAST, str):
			return escape(pyAST)
		if type(pyAST) is Symbol:
			result = u"<" + pyAST[0].replace("_", "-") + u">"
			for e in pyAST[1:]:
				result += self.pyAST2XML(e)
			result += u"</" + pyAST[0].replace("_", "-") + u">"
		else:
			result = u""
			for e in pyAST:
				result += self.pyAST2XML(e)
		return result
	@property
	def result_xml(self):

		return self.pyAST2XML(self.result)

	def to_object(self):
		class symbol_class(object):
			def __init__2(self,text):
				self.name = u""
				#self.value = u""
				#print "text=",text
				if type(text) is tuple:
					self.unparsed = text[1]
					text = text[0]
				
				if type(text) is list and len(text) == 1:
					text = text[0]
					

				
				if type(text) is Symbol:					
					self.name = text[0]
					text = text[1]
					if isinstance(text, unicode) or isinstance(text, str):		
						#print "UNICODE6",type(text)			
						self.value = text#.encode("utf-8")					
					if type(text) is list:
						if len(text) == 1:
							if type(text) is list and len(text) == 1 and (isinstance(text[0], unicode) or isinstance(text[0], str)):
								#print "TEXT='%s'"%text
								#print "UNICODE2"		
								self.value = text[0]
							else:
								#print "UNICODE3"		
								self.value = symbol_class(text)
						elif len(text) > 1:
							print "LEN>1",self.name
							#print "TEXT=",text
							#print "NAME=",self.name
							#print "value=",text[1].__name__

							#проверяем из каких типов состоит массив
							s = set([type(a) for a in text])							
							#если он состоит только из элементов Symbol
							if len(s) == 1 and Symbol in s:
								#проверяем что все Symbol одного типа
								if len(set([a.__name__ for a in text])) == 1:
									self.value = dict()
									for a in text:
										sym = symbol_class(a)
										#v = object()
										#setattr(v,sym.value.name,sym.value.value)
										self.value[sym.name] = sym.value#print "TEXT=",
										#print "NAME=",sym.name,u"VALUE="+sym.value.__unicode__()#.encode('utf-8')
								else:
									self.value = [symbol_class(a) for a in text]
									#print "SELF.VALUE=",self.value.__repr__().encode('utf-8')
							#если элемент состоит из строки и символа за ней
							elif len(s) > 1 and (isinstance(text[0], unicode) or isinstance(text[0], str)) \
										    and type(text[1]) is Symbol:
								#print "UNICODE4"
								self.name = text[0]
								self.value = symbol_class(text[1])
							else:
								#print "UNICODE5",self.name
								self.value = [symbol_class(a) for a in text]


								#print "value=",self.value.__repr__().encode('utf-8').decode('unicode-escape')
								#for a in self.value:
								#	print "a=",a.name,"value=",a.value
								#if not hasattr(a,"name") and type(a.value) is Symbol:
								#	self = symbol_class(a.value)

								d = dict([(a.name,a.value)for a in self.value])
								if len(self.value) == len(d):
									self.value = d
					#else:
						#print "TYPE=",type(text)
				if isinstance(text, unicode) or isinstance(text, str):		
					#print "UNICODE",text
					self.value = unicode(text)
				if not self.value:
					print "NONE=",self.name,type(text),text
					if type(text) == list:
						print "LEN=",len(text)
			def __init__(self,text):
				self.name = u""
				#self.value = u""
				#print "text=",text
				if type(text) is tuple:
					self.unparsed = text[1]
					text = text[0]
				if type(text) is list and len(text)==1:
					#print "LISTTYPE"
					text = text[0]


				if isinstance(text, unicode) or isinstance(text, str):
					self.value = text
				elif type(text) is Symbol:
					#print "SYMBOL=",text[0]
					self.name = text[0]
					a = text[1]
					if isinstance(a, unicode) or isinstance(a, str):
						#print "SYMBOL UNICODE"
						self.value = a
					#elif type(a) is Symbol:
					else:
						#print "SYMBOL NEW"
						self.value = symbol_class(a)
					#self.set_value(text[1])
					#for e in pyAST[1:]:
					#	result += self.pyAST2XML(e)
					#result += u"</" + pyAST[0].replace("_", "-") + u">"
				else:
					#print "LIST",len(text),self.name
					if len(text)==1:
						a = text[0]
						#print "TYPE",type(a)
						if isinstance(a, unicode) or isinstance(a, str):
							#print "1SYMBOL UNICODE"
							self.value = a
						#elif type(a) is Symbol:
						else:
							#print "1SYMBOL NEW"
							self.value = symbol_class(a)

					elif len(text)>1:
						self.value = list()
						for a in text:
							if isinstance(a, unicode) or isinstance(a, str):
								#print "UNICODE"
								self.value.append(a)
							elif type(a) is Symbol:
								#print "new"
								#print "LIST EL TYPE=",type(a)
								self.value.append(symbol_class(a))
							#self.set_value(a)
					else:
						#print "len=",len(text)
						self.value = ""
			# def set_value(self,a):
			# 	if isinstance(a, unicode) or isinstance(a, str):
			# 		self.value.append(a)
			# 	elif type(a) is Symbol:
			# 		self.value.append(symbol_class(a))
					

			def __unicode__(self):
				value_text = u""
				if type(self.value) == list:
					for i,a in enumerate(self.value):
						value_text += u" %2s:%s\n"%(i,unicode(a))

					value_text = u"\n[%s]\n"%value_text.rstrip('\n')[1:]
				elif type(self.value) == dict:
					r = u""
					for k,v in self.value.iteritems():
						r += u"%s:%s,"%(k,v)
					value_text = "{%s}"%r.rstrip(",")
					#value_text = u"{%s:%s}"%(self.value.__repr__().decode('unicode-escape')
				else:
					value_text = self.value#.decode('utf-8')
				
				value_text = u"{%s,%s}"%(self.name,value_text)
				#print u"value_text="+value_text#.decode('utf-8')
				return value_text
			def __str__(self):
				#print "STR"
				return self.__repr__().encode('utf-8')
				# value_text = ""
				# if type(self.value) == list:
				# 	for a in self.value:
				# 		value_text += "\n" + a
				# elif type(self.value) == dict:
				# 	#import unicodedata					
				# 	#print "значение = ",self.value.__repr__().decode('unicode-escape')
				# 	#print "VALUETYPE=",type(self.value)
				# 	print "REPR=",self.value.__repr__()
				# 	value_text = self.value.__repr__().encode('utf-8')
				# 	#print u"value_text="+value_text#.decode('utf-8')
				# else:
				# 	#print "value=",self.value
				# 	value_text = self.value
				# value_text = value_text.decode("utf-8")
				# value_text = "{%s,%s}"%(self.name,value_text)
				# #print u"value_text="+value_text#.decode('utf-8')
				# return value_text
			def __repr__(self):
				#print "unicode",unicode(self)
				return unicode(self)#.encode('utf-8')
			def __getitem__(self, key):
				#if type(self.value) == list:
				#	return self.
				#cl = self.classes[key]
				#cl.update()
				return self.value[key]
			def __getattr__(self,name):
				if self.name == name:
					return self.value
		return symbol_class(self.result)

class print_cmdCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		view = dataView.active()
		
		p = plplus(view.current_text)
		print p.funcs
		print p.func
		print p.vars
		#print view.current_text


#Класс для обработки событий
#например события открытия выпадающего списка
class el(sublime_plugin.EventListener):
	def on_activated(self,view):
		pass
		#print "on_activated"
	def on_load(self,view):
		#print "on_load_"
		pass
	def on_pre_save(self,view):
		#print "on_pre_save_"
		pass
	def on_post_save(self,view):		
		pass
		#print "on_post_save"
	def on_modified(self,view):
		if view:
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
		
		if view.match_selector(locations[0], 'source.python'):

			return []
		print "ON_QUERY_COMPLETIONS"
		#print "1:%s,2:%s,3:%s,4:%s" % (self,view,prefix,locations)

		view = dataView(view)
		#completion_flags = sublime.INHIBIT_WORD_COMPLETIONS #Только то что в списке
		completion_flags = sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS #Список и автоподсказки
		
		a = []
		last_text = view.until_caret_row_text
		#last_section = plplus_class(view.text[:locations[0]]).blocks_parser().last_section
		#print last_section
		#print last_text
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
			t = timer()
			current_class = None

			
			is_class = None

			#for m in re.finditer(r"((::)*\[[a-zA-Z_#0-9]+\])",view.until_caret_row_text):
			for m in re.finditer(r"((::)*\[*[a-zA-Z_#0-9]+\]*)",view.until_caret_row_text):
				name = m.group(1)
				if name[0:2] == "::":
					current_class = db[name[3:-1]]
					#a = current_class.autocomplete
					is_class = True
						#a = current_class.attrs.autocomplete
				elif current_class:
					if current_class.attrs.has_key(name[1:-1]):
						current_class = current_class.attrs[name[1:-1]].self_class
						if current_class.base_class_id == 'COLLECTION':
							current_class = current_class.target_class
						if current_class.base_class_id == 'REFERENCE':
							current_class = current_class.target_class

						#a = current_class.autocomplete
						is_class = True
						#print current_class			
				else:
					
					#variables = plplus_class(view.sections[view.current_section].text).exec_block_parser().variables
					#variables = plplus_class(last_section.text).exec_block_parser().variables
					#variables = exec_parser_class(last_section.text).variables

					# if name in variables:
					# 	v = variables[name]
					# 	if v.kind == "cft":
					# 		current_class = db[v.type]
					x,arr = view.block_autocomplete
					if arr.has_key(name):

						current_class = arr[name]
						#print "ARR=",arr

					if name == "this":
						current_class = view.data.class_ref

					is_class = True
			if current_class:
				if is_class:				
					a = current_class.autocomplete
				else:
					a = current_class.attrs.autocomplete

			# if not a:#Если автокомплит еще не заполнен
			# 		 #попытаемся заполнить его парсером plplus
			# 	plplus_text = view.until_caret_text[:-1]
			# 	plplus = plplus_class(plplus_text)
			# 	plplus.parse()
			# 	#print plplus.result#_xml
			# 	#print plplus.result
			# 	if plplus.block.vars.has_key(plplus.last):
			# 		v = plplus.block.vars[plplus.last]
			# 		if v.type == "cfttype":
			# 			a = db[v.type_name].attrs.autocomplete
						##print a


			t.print_time("DOT")
		elif last_text[-2:] == "::": #Вводим класс
			a = db.classes.autocomplete
			# elif view.current_section == 'EXECUTE':# last_section.name == 'EXECUTE':
			# 	#print "EXECUTE"
			# 	#for v in exec_parser_class(last_section.text).variables:
			# 	#	print v

			# 	#переменные из секции EXECUTE
			# 	a = [("E %s\t%s"%(v.name,v.type),""+v.name) for vk,v in plplus_class(last_section.text).exec_block_parser().variables.iteritems()]
			# 	#переменная THIS
			# 	a.append(("E this\t%s"%view.data.class_ref.id,"this"))
			# 	#Локальные объявления, функции и переменные
			# 	blocks_parser = plplus_class(view.text).blocks_parser()
			# 	private_parser = plplus_class(blocks_parser.sections["PRIVATE"].text).private_parser()
			# 	for fk,f in private_parser.funcs.iteritems():
			# 		params_snippet = "\n\t "
			# 		for i,(pk,p) in enumerate(f.params.iteritems()):
			# 			params_snippet += "%-15s --%-2s %s\n\t,"%(p.name,i,p.datatype.type)
			# 		params_snippet = params_snippet.rstrip("\t,")
			# 		a.append(("L %s()\t%s"%(f.name,f.return_type.type),"%s(%s);"%(f.name,params_snippet)))

			# 	for vk,v in private_parser.variables.iteritems():
		# 		a.append(("L %s\t%s"%(v.name,v.type),v.name))
		else:
			#t,tt = view.block_autocomplete
			#a += t
			a += plplus(view.current_text).autocomplete
			#print "A=",a

		#completion_flags = sublime.INHIBIT_EXPLICIT_COMPLETIONS | sublime.INHIBIT_WORD_COMPLETIONS
		#completion_flags = sublime.INHIBIT_WORD_COMPLETIONS
		completion_flags = sublime.INHIBIT_EXPLICIT_COMPLETIONS
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
        sublime.set_timeout(self.show_auto_complete, 1)

    def show_auto_complete(self):
    	#print "second"
        self.view.run_command(
            'auto_complete', {
                'disable_auto_insert': True,
                'api_completions_only': True,
                'next_completion_if_showing': False
            }
        )
