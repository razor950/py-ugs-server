#-*- coding: utf-8 -*-

from dbutils.pooled_db  import PooledDB
import pymysql
from pymysql import OperationalError, InternalError, ProgrammingError
import os

# Reading database configuration from environment variables
DB_HOST = os.getenv('DB_UGS_HOST')
DB_PORT = os.getenv('DB_UGS_PORT')
DB_USERNAME = os.getenv('DB_UGS_USERNAME')
DB_PASSWORD = os.getenv('DB_UGS_PASSWORD')
DB_NAME = os.getenv('DB_UGS_DBNAME')
DB_CHARSET = os.getenv('DB_UGS_CHARSET')

class DbConnectPool():
	def __init__(self):
		self._pool = None
		try:
			print("DbConnectPool Construct!")
			self._pool = PooledDB(
				creator=pymysql, 
				host = DB_HOST,
				port = DB_PORT if DB_PORT is not None else 3306,
				user = DB_USERNAME,
				password = DB_PASSWORD,
				db = DB_NAME,
				charset = DB_CHARSET if DB_CHARSET is not None else 'utf8mb4', 
				blocking=True, 
				mincached=10, 
				maxcached=10,
				maxshared=30, 
				maxconnections=100, 
				maxusage=0, 
				setsession=None
			)
		except Exception as why:
			print("Create PooledDB error:{0}".format(why))
	
	def _getConn(self):
		if self._pool:
			return self._pool.connection()
		else:
			raise Exception("Connection pool is not available.")

g_dbManager = DbConnectPool()

def fetchOneValue(sql, index, defValue):
	with g_dbManager._getConn() as db:
		with db.cursor() as cursor:
			try:
				cursor.execute(sql)
				ret=cursor.fetchone()
				return ret[index]
			except Exception as why:
				print("fetchOneValue error:{0}".format(why))
				return defValue
	return defValue

def fetchObjects(sql, defValue):
	with g_dbManager._getConn() as db:
		with db.cursor() as cursor:
			try:
				counts = cursor.execute(sql)
				return cursor.fetchall()
			except Exception as why:
				print("fetchObjects error:{0}".format(why))
				return defValue
	return defValue

def executeSql(sql):
	with g_dbManager._getConn() as db:
		with db.cursor() as cursor:
			try:
				counts = cursor.execute(sql)
				db.commit()
				return True
			except Exception as why:
				print("executeSql error:{0}".format(why))
				return False
	return False

def executeSql_InsertRow(sql):
	with g_dbManager._getConn() as db:
		with db.cursor() as cursor:
			try:
				counts = cursor.execute(sql)
				db.commit()
				return cursor.lastrowid
			except Exception as why:
				db.rollback()
				print("executeSql error:{0}".format(why))
				return -1
	return -1

# Common DB Function
def commonTryInsertAndGetProject(project):
	with g_dbManager._getConn() as db:
		with db.cursor() as cursor:
			try:
				sql="INSERT IGNORE INTO ugs_db.Projects (Name) VALUES ('{0}')".format(project)
				cursor.execute(sql)
				db.commit()
				sql="SELECT Id FROM ugs_db.Projects WHERE Name = '{0}'".format(project)
				cursor.execute(sql)
				ret=cursor.fetchone()
				return ret[0]
			except Exception as why:
				print("commonTryInsertAndGetProject error:{0}".format(why))
				return ""
	return ""

def commonFindOrAddUserId(userName):
	if(userName == None or len(userName)==0) : 
		return -1
	with g_dbManager._getConn() as db:
		with db.cursor() as cursor:
			try:
				normalizedName = userName.upper()
				sql_1="SELECT Id FROM ugs_db.Users WHERE Name = '{0}'".format(normalizedName)
				cursor.execute(sql_1)
				ret=cursor.fetchone()
				if(ret != None) :
					return int(ret[0])
				sql_2="INSERT IGNORE INTO ugs_db.Users (Name) VALUES ('{0}')".format(normalizedName)
				cursor.execute(sql_2)
				db.commit()
				cursor.execute(sql_1)
				ret=cursor.fetchone()
				if(ret != None) :
					return int(ret[0])
			except Exception as why:
				print("commonFindOrAddUserId error:{0}".format(why))
				return -1
	return -1

def matchesWildcard(wildCard, project):
	return (wildCard.endswith("...") and project.lower().startswith(wildCard[:-4].lower()))

def sanitizeText(text, length):
	if(len(text)<=length):
		return text
	newLineIdx = text.rfind('\n')
	if(newLineIdx<0):
		return text[:length-3] + "..."
	else :
		return text[:newLineIdx+1] + "..."
