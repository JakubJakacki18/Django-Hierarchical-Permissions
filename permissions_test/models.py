from django.contrib.auth.models import User
from django.db import models

from permissions.models import OrganizationalUnit, BaseModel


# Create your models here.
class Product(BaseModel):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "products"
        permissions = []
