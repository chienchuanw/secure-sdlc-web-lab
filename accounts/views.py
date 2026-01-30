from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm


def register(request):
    """
    使用者註冊視圖

    ⚠️ 安全問題（刻意引入）：
    1. 密碼以明文方式處理（雖然最後有用 set_password 加密，但過程中可能被記錄）
    2. 無 Rate Limiting（可以無限次嘗試註冊）
    3. 成功/失敗訊息差異可能洩漏資訊
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # 建立使用者
            # ⚠️ 注意：這裡雖然使用 set_password() 會加密密碼
            # 但在此之前，密碼已經以明文形式存在於記憶體和可能的 log 中
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # 🔴 漏洞：成功訊息可能洩漏資訊
            messages.success(request, f'帳號 {username} 註冊成功！請登入。')
            return redirect('accounts:login')
        else:
            # 🔴 漏洞：錯誤訊息會顯示具體的驗證失敗原因
            # 攻擊者可以利用這些訊息進行使用者列舉
            messages.error(request, '註冊失敗，請檢查表單內容')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    使用者登入視圖

    ⚠️ 安全問題（刻意引入）：
    1. Timing Attack（透過 LoginForm 的驗證邏輯）
    2. 無 Rate Limiting（可以無限次嘗試登入）
    3. Session Fixation（Django 預設會重新產生 session ID，但這裡不特別處理）
    """
    # 如果已登入，導向首頁
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            # form.clean() 已經驗證過使用者和密碼
            # 並將 user 物件儲存在 form.user
            user = form.user

            # 登入使用者（建立 session）
            login(request, user)

            messages.success(request, f'歡迎回來，{user.username}！')

            # 🔴 潛在漏洞：Open Redirect
            # 如果 next 參數可以被控制，可能導致釣魚攻擊
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            # 🔴 漏洞：詳細的錯誤訊息已經在 form 中顯示
            # 攻擊者可以利用這些訊息進行使用者列舉和暴力破解
            messages.error(request, '登入失敗，請檢查帳號和密碼')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """
    使用者登出視圖

    ⚠️ 安全問題（刻意引入）：
    1. CSRF 漏洞 - 使用 GET 而非 POST
    2. 沒有確認使用者意圖
    """
    # 🔴 漏洞：應該要求 POST 方法並檢查 CSRF token
    # 現在任何人都可以透過 <img src="/accounts/logout/"> 登出使用者

    username = request.user.username if request.user.is_authenticated else '訪客'

    logout(request)
    messages.success(request, f'{username}，您已成功登出')

    return redirect('home')


@login_required
def profile(request):
    """
    個人資料頁面

    ⚠️ 安全問題（刻意引入）：
    1. XSS 漏洞 - 模板中使用 |safe filter 導致 Stored XSS
    """
    return render(request, 'accounts/profile.html')
