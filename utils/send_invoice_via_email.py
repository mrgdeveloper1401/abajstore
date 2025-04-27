from django.conf import settings
from django.core.mail import EmailMessage
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import getSampleStyleSheet
import jdatetime
from reportlab.lib.enums import TA_RIGHT
import logging
import json

pdfmetrics.registerFont(TTFont('vazir', '/home/mg/Desktop/django-project/abajstore-main/utils/VAZIR.TTF'))

def get_persian_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

def wrap_long_text(text, max_words_per_line=3):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

def generate_invoice_pdf(invoice):
    buffer = BytesIO()
    page_width = 283.5
    page_height = letter[1]
    
    pdf = SimpleDocTemplate(
        buffer, 
        pagesize=(page_width, page_height), 
        topMargin=5, 
        bottomMargin=5
    )
    
    elements = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Farsi', 
        fontName='vazir', 
        fontSize=10, 
        alignment=TA_RIGHT,
        wordWrap='RTL'
    ))

    # Title Section
    title = Paragraph(get_persian_text("فاکتور فروش سایت آباج استور"), styles['Farsi'])
    elements.append(title)

    # Invoice Information
    info_data = [
        [get_persian_text("شماره فاکتور:"), invoice.order.code],
        [get_persian_text("تاریخ فاکتور:"), jdatetime.datetime.fromgregorian(datetime=invoice.created).strftime("%Y/%m/%d - %H:%M")],
        [get_persian_text("نام خریدار:"), invoice.buyer_name],
        [get_persian_text("وضعیت پرداخت:"), invoice.get_payment_status_display()],
        [get_persian_text("آدرس تحویل:"), wrap_long_text(invoice.address)],
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'vazir'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(info_table)

    # Products Table
    try:
        products = json.loads(invoice.products)
    except Exception as e:
        products = []
        logging.error(f"Error loading products: {e}")

    table_data = [
        [
            get_persian_text("ردیف"),
            get_persian_text("نام محصول"),
            get_persian_text("تعداد"),
            get_persian_text("قیمت واحد"),
            get_persian_text("جمع"),
        ]
    ]
    
    for idx, product in enumerate(products, 1):
        table_data.append([
            str(idx),
            wrap_long_text(product.get('name', '')),
            str(product.get('quantity', 0)),
            f"{product.get('unit_price', 0):,}",
            f"{product.get('total_price', 0):,}",
        ])

    products_table = Table(table_data, colWidths=[0.5*inch, 2.5*inch, 1*inch, 1.5*inch, 1.5*inch])
    products_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#CCCCCC')),
        ('FONTNAME', (0,0), (-1,-1), 'vazir'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ]))
    elements.append(products_table)

    # Total Section
    total_data = [
        [get_persian_text("مبلغ کل:"), f"{invoice.total_price:,} ریال"],
        [get_persian_text("وضعیت پرداخت:"), get_persian_text(invoice.get_payment_status_display())],
    ]
    
    total_table = Table(total_data, colWidths=[2*inch, 4*inch])
    total_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'vazir'),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
    ]))
    elements.append(total_table)

    pdf.build(elements)
    buffer.seek(0)
    return buffer

def send_invoice_email(invoice):
    try:
        pdf_buffer = generate_invoice_pdf(invoice)
        
        email = EmailMessage(
            subject=f"فاکتور {invoice.order.code}",
            body=get_persian_text("پیوست فاکتور خرید شما"),
            from_email=settings.EMAIL_HOST_USER,
            to=[settings.RECEIVER_EMAIL_FOR_INVOICE],
        )
        
        email.attach(
            filename=f"Invoice_{invoice.order.code}.pdf",
            content=pdf_buffer.getvalue(),
            mimetype="application/pdf"
        )
        
        email.send(fail_silently=False)
        return True
        
    except Exception as e:
        logging.error(f"Error sending invoice email: {e}")
        return False
