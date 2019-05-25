#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, Response, request, flash, redirect, url_for, render_template, session, abort
import database as DB
import config

app = Flask(__name__)

@app.route('/')
def main():
	return render_template('main.html')

@app.route('/login', methods=['POST'])
def login():
	if request.form['id'] == None or request.form['pw'] == None:
		abort(400)
	result = DB.login(request.form['id'],request.form['pw'])
	if result != None:
		session['id'], session['name'], session['auth'] = result
		flash('로그인되었습니다')
		return redirect(url_for('main'))
	else:
		flash('로그인에 실패했습니다')
		return redirect(url_for('main'))

@app.route('/signup',methods=['POST'])
def signup():
	if request.form['id'] == None or request.form['pw'] == None or request.form['name'] == None:
		abort(400)
	if DB.signup(request.form['name'],request.form['id'],request.form['pw'],request.form['key']):
		flash('회원가입되었습니다')
		return redirect(url_for('main'))
	else:
		flash('이미 존재하는 ID입니다')
		return redirect(url_for('main'))

@app.route('/logout')
def logout():
	session.clear()
	flash('로그아웃되었습니다')
	return redirect(url_for('main'))

@app.route('/about')
def about():
	return 'About page'

@app.route('/ctf', methods=['GET','POST'])
def ctf():
	if session.get('auth'):
		if request.method == 'POST':
			result = DB.solve(session.get('id'),request.form['id'],request.form['flag'])
			if result < 0:
				flash('Error happened. tell admin.\nError code : '+str(result))
				return redirect(url_for('ctf'))
			elif result == 0:
				flash('Wrong!')
				return redirect(url_for('ctf'))
			else:
				flash('Correct!')
				return redirect(url_for('ctf'))
		else:
			return render_template('ctf.html',quizs = DB.getquiz(session.get('id')), score=DB.getscore(session.get('id')))
@app.route('/sql', methods=['POST','GET'])
def sql():
	if session.get('auth') and session.get('auth') >= 2:
		if request.form.get('query'):
			query = request.form.get('query')
			return render_template('sql.html', query = query, result = DB.query(query))
		else:
			query = 'SELECT * FROM sqlite_master'
			return render_template('sql.html', query = query, result = DB.query(query))
	abort(404)

@app.route('/rank')
def rank():
	if session.get('auth') and session.get('auth') >= 1:
		return render_template('rank.html', scores=DB.getscores())	
@app.route('/enroll', methods=['GET','POST'])
def enroll():
	if session.get('auth') and session.get('auth')>=2:
		if request.method == 'POST':	
			DB.enroll(request.form.get('title'),request.form.get('content'),request.form.get('flag'),int(request.form.get('point')),request.form.get('prev'))
			return redirect(url_for('enroll'))
		else:
			return render_template('enroll.html')
	abort(403)
if __name__ == '__main__':
	app.secret_key = config.secret_key
	app.run(host='0.0.0.0',port=5000,debug=True)
