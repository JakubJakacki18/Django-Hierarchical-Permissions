from django.contrib import admin
from django.contrib.auth.models import Permission

from permissions.form import FieldPermissionForm
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
    form = FieldPermissionForm

    def get_form(self, request, obj=None, **kwargs):
        base_form = super().get_form(request, obj=obj, **kwargs)

        class FormWithUserAndObj(base_form):
            def __init__(self, *args, **inner_kwargs):
                super().__init__(*args, user=request.user, obj=obj, **inner_kwargs)

        return FormWithUserAndObj
