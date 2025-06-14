from enum import Enum


class PermissionSubType(str, Enum):
    FIELD = "field"
    ALL_FIELDS = "fields"
    WEEKEND = "weekend"
    OWNER = "owner"


PERMISSION_SUBTYPES_LABELS = {
    PermissionSubType.WEEKEND: lambda action_value,
                                      model_name: f"Can {action_value} {model_name} only when it's weekend",
    PermissionSubType.FIELD: lambda action_value, model_name,
                                    field: f"Can {action_value} {field} field from {model_name} model",
    PermissionSubType.OWNER: lambda action_value,
                                    model_name: f"Can {action_value} {model_name} when user is assigned to owner field",
    PermissionSubType.ALL_FIELDS: lambda action_value, model_name: f"Can {action_value} all fields in {model_name}",
}

PERMISSION_DIVIDER_BY_TYPES = {
    "olp": [
        PermissionSubType.OWNER,
    ],
    "regular": [
        PermissionSubType.FIELD,
        PermissionSubType.ALL_FIELDS,
    ],
    "hardcoded": [
        PermissionSubType.WEEKEND,
    ],
}


# Possible actions
class Action(str, Enum):
    ADD = "add"
    CHANGE = "change"
    VIEW = "view"
    DELETE = "delete"
