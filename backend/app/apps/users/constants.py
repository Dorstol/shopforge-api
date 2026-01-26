from enum import StrEnum


class UserPermissionsEnum(StrEnum):
    CAN_SEE_USERS = "CAN_SEE_USERS"
    CAN_SELF_DELETE = "CAN_SELF_DELETE"
    CAN_CREATE_CATEGORY = "CAN_CREATE_CATEGORY"
