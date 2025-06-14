from django.contrib.auth.models import Group, User
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


# Create your models here.
class OrganizationalUnit(MPTTModel):
    name = models.CharField(max_length=100)
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    type = models.CharField(
        max_length=20,
        choices=[
            ("ROOT", "Root"),
            ("UNIVERSITY", "University"),
            ("FACULTY", "Faculty"),
            ("CATHEDRAL", "Cathedral"),
            ("GROUP", "Group"),
        ],
    )

    class MPTTMeta:
        order_insertion_by = ["name"]

    def __str__(self):
        return f"{self.name} ({self.type})"


class UserGroup(models.Model):
    organizational_units = models.ManyToManyField(
        OrganizationalUnit, related_name="user_groups"
    )
    users = models.ManyToManyField(User, related_name="user_groups")
    permission_groups = models.ManyToManyField(
        Group, related_name="user_groups"
    )


class BaseModel(models.Model):
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    class Meta:
        abstract = True
