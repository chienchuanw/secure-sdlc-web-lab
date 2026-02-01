from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from .forms import RegisterForm, LoginForm, PasswordResetRequestForm, PasswordResetForm
from .models import PasswordResetToken


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


def password_reset_request(request):
    """
    密碼重設請求視圖

    ⚠️ 安全問題（刻意引入）：
    1. Email 列舉（透過表單驗證）
    2. 無 Rate Limiting
    3. Token 使用弱隨機數產生
    """
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']

            # 取得使用者
            user = User.objects.get(email=email)

            # 🔴 漏洞：產生弱 Token（可預測）
            token = PasswordResetToken.generate_weak_token()

            # 建立 Token 記錄
            reset_token = PasswordResetToken.objects.create(
                user=user,
                token=token
            )

            # 建立重設連結
            reset_url = request.build_absolute_uri(
                reverse('accounts:password_reset', args=[token])
            )

            # 發送 Email
            subject = '密碼重設請求'
            message = f'''
您好 {user.username}，

您請求重設密碼。請點擊以下連結來重設您的密碼：

{reset_url}

如果您沒有請求重設密碼，請忽略此信件。

---
Secure SDLC Lab
            '''

            send_mail(
                subject,
                message,
                'noreply@secure-sdlc-lab.local',
                [email],
                fail_silently=False,
            )

            # 🔴 漏洞：成功訊息洩漏資訊
            messages.success(request, f'密碼重設連結已發送至 {email}')
            return redirect('accounts:login')
        else:
            # 🔴 漏洞：錯誤訊息洩漏資訊（Email 不存在）
            messages.error(request, '請檢查您的 Email')
    else:
        form = PasswordResetRequestForm()

    return render(request, 'accounts/password_reset_request.html', {'form': form})


def password_reset(request, token):
    """
    密碼重設視圖（透過 token）

    ⚠️ 安全問題（刻意引入）：
    1. 沒有檢查 token 是否過期
    2. 沒有檢查 token 是否已使用
    3. Token 可以重複使用
    """
    # 驗證 token
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        messages.error(request, '無效的重設連結')
        return redirect('accounts:login')

    # 🔴 漏洞：沒有檢查 token 是否過期
    # if reset_token.is_expired():
    #     messages.error(request, '重設連結已過期')
    #     return redirect('accounts:password_reset_request')

    # 🔴 漏洞：沒有檢查 token 是否已使用
    # if reset_token.is_used:
    #     messages.error(request, '此重設連結已被使用')
    #     return redirect('accounts:password_reset_request')

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)

        if form.is_valid():
            new_password = form.cleaned_data['new_password']

            # 更新密碼
            user = reset_token.user
            user.set_password(new_password)
            user.save()

            # 🔴 漏洞：沒有標記 token 為已使用
            # reset_token.mark_as_used()

            messages.success(request, '密碼已成功重設，請使用新密碼登入')
            return redirect('accounts:login')
    else:
        form = PasswordResetForm()

    context = {
        'form': form,
        'token': token,
        'username': reset_token.user.username
    }
    return render(request, 'accounts/password_reset.html', context)
