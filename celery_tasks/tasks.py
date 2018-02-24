from celery import Celery
from django.core.mail import send_mail
from django.conf import settings


# # 创建delery实例对象
# app = Celery('celery_tasks.tasks',broker='redis://47.94.238.54:6379/12')
# 这两行代码在启动worker进行的一端打开
# 设置django配置依赖的环境变量
# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")

# 创建一个Celery类的对象
app = Celery('celery_tasks.tasks', broker='redis://47.52.206.201:6379/11')


@app.task
def send_register_active_email(username,token,email):
    '''用户邮件激活任务'''
    # # 发送邮件
    print('多线程')
    subject = '天天生鲜欢迎你'
    message = ''
    from_email = settings.EMAIL_FROM
    recipient_list = [email]
    html_message = """
                        <h1>%s, 欢迎您成为天天生鲜注册会员</h1>
                        请点击以下链接激活您的账户<br/>
                        <a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>
                    """ % (username, token, token)
    # 发送激活邮件
    # send_mail(subject=邮件标题, message=邮件正文,from_email=发件人, recipient_list=收件人列表)
    send_mail(subject, message, from_email, recipient_list, html_message=html_message)
