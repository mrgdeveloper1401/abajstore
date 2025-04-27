from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import get_object_or_404, redirect
from django.urls import path
from django.contrib import messages
from utils.send_invoice_via_email import send_invoice_email
from .models import Order, OrderItem, Coupon, Payment, Invoice


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    # readonly_fields = ('quantity', 'price')
    readonly_fields = ('product_name', 'product_code', 'product_unit_price', 'quantity', 'price')
    # autocomplete_fields = ('product',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'user', 'status', 'get_price', 'get_payment', 'created_at']
    list_filter = ['status', 'created']
    search_fields = ['id', 'user__phone_number', 'code', 'payment__token']
    inlines = [OrderItemInline]
    readonly_fields = ['get_price', 'code', 'get_full_address', 'get_receiver_info', 'rrn']
    autocomplete_fields = ['address', 'user', 'payment']
    list_display_links = ['id', 'code']
    ordering = ['-created', ]
    exclude = ['coupon', ]

    @admin.display(description='تاریخ ثبت سفارش')
    def created_at(self, obj):
        return obj.created_datetime_to_jalali().strftime('%Y/%m/%d %H:%M')

    @admin.display(description='قیمت کل')
    def get_price(self, obj):
        return f'{obj.get_price_with_send():,}'

    @admin.display(description='اطلاعات گیرنده')
    def get_receiver_info(self, obj):
        return obj.address.receiver_info()

    @admin.display(description='آدرس')
    def get_full_address(self, obj):
        return obj.address.get_full_address()

    @admin.display(description='کد فاکتور')
    def get_payment(self, obj):
        return obj.payment.token if obj.payment else '-'

    def print_invoice_button(self, obj):
        return format_html(
            '<a class="button" href="{}"> چاپ فاکتور </a>',
            f'/admin/orders/order/{obj.id}/print-invoice/'
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:order_id>/print-invoice/', self.admin_site.admin_view(self.print_invoice), name='send-invoice'),
        ]
        return custom_urls + urls

    def print_invoice(self, request, order_id):
        order = self.get_object(request, order_id)
        try:
            if order:
                send_invoice_as_pdf(order)
                messages.success(request, "فاکتور با موفقیت ارسال شد.")
            else:
                messages.error(request, "سفارش یافت نشد.")

        except Exception as e:
            print(str(e))
            messages.error(request, "خطا ذر انجام عملیات.")

        return redirect(f'/admin/orders/order/{order_id}/change/')

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['send_invoice_button'] = self.print_invoice_button(self.get_object(request, object_id))
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    # def get_search_results(self, request, queryset, search_term):
    #     queryset, use_distinct = super().get_search_results(request, queryset, search_term)
    #     try:
    #         queryset |= self.model.objects.filter(payment__token=search_term)
    #     except Exception as e:
    #         pass
    #     return queryset, use_distinct

# @admin.register(Coupon)
# class CouponAdmin(admin.ModelAdmin):
#     list_display = ['code', 'value', 'valid_until', 'active']
#     list_filter = ['active', 'valid_until']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'token', 'order_code', 'bank', 'amount', 'status', 'jalali_created']
    list_filter = ['status', 'response_code', 'bank']
    search_fields = ['token', ]
    list_display_links = ['id', 'token', ]
    readonly_fields = ['bank', 'token', 'rrn', 'amount', 'terminal_no', 'hash_card_no', 'response', 'response_code', 'status']

    @admin.display(description='تاریخ ثبت')
    def jalali_created(self, obj):
        return obj.created_datetime_to_jalali().strftime('%Y/%m/%d %H:%M')

    @admin.display(description='کد سفارش')
    def order_code(self, obj):
        order = obj.order_payment.first()
        return order.code if order else '-'

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'total_price', 'payment_status', 'created_to_jalali')
    search_fields = ('order__code', 'user__username', 'payment_status')
