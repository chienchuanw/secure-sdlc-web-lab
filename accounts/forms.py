from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import time


class LoginForm(forms.Form):
    """
    使用者登入表單

    ⚠️ 安全問題（刻意引入）：
    1. Timing Attack - 帳號存在/不存在的驗證時間不同
    2. 資訊洩漏 - 明確告知帳號或密碼錯誤
    3. 無 Rate Limiting
    """
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '使用者名稱'
        })
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '密碼'
        })
    )

    def clean(self):
        """
        驗證登入資訊

        ⚠️ 漏洞：Timing Attack + 資訊洩漏
        """
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            # 🔴 漏洞：先檢查使用者是否存在（Timing Attack）
            # 如果使用者不存在，這裡會立即返回錯誤
            # 如果使用者存在，才會進行密碼驗證（較耗時）
            # 攻擊者可以透過測量回應時間來判斷帳號是否存在
            try:
                user = User.objects.get(username=username)
                # 模擬密碼驗證的時間延遲（讓 timing attack 更明顯）
                time.sleep(0.1)

                # 驗證密碼
                if not user.check_password(password):
                    # 🔴 漏洞：明確告知「密碼錯誤」
                    raise forms.ValidationError('密碼錯誤')

                # 檢查帳號是否啟用
                if not user.is_active:
                    raise forms.ValidationError('此帳號已被停用')

                # 將 user 物件儲存起來，供 view 使用
                self.user = user

            except User.DoesNotExist:
                # 🔴 漏洞：明確告知「使用者不存在」
                # 這裡會立即返回，沒有密碼驗證的時間延遲
                raise forms.ValidationError('使用者不存在')

        return cleaned_data


class RegisterForm(forms.Form):
    """
    使用者註冊表單

    ⚠️ 安全問題（刻意引入）：
    1. 沒有檢查密碼強度（允許弱密碼）
    2. 使用者名稱和 Email 重複時會顯示明確錯誤訊息（使用者列舉）
    """
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '使用者名稱'
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '密碼'
        })
    )

    password_confirm = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '確認密碼'
        })
    )

    def clean_username(self):
        """
        驗證使用者名稱

        ⚠️ 漏洞：使用者名稱列舉
        - 攻擊者可以用此功能列舉系統中存在的帳號
        - 正確做法：不要明確告知使用者名稱是否已存在
        """
        username = self.cleaned_data.get('username')

        # 🔴 漏洞：明確告知使用者名稱已存在
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('此使用者名稱已被使用')

        return username

    def clean_email(self):
        """
        驗證 Email

        ⚠️ 漏洞：Email 列舉
        - 攻擊者可以用此功能列舉系統中存在的 Email
        """
        email = self.cleaned_data.get('email')

        # 🔴 漏洞：明確告知 Email 已存在
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('此 Email 已被使用')

        return email

    def clean(self):
        """
        驗證整個表單
        """
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        # 檢查兩次密碼是否一致
        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError('兩次輸入的密碼不一致')

        # ⚠️ 漏洞：沒有檢查密碼強度
        # 🔴 允許弱密碼如 "123456", "password", "admin" 等
        # 正確做法：應該檢查密碼長度、複雜度（大小寫、數字、特殊字元）

        return cleaned_data
