#!/bin/bash


source /home/ubuntu/abajstore/venv/bin/activate


cd /home/ubuntu/abajstore


python configs/sepandyar_webAPI.py update_category
python manage.py delete_old_unpaid_orders
python configs/sepandyar_webAPI.py update_products
python configs/sepandyar_webAPI.py resend_failed_invoices
python configs/sepandyar_webAPI.py reconnect


deactivate
