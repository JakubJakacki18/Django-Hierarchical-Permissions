from enum import Enum


class PermissionSubType(str, Enum):
    SCOPED = "scoped"
    ALL_FIELDS = "fields"
    FIELD = "field"


PERMISSION_SUBTYPES_LABELS = {
    PermissionSubType.SCOPED: lambda action_value, model_name: f"Can {action_value} {model_name} only when user is in scope of organizational unit",
    PermissionSubType.ALL_FIELDS: lambda action_value, model_name: f"Can {action_value} all fields in {model_name}",
    PermissionSubType.FIELD: lambda action_value, model_name, field: f"Can {action_value} {field} from {model_name} model",
}

PERMISSION_DIVIDER_BY_TYPES = {
    "olp": [
        PermissionSubType.SCOPED,
        PermissionSubType.ALL_FIELDS,
        PermissionSubType.FIELD,
    ],
    "regular": [],
    "hardcoded": [],
}


# Possible actions
class Action(str, Enum):
    ADD = "add"
    CHANGE = "change"
    VIEW = "view"
    DELETE = "delete"
