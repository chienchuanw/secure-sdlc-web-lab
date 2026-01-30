from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # 使用者認證相關路由
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),  # 🔴 漏洞：GET 方法的登出（CSRF）
]
