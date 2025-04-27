from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Order, OrderItem
from site_settings.models import SiteSettings
from configs.sms_panel import send_sms

from .models import Invoice
import logging

logger = logging.getLogger(__name__)



@receiver(pre_save, sender=Order)
def pre_save_order(sender, instance, **kwargs):
    if instance.pk:
        instance._old_instance = Order.objects.get(pk=instance.pk)


@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, **kwargs):
    admin_phone_number = SiteSettings.objects.first().admin_phone_number
    key = {
        'token1': instance.code,
        'token2': instance.get_price_with_send(),
    }
    if instance.status == "پرداخت شده":
        # ================= sms for user ====================
        user_pattern = 'a621ae86-db4c-41fc-ba76-9dfa05390ba9'
        send_sms(user_pattern, instance.user.phone_number, key)
        # ===================================================
        # ================= sms for admin ===================
        admin_pattern = 'f923cf23-411c-4017-abe9-8a158714eaee'
        send_sms(admin_pattern, admin_phone_number, key)
        # ===================================================
        print(f"Order with code {instance.code} has been paid.")

    if hasattr(instance, '_old_instance'):
        old_instance = instance._old_instance
        old_status = old_instance.status
        new_status = instance.status

        if (old_status == 'پرداخت درب منزل') and (new_status == 'تحویل داده شده'):
            from .views import create_invoice
            create_invoice(instance)


@receiver(post_save, sender=OrderItem)
def create_or_update_invoice(sender, instance, created, **kwargs):
    order = instance.order

    # دریافت نام و نام خانوادگی
    first_name = order.user.first_name or ""
    last_name = order.user.last_name or ""
    buyer_name = f"{first_name} {last_name}".strip()

    # اگر نام خریدار خالی بود، شماره موبایل را بگذار
    if not buyer_name:
        buyer_name = order.user.phone_number

    # ایجاد یا بروزرسانی فاکتور
    invoice, _ = Invoice.objects.get_or_create(order=order, defaults={
        'user': order.user,
        'buyer_name': buyer_name,  # ✅ مقداردهی درست
        'total_price': 0,
        'payment_status': order.status,
        'address': str(order.address),
    })

    # تولید لیست محصولات
    products_text = "\n".join(
        [
            f"کد: {item.product.code} | نام: {item.product_name} (x{item.quantity}) - {item.price} تومان"
            for item in order.order_items.all()
        ]
    )

    # بروزرسانی فاکتور
    invoice.products = products_text
    invoice.total_price = order.get_price_with_send()
    invoice.payment_status = order.status
    invoice.save()

def send_invoice_email(invoice):
    try:
        subject = f'فاکتور شماره {invoice.id}'
        message = f'مشخصات فاکتور:\n\nشماره فاکتور: {invoice.id}'
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.RECEIVER_EMAIL_FOR_INVOICE],
            fail_silently=False,
        )
        logger.info(f"ایمیل فاکتور {invoice.id} ارسال شد")
        return True
    except Exception as e:
        logger.error(f"خطا در ارسال ایمیل: {str(e)}")
        return False


@receiver(post_save, sender=OrderItem)
def decrees_inventory(sender, instance, created, **kwargs):
    if instance.order.status != "6":
        instance.product.quantity -= instance.quantity
        instance.product.save()
