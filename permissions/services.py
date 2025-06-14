from typing import Any
import rules
from django.contrib.auth.models import User, Permission
from permissions.constants import (
    PERMISSION_SUBTYPES_LABELS,
    Action,
    PermissionSubType,
)
from permissions.utils import actions_to_list, permissions_divider
from .models import UserGroup
from django.contrib.contenttypes.models import ContentType
from django.db import models


# Class responsible for checking permissions
class PermissionService:
    """Class responsible for checking permissions."""

    # Fetching UserGroups to optimaze process of checking permissions
    # PermissionService should be singleton/multiton to use the potential of that constructor.
    def __init__(self, user: User):
        self.user = user
        self.user_groups = UserGroup.objects.filter(
            assigned_users=user
        ).prefetch_related(
            "assigned_permission_groups", "assigned_organizational_units"
        )

    @staticmethod
    def get_all_permissions_for_model(model, action=None):
        """Get all permissions for model. Use ``action`` argument to filter all permissions"""
        content_type = ContentType.objects.get_for_model(model)
        permissions = Permission.objects.filter(content_type=content_type)
        if action:
            permissions = permissions.filter(codename__contains=action.value)
        return [
            f"{content_type.app_label}.{permission.codename}"
            for permission in permissions
        ]

    def _regular_permissions_checker(self, permissions, obj) -> bool:
        """Check regular permissions"""
        return any(self.has_permission(permission, obj) for permission in permissions)

    def _olp_permissions_checker(self, permissions, obj) -> bool:
        """Check OLP (Object Level Permission)"""
        # print(f"Sprawdzane olp uprawnien: {permissions}")
        if obj is None:
            return False  # could be unnecessary
        for permission in permissions:
            has_perm = self.has_permission(permission, obj)
            print("HAS_PERM: ", has_perm)
            if has_perm:
                test_rule = rules.test_rule(permission, self.user, obj)
                print("TEST_RULE: ", test_rule)
                return test_rule
        return False

    def _model_level_has_permission(self, permission):
        """Check if user has permission in any of his user groups."""
        return self._is_permission_in_user_groups(permission, self.user_groups)

    def _object_level_has_permission(self, permission, obj) -> bool:
        """Check if user has permission in any of his user groups in scope of organizational units"""
        parent_organizational_unit = obj.parent
        list_of_organizational_units = parent_organizational_unit.get_ancestors(
            include_self=True, ascending=True
        )
        for organizational_unit in list_of_organizational_units:
            user_groups = UserGroup.objects.filter(
                assigned_users=self.user,
                assigned_organizational_units=organizational_unit,
            )
            if self._is_permission_in_user_groups(permission, user_groups):
                return True
        return False

    def _is_permission_in_user_groups(self, permission, user_groups) -> bool:
        """
        Check if permission is in any of user groups.

        Args:
            permission (str): Permission codename in format 'app_label.codename'.
            user_groups (QuerySet): UserGroups queryset.

        Returns:
            bool: True if user has permission, False otherwise.
        """
        permission_groups_set = set()
        for user_group in user_groups:
            permission_groups_set.update(user_group.assigned_permission_groups.all())
        permissions_set = set()
        for group in permission_groups_set:
            perms = group.permissions.all()
            formatted_perms = {
                f"{perm.content_type.app_label}.{perm.codename}" for perm in perms
            }
            permissions_set.update(formatted_perms)
        if permission in permissions_set:
            return True
        return False

    def has_permission(self, permission, obj=None):
        if obj is not None and (not hasattr(obj, "parent") or not obj.parent):
            raise AttributeError(
                f"{obj.__class__.__module__}.{obj.__class__.__name__} doesn't have parent attribute or parent is null."
            )
        return (
            self._object_level_has_permission(permission, obj)
            if obj is not None
            else self._model_level_has_permission(permission)
        )

    def has_perm_to_action(self, model, action: Action, obj=None):
        if self.user.is_superuser:
            return True
        # print("------------------------------------\n")
        # print("Model", model)
        # print("Obj", obj)
        # print("Action", action)
        # print("------------------------------------\n")
        all_permissions_for_model = PermissionService.get_all_permissions_for_model(
            model, action
        )
        return self.has_perm_checker(obj, *all_permissions_for_model)

    def has_perm_checker(self, obj, *permissions):
        # print("Permissions has perm checker:", permissions)
        permissions_dict = permissions_divider(*permissions)
        if self._regular_permissions_checker(permissions_dict.get("regular"), obj):
            print("Regular: ", True)

            return True
        if self._olp_permissions_checker(permissions_dict.get("olp"), obj):
            print("Olp: ", True)
            return True
        print("has_perm_checker", False)
        return False


class PermissionCreationService:
    """Class responsible for checking permissions.    Permission Creation Service is used to create codenames and assign rules to permission"""

    @staticmethod
    def create_crud_permissions_by_type(
            model_name: str, permission_type: PermissionSubType, description: str = None
    ) -> list:
        if permission_type not in PERMISSION_SUBTYPES_LABELS.keys():
            raise KeyError(
                f"Key {permission_type} doesn't exist in PERMISSION_TYPES_LABELS"
            )
        if permission_type == PermissionSubType.FIELD:
            raise TypeError(
                "Argument 'permission_type' cannot be 'PermissionType.FIELD'. Use 'create_fields_permissions' method."
            )
        permissions_list = []
        action_values = actions_to_list(
            Action.ADD, Action.VIEW, Action.CHANGE, Action.DELETE
        )
        for action_value in action_values:
            permissions_list.append(
                tuple(
                    (
                        f"{permission_type.value}_{action_value}_{model_name}",
                        (
                            PERMISSION_SUBTYPES_LABELS[permission_type](
                                action_value, model_name
                            )
                            if description is None
                            else f"Can {action_value} {model_name} {description}"
                        ),
                    )
                )
            )
        return permissions_list

    @staticmethod
    def create_fields_permissions(model) -> list:
        if PermissionSubType.FIELD not in PERMISSION_SUBTYPES_LABELS.keys():
            assert KeyError(
                "Key 'PermissionType.FIELD' doesn't exist in PERMISSION_TYPES_LABELS"
            )
        model_name = model.__name__
        fields = [field.name for field in model._meta.get_fields()]
        permissions_list = []
        action_values = actions_to_list(Action.VIEW, Action.CHANGE)
        for action_value in action_values:
            for field in fields:
                permissions_list.append(
                    tuple(
                        (
                            f"fields_{field}_{action_value}_{model_name.lower()}",
                            PERMISSION_SUBTYPES_LABELS[PermissionSubType.FIELD](
                                action_value, model_name, field
                            ),
                        )
                    )
                )
        return permissions_list

    @staticmethod
    def add_rule_to_permission(
            app_name: str, codename: str, description: str, rule: callable
    ):
        rules.add_rule(
            f"{app_name}.{codename}",
            rule,
        )
        return (codename, description)

    @staticmethod
    def add_rules_to_permissions(
            app_name: str,
            codenames_with_descriptions: list[tuple[str, str]],
            rules_to_assign: list[callable],
    ) -> list[tuple[str, str]]:

        if (
                len(rules_to_assign) != len(codenames_with_descriptions)
                and len(rules_to_assign) != 1
        ):
            raise ValueError(
                "Count of rules and permissions must be the same or rules must be 1"
            )
        permissions_list = []
        for i, (codename, description) in enumerate(codenames_with_descriptions):
            if len(rules_to_assign) == 1:
                rule = rules_to_assign[0]
            else:
                rule = rules_to_assign[i]
            permissions_list.append(
                PermissionCreationService.add_rule_to_permission(
                    app_name, codename, description, rule
                )
            )
        return permissions_list

    @staticmethod
    def add_permissions_to_permissions_groups(
            group_permissions: dict[str, list[dict[str, Any]]],
    ):
        """
        Method to add permissions to groups.
        This method should be called after creating permissions.

        Args:
        group_permissions (dict): A dictionary where keys are role names (str) and values are lists of dictionaries.
                      Each dictionary must contain:
                      - "model": A model class (e.g., Product).
                      - "codenames": A list of permission codenames (list[str]).
        """
        from django.contrib.auth.models import Group

        # Validation of group_permissions structure should be done.
        for group_name, permissions_list in group_permissions.items():
            group, _ = Group.objects.get_or_create(name=group_name)

            for perm_info in permissions_list:
                content_type = ContentType.objects.get_for_model(perm_info["model"])
                for codename in perm_info["codenames"]:
                    permission = Permission.objects.get(
                        codename=codename, content_type=content_type
                    )
                    group.permissions.add(permission)
