from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # 使用者認證相關路由
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),  # 🔴 漏洞：GET 方法的登出（CSRF）
    path('profile/', views.profile, name='profile'),  # 🔴 漏洞：XSS（使用 |safe）

    # 密碼重設
    path('password-reset/', views.password_reset_request, name='password_reset_request'),  # 🔴 漏洞：Email 列舉
    path('password-reset/<str:token>/', views.password_reset, name='password_reset'),  # 🔴 漏洞：Token 可預測、無過期檢查
]
