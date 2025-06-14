from django.db import models
from permissions.constants import PERMISSION_DIVIDER_BY_TYPES, Action


def permission_extractor(self, *permissions_in_fun_or_args):
    permission = ()
    for perm in permissions_in_fun_or_args:
        if callable(perm):
            permission += perm(self)
        else:
            permission += (perm,)
    return permission


def args_extractor(*args):
    obj = None
    if len(args) == 2:
        self, request = args
    elif len(args) == 3:
        self, request, obj = args
    else:
        raise TypeError("Count of arguments must be 2 or 3")
    return self, request, obj


def permissions_divider(*permissions) -> dict[str, list]:
    if "regular" not in PERMISSION_DIVIDER_BY_TYPES.keys():
        raise KeyError(f"Key 'regular' doesn't exist in PERMISSION_DIVIDER_BY_TYPES.")
    permissions_dict = {key: [] for key in PERMISSION_DIVIDER_BY_TYPES}
    for permission in permissions:
        prefix = get_prefix_from_permission(permission)
        key = next(
            (
                key
                for key, permission_types_list in PERMISSION_DIVIDER_BY_TYPES.items()
                if any(
                    permission_type.value == prefix
                    for permission_type in permission_types_list
                )
            ),
            None,
        )
        if key is not None:
            permissions_dict[key].append(permission)
            continue
        permissions_dict["regular"].append(permission)
    return permissions_dict


def actions_to_list(*actions: Action) -> list[str]:
    actions_list = []
    for action in actions:
        actions_list.append(action.value)
    return actions_list


def get_prefix_from_permission(permission: str):
    if len(permission.split(".")) != 2:
        raise ValueError("Permission have to start with app name")
    permission_codename = permission.split(".")[1]
    return permission_codename.split("_")[0]


def get_model(model_or_obj):
    if isinstance(model_or_obj, models.Model):
        return model_or_obj.__class__
    else:
        return model_or_obj
