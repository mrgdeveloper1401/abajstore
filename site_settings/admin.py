from .models import SiteSettings, BannerImages, Link, Address, Phone
from django.contrib import admin


class BannerImagesAdmin(admin.TabularInline):
    model = BannerImages
    extra = 1


class LinkAdmin(admin.TabularInline):
    model = Link
    extra = 1


class AddressAdmin(admin.TabularInline):
    model = Address
    extra = 1


class PhoneAdmin(admin.TabularInline):
    model = Phone
    extra = 1


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    inlines = [BannerImagesAdmin, LinkAdmin, AddressAdmin, PhoneAdmin]


class CustomAdminSite(admin.AdminSite):
    site_header = '(site_header)'
    site_title = '(site_title)'
    index_title = '(index_title)'

    # def get_urls(self):
    #     urls = super().get_urls()
    #     custom_urls = [
    #         path('settings/', self.admin_view(self.settings_view), name='settings'),
    #     ]
    #     return custom_urls + urls

    # def settings_view(self, request):
    #     if request.method == 'POST':
    #         form = SiteSettingsAdmin.form(request.POST, request.FILES, instance=SiteSettings.get_solo())
    #         if form.is_valid():
    #             form.save()
    #             self.message_user(request, "تنظیمات با موفقیت اعمال شد!")
    #             return HttpResponseRedirect(request.path)
    #     else:
    #         form = SiteSettingsAdmin.form(instance=SiteSettings.get_solo())
    #
    #     context = {
    #         'form': form,
    #         'title': 'Site Settings'
    #     }
    #     return render(request, 'admin/settings.html', context)


admin_site = CustomAdminSite(name='custom_admin')
