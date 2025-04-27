from django.core.mail import send_mail
from django.conf import settings

def send_test_email():
    subject = "ایمیل تستی از Django"
    message = "این یک ایمیل تستی است که از طریق Django ارسال شده است."
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [settings.RECEIVER_EMAIL_FOR_INVOICE]

    print("📧 در حال ارسال ایمیل به:", recipient_list)
    print("📨 ارسال از:", from_email)

    try:
        result = send_mail(subject, message, from_email, recipient_list)
        if result:
            print("✅ ایمیل با موفقیت ارسال شد!")
        else:
            print("❌ ایمیل ارسال نشد!")
    except Exception as e:
        print("🚨 خطا در ارسال ایمیل:", e)

send_test_email()
