from django.conf.urls import url
from .views import RegisterView,ActiveView,LoginView,LogoutvView
urlpatterns = [
    url(r'^register$', RegisterView.as_view(), name='register'),  # 注册
    url(r'^active/(?P<token>.*)$',ActiveView.as_view(),name='active'), # 激活
    url(r'^login$',LoginView.as_view(),name='login'),   # 登录页面
    url(r'^logout$',LoginView.as_view(),name='logout'), # 退出登录
]