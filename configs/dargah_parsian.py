import json
import requests
from django.conf import settings
import xml.etree.ElementTree as ET

# qjEOCMYr122B7O04NJyl
# 5E04tJJJ3po13qE6equ5
class PaymentGateway:
    @staticmethod
    def request_payment(order_id, amount, callback_url):
        url = "https://pec.shaparak.ir/NewIPGServices/Sale/SaleService.asmx"

        headers = {
            'Content-Type': 'text/xml',
            'soap-action': 'https://pec.Shaparak.ir/NewIPGServices/Sale/SaleService/SaleServiceSoap/SalePaymentRequestRequest'
        }

        data = f'''<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:sal="https://pec.Shaparak.ir/NewIPGServices/Sale/SaleService">
           <soap:Header/>
           <soap:Body>
              <sal:SalePaymentRequest>
                 <sal:requestData>
                    <sal:LoginAccount>{settings.PAYMENT_GATEWAY_LOGIN}</sal:LoginAccount>
                    <sal:Amount>{amount}</sal:Amount>
                    <sal:OrderId>{order_id}</sal:OrderId>
                    <sal:CallBackUrl>{callback_url}</sal:CallBackUrl>
                 </sal:requestData>
              </sal:SalePaymentRequest>
           </soap:Body>
        </soap:Envelope>'''

        response = requests.post(url, headers=headers, data=data)

        root = ET.fromstring(response.text)
        namespaces = {'soap': 'http://www.w3.org/2003/05/soap-envelope',
                      'ns': 'https://pec.Shaparak.ir/NewIPGServices/Sale/SaleService'}
        token = root.find('.//ns:SalePaymentRequestResult/ns:Token', namespaces).text
        status = root.find('.//ns:SalePaymentRequestResult/ns:Status', namespaces).text
        message = root.find('.//ns:SalePaymentRequestResult/ns:Message', namespaces).text

        if status == '0' and token > '0':
            return token
        else:
            raise Exception(f"Payment request failed: {message}")

    @staticmethod
    def verify_payment(token):
        url = 'https://pec.shaparak.ir/NewIPGServices/Confirm/ConfirmService.asmx'
        headers = {
            'Content-Type': 'text/xml',
            'soap-action': 'https://pec.Shaparak.ir/NewIPGServices/Confirm/ConfirmService/ConfirmPayment'
        }

        data = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:con="https://pec.Shaparak.ir/NewIPGServices/Confirm/ConfirmService">
           <soapenv:Header/>
           <soapenv:Body>
              <con:ConfirmPayment>
                 <con:requestData>
                    <con:LoginAccount>{settings.PAYMENT_GATEWAY_LOGIN}</con:LoginAccount>
                    <con:Token>{token}</con:Token>
                 </con:requestData>
              </con:ConfirmPayment>
           </soapenv:Body>
        </soapenv:Envelope>'''

        response = requests.post(url, headers=headers, data=data)

        root = ET.fromstring(response.text)
        namespaces = {'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
                      'ns': 'https://pec.Shaparak.ir/NewIPGServices/Confirm/ConfirmService'}

        status = root.find('.//ns:ConfirmPaymentResult/ns:Status', namespaces).text
        card_number_masked = root.find('.//ns:ConfirmPaymentResult/ns:CardNumberMasked', namespaces).text
        rrn = root.find('.//ns:ConfirmPaymentResult/ns:RRN', namespaces).text
        token = root.find('.//ns:ConfirmPaymentResult/ns:Token', namespaces).text

        if status == '0':
            return True
        else:
            return False


# ================================================+++++++++++++++++++++++++++++++++++

        # ========================================================================================
        # callback_url = self.request.build_absolute_uri(reverse('payment_callback'))
        #
        # try:
        #     token = PaymentGateway.request_payment(order.id, order.amount, callback_url)
        #     return redirect(f"https://pec.shaparak.ir/NewIPG/?Token={token}")
        # except Exception as e:
        #     # Log the error
        #     return redirect('payment_error')
        # ========================================================================================

# ========================================================================================
# @method_decorator(csrf_exempt, name='dispatch')
# class PaymentCallbackView(View):
#     def post(self, request, *args, **kwargs):
#         token = request.POST.get('Token')
#         status = request.POST.get('status')
#         order_id = request.POST.get('OrderId')
#         rrn = request.POST.get('RRN')
#
#         if not all([token, status, order_id, rrn]):
#             return HttpResponseBadRequest("Missing required parameters")
#
#         if status == '0' and int(rrn) > 0:
#             # Payment was successful, verify it
#             if PaymentGateway.verify_payment(token):
#                 try:
#                     order = Order.objects.get(id=order_id)
#                     order.status = 'paid'
#                     order.save()
#                     return redirect('payment_success')
#                 except Order.DoesNotExist:
#                     return HttpResponseBadRequest("Invalid order")
#             else:
#                 # Payment verification failed
#                 return redirect('payment_failed')
#         else:
#             # Payment was not successful
#             return redirect('payment_failed')
# ========================================================================================

