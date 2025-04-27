# import base64
#
# # اطلاعات برای کدگذاری
# username_password = 'abajmarket:76812801250'
#
# # کدگذاری به Base64
# encoded_bytes = base64.b64encode(username_password.encode('utf-8'))
# encoded_str = encoded_bytes.decode('utf-8')
#
# print(f"Base64 Encoded: {encoded_str}")

# YWJham1hcmtldDo3NjgxMjgwMTI1MA==
# ======================================================================
# "https://smspanel.trez.ir/SendPatternWithUrl.ashx\
# ?AccessHash=1c738e0e-4f10-4299-bdaa-1cff6eb84908\
# &PhoneNumber=5000202\
# &PatternId=ffa78efa-58ad-41e5-a37e-63eb5c76cf89\
# &RecNumber=+989116665601\
# &Smsclass=1\
# &token1=\
# &token2=\
# &token3="
from django.conf import settings
import requests
import json


send_sms_url = 'https://smspanel.trez.ir/SendPatternWithPost.ashx'


def send_sms(pattern_id, rec_number, key):
    data = {
        'AccessHash': settings.SMS_API_KEY,
        'PhoneNumber': settings.SMS_NUMBER,
        'PatternId': pattern_id,
        'RecNumber': rec_number,
        'Smsclass': '1',
    }
    data.update(key)

    # headers = {
    #     'Content-Type': 'application/x-www-form-urlencoded',
    #     'Authorization': f'Bearer {settings.SMS_AUTH_BASE64}'
    # }

    response = requests.post(send_sms_url, data=data)
    return {
        'data': data,
        'response': response,
    }
