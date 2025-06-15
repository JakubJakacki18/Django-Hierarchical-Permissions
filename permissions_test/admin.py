from django import forms
from django.contrib import admin
from django.contrib.auth.models import Permission

from permissions.constants import Action
from permissions.form import FieldPermissionForm
from permissions.mixins import BaseAdminMixin
from permissions.models import UserGroup, OrganizationalUnit
from permissions.services import PermissionService
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
            class Meta:
                fields = '__all__'
                model = Product

            def __init__(self, *args, **inner_kwargs):
                super().__init__(*args, user=request.user, obj=obj, **inner_kwargs)

        return FormWithUserAndObj

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        perm_service = PermissionService(request.user)
        allowed_ids = [
            (obj.id, obj)
            for obj in qs
            if perm_service.has_perm_to_action(self.model, Action.VIEW, obj)
        ]
        obj_with_visible_fields = lambda obj: any(
            perm_service.has_field_permission_checker(self.model, field_name, obj)[0] for field_name in
            [field.name for field in self.model._meta.fields])
        allowed_ids = list(filter(lambda item: obj_with_visible_fields(item[1]), allowed_ids))
        return qs.filter(id__in=[item[0] for item in allowed_ids])
