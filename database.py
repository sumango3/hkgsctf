import sqlite3 as sql
import hashlib
import os
import config
member_salt = config.member_salt.encode('utf-8')
quiz_salt = config.quiz_salt.encode('utf-8')
dbpath = config.dbpath
bonus = config.bonus
def str2set(x):
	l = x.split('|')
	if '' in l:
		l.remove('')
	return set(map(int,l))
def set2str(x):
	return '|'.join(map(str,x))
def query(sqlquery):
	with sql.connect(dbpath) as db:
		if sqlquery:
			c = db.cursor()
			c.execute(sqlquery)
			return c.fetchall()
def login(login_id, login_pw):
	with sql.connect(dbpath) as db:
		c = db.cursor()
		m = hashlib.sha256()
		m.update(login_pw.encode('utf-8'))
		m.update(member_salt)
		pwhash = m.hexdigest()
		query = 'SELECT id,name,auth FROM member WHERE id=? and pw=?'
		c.execute(query,[login_id,pwhash])
		return c.fetchone()
def signup(signup_name, signup_id, signup_pw, signup_key):
	with sql.connect(dbpath) as db:
		c = db.cursor()
		query = 'SELECT * from member WHERE id=?'
		c.execute(query,[signup_id])
		result = c.fetchone()
		if result != None:
			return False
		m = hashlib.sha256()
		m.update(signup_pw.encode('utf-8'))
		m.update(member_salt)
		pwhash = m.hexdigest()
		query = 'INSERT INTO member (id,name,pw,auth,solved,point) VALUES (?,?,?,?,"",0)'
		auth = 0
		if signup_key == config.admin_key:
			auth = 2
		elif signup_key == config.member_key:
			auth = 1
		c.execute(query,[signup_id,signup_name,pwhash,auth])
	return True
def enroll(enroll_title, enroll_content, enroll_flag, enroll_point, enroll_prev):
	with sql.connect(dbpath) as db:
		c = db.cursor()
		m = hashlib.sha256()
		m.update(enroll_flag.encode('utf-8'))
		m.update(quiz_salt)
		flaghash = m.hexdigest()
		query = 'INSERT INTO quiz (title,content,flag,point,champ,solved,prev) VALUES(?,?,?,?,"",0,?)'
		c.execute(query,[enroll_title, enroll_content, flaghash, enroll_point, enroll_prev])
def solve(member_id, quiz_id, member_flag):
	with sql.connect(dbpath) as db:
		quiz_id = int(quiz_id)
		c = db.cursor()
		query = 'SELECT auth,point,solved from member WHERE id=?'
		c.execute(query, [member_id])
		result = c.fetchone()
		if result == None:
			return -1
		auth, member_point, solved = result
		solvedset = str2set(solved)
		query = 'SELECT flag,point,prev,solved from quiz WHERE id=?'
		c.execute(query, [quiz_id])
		result = c.fetchone()
		if result == None:
			return -2
		quiz_flag,quiz_point,prev,solved = result
		if quiz_id in solvedset:
			return -3
		prevset = str2set(prev)
		if not prevset.issubset(solvedset):
			print('solvedset : '+str(solvedset))
			print('prevset : '+str(prevset))
			return -4
		m = hashlib.sha256()
		m.update(member_flag.encode('utf-8'))
		m.update(quiz_salt)
		if quiz_flag == m.hexdigest():
			addpoint = quiz_point
			solvedset.add(quiz_id)
			newsolved = set2str(solvedset)
			if solved == 0 and auth == 1:
				addpoint += bonus
				query = 'UPDATE quiz set champ=?, solved=? where id=?'
				c.execute(query,[member_id, solved+1, quiz_id])
			else:
				query = 'UPDATE quiz set solved=? where id=?'
				c.execute(query,[solved+1, quiz_id])
			query = 'UPDATE member set solved=?, point=? where id=?'
			c.execute(query,[newsolved, member_point+addpoint, member_id])
			return 1
		else:
			return 0
	return -5
def getquiz(member_id):
	with sql.connect(dbpath) as db:
		c = db.cursor()
		query = 'SELECT solved from member where id=?'
		c.execute(query,[member_id])
		solvedset = str2set(c.fetchone()[0])
		query = 'SELECT id,title,content,point,champ,solved,prev from quiz ORDER BY id'
		c.execute(query)
		result = c.fetchall()
		#instead of prev set, we will write problem state on result[i][6].
		for i in range(len(result)):
			prevset = str2set(result[i][6])
			result[i] = list(result[i])
			if not prevset.issubset(solvedset):
				result[i][6] = 'locked'
			elif int(result[i][0]) in solvedset:
				result[i][6] = 'solved'
			else:
			 	result[i][6] = 'solvable'
		return result
def getscore(member_id):
	with sql.connect(dbpath) as db:
		c = db.cursor()
		query = 'SELECT point from member where id=?'
		c.execute(query,[member_id])
		return c.fetchone()[0]
def getscores():
	with sql.connect(dbpath) as db:
		c = db.cursor()
		query = 'SELECT name,point from member where auth=1 ORDER BY point DESC'
		c.execute(query)
		return c.fetchall()
def init():
	with sql.connect(dbpath) as db:
		c = db.cursor()
		checkquery = 'SELECT name FROM sqlite_master WHERE type="table" AND name=?'
		c.execute(checkquery,['member'])
		if c.fetchone() == None:
			memberquery = 'CREATE TABLE member(id TEXT PRIMARY KEY,name TEXT,pw TEXT,auth INTEGER,solved TEXT,point INTEGER)'
			c.execute(memberquery)
		c.execute(checkquery,['quiz'])
		if c.fetchone() == None:
			quizquery = 'CREATE TABLE quiz(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,content TEXT,flag TEXT,point INTEGER,champ TEXT,solved INTEGER,prev TEXT)'
			c.execute(quizquery)
init()
