from django.apps import AppConfig

from permissions.constants import PermissionSubType
from permissions_test.rules import is_owner


class PermissionsTestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'permissions_test'

    def ready(self):
        # import permissions_test.rules
        from .models import Product
        from permissions.services import PermissionCreationService
        Product._meta.permissions += *PermissionCreationService.create_fields_permissions(Product),
        Product._meta.permissions += *PermissionCreationService.add_rules_to_permissions(
            self.name,
            PermissionCreationService.create_crud_permissions_by_type(
                Product._meta.model_name,
                PermissionSubType.OWNER),
            [is_owner]),
