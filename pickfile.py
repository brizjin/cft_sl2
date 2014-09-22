# -*- coding: utf-8 -*-
import cPickle as pickle
import gzip
import os
import sublime
import zipfile
import sublime_plugin
import hashlib
import json
import datetime

plugin_name = "CFT"
cache_path  = os.path.join(sublime.packages_path(),plugin_name,"cache")


def save(object, filename, bin = 1):
	file = gzip.GzipFile(filename, 'wb')
	file.write(pickle.dumps(object, bin))
	file.close()

def load(object,filename):
	file = gzip.GzipFile(filename, 'rb')
	object = pickle.loads(file.read())
	file.close()
	return object

class timer(object):
	def __init__(self):
		self.begin = datetime.datetime.now()
	def interval(self):
		#return (datetime.datetime.now() - self.begin).seconds
		delta = datetime.datetime.now() - self.begin
		delta = float(delta.seconds) + float(delta.microseconds)/1000000
		return delta

class cache(dict):
	def __init__(self,file_name):
		super(cache,self).__init__()
		self.file_name = file_name
		
	def __setitem__(self,key,value):
		super(cache,self).__setitem__(key,value)

	def __getitem__(self,key):
		if key in super(cache,self).keys():
			return super(cache,self).__getitem__(key)
		else:
			if os.path.isfile(self.file_name):						
				t = timer()
				z = zipfile.ZipFile(self.file_name, "r")
				obj_bin  = z.read(key)			
				z.close()
				obj = pickle.loads(obj_bin)
				super(cache,self).__setitem__(key,obj)
				print u"Чтение кэша %s с диска за %s"%(key,t.interval())
				return obj
			return None
	def get(self,key,default = ''):
		try:
			return self[key]
		except KeyError as e:
			params, = e.args
			#print "ERR=",params
			return default

	def save_cache(self):
		z = zipfile.ZipFile(self.file_name,"a",zipfile.ZIP_DEFLATED)
		for k,v in self.items():
			#z.writestr(k,json.dumps(v, ensure_ascii=False).encode('utf8'))
			z.writestr(k,pickle.dumps(v, 1))
		z.close()
	def save(self):
		
		new_filename = self.file_name + ".new"		
		old_filename = self.file_name	

		znew = zipfile.ZipFile(new_filename,"w",zipfile.ZIP_DEFLATED)
		for k,v in self.items():							#сохранили обновления
			znew.writestr(k,pickle.dumps(v, 1))

		if os.path.isfile(old_filename):
			zold = zipfile.ZipFile(old_filename,"r",zipfile.ZIP_DEFLATED)
			for k in set(zold.namelist()) - set(self.keys()) :	#перезаписываем на диске
				znew.writestr(k,pickle.dumps(zold.read(k), 1))
			zold.close()
			os.remove(old_filename)			
		znew.close()		
		os.rename(new_filename,old_filename)

	def load(self,file_in_zip):
		z = zipfile.ZipFile(self.file_name,  "r")
		obj_json = z.read(file_in_zip)
		#print "C1=",obj_json
		#z.infolist()[1].comment = "TEST"
		#info = z.infolist()[0]
		#z.writestr(info, "TEST")
		z.close()
		return obj_json
		return json.loads(obj_json)
		#print obj["hello"]


	def write(self,key,value):
		z = zipfile.ZipFile(self.file_name, "a")
		#self[key] = value
		#self.z.writestr("hello\\"+hashlib.md5(key).hexdigest(), value)
		z.writestr(key, json.dumps(value, ensure_ascii=False).encode('utf8'))
		z.close()


c = cache(os.path.join(cache_path,"test3.zip"))
class test_cacheCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		# self.window.set_layout({
		#     "cols": [0, 0.5, 1],
		#     "rows": [0, 0.5, 1],
		#     "cells": [[0, 0, 1, 2], [1, 0, 2, 1],
		#                             [1, 1, 2, 2]]
		# })
				
		
		#c['classes'] = dict({u"hello":u'ПРИВЕТ!'})#'TEST STRING'
		#print c['classes2']
		z = zipfile.ZipFile(os.path.join(cache_path,"db.cfttest.cache"), "r")
		#obj_bin  = z.read(u'methods/PR_CRED')
		k = ['classes']
		print "K=",k
		print "Z=",z.namelist() - k
		z.close()
		#print len(obj_bin)
		#c.load()
		#c["classes_bin2"] = {u"hello":u'ПРИВЕТ!'}
		#c.save()

		#c.save()

		#c.write("classes",{u"hello":u'ПРИВЕТ1!'})
		#c.write("classes",{u"hello":u'ПРИВЕТ2!'})
		#c.load()