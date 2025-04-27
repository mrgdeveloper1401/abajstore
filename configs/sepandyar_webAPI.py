import os
import sys
import time
import django
import jdatetime
# import sys
# sys.path.append('C:/Users/CreatorMilad.DESKTOP-91ENPR2/Desktop/abaj/abajstore')

# source /home/abajstor/virtualenv/django_abajstore/3.9/bin/activate && cd /home/abajstor/django_abajstore && cd configs && export PYTHONPATH=/home/abajstor/django_abajstore/ && python sepandyar_webAPI.py update_products
# source /home/abajstor/virtualenv/django_abajstore/3.9/bin/activate && cd /home/abajstor/django_abajstore && cd configs && export PYTHONPATH=/home/abajstor/django_abajstore/ && python sepandyar_webAPI.py update_category
sys.path.append('/home/ubuntu/abajstore')
# export PYTHONPATH=/home/abajstor/django_abajstore/
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abajstore.settings')
django.setup()

import sqlite3
import requests
import json
from products.models import Product, MainCategory
from site_settings.models import SiteSettings
from configs.sms_panel import send_sms
from django.core.files import File
from django.conf import settings
from django.db import close_old_connections
import unicodedata
from io import BytesIO
import logging
from datetime import datetime, timedelta

# tail -f django_debug.log
# logging.basicConfig(filename='sepandyar_WebAPI.log',
#                     level=logging.WARNING,
#                     format='%(asctime)s - %(levelname)s - %(message)s')

base_url = settings.SEPANDYAR_IP
USERNAME = settings.SEPANDYAR_USER
PASSWORD = settings.SEPANDYAR_PASS
TOKEN_EXPIRY_HOURS = 1
DATABASE = 'webAPI.db'
LOGIN_URL = base_url + "user/login"
# admin_phone_number = SiteSettings.objects.first().admin_phone_number


# ===================================================================================================
# ===================================================================================================
# ===================================================================================================
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tokens (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        token TEXT NOT NULL,
                        timestamp DATETIME NOT NULL
                      )''')

    conn.commit()

    cursor.execute('''CREATE TABLE IF NOT EXISTS failed_requests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        invoice_list TEXT NOT NULL,
                        desc TEXT,
                        name TEXT,
                        mobile TEXT,
                        postalcode TEXT,
                        address TEXT,
                        person TEXT,
                        timestamp DATETIME NOT NULL
                      )''')
    conn.commit()
    conn.close()


# ===================================================================================================
# ===================================================================================================
def save_token(token, timestamp):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO tokens (token, timestamp) VALUES (?, ?)''',
                   (token, timestamp.isoformat()))
    conn.commit()
    conn.close()


def load_token():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''SELECT token, timestamp FROM tokens ORDER BY id DESC LIMIT 1''')
    row = cursor.fetchone()
    conn.close()
    if row:
        return {'token': row[0], 'timestamp': row[1]}
    return None


def is_token_expired(timestamp):
    expiry_time = datetime.fromisoformat(timestamp) + timedelta(hours=TOKEN_EXPIRY_HOURS)
    return datetime.now() > expiry_time


def is_token_valid(token):
    test_url = base_url + 'product/GetUnits'
    headers = {
        'Authorization': 'Bearer ' + str(token),
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(test_url, headers=headers)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error checking token validity: {e}")
        return False


def login(username, password):
    login_data = {
        'username': username,
        'password': password
    }
    try:
        login_response = requests.get(LOGIN_URL, data=login_data, timeout=5)

        if login_response.status_code == 200:
            result = login_response.json()
            return result['Token']
        else:
            print(f"Error in 'login': {login_response.json()}")
            return None

    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
        return None


def get_token():
    try:
        init_db()
        token_info = load_token()
        if token_info:
            token = token_info['token']
            timestamp = token_info['timestamp']
            if not is_token_expired(timestamp):
                if is_token_valid(token):
                    return token

        new_token = login(USERNAME, PASSWORD)
        if new_token:
            save_token(new_token, datetime.now())
            return new_token
        return None
    except Exception as e:
        print(str(e))
        return None


token = get_token()
headers = {
    'Authorization': 'Bearer ' + str(token),
    'Content-Type': 'application/json'
}


# ===================================================================================================
# ===================================================================================================

# def login(username, password):
#     login_url = base_url + 'user/login'
#     login_data = {
#         'username': username,
#         'password': password
#     }
#
#     login_response = requests.get(login_url, data=login_data)
#
#     if login_response.status_code == 200:
#         result = login_response.json()
#         return result['Token']
#     else:
#         print(f"Error in 'login' : {login_response.json()}")
#
#
# token = login(username, password)
# headers = {
#     'Authorization': 'Bearer ' + token,
#     'Content-Type': 'application/json'
# }


# ===================================================================================================
# ===================================================================================================
# ===================================================================================================
def standardize_persian_text(text):
    replacements = {
        'ي': 'ی',
        'ك': 'ک',
        'ة': 'ه',
    }

    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def update_category():
    try:
        url = base_url + 'product/GetCategories'
        response_with_headers = requests.get(url, headers=headers, timeout=200, stream=True)
        if response_with_headers.status_code == 200:
            result = response_with_headers.json()
            categories = result.get('Categories', [])
            received_category_codes = []

            for item in categories:
                _id = item.get('Id')
                _name = item.get('Name')
                _parent = int(item.get('Parent'))
                # received_category_codes.append(_id)

                if _parent == 0:
                    _parent = None
                else:
                    _parent = None

                MainCategory.objects.update_or_create(id=_id, defaults={'name': _name, 'parent': _parent})

            # wen forloop has been done successfully
            else:
                for item in categories:
                    _id = item.get('Id')
                    _name = item.get('Name')
                    _parent = int(item.get('Parent'))

                    if _parent != 0:
                        try:
                            parent = MainCategory.objects.get(id=_parent)
                        except MainCategory.DoesNotExist:
                            parent = None

                        MainCategory.objects.update_or_create(id=_id, defaults={'name': _name, 'parent': parent})

                if received_category_codes:
                    MainCategory.objects.exclude(id__in=received_category_codes).delete()
                    print('Some Categories Deleted Successfully!')

            print('Categories updated successfully!')
        else:
            print(f"Error In 'update_category' : {response_with_headers.json()}")
    except Exception as e:
        print(str(e))
        return None


# ===================================================================================================
# ===================================================================================================
def save_products_to_file(products, filename='products.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)


def load_products_from_file(filename='products.json'):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


# ===================================================================================================
def get_products_from_api():
    try:
        print('Loading Products From API...')
        url = base_url + 'product/GetProducts'
        response_with_headers = requests.get(url, headers=headers, timeout=400)

        if response_with_headers.status_code == 200:
            print(f'Status Code: {response_with_headers.status_code}')

            result = response_with_headers.json()
            products_list = result.get('Products', [])
            save_products_to_file(products_list)
            return True
        return False
    except Exception as e:
        print(str(e))
        return False


# ===================================================================================================
counter = 0
def update_products():
    print('Updating Products...')
    global counter
    close_old_connections()
    loaded_products = load_products_from_file()
    received_product_codes = []

    try:
        for item in loaded_products:
            _code = item.get('Code')
            _name = item.get('Name')
            _price = int(item.get('Price1')) // 10
            _category_id = item.get('CategoryId')
            _quantity = item.get('Quantity')
            _unit_type = item.get('Unit1Id')
            # _quantity = 1
            _category = None if _category_id == 0 else _category_id

            # if _quantity > 0.1:
            #     print(_quantity)

            try:
                category = MainCategory.objects.get(id=_category) if _category else None
            except MainCategory.DoesNotExist:
                print(f"Category with ID {_category} does not exist.")
                category = None

            # image_path = f'cover_images/{_code}.jpg'
            # image_path = f'/home/abajstor/public_html/media/cover_images/{_code}.jpg'

            # if os.path.isfile(image_path):
            #     with open(image_path, 'rb') as image_file:
            #         cover_image = File(BytesIO(image_file.read()), name=f'{_code}.jpg')
            # else:
            #     cover_image = None

            # print(image_path)
            # if os.path.exists(image_path):
            #     image_path = f'cover_images/{_code}.jpg'
            # else:
            #     image_path = 'cover_images/default-image2.jpg'

            product, created = Product.objects.update_or_create(
                id=int(_code),
                defaults={
                    'code':_code,
                    'name': standardize_persian_text(_name),
                    'price': _price,
                    'category': category,
                    'quantity': _quantity,
                    'unit_type': _unit_type
                    # 'cover_image': image_path,
                }
            )

            received_product_codes.append(_code)

            image_path = f'/home/abajstor/public_html/media/cover_images/{_code}.jpg'
            if os.path.exists(image_path):
                image_path = f'cover_images/{_code}.jpg'
                product.cover_image = image_path
                product.save()

            if created:
                print(f"Product {_code} created successfully.")
            else:
                print(f"Product {_code} updated successfully.")

    except Exception as e:
        print(str(e))
        if counter < 3:
            print('Trying Again After 5min...')
            counter += 1
            # time.sleep(300)
            # get_products_from_api()
            update_products()
        return

    # delete if not in api_products
    if received_product_codes:
        Product.objects.exclude(code__in=received_product_codes).delete()
        print('Some Products Deleted Successfully!')

    print('\nProducts Updated Successfully!')

    # try:
    #     user_pattern = '97d4fb08-05ac-45e6-bfb4-b53c12e68b95'
    #     key = {
    #         'token1': jdatetime.datetime.now().strftime('%Y/%m/%d-%H:%M'),
    #     }
    #     send_sms(user_pattern, admin_phone_number, key)
    # except Exception as e:
    #     print(str(e))
    # else:
    #     print(f"Error In 'update_products' : {response_with_headers.json()}")


# ===================================================================================================
def get_product(product_code):
    url = base_url + 'product/GetProducts'
    data = {
        'IdKalas': product_code,
    }
    json_data = json.dumps(data)

    try:
        response_with_headers = requests.get(url, data=json_data, headers=headers, timeout=7)

        if response_with_headers.status_code == 200:
            result = response_with_headers.json()
            product = result.get('Products', [])
            return product[0] if product[0] else None

        # logging.warning(response_with_headers.json())
        return None

    except Exception as e:
        # logging.warning(str(e))
        return None

    # if response_with_headers.json().get("Messages") == 'توکن باطل شده است، لطفا از برنامه خارج شده و دوباره وارد شوید':
    #     global token
    #     token = login(username, password)
    #     get_product(product_code)


# ===================================================================================================
# ===================================================================================================
def save_failed_invoice_request(order_code, invoice_list, desc, name, mobile, postalcode, address, person):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''SELECT COUNT(*) FROM failed_requests WHERE order_code = ?''', (order_code,))
    result = cursor.fetchone()

    if result[0] == 0:
        cursor.execute('''INSERT INTO failed_requests (order_code, invoice_list, desc, name, mobile, postalcode, address, person, timestamp)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (order_code, json.dumps(invoice_list), desc, name, mobile, postalcode, address, person, datetime.now()))
        conn.commit()
    else:
        print(f"Duplicate entry for order_id: {order_code}, skipping insertion.")

    conn.close()


def resend_failed_invoice_requests():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM failed_requests')
        rows = cursor.fetchall()

        for row in rows:
            id, invoice_list, desc, name, mobile, postalcode, address, person, timestamp = row
            send_invoice_list(json.loads(invoice_list), desc, name, mobile, postalcode, address, person)

            cursor.execute('DELETE FROM failed_requests WHERE id = ?', (id,))
            conn.commit()

        conn.close()
        return True

    except Exception as e:
        print(str(e))
        return False


# ===================================================================================================
def send_invoice_list(invoice_list, desc, name, mobile, postalcode, address, person, order_code=None):
    url = base_url + 'invoice/PostInvoices'
    data = {
        "userId": 1,
        "Invoices": invoice_list,
        "desc": desc,
        "name": name,
        "mobile": mobile,
        "postalcode": postalcode,
        "address": address,
        "person": person
    }
    json_data = json.dumps(data)

    # logging.warning(json_data)

    try:
        response_with_headers = requests.post(url, data=json_data, headers=headers, timeout=10)

        # if response_with_headers.status_code == 200:
        #     resend_failed_invoice_requests()
        # else:
        if response_with_headers.status_code != 200:
            save_failed_invoice_request(order_code, invoice_list, desc, name, mobile, postalcode, address, person)

        # logging.warning(response_with_headers.json())

    except requests.exceptions.RequestException as e:
        save_failed_invoice_request(invoice_list, desc, name, mobile, postalcode, address, person)
        # logging.warning(str(e))


# if response_with_headers.status_code == 200:
#     print("invoices sent successfully")
#     print("response:", response_with_headers.json())
# else:
#     print(f"error: {response_with_headers.status_code}")
#     print("response:", response_with_headers.text)

# if response_with_headers.json().get("Messages") == 'توکن باطل شده است، لطفا از برنامه خارج شده و دوباره وارد شوید':
#     global token
#     token = login(username, password)
#     send_invoice_list(invoice_list, desc, name, mobile, postalcode, address, user_id)

# *****************************

# update_category()
# update_products()

# *****************************


if __name__ == "__main__":
    if len(sys.argv) > 1:
        func_name = sys.argv[1]

        if func_name == "update_products":
            products = get_products_from_api()
            if products:
                update_products()

        elif func_name == "update_category":
            update_category()

        elif func_name == "resend_failed_invoices":
            resend_failed_invoice_requests()

        elif func_name == "reconnect":
            get_token()

        else:
            print(f"No such function: {func_name}")

        print("\nDone.")
    else:
        print("No function name provided.")
