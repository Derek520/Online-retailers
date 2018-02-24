import re
import threading
from django.conf import settings
from django.shortcuts import render,redirect,HttpResponse
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.http import JsonResponse
# Create your views here.
from django.views.generic import View
from .models import User
from celery_tasks.tasks import send_register_active_email
# pp

class RegisterView(View):
    '''注册页面'''
    def get(self,request):
        '''页面请求'''
        return render(request,'register.html')

    def post(self,request):
        '''注册页面提交'''
        # 1.接收参数
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        print(username,password,email)
        # 2.参数校验
        if not all([username,password,email]):
            return render(request,'register.html',{'errmsg':'参数不完整'})

        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request,'register.html',{'errmsg':'邮箱格式错误'})
        # 3.逻辑处理
        # 查询数据库,用户是否注册
        try:
            user = User.objects.filter(username=username)
        except Exception as e:
            return render(request,'register.html',{'errmsg':'查询数据失败'})

        # 判断查询的数据是否为空
        if user:
            return render(request,'register.html',{'errmsg':'用户已存在'})

        # 如果用户不存在,创建用户
        try:
            # 创建用户,采用django用户认证系统
            user = User.objects.create_user(username,email,password)
            user.is_active =False
            user.save()
        except Exception as e:
            '''如果创建失败,需要回退'''
            user.rollback()
            return render(request,'register.html',{'errmsg':'创建用户失败'})

        '''
        创建完用户后,进行邮箱验证,激活账户,需要对用户id进行加密处理
        
        '''
        # 注册成功之后需要给用户的注册邮箱发送激活邮件，在激活邮件中要包含激活链接
        # 激活链接: /user/active/用户id, 如果直接写用户id，其他人可能恶意请求网站
        # 解决方式: 先对用户身份信息加密，把加密后的信息放在激活链接中
        # /user/active/token信息
        # 使用itsdangerous生成激活的token信息
        # serializer = Serializer(settings.SECRET_KEY,3600)
        # # 将用户id装进字典,进行加密
        # info = {'confirm':user.id}
        # # 进行加密
        # token = serializer.dumps(info) # bytes
        # # 转换成str类型
        # token = token.decode()
        # print(token)
        # 使用itsdangerous生成激活的token信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        # 进行加密
        token = serializer.dumps(info)  # bytes
        # 转换成str类型
        token = token.decode()

        # # 发送邮件
        # subject = '天天生鲜欢迎你'
        # message = ''
        # from_email = settings.EMAIL_FROM
        # recipient_list = [email]
        # html_message = """
        #             <h1>%s, 欢迎您成为天天生鲜注册会员</h1>
        #             请点击以下链接激活您的账户<br/>
        #             <a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>
        #         """ % (username, token, token)
        # # 发送激活邮件
        # # send_mail(subject=邮件标题, message=邮件正文,from_email=发件人, recipient_list=收件人列表)
        # send_mail(subject, message, from_email, recipient_list,html_message=html_message)
        thd1 =threading.Thread(target=self.thd,args=(username, token, email))
        thd1.start()

        # 4.返回结果
        print('ok')
        return redirect(reverse('goods:index'))

    def thd(self,username,token,email):
        print(456)
        send_register_active_email(username, token, email)


# 激活用户
# user/active/
class ActiveView(View):
    '''邮箱激活'''
    def get(self,request,token):
        '''激活用户'''
        # 进行解密
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取用户id
            user_id = info['confirm']
        except Exception as e:
            return HttpResponse('激活链接失效')

        # 激活用户
        user = User.objects.get(id=user_id)
        user.is_active = True
        user.save()

        return redirect(reverse('user:login'))



# 登录页面
# user/login
class LoginView(View):
    '''登录页面'''
    def get(self,request):
        '''请求登录页面'''
        return render(request,'login.html')
    def post(self,request):
        '''用户登录'''
        print(123)
        # 1.接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        print(username,password)
        # 2.参数校验
        if not all([username,password]):
            return render(request,'login.html',{'errmsg':'参数不完整'})
        # 3.逻辑处理
        # 查询用户是否注册并激活
        # 业务处理：登录校验
        # 根据用户名和密码查找用户的信息
        user = authenticate(username=username, password=password)
        # 判断查询的数据是否为空
        if user is not None:
            # 用户名和密码正确
            if user.is_active:
                login(request,user)
                # 4.返回数据
                return redirect(reverse('goods:index'))

            return render(request,'login.html',{'errmsg':'用户未激活'})
        else:
            return render(request,'login.html',{'errmsg':'用户密码或账户错误'})

# 用户退出
class LogoutvView(View):
    '''用户退出功能'''
    def get(self,request):
        '''用户退出'''
        logout(request)

        return redirect(reverse('user:login'))