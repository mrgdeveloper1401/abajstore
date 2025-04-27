from configs.sepandyar_webAPI import send_invoice_list
import logging


def create_invoice(order):
    invoice_list = []
    for item in order.order_items.all():
        invoice_list.append(
            {
                "InvoiceNum": int(order.code),
                "InvoiceDate": order.created_to_jalali().strftime('%Y/%m/%d'),
                "AnbarId": 1,
                "RelationId": int(item.product.code),
                "RelationType": 0,
                "Quantity": item.quantity,
                "Bed": 0,
                "Bes": item.price * 10
            }
        )
    invoice_list.append(
            {
                "InvoiceNum": int(order.code),
                "InvoiceDate": order.created_to_jalali().strftime('%Y/%m/%d'),
                "AnbarId": 0,
                "RelationId": 2,
                "RelationType": 2,
                "Quantity": 0,
                "Bed": order.get_price() * 10,
                "Bes": 0
            })
    logging.warning(invoice_list)

    send_invoice_list(invoice_list=invoice_list,
                      desc="pardakht interneti",
                      name="abajstore",
                      mobile=order.address.phone_number,
                      postalcode="0",
                      address="yazd",
                      person="1")
