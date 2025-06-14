from django import forms

from permissions.services import PermissionService


class FieldPermissionForm(forms.ModelForm):
    def __init__(self, *args, user=None, obj=None, **kwargs):
        super().__init__(*args, **kwargs)
        perm_service = PermissionService(user)
        for field_name in list(self.fields.keys()):
            view_permission, change_permission = perm_service.has_field_permission_checker(self._meta.model, field_name,
                                                                                           obj)
            print(view_permission, change_permission, field_name, "form")
            if not view_permission:
                self.fields[field_name].widget = forms.HiddenInput()
                continue
            if not change_permission:
                self.fields[field_name].disabled = True

                # del self.fields[field_name]
