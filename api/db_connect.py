#-*- coding: utf-8 -*-

from dbutils.pooled_db  import PooledDB
import pymysql
from pymysql import OperationalError, InternalError, ProgrammingError

import db_config

#db_config.py looks like:
'''
DB_UGS_HOST="127.0.0.1"
DB_UGS_PORT=3306
DB_UGS_DBNAME="ugs_db"
DB_UGS_USERNAME="root"
DB_UGS_PASSWORD="*******"
DB_UGS_CHARSET="utf8"
'''

class DbConnectPool():
	def __init__(self):
		try:
			print("DbConnectPool Construct!")
			self._pool = PooledDB(
				creator=pymysql, 
				host=db_config.DB_UGS_HOST, port=db_config.DB_UGS_PORT, user=db_config.DB_UGS_USERNAME, password=db_config.DB_UGS_PASSWORD, db=db_config.DB_UGS_DBNAME, charset=db_config.DB_UGS_CHARSET,
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
		return self._pool.connection()

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
