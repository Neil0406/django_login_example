from django.shortcuts import render,redirect, HttpResponse
from django.urls import reverse
from django.http import HttpResponseRedirect
#from login_app.models import User

from .utils.es_helpers import User
from .utils.password_encode import PasswordEncode
import time
User = User()
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