from typing import Type
from django.db.models import Model
from permissions.constants import Action
from permissions.services import PermissionService
from permissions.decorators import has_perm_checker_decorator


# Approach with decorator.
# After many changes has_perm_checker_decorator probably doesn't work.
# I leave it, because maybe it'll be idea to improve admin site permissions.
class DecoratorAdminMixin:
    model: Type[Model]

    def get_app_name(self):
        return self.model._meta.app_label

    def get_model_name(self):
        return self.model._meta.model_name

    @has_perm_checker_decorator(
        lambda self: (f"{self.get_app_name()}.add_{self.get_model_name()}",)
    )
    def has_add_permission(self, request):
        return False

    @has_perm_checker_decorator(
        lambda self: (
                f"{self.get_app_name()}.delete_{self.get_model_name()}",
                f"{self.get_app_name()}.scoped_delete_{self.get_model_name()}",
        )
    )
    def has_delete_permission(self, request, obj=None):
        return False

    @has_perm_checker_decorator(
        lambda self: (
                f"{self.get_app_name()}.change_{self.get_model_name()}",
                f"{self.get_app_name()}.scoped_change_{self.get_model_name()}",
        )
    )
    def has_change_permission(self, request, obj=None):
        return False

    @has_perm_checker_decorator(
        lambda self: (
                f"{self.get_app_name()}.view_{self.get_model_name()}",
                f"{self.get_app_name()}.scoped_view_{self.get_model_name()}",
        )
    )
    def has_view_permission(self, request, obj=None):
        return False


class BaseAdminMixin:

    def has_add_permission(self, request):
        perm_service = PermissionService(request.user)
        return perm_service.has_perm_to_action(self.model, Action.ADD)

    def has_delete_permission(self, request, obj=None):
        perm_service = PermissionService(request.user)
        return perm_service.has_perm_to_action(self.model, Action.DELETE, obj)

    def has_change_permission(self, request, obj=None):
        perm_service = PermissionService(request.user)
        return perm_service.has_perm_to_action(self.model, Action.CHANGE, obj)

    def has_view_permission(self, request, obj=None):
        perm_service = PermissionService(request.user)
        return perm_service.has_perm_to_action(self.model, Action.VIEW, obj)

    def has_module_permission(self, request):
        if request.user.is_authenticated:
            perm_service = PermissionService(request.user)
            return perm_service.has_perm_to_action(self.model, Action.VIEW)
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        perm_service = PermissionService(request.user)
        # Heavy but easy to implement. In the future I suggest optimization.
        allowed_ids = [
            obj.id
            for obj in qs
            if perm_service.has_perm_to_action(self.model, Action.VIEW, obj)
        ]
        return qs.filter(id__in=allowed_ids)
