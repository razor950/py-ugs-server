#-*- coding: utf-8 -*-
import sys
import db_connect
import pymysql
import model_build
import json

class BuildController:
	def GetBuilds(project, lastBuildId):
		result=[]
		sql = ("SELECT Badges.Id, Badges.ChangeNumber, Badges.BuildType, Badges.Result, Badges.Url, Projects.Name, Badges.ArchivePath, Badges.Metadata FROM ugs_db.Badges " 
				"INNER JOIN ugs_db.Projects ON Projects.Id = Badges.ProjectId WHERE Badges.Id > {0} AND Projects.Name LIKE '%{1}%' ORDER BY Badges.Id").format(lastBuildId, project)
		buildObjs = db_connect.fetchObjects(sql, None)
		for build in buildObjs :
			Id = build[0]
			ChangeNumber = build[1]
			BuildType = build[2]
			Result=model_build.getResultString(int(build[3]))
			if(Result):
				Url = build[4]
				Project= build[5] if (len(build)>5) else None
				
				# if metadata doesn't exist, check if it can be loaded to be appended. If it can't, it's set to None
				if Metadata == None:
						try:
								Metadata = json.loads(build[7])
						except json.JSONDecodeError:
								pass 
				if(Project==None or Project.lower()==project.lower() or db_connect.matchesWildcard(Project, project)):
					result.append(model_build.BuildData(Id, ChangeNumber, BuildType, Result, Url, Project, None))
		return result
	
	def PostBuild(buildData):
		changeNumber = buildData["ChangeNumber"]
		buildType = buildData["BuildType"]
		result = buildData["Result"]
		url = buildData["Url"]
		archivePath = buildData["ArchivePath"]
		project =  buildData["Project"]
		metadata = buildData.get("Metadata", None)
		
		# if metadata exists, dump it so we can insert it into the db
		if metadata != None:
			try:
				metadata_json = json.dumps(metadata)
			except json.JSONDecodeError:
				pass	
						
		projectId=db_connect.commonTryInsertAndGetProject(project)
		
		sql = "INSERT INTO ugs_db.Badges (ChangeNumber, BuildType, Result, URL, ArchivePath, Metadata, ProjectId) VALUES ({0}, '{1}', {2}, '{3}', '{4}', {5}, {6})".format(
				changeNumber, buildType, result, url, archivePath, metadata_json, projectId)
		return db_connect.executeSql(sql)
	
	def GetBuildsWithBuildType(project, buildType):
		result=[]
		sql = ("SELECT Badges.Id, Badges.ChangeNumber, Badges.BuildType, Badges.Result, Badges.Url, Projects.Name, Badges.ArchivePath FROM ugs_db.Badges " 
				"INNER JOIN ugs_db.Projects ON Projects.Id = Badges.ProjectId WHERE Badges.BuildType = '{0}' "
				"AND Projects.Name LIKE '%{1}%' AND Badges.Result={2} ORDER BY Badges.ChangeNumber DESC LIMIT 1").format(buildType, project, model_build.BR_Success)
		buildObjs = db_connect.fetchObjects(sql, None)
		for build in buildObjs :
			Id = build[0]
			ChangeNumber = build[1]
			BuildType = build[2]
			Result=model_build.getResultString(int(build[3]))
			if(Result):
				Url = build[4]
				Project= build[5] if (len(build)>5) else None
				if(Project==None or Project.lower()==project.lower() or db_connect.matchesWildcard(Project, project)):
					result.append(model_build.BuildData(Id, ChangeNumber, BuildType, Result, Url, Project, None))
		return result
	
	def GetBuildsWithBuildTypeAndChangeNumber(project, buildType, changeNumber):
		result=[]
		sql = ("SELECT Badges.Id, Badges.ChangeNumber, Badges.BuildType, Badges.Result, Badges.Url, Projects.Name, Badges.ArchivePath FROM ugs_db.Badges " 
				"INNER JOIN ugs_db.Projects ON Projects.Id = Badges.ProjectId WHERE Badges.BuildType = '{0}' AND Badges.ChangeNumber={1} "
				"AND Projects.Name LIKE '%{2}%' AND Badges.Result={3} ORDER BY Badges.ChangeNumber DESC LIMIT 1").format(buildType, changeNumber, project, model_build.BR_Success)
		buildObjs = db_connect.fetchObjects(sql, None)
		for build in buildObjs :
			Id = build[0]
			ChangeNumber = build[1]
			BuildType = build[2]
			Result=model_build.getResultString(int(build[3]))
			if(Result):
				Url = build[4]
				Project= build[5] if (len(build)>5) else None
				if(Project==None or Project.lower()==project.lower() or db_connect.matchesWildcard(Project, project)):
					result.append(model_build.BuildData(Id, ChangeNumber, BuildType, Result, Url, Project, None))
		return result	