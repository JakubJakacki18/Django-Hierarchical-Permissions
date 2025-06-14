from django.contrib import admin
from django.contrib.auth.models import Permission

from permissions.mixins import BaseAdminMixin
from permissions.models import UserGroup, OrganizationalUnit
from permissions_test.models import Product

# Register your models here.
admin.site.register(Permission)
admin.site.register(UserGroup)
admin.site.register(OrganizationalUnit)


@admin.register(Product)
class ProductAdmin(BaseAdminMixin, admin.ModelAdmin):
    list_display = ("name", "price")
    search_fields = ("name",)
    ordering = ("name",)
