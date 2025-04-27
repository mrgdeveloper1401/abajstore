from .models import SiteSettings


def site_settings(request):
    settings = SiteSettings.objects.first()
    if settings:
        header_message = settings.header_message
        fast_send_price = settings.fast_send_price
        pay_with_mellat = settings.pay_with_mellat
        pay_with_parsian = settings.pay_with_parsian
        pay_at_home = settings.pay_at_home
        banner_images = settings.banner_images.all()
        links = settings.links.all()
        address = settings.address.all()
        phone = settings.phone.all()

        return {'header_message': header_message,
                'fast_send_price': fast_send_price,
                'pay_with_mellat': pay_with_mellat,
                'pay_with_parsian': pay_with_parsian,
                'pay_at_home': pay_at_home,
                'banner_images': banner_images,
                'links': links,
                'addresses': address,
                'phones': phone,
                }
    return {}
