from django.shortcuts import render,redirect, HttpResponse
from django.urls import reverse
from django.http import HttpResponseRedirect
#from login_app.models import User

from .utils.es_helpers import User, UserControl
from .utils.password_encode import PasswordEncode
import time
import json
User = User()
UserControl = UserControl()
PasswordEncode = PasswordEncode()


def home(request):
	if 'email' in request.session:
		email = request.session['email']
		user = User.get_user_info(email)       
		if user == 0:                                          #如果使用者被手動從資料庫中刪除 或 session過期
			request.session.flush() 
			return redirect('/')
		return render(request,'home.html', {'user':user['_source']})
	else:
		return redirect('/')


def login(request):
	if 'email' in request.session:
		return redirect('home/')
	if request.method == 'POST':
		password = request.POST.get('password')
		email = request.POST.get('email')
		user = User.check_login(email)   #撈出user
		if user != 0:
			re_pwd = PasswordEncode.decrypt(user['_source']['password_key'], user['_source']['password_value'])   #解碼
			if re_pwd == password:
				request.session['email'] = email                #瀏覽器寫入 session
				User.set_session_expire(user['_id'])   #db 寫入 session 有效時間
				return redirect('home/')
			else:
				return render(request,'login.html', {'info':'密碼錯誤'})
		else:
			return render(request,'login.html', {'info':'沒有使用者'})
	return render(request,'login.html')

def logout(request):
	if 'email' in request.session:
		del request.session['email']
		request.session.flush()
		return redirect('/')
	else:
		return redirect('/')

def create_user(request):
	if request.method == 'POST':
		name = request.POST.get('name')
		email = request.POST.get('email')                    
		password = request.POST.get('password')
		password_key, password_value = PasswordEncode.encrypt(password)
		ret = User.create_user(name, email, password_key, password_value)
		if ret == 'success':
			request.session['email'] = email        
			time.sleep(1)                         #寫入session需要時間 / 沒有sleep 有時候會跳回登入頁
			return redirect('/')
		else:
			return render(request,'create_user.html',{'info':'帳號已存在'})
	return render(request,'create_user.html')

def update_user(request):
	if 'email' in request.session:
		email = request.session['email']
		user = User.get_user_info(email) 
		return render(request,'update_user.html',{'user':user['_source']})
	else:
		return redirect('/')	

class User_Control():
	def user_control(self, request):
		if 'email' in request.session:
			email = request.session['email']
			user = User.get_user_info(email)
			user = user['_source']
			if user == 0:                                          
				request.session.flush() 
				return redirect('/')
			if user['permissions'] == 'Medium' or user['permissions'] == 'Height':
				user_list = UserControl.user_list()
				count = len(user_list)
				return render(request,'user_control.html',locals())
			else:
				return redirect('/')
		else:
			return redirect('/')

	def search_user_by_name(self, request):
		if 'email' in request.session:
			email = request.session['email']
			user = User.get_user_info(email)
			user = user['_source']
			if user == 0:                                          
				request.session.flush() 
				return redirect('/')
			if user['permissions'] == 'Medium' or user['permissions'] == 'Height' and request.method == 'POST':
				name = request.POST.get('name')
				ret = UserControl.search_user_by_name(name)
				ret = json.dumps({'data': ret})
				return HttpResponse(ret)
			else:
				return redirect('/')
		else:
			return redirect('/')

	def search_user_by_email(self, request):
		if 'email' in request.session:
			email = request.session['email']
			user = User.get_user_info(email)
			user = user['_source']
			if user == 0:                                          
				request.session.flush() 
				return redirect('/')
			if user['permissions'] == 'Medium' or user['permissions'] == 'Height' and request.method == 'POST':
				email = request.POST.get('email')
				ret = UserControl.search_user_by_email(email)
				ret = json.dumps({'data': ret})			
				return HttpResponse(ret)
			else:
				return redirect('/')
		else:
			return redirect('/')

	def user_control_update(self, request):
		if 'email' in request.session:
			email = request.session['email']
			user = User.get_user_info(email)
			user = user['_source']
			if user == 0:                                          
				request.session.flush() 
				return redirect('/')
			if user['permissions'] == 'Medium' or user['permissions'] == 'Height' and request.method == 'POST':
				_id = request.POST.get('_id')
				id_list = _id.split(',')
				ret = UserControl.search_user_by_id(id_list)
				ret = json.dumps({'data': ret})			
				return HttpResponse(ret)
			else:
				return redirect('/')
		else:
			return redirect('/')

	def update(self, request):
		if 'email' in request.session:
			email = request.session['email']
			user = User.get_user_info(email)
			user = user['_source']
			if user == 0:                                          
				request.session.flush() 
				return redirect('/')
			if user['permissions'] == 'Medium' or user['permissions'] == 'Height' and request.method == 'POST':
				up_list = request.POST.get('up_list')
				up_list = json.loads(up_list)
				for i in up_list:
					i['session_expire'] = int(i['session_expire'])
				ret = UserControl.update(up_list)
				time.sleep(1)	
				ret = json.dumps({'data': ret})
				return HttpResponse(ret)
			else:
				return redirect('/')
		else:
			return redirect('/')


	def delete_user(self, request):
		if 'email' in request.session:
			email = request.session['email']
			user = User.get_user_info(email)
			user = user['_source']
			if user == 0:                                          
				request.session.flush() 
				return redirect('/')
			if user['permissions'] == 'Height' and request.method == 'POST':
				_id = request.POST.get('_id')
				id_list = _id.split(',')
				ret = UserControl.delete_user(id_list)
				return HttpResponse(ret)
			else:
				return redirect('/')
		else:
			return redirect('/')