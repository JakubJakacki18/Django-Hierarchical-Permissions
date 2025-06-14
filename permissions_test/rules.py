import rules


@rules.predicate
def is_owner(user, obj):
    return obj.owner == user
