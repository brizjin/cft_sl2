# -*- coding: utf-8 -*-
from timer import timer
import os,sys,datetime

cft_path = os.path.dirname(os.path.realpath(__file__))
lib_path = os.path.join(cft_path,'libs')

if lib_path not in sys.path:
	sys.path.insert(0,lib_path)

import czipfile as zipfile
import cPickle  as pickle

class cache(dict):
	def __init__(self,file_name,read = None,read_time_func = None):
		try:
			t = timer()	
			super(cache,self).__init__()			
			self.read_time_func = read_time_func
			self.file_name 		= file_name
			self.read 			= read
			self.read_time_index= {}
			if os.path.isfile(self.file_name):	
				self.z = zipfile.ZipFile(self.file_name, "r")
			#else:
			#	o = object()
			#	o.close = lambda:None
			#	self.z = o
				if "read_time_index" in self.z.namelist():
					obj_bin  = self.z.read("read_time_index")
					self.read_time_index = pickle.loads(obj_bin)
				#else:
				#except Exception,e:
				#	self["read_time_index"] = {}
				#self.z.close()
			print u'Инициализация кэша %s за %s'%(file_name,t.interval())
		except Exception,e:
			print u"Ошибка инициалицации кэша %s, %s"%(self.file_name,e)

	def __del__(self):
		if hasattr(self,"z"):
			self.z.close()
	def get_key(self,key):
		val = ''
		if type(key) == tuple:
			val = key[0]		
			for arg in key[1:]:
				val += '/' + arg
			return val.replace('\\','/')
		else:
			return key
	def __setitem__(self,key,value):
		key = self.get_key(key)
		super(cache,self).__setitem__(key,value)

	def __getitem__(self,key):
		key = self.get_key(key)
		need_update = False
		if self.read_time_func:
			index_time				   = self.read_time_index.get(key,None)
			self.read_time_index[key]  = self.read_time_func (key)		#прочитаем время записи кэша					
			need_update = index_time  != self.read_time_index[key]
		if not need_update:	
			if key in super(cache,self).keys():
				print u"Чтение из памяти %s"%key
				return super(cache,self).__getitem__(key)							#3.Чтение из памяти        (Самая быстрая)
			elif os.path.isfile(self.file_name) and key in self.z.namelist():						
				t = timer()							
				obj_bin  = self.z.read(key)
				obj      = pickle.loads(obj_bin)
				super(cache,self).__setitem__(key,obj)								#2.Чтение из архива        (Вторая по скорости)
				print u"Чтение из архива %s за %s"%(key,t.interval())
				return obj
		if self.read:
			t = timer()
			value = self.read(key)													#1.Непосредственное чтение (По идее самое медленное)
			super(cache,self).__setitem__(key,value)							
			print u"Чтение c  диска  %s за %s %s"%(key,t.interval(),u"новая версия от %s"%self.read_time_index[key] if need_update else u'')
			return value
		return None

	def get(self,key,default = ''):
		try:
			k = self[key]
			if k:
				return k
			else:
				return default
		except KeyError as e:
			print "KEY ERROR",e
			return default

	def save_news(self):
		z = zipfile.ZipFile(self.file_name,"a",zipfile.ZIP_DEFLATED)
		for k,v in self.items():
			#z.writestr(k,json.dumps(v, ensure_ascii=False).encode('utf8'))
			z.writestr(k,pickle.dumps(v, 1))
		z.close()

	def save(self):
		
		new_filename = self.file_name + ".new"		
		old_filename = self.file_name	

		znew = zipfile.ZipFile(new_filename,"w",zipfile.ZIP_DEFLATED)
		for k,v in self.items():										#сохранили обновления
			znew.writestr(k,pickle.dumps(v, 1))
			#znew.writestr(k,v)
		znew.writestr("read_time_index",pickle.dumps(self.read_time_index, 1))

		if os.path.isfile(old_filename):
			for k in set(self.z.namelist()) - set(self.keys()) - set(["read_time_index"]) :			#перезаписываем на диске
				znew.writestr(k,self.z.read(k))
			self.z.close()

			try:
				os.remove(old_filename)				
			except Exception, e:
				print u"Ошибка удаления файла %s"%old_filename,e
			
		znew.close()		
		os.rename(new_filename,old_filename)
		if os.path.isfile(self.file_name):	
			self.z = zipfile.ZipFile(self.file_name, "r")