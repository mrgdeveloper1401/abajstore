from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import FormView, CreateView, RedirectView, UpdateView, DeleteView, DetailView, ListView, \
    TemplateView, View
from .forms import UserCreationForm, OTPForm, ForgetPasswordForm, UserProfileForm, AddressForm, \
    CustomAuthenticationForm, ChangePasswordForm
from .models import User, OTP, Address
from .mixins import AddressFormMixin
from configs.sms_panel import send_sms
from datetime import datetime, timedelta
import random
import time
# import logging

# logging.basicConfig(filename='account_view.log',
#                     level=logging.DEBUG,
#                     format='%(asctime)s - %(levelname)s - %(message)s')


# =====================================================================================================
# ======================================== UseFull Functions ==========================================
def generate_random_password(length=8):
    password = ''.join(random.choices('0123456789', k=length))
    return password


def generate_otp(phone_number):
    random_number = random.randint(10 ** 4, 10 ** 7)
    timestamp = int(time.time() * 1000)
    code = str(timestamp + random_number)[-6:]
    OTP.objects.update_or_create(phone_number=phone_number, defaults={'code': int(code)})
    return int(code)


def send_otp(phone_number, reason):
    code = generate_otp(phone_number)

    if reason == 'register':
        pattern = '7928a99a-41b4-4e6a-a0bf-1ab47dbcaa30'
        key = {
            'token1': code,
        }
        send_sms(pattern, phone_number, key)

    if reason == 'set_new_password':
        pattern = 'da1885d9-bb31-4f8e-9bfd-0ebabb490514'
        key = {
            'token1': code,
        }
        send_sms(pattern, phone_number, key)

    if reason == 'set_new_phone_number':
        pattern = 'fb3b6bdb-a5e5-40f1-9edc-f04e0a63ef68'
        key = {
            'token1': code,
        }
        send_sms(pattern, phone_number, key)


def create_or_update_user(request):
    """ This Method Calls After Confirmation """
    if 'user_info' in request.session:
        session = request.session['user_info']
        reason = session['reason']
        phone_number = session['phone_number']

        user, created = User.objects.get_or_create(phone_number=phone_number)

        # ============================================================
        # =================== Login After Register ===================

        if reason == 'register':
            password = session['password']

            user.set_password(password)
            user.is_verified = True
            user.save()
            auth = authenticate(request, phone_number=phone_number, password=password)

            if auth is not None:
                del session
                login(request, auth)
                return 'تبریک ! حساب شما با موفقیت ایجاد شد.'
                # messages.warning(request, 'تبریک ! حساب شما با موفقیت ایجاد شد.')
                # return redirect('panel:home')

    # ============================================================
    # ======================= Update User ========================

        if reason == 'set_new_password':
            new_password = generate_random_password()
            user.set_password(new_password)
            try:
                # ==================== send sms ==========================
                pattern = 'b30f2c41-e2d1-4bcb-a26b-0d6aeb8d3ffb'
                key = {
                    'token1': new_password,
                }
                send_sms(pattern, phone_number, key)
                # =========================================================
            except Exception as e:
                print('error for sending sms : ', e)

        if reason == 'set_new_phone_number':
            new_phone_number = session['phone_number']
            user.phone_number = new_phone_number

        user.save()
        del session
        return 'عملیات با موفقت انجام  شد.'


def check_delay(request):
    now = datetime.now()

    if 'delay' in request.session:
        str_time = request.session['delay']['time']
        last_try = datetime.strptime(str_time, '%Y-%m-%d %H:%M:%S')
    else:
        last_try = now

    if last_try <= now:
        delay = now + timedelta(minutes=2)
        request.session['delay'] = {
            'time': delay.strftime('%Y-%m-%d %H:%M:%S'),
        }
        return True

    time_left = last_try - now
    total_seconds = int(time_left.total_seconds())
    request.session['total_seconds'] = total_seconds
    return False, total_seconds


def check_delay_and_send_otp(request):
    session = request.session

    if 'user_info' in session:
        user_info = session['user_info']
        phone_number = user_info['phone_number']
        reason = user_info['reason']

        delay = check_delay(request)
        if delay is True:
            try:
                send_otp(phone_number, reason)
                return 'کد یکبارمصرف برای شما ارسال شد.'
                # messages.warning(request, 'کد یکبارمصرف برای شما ارسال شد.')
                # return redirect('panel:home')

            except Exception as e:
                print('error for sending sms : ', str(e))

                return 'خطای ارسال پیامک!'
                # messages.warning(request, '!خطای ارسال پیامک')
                # return redirect('panel:home')

        return f"{delay[1]} ثانیه صبر کنید.. "
        # messages.warning(request, f"{delay[1]} ثانیه صبر کنید.. ")
        # return redirect('panel:home')
# =====================================================================================================
# =====================================================================================================


class UserRegisterView(SuccessMessageMixin, FormView):
    form_class = UserCreationForm
    template_name = 'accounts/register.html'
    success_message = "کد یکبار مصرف ارسال شد!"
    success_url = reverse_lazy('auth:verify')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'شما از قبل وارد شده اید..')
            return redirect('products:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if form.is_valid():
            cd = form.cleaned_data
            phone_number = cd['phone_number']
            password = cd['password']

            self.request.session['user_info'] = {
                'phone_number': phone_number,
                'password': password,
                'reason': 'register',
                }

            result = check_delay_and_send_otp(self.request)
            messages.success(self.request, result)

        messages.success(self.request, form.errors)
        return super().form_valid(form)


class UserLoginView(SuccessMessageMixin, LoginView):
    """
    Login and send success message.
    """
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    success_message = "با موفقیت وارد شدید !"
    next_page = reverse_lazy('products:home')


from django.shortcuts import get_object_or_404

class VerifyView(FormView):
    form_class = OTPForm
    template_name = 'accounts/otp.html'
    success_url = reverse_lazy('products:home')

    def form_valid(self, form):
        session = self.request.session.get('user_info')

        if form.is_valid() and session:
            cd = form.cleaned_data
            user_entered_code = cd['code']

            try:
                otp = OTP.objects.get(phone_number=session['phone_number'], code=user_entered_code)
            except OTP.DoesNotExist:
                messages.error(self.request, 'کد وارد شده صحیح نمی‌باشد ❌')
                return self.form_invalid(form)  # جلوگیری از ادامه روند

            # حذف OTP فقط بعد از تأیید کامل
            otp.delete()

            # ساخت یا به‌روزرسانی کاربر
            result = create_or_update_user(self.request)
            messages.success(self.request, result)

            return redirect('products:home')

        messages.info(self.request, 'کد وارد شده صحیح نمیباشد')
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.request.session
        if session:
            if 'user_info' in session:
                context['user_phone_number'] = session['user_info']['phone_number']
            context['total_seconds'] = session.get('total_seconds', 120)
        return context


  


class ForgetPasswordView(FormView):
    form_class = ForgetPasswordForm
    template_name = 'accounts/forget_password.html'
    success_url = reverse_lazy('auth:verify')

    def form_valid(self, form):
        if form.is_valid():
            cd = form.cleaned_data
            phone_number = cd['phone_number']

            self.request.session['user_info'] = {
                'phone_number': phone_number,
                'reason': 'set_new_password'
            }

            result = check_delay_and_send_otp(self.request)
            messages.info(self.request, result)

        return super().form_valid(form)


class ResendOTPView(RedirectView):
    pattern_name = 'auth:verify'

    def get(self, request, *args, **kwargs):
        result = check_delay_and_send_otp(request)
        messages.info(request, result)

        return super().get(request, *args, **kwargs)


class UserProfileView(LoginRequiredMixin, TemplateView):
    model = User
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('auth:profile')
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return self.request.user

    def get_form_class(self):
        if 'change_password' in self.request.POST:
            return ChangePasswordForm
        return UserProfileForm

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(self.request.POST or None, instance=self.request.user)

    def post(self, request, *args, **kwargs):
        profile_form = UserProfileForm(request.POST, instance=request.user)
        password_form = ChangePasswordForm(request.POST, user=request.user)

        if 'update_profile' in request.POST:
            if profile_form.is_valid():
                if 'phone_number' in profile_form.changed_data:
                    request.session['user_info'] = {
                        'phone_number': profile_form.cleaned_data['phone_number'],
                        'reason': 'set_new_phone_number'
                    }
                    result = check_delay_and_send_otp(request)
                    messages.info(request, result)
                    return redirect('auth:verify')
                else:
                    profile_form.save()
                    messages.success(request, 'پروفایل شما با موفقیت به‌روزرسانی شد!')
                    return redirect(self.success_url)
            else:
                messages.error(request, 'خطا در به‌روزرسانی پروفایل. لطفاً دوباره اطلاعات را بررسی کنید.')

        elif 'change_password' in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'رمز عبور شما با موفقیت تغییر یافت!')
                return redirect(self.success_url)
            else:
                messages.error(request, 'خطا در تغییر رمز عبور. لطفاً دوباره اطلاعات را بررسی کنید.')

        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_form'] = UserProfileForm(instance=self.request.user)
        context['password_form'] = ChangePasswordForm(user=self.request.user)
        return context


class AddressListView(LoginRequiredMixin, ListView):
    model = Address
    template_name = 'accounts/my-addresses.html'
    context_object_name = 'addresses'

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user, active=True)


class AddressDetailView(LoginRequiredMixin, DetailView):
    model = Address
    template_name = 'accounts/my-addresses.html'
    context_object_name = 'address'


class AddressCreateView(LoginRequiredMixin, View):
    # model = Address
    # form_class = AddressForm
    # success_url = reverse_lazy('orders:checkout')
    # template_name = 'orders/checkout.html'

    def post(self, request, *args, **kwargs):
        form = AddressForm(request.POST)
        if form.is_valid():
            Address.objects.create(user=request.user, **form.cleaned_data)
        else:
            # messages.error(request, f'{[f for f, e in form.errors.items()]}')
            messages.error(request, 'لطفا مقادیر را به درستی وارد کنید!')
        messages.success(request, 'آدرس جدید ایجاد شد ، میتوانید آن را انتخاب کنید!')
        # print(form.errors)
        return redirect('orders:checkout')

    # def form_valid(self, form):
    #     form.instance.user = self.request.user
    #     if form.is_valid():
    #         Address.objects.create(user=self.request.user, **form.cleaned_data)
    #         print(form.cleaned_data)
    #         return redirect('orders:checkout')
    #
    #     return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, AddressFormMixin, UpdateView):
    model = Address
    form_class = AddressForm
    template_name = 'accounts/my-addresses.html'
    success_url = reverse_lazy('auth:address_list')


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = Address
    # template_name = 'accounts/my-addresses.html'
    success_url = reverse_lazy('auth:address_list')

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        success_url = self.get_success_url()
        obj = self.get_object()
        obj.active = False
        obj.save()
        return HttpResponseRedirect(success_url)
