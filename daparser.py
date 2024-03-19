#!/usr/bin/python3
# Disc Archive Parser Library
# Powered by Ayaka7452
# Version: 1.0.0 Release




import os
import re
import py7zr
import base64
import shutil
import codecs
import chardet
import tempfile
from configparser import ConfigParser



class rawdaparser(object):
	
	
	def __init__(self):
		# defines
		# disc pack path
		self.discpak = None
		self.dpdb = None
		# disc archive record path
		self.archrec = None
		self.__writemode = False
		# disc pack metadata path
		self.metadat = None
		self.__mdwritemode = False
		# content storage of record file
		self.rname = None
		self.rdate = None
		self.rform = None
		self.disct = None
		self.conte = None
		self.rdesc = None
		self.redun = None
		self.custm = None
		# content storage of meta-data file
		self.mname = None
		self.mdate = None
		self.mdesc = None
		self.mloca = None
		self.mlkst = None
		self.mmaxd = None
		# disc pack data storage for reading dpdb
		self.recpack = []
		self.mdpack = []
		self.__dbwrite = False
		# temporary directory
		self.tmpdir = None
	
	
	def __del__(self):
		# cleans up temp directory
		if self.tmpdir != None and os.path.exists(self.tmpdir) and os.path.isdir(self.tmpdir):
			shutil.rmtree(self.tmpdir)
		
	
	# defines
	global DEF_DP_SFX
	global DEF_MASKING_KEY
	global DEF_FILEOP_NAME
	global STD_ROOTFD_NAME
	global STD_METADATA_NAME
	global STD_RECORD_SFX
	global STD_DP_SFX
	global NO_RES
	DAPARSER_VERSION = 'Alpha'
	DEF_DP_SFX = '.dpdb'
	DEF_MASKING_KEY = 'QXlha2E3NDUy'
	STD_ROOTFD_NAME = 'disc_pack'
	DEF_FILEOP_NAME = 'operating.dpdb'
	STD_METADATA_NAME = 'meta-data.ini'
	STD_RECORD_SFX = '.ini'
	STD_DP_SFX = '.dpdb'
	NO_RES = 'no_result'
	
	
	# reset all variables
	def resetall(self):
		self.mdclose()
		self.daclose()
		
		
	# open a record file
	# params:
	# targetf - the record file target
	def daopen(self, targetf, mode = None):
		

		if mode:
			match mode:
				case 'w':
					# write mode
					self.__writemode = True
					self.archrec = targetf
					return targetf
				case 'r':
					# read mode
					pass
		
		
		# default: read mode
		self.__writemode = False
		# errors check
		if not os.path.exists(targetf) or not os.path.isfile(targetf):
			raise FileNotFoundError
		
		# check record file validation
		self.recvali(targetf)
		
		self.archrec = targetf
		
		return targetf
		
	
	# closes an opened record
	def daclose(self):
		# reset all variables to none
		self.archrec = None
		self.archnrecf = None
		self.rname = None
		self.rdate = None
		self.rform = None
		self.disct = None
		self.conte = None
		self.rdesc = None
		self.redun = None
		self.custm = None
		self.__writemode = False
		
	
	
	# open a disc pack folder
	# targetd - should be the path of disc pack folder or the path of meta-data.ini
	def dpopen(self, targetd):
		
		cp = ConfigParser()
		
		if os.path.isfile(targetd):
			raise ValueError('object must be a folder')
	
		if not os.path.exists(targetd):
			raise ValueError('no such directory')
			
		# scans disc pack and validates it
		res = self.dpscan(targetd)[0]
		if res:
			pass
		else:
			raise ValueError('target disc pack contains invalid contents')
			
		self.discpak = targetd
		
	
	# closes a opened disc pack
	def dpclose(self):
		# reset discpak to none
		self.discpak = ''
		
		
	# open a meta-data file
	def mdopen(self, targetf, mode = None):
		
		if mode:
			match mode:
				case 'w':
					# write mode
					self.__mdwritemode = True
					self.metadat = targetf
					return targetf
				case 'r':
					# read mode
					pass
		
		
		# default: read mode
		# error check
		if not os.path.exists(targetf) or not os.path.isfile(targetf):
			raise FileNotFoundError
		
		# check record file validation
		self.mdvali(targetf)
		
		self.metadat = targetf
		
		return targetf


	# closes a opened metadata file
	def mdclose(self):
		# reset metadata items to none
		self.__mdwritemode = False
		self.mname = None
		self.mdate = None
		self.mdesc = None
		self.mloca = None
		self.mlkst = None
		self.mmaxd = None



	# reads disc pack metadata
	# params:
	# target - content target of meta-data.ini
	def mdget(self, target):
		
		# mode check
		if self.__mdwritemode:
			raise Exception('file cannot be read in write mode')
		
		cp = ConfigParser()
		
		metafile = os.path.join(self.discpak + '/meta-data.ini')
		
		if not os.path.exists(metafile):
			raise FileNotFoundError
		
		# read start
		cp.read(metafile)
		
		# basic data
		dpname = cp.get('Basic', 'name')
		dpdate = cp.get('Basic', 'date')
		
		# detail data
		dpdes = cp.get('Detail', 'description')
		dploc = cp.get('Detail', 'location')
		
		# param data
		dplock = cp.get('Param', 'lockstate')
		dpmaxd = cp.get('Param', 'maxdisc')
		
		# target handler
		match target:
			
			case 'n':
				return dpname
			
			case 'd':
				return dpdate
				
			case 'ds':
				return dpdes
			
			case 'l':
				return dploc
				
			case 'ls':
				return dplock
			
			case 'm':
				return dpmaxd
				
			case _:
				raise ValueError('target param empty')
				
	
	
	# reads metadata file
	def mdread(self):
		
		# mode check
		if self.__mdwritemode:
			raise Exception('file cannot be read in write mode')
		
		cp = ConfigParser()
		
		if not os.path.exists(self.metadat):
			raise FileNotFoundError
		
		# read start
		cp.read(self.metadat, encoding = 'utf-8')
		# basic data
		self.mname = cp.get('Basic', 'name')
		self.mdate = cp.get('Basic', 'date')
		
		# detail data
		self.mdesc = cp.get('Detail', 'description')
		self.mloca = cp.get('Detail', 'location')
		
		# param data
		self.mlkst = cp.get('Param', 'lockstate')
		self.mmaxd = cp.get('Param', 'maxdisc')
		
		# read completed



	# reads specified record items of record file
	# params:
	# target - target content of reading
	def daget(self, target):
		
		if self.__writemode:
			raise Exception('file cannot be read in write mode')
		
		cp = ConfigParser()
		
		# archrec state detect
		if not self.archrec:
			raise FileNotFoundError
		
		cp.read(self.archrec, encoding = 'utf-8')
		
		# check format validation
		if not 'Basic' in cp.sections():
			raise ValueError('file format invalid')
		if not 'Content' in cp.sections():
			raise ValueError('file format invalid')
		
		# reads basic info
		try:
			recname = cp.get('Basic', 'name')
			recdate = cp.get('Basic', 'date')
			rformat = cp.get('Basic', 'rformat')
			disctyp = cp.get('Basic', 'disctype')
		except:
			raise ValueError('file format invalid')
				
		# handles the target param
		match target:
			
			# name of record
			case 'n':
				return recname
		
			# date of record
			case 'd':
				return recdate
		
			# record format
			case 'f':
				return rformat
			
			# disc type
			case 'dt':
				return disctyp
				
			# reads record content
			case 'ct':
				contentdat = cp.items('Content')
				
				return contentdat
						
			case 'rd':
						
				try:
					redundat = cp.items('Redundancy')
				except:
					return ''
						
				return redundat
						
			case 'ds':
						
				try:
					descri = cp.items('Description')
				except:
					return ''
							
				return descri
					
			case 'cs':
						
				try:
					customd = cp.items('Custom')
				except:
					return ''
							
				return customd
		
		
			# error exit
			case _:
			
				raise ValueError('unsupported disc type')


	
	# lists all records in opened disc pack
	def lsrec(self):
		
		# locates the records folder
		recdir = os.path.join(self.discpak + '/records')
		
		if not os.path.exists(recdir) or os.path.isfile(recdir):
			raise ValueError('cannot access records folder')
			
		reclist = os.listdir(recdir)
		
		return reclist
		
	
	# reads the content of whole record file to object
	def daread(self):
		
		if self.__writemode:
			raise Exception('file cannot be read in write mode')
		
		cp = ConfigParser()
		
		if not os.path.exists(self.archrec):
			raise FileNotFoundError
		
		# read start
		cp.read(self.archrec, encoding = 'utf-8')
		self.rname = cp.get('Basic', 'name')
		self.rdate = cp.get('Basic', 'date')
		self.rform = cp.get('Basic', 'rformat')
		self.disct = cp.get('Basic', 'disctype')
		self.conte = cp.items('Content')
		
		try:
			self.redun = cp.items('Redundancy')
		except:
			self.redun = ''
			
		try:
			self.rdesc = cp.items('Description')
		except:
			self.rdesc = ''
			
		try:
			self.custm = cp.items('Custom')
		except:
			self.custm = ''
		
		# read completed
	
	
	# select and open a record in an opened disc pack (disc pack wrapper)
	# param:
	# target - specify which record should be selected in disc pack
	def selrec(self, target, mode = None):
		
		if target == 'meta-data.ini':
			recpath = self.discpak + '/meta-data.ini'
			ismeta = True
		else:
			recpath = self.discpak + '/records/' + target
			ismeta = False
		
		if not os.path.exists(recpath) or not os.path.isfile(recpath):
			raise FileNotFoundError
			
		if ismeta:
			if mode:
				self.mdopen(recpath, mode)
			else:
				self.mdopen(recpath)
		else:
			if mode:
				self.daopen(recpath, mode)
			else:
				self.daopen(recpath)
		
		
	# record file format validation
	# param:
	# recfile - the record file to be validated
	def recvali(self, recfile):
		
		cp = ConfigParser()
		
		# errors check
		if not os.path.exists(recfile) or not os.path.isfile(recfile):
			raise FileNotFoundError
		
		try:
			cp.read(recfile, encoding = 'utf-8')
		except:
			raise ValueError('not a valid record')
		
		try:
			# try reading all key items
			recname = cp.get('Basic', 'name')
			cp.get('Basic', 'date')
			cp.get('Basic', 'rformat')
			cp.get('Basic', 'disctype')
			cp.items('Content')
			# check if name match filename
			if str.split(os.path.basename(recfile), '.')[0] != recname:
				raise Exception()
		except:
			raise ValueError('not a valid record')
	
	
	# meta data file format validation
	def mdvali(self, mdfile):
		
		cp = ConfigParser()
		
		# errors check
		if not os.path.exists(mdfile) or not os.path.isfile(mdfile):
			raise FileNotFoundError
		
		try:
			cp.read(mdfile, encoding = 'utf-8')
		except:
			raise ValueError('not a valid metadata file')
			
		try:
			cp.get('Basic', 'name')
			cp.get('Basic', 'date')
		
			# detail data
			cp.get('Detail', 'description')
			cp.get('Detail', 'location')
		
			# param data
			cp.get('Param', 'lockstate')
			cp.get('Param', 'maxdisc')
		except:
			raise ValueError('not a valid metadata file')
	
	
	
	# scans disc pack and verifies if it is valid
	def dpscan(self, discpak):
		
		cp = ConfigParser()
		
		# errors check
		if not os.path.exists(discpak) or not os.path.isdir(discpak):
			raise ValueError('disc pack must be a folder')
		
		recfd = os.path.join(discpak + '/records')
		mdfile = os.path.join(discpak + '/meta-data.ini')
		
		# scan start
		if not os.path.exists(recfd) or not os.path.isdir(recfd):
			raise ValueError('cannot access records folder')
			
		# check metadata file
		try:
			self.mdvali(mdfile)
		except ValueError:
			errnfo = ((False, 'meta-data.ini'))
			return errnfo
		
		# check records
		reclist = os.listdir(recfd)
		for rec in reclist:
			# invalid file name check
			if rec == 'meta-data.ini':
				raise ValueError('record cannot be named as meta-data.ini')
			recfp = os.path.join(recfd + '/' + rec)
			# verify each record
			try:
				self.recvali(recfp)
			except ValueError:
				errnfo = ((False, rec))
				return errnfo
				
		# validation passed
		errnfo = ((True, ''))
		return errnfo
			
	
	# writes configurated record files to disk
	# alternative mode options:
	# o - override mode: overrides a exist file
	def dawrite(self):
		
		# mode check
		if not self.__writemode:
			raise ValueError('file is not opened as write mode')
			
		filepath = self.archrec
		
		cp = ConfigParser()
		
		# Basic section
		cp.add_section('Basic')
		cp.set('Basic', 'name', self.rname)
		cp.set('Basic', 'date', self.rdate)
		cp.set('Basic', 'rformat', self.rform)
		cp.set('Basic', 'disctype', self.disct)
		
		# Content section
		cp.add_section('Content')
		if len(self.conte[0]) == 1:
			# circumstance of one-element
			cp.set('Content', self.conte[0], self.conte[1])
		else:
			# circumstance of multi-element
			for content in self.conte:
				cp.set('Content', content[0], content[1])
			
		# selective sections handling
		# Redundancy section
		if self.redun:
			cp.add_section('Redundancy')
			if len(self.redun[0]) == 1:
				# circumstance of one-element
				cp.set('Redundancy', self.redun[0], self.redun[1])
			else:
				# circumstance of multi-element
				for redun in self.redun:
					cp.set('Redundancy', redun[0], redun[1])
					
		# Description section
		if self.rdesc:
			cp.add_section('Description')
			if len(self.rdesc[0]) == 1:
				# circumstance of one-element
				cp.set('Description', self.rdesc[0], self.rdesc[1])
			else:
				for rdesc in self.rdesc:
					# circumstance of multi-element
					cp.set('Description', rdesc[0], rdesc[1])
		
		# Custom section
		if self.custm:
			cp.add_section('Custom')
			if len(self.custm[0]) == 1:
				# circumstance of one-element
				cp.set('Custom', self.custm[0], self.custm[1])
			else:
				for custm in self.custm:
					# circumstance of multi-element
					cp.set('Custom', custm[0], custm[1])
		
		
		f = open(filepath, 'w')
		cp.write(f)
		f.close()
		# write completed
		
		
	# write metadata.ini content to disk
	def mdwrite(self):
			
		# mode check
		if not self.__mdwritemode:
			raise Exception('file is not opened as write mode')
				
		filepath = self.metadat
			
		cp = ConfigParser()
			
		# applies tags
		cp.add_section('Basic')
		cp.set('Basic', 'name', self.mname)
		cp.set('Basic', 'date', self.mdate)
		cp.add_section('Detail')
		cp.set('Detail', 'description', self.mdesc)
		cp.set('Detail', 'location', self.mloca)
		cp.add_section('Param')
		cp.set('Param', 'lockstate', self.mlkst)
		cp.set('Param', 'maxdisc', self.mmaxd)
		
		f = open(filepath, 'w')
		cp.write(f)
		f.close()
		# write completed
		
		
	# creates disc pack folder structure to target path
	def mkstruct(self, targetd):
		
		if os.path.exists(targetd) and os.path.isdir(targetd):
			raise Exception('such folder is exist')
		
		os.makedirs(os.path.join(targetd))
		os.makedirs(os.path.join(targetd + '/records'))

		
	# packs a disc pack to dpdb file (dpdb: disc pack data base)
	def packdp(self):
		
		key = DEF_MASKING_KEY.encode()
		key = base64.b64decode(key)
		key = key.decode()
	
		# disc pack verification
		errnfo = self.dpscan(self.discpak)
		if not errnfo[0]:
			raise ValueError('invalid disc pack specified')
			
		# get the name of disc pack
		self.selrec('meta-data.ini')
		dpname = self.mdget('n')
		self.mdclose()
		
		tmpdir = tempfile.mkdtemp()
		
		# rename disc pack folder to standard name
		shutil.move(self.discpak, tmpdir)
		oldfdn = os.path.join(tmpdir + '/' + os.path.basename(self.discpak))
		newpath = os.path.join(tmpdir + '/' + STD_ROOTFD_NAME)
		os.rename(oldfdn, newpath)
		
		# start packing
		zout = os.path.join(self.discpak + '/../' + dpname +  DEF_DP_SFX)
		z = py7zr.SevenZipFile(zout, mode = 'w', password = key)
		z.writeall(path = newpath, arcname = STD_ROOTFD_NAME)
		z.close()
		shutil.rmtree(tmpdir)
		# done packing
		

	# unpack dpdb file as disc pack folder
	def unpkdp(self, targetf, mode = None):
		
		if not os.path.exists(targetf) or os.path.isdir(targetf):
			raise Exception('specify a valid file')
		
		key = DEF_MASKING_KEY.encode()
		key = base64.b64decode(key)
		key = key.decode()
		
		extpath = os.path.dirname(targetf)
		
		# start unpack
		z = py7zr.SevenZipFile(targetf, mode='r', password = key)
		z.extractall(path = extpath)
		z.close()
		# done unpack
		
		# rename mode: rename extracted folder to its disc pack name
		if mode == 'r':
			# recover disc pack name
			self.dpopen(extpath + '/' + STD_ROOTFD_NAME)
			dpname = self.mdget('n')
			self.dpclose()
			os.rename(os.path.join(extpath + '/' + STD_ROOTFD_NAME), os.path.join(extpath + '/' + dpname))
			# all done
			
	
	# converts all files to utf-8 codec under specified folder
	def fd2utf8(self, fd):
		
		if not os.path.exists(fd) or not os.path.isdir(fd):
			raise Exception('target must be a exist folder')
		
		flist = os.listdir(fd)
		
		for file in flist:
			ffp = os.path.join(fd + '/' + file)
			
			with open(ffp, 'r') as f:
				conte = f.read()
			with open(ffp, 'w', encoding = 'utf-8') as f:
				f.write(conte)



class daparser(rawdaparser):
	
	
	# open a dpdb file
	def open(self, targetf, mode = None):
		
		# check if already opened
		if self.dpdb:
			raise Exception('file has already been opened')
		
		if mode == 'w':
			# write mode
			self.__dbwrite = True
			self.dpdb = targetf
		else:
			# file check
			if not os.path.exists(targetf) or os.path.isdir(targetf):
				raise Exception('file not found')
			
			# opening file
			self.dpdb = targetf
			self.tmpdir = tempfile.mkdtemp()
			tmpfile = os.path.join(self.tmpdir + '/' + DEF_FILEOP_NAME)
			tmpdp = os.path.join(self.tmpdir + '/' + STD_ROOTFD_NAME)
			
			# unpack file
			shutil.copy(self.dpdb, tmpfile)
			self.unpkdp(tmpfile)
			self.dpopen(tmpdp)


	# close an opened dpdb file
	def close(self):
		self.dpclose()
		self.dpdb = None
		self.__dbwrite = False
		if not self.tmpdir:
			pass
		elif os.path.exists(self.tmpdir) and os.path.isdir(self.tmpdir):
			shutil.rmtree(self.tmpdir)
		self.tmpdir = None
		
	
	# erase cached data packs
	def erase(self, target = None):
		
		if not target:
			# erases all packs by default
			self.recpack = []
			self.mdpack = []
		elif target == 'r':
			# erases record pack
			self.recpack = []
		elif target == 'm':
			# erases metadata pack
			self.mdpack = []
		else:
			raise ValueError('invalid target parameter')
		
		
	# loads all the dpdb to ram
	def read(self):
		
		if self.recpack:
			raise Exception('erase old content before read')
		
		try:
			
			# read meta-data info from file
			self.selrec(STD_METADATA_NAME)
			self.mdread()
			# pack metadata to ram
			self.mdpack = [self.mname, self.mdate, self.mdesc, self.mloca, self.mlkst, self.mmaxd]
			self.mdclose()
			
			# read record contents from file
			reclist = self.lsrec()
			for rec in reclist:
				self.selrec(rec)
				self.daread()
				# pack records to ram
				self.recpack.append([self.rname, self.rdate, self.rform, self.disct, self.conte, self.rdesc, self.redun, self.custm])
				self.daclose()
				
		except:
			raise Exception('no valid files specified')

		
	# ls all records in dpdb file
	def ls(self):
		
		if not self.recpack:
			raise ValueError('recpack is empty')
			
		reclist = []
		
		snum = 0
		for i in self.recpack:
			reclist.append(i[0])
		
		return reclist

	
	# write cached record pack to file
	def write(self):
		
		# write mode check
		if not self.__dbwrite:
			raise ValueError('file cannot be written in read mode')
		
		tmpd = tempfile.mkdtemp()
		tmpdp = os.path.join(tmpd + '/' + STD_ROOTFD_NAME)
		tmpr = os.path.join(tmpdp + '/records')
		self.mkstruct(tmpdp)
		
		# write records
		for i in self.recpack:
			# read data from pack
			self.rname = i[0]
			self.rdate = i[1]
			self.rform = i[2]
			self.disct = i[3]
			self.conte = i[4]
			self.rdesc = i[5]
			self.redun = i[6]
			self.custm = i[7]
			# write single record file
			self.daopen(os.path.join(tmpr + '/' + self.rname + STD_RECORD_SFX), 'w')
			self.dawrite()
			self.daclose()

		

		# read data from pack
		self.mname = self.mdpack[0]
		self.mdate = self.mdpack[1]
		self.mdesc = self.mdpack[2]
		self.mloca = self.mdpack[3]
		self.mlkst = self.mdpack[4]
		self.mmaxd = self.mdpack[5]
		dpname = self.mname
		self.mdopen(os.path.join(tmpdp + '/' + STD_METADATA_NAME), 'w')
		self.mdwrite()
		self.mdclose()
		
		# convert record files to UTF-8 codec
		self.fd2utf8(tmpr)
					
		# repack disc pack
		self.dpopen(tmpdp)
		self.packdp()
				
		# move it to target path
		if os.path.exists(self.dpdb):
			# overrides the original file
			os.remove(self.dpdb)

		# creating a new file
		shutil.move(os.path.join(tmpd + '/' + dpname + STD_DP_SFX), self.dpdb)
			
		# write completed
		
	
	# seek target items by using keywords
	def seek(self, phrase = {}):
		
		if phrase == []:
			raise Exception('no param specified')
		if not self.recpack:
			raise ValueError('recpack is empty')
		
		try:
			# variables init
			reclist = self.recpack
			reslist = []
			ctlist = []
			dlist = []
			flist = []
			dtlist = []
			dslist = []
			cslist = []
			rlist = []
			
			# search each tag
			# content
			if 'ct' in phrase:
				for rec in reclist:
					rname = rec[0] # get record name
					item = rec[4] # get record contents
					# match each filename
					for i in item:
						# match keyword
						res = re.search(phrase['ct'], i[1])
						if res:
							ctlist.append(rname)
				if not ctlist:
					return NO_RES
			
			# date
			if 'd' in phrase:
				for rec in reclist:
					rname = rec[0] # get record name
					res = re.search(phrase['d'], rec[1])
					if res:
						dlist.append(rname)
				if not dlist:
					return NO_RES
			
			# record format
			if 'f' in phrase:
				for rec in reclist:
					rname = rec[0] # get record name
					res = re.search(phrase['f'], rec[2])
					if res:
						flist.append(rname)
				if not flist:
					return NO_RES
			
			# disc type
			if 'dt' in phrase:
				for rec in reclist:
					rname = rec[0] # get record name
					res = re.search(phrase['dt'], rec[3])
					if res:
						dtlist.append(rname)
				if not dtlist:
					return NO_RES

			# description
			if 'ds' in phrase:
				for rec in reclist:
					rname = rec[0] # get record name
					item = rec[5] # get description
					# match each filename
					for i in item:
						# match keyword
						res = re.search(phrase['ds'], i[1])
						if res:
							dslist.append(rname)
				if not dslist:
					return NO_RES

			# redundancy
			if 'r' in phrase:
				for rec in reclist:
					rname = rec[0] # get record name
					item = rec[6] # get redundancy info
					# match each filename
					for i in item:
						# match keyword
						res = re.search(phrase['r'], i[1])
						if res:
							rlist.append(rname)
				if not rlist:
					return NO_RES
				
				
			# custom info
			if 'cs' in phrase:
				for rec in reclist:
					rname = rec[0] # get record name
					item = rec[7] # get custom info
					# match each cs
					for i in item:
						# match keyword with tag
						tag = re.search(phrase['cs'][0], i[0])
						# match keyword with custom content
						custm = re.search(phrase['cs'][1], i[1])
						if tag and custm:
							cslist.append(rname)
				if not cslist:
					return NO_RES
			
			

			# result handling logic
			ctlist = set(ctlist)
			dlist = set(dlist)
			dtlist = set(dtlist)
			flist = set(flist)
			rlist = set(rlist)
			dslist = set(dslist)
			cslist = set(cslist)
			
			if ctlist:
				reslist = ctlist
			if dlist and reslist:
				reslist = (reslist & dlist)
			elif dlist and not reslist:
				reslist = dlist
			if dtlist and reslist:
				reslist = (reslist & dtlist)
			elif dtlist and not reslist:
				reslist = dtlist
			if flist and reslist:
				reslist = (reslist & flist)
			elif flist and not reslist:
				reslist = flist
			if rlist and reslist:
				reslist = (reslist & rlist)
			elif rlist and not reslist:
				reslist = rlist
			if dslist and reslist:
				reslist = (reslist & dslist)
			elif dslist and not reslist:
				reslist = dslist
			if cslist and reslist:
				reslist = (reslist & cslist)
			elif cslist and not reslist:
				reslist = cslist
			
			return tuple(reslist)
			
		except:
			
			raise('errors encountered while searching')


	# show all info of specified record of a recpack
	def cat(self, targetr):
		
		if not self.recpack:
			raise ValueError('recpack is empty')
	
		# scan pack for target record
		try:
			snum = 0
			for i in self.recpack:
				if self.recpack[snum][0] == targetr:
					return self.recpack[snum]
				snum +=1
			return []
		except:
			raise ValueError('invalid parameter')


	# appends new record to pack
	def append(self):
		
		# check key value of new record
		if not self.rname or not self.rdate and not self.rform and not self.disct and not self.conte:
			raise ValueError('missing key content of record')
			
		# pack to a variable
		rec = []
		rec.append(self.rname)
		rec.append(self.rdate)
		rec.append(self.rform)
		rec.append(self.disct)
		rec.append(self.conte)
		if self.rdesc:
			rec.append(self.rdesc)
		else:
			rec.append('')
		if self.redun:
			rec.append(self.redun)
		else:
			rec.append('')
		if self.custm:
			rec.append(self.custm)
		else:
			rec.append('')
		
		# pack to recpack
		self.recpack.append(rec)

	
	# delete specified record from pack
	def delete(self, recn):
		
		if not self.recpack:
			raise ValueError('recpack is empty')
		
		# get full content of record
		for i in self.recpack:
			if i[0] == recn:
				self.recpack.remove(i)
				return True
		
		return False

		
