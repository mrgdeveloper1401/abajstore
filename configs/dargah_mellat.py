import logging
from json import dumps, loads
from time import gmtime, strftime
from zeep import Client, Transport
from django.conf import settings


class Mellat:
    def __init__(self, callback_url, amount, mobile_number=None):
        self.terminal_code = '6378185'
        self.username = 'abajmarket20'
        self.password = '36001767'
        self.tracking_code = '36001767'
        self.callback_url = callback_url
        self.amount = amount
        self.mobile_number = mobile_number
        self.reference_number = 0
        self.sale_reference_id = ""
        self.transaction_status_text = ""
        self.payment_url = "https://bpm.shaparak.ir/pgwchannel/startpay.mellat"

    def get_payment_data(self, code):
        description = f"خرید با شماره پیگیری - {code}"
        return {
            "terminalId": int(self.terminal_code),
            "userName": self.username,
            "userPassword": self.password,
            "orderId": int(code),
            "amount": int(self.amount),
            "localDate": self._get_current_date(),
            "localTime": self._get_current_time(),
            "additionalData": description,
            "callBackUrl": self.callback_url,
            "payerId": 0,
        }

    def pay(self, code):
        data = self.get_payment_data(code)
        client = self._get_client()
        response = client.service.bpPayRequest(**data)

        # logging.critical(data)
        # logging.critical(client)
        # logging.critical(response)

        try:
            status, token = response.split(",")
            if status == "0":
                self.reference_number = token
            else:
                self.transaction_status_text = f"Payment failed with status {status}"
        except ValueError:
            self.transaction_status_text = "Unknown error"
            # logging.critical(self.transaction_status_text)

    def verify(self):
        data = self.get_verify_data()
        client = self._get_client()
        verify_result = client.service.bpVerifyRequest(**data)
        if verify_result == "0":
            self._settle_transaction()
        else:
            self._handle_failed_verification(client, data)

    def _settle_transaction(self):
        data = self.get_verify_data()
        client = self._get_client()
        settle_result = client.service.bpSettleRequest(**data)
        if settle_result == "0":
            self._set_payment_status('completed')
        else:
            print("Mellat gateway did not settle the payment")
            # logging.debug("Mellat gateway did not settle the payment")

    def _handle_failed_verification(self, client, data):
        # logging.debug("Verification failed, attempting inquiry")
        print("Verification failed, attempting inquiry")
        inquiry_result = client.service.bpInquiryRequest(**data)
        if inquiry_result == "0":
            self._settle_transaction()
        else:
            # logging.debug("Inquiry failed, attempting reversal")
            print("Inquiry failed, attempting reversal")
            reversal_result = client.service.bpReversalRequest(**data)
            if reversal_result != "0":
                # logging.debug("Reversal request failed")
                print("Reversal request failed")
            self._set_payment_status('canceled')
            # logging.debug("Mellat gateway unapproved the payment")
            print("Mellat gateway unapproved the payment")

    def get_verify_data(self):
        return {
            "terminalId": self.terminal_code,
            "userName": self.username,
            "userPassword": self.password,
            "orderId": self.reference_number,
            "saleOrderId": self.reference_number,
            "saleReferenceId": self.sale_reference_id,
        }

    def _get_sale_reference_id(self):
        extra_information = loads(getattr(self, "extra_information", "{}"))
        return extra_information.get("SaleReferenceId", "1")

    @staticmethod
    def _get_client():
        transport = Transport(timeout=5, operation_timeout=5)
        return Client("https://bpm.shaparak.ir/pgwchannel/services/pgw?wsdl", transport=transport)

    @staticmethod
    def _get_current_time():
        return strftime("%H%M%S")

    @staticmethod
    def _get_current_date():
        return strftime("%Y%m%d", gmtime())

    def _set_payment_status(self, status):
        self.payment_status = status
