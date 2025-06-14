import rules
from datetime import date


@rules.predicate
def is_owner(user, obj):
    return obj.owner == user


@rules.predicate
def is_weekend():
    return date.today().weekday() in (5, 6)


rules.add_perm("permissions_test.isWeekend", is_weekend)
