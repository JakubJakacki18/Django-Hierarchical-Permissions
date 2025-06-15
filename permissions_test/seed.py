from django.core.exceptions import ObjectDoesNotExist
from rules import is_staff, is_superuser

from permissions.services import PermissionCreationService
from .models import *
from django.contrib.auth.models import Group, Permission
from permissions.models import UserGroup, OrganizationalUnit, BaseModel

priority = 100


def run():
    seed_groups()
    seed_organizational_units()
    seed_users()
    seed_user_groups()
    seed_products()


def seed_users():
    User.objects.create_user(
        username="t_janek", email="janek@example.com", password="admin", is_staff=True
    )
    User.objects.create_user(
        username="t_franek", email="franek@example.com", password="admin", is_staff=True
    )
    User.objects.create_user(
        username="t_piotrek",
        email="piotrek@example.com",
        password="admin",
        is_staff=True,
    )
    User.objects.create_user(
        username="adm_maciek",
        email="maciek@example.com",
        password="admin",
        is_staff=True,
    )
    User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="admin",
        is_staff=True,
        is_superuser=True,
    )


def seed_organizational_units():
    root = OrganizationalUnit.objects.create(
        name="Root Unit",
        type="ROOT",
    )

    pb = OrganizationalUnit.objects.create(
        name="Bialystok University of Technology",
        parent=root,
        type="UNIVERSITY",
    )

    it_faculty = OrganizationalUnit.objects.create(
        name="IT Faculty",
        parent=pb,
        type="FACULTY",
    )

    mech_faculty = OrganizationalUnit.objects.create(
        name="Mechanical Faculty",
        parent=pb,
        type="FACULTY",
    )
    it_cathedral = OrganizationalUnit.objects.create(
        name="IT Cathedral",
        parent=it_faculty,
        type="CATHEDRAL",
    )
    math_cathedral = OrganizationalUnit.objects.create(
        name="Math Cathedral",
        parent=it_faculty,
        type="CATHEDRAL",
    )
    mech_cathedral = OrganizationalUnit.objects.create(
        name="Mechanical Cathedral",
        parent=mech_faculty,
        type="CATHEDRAL",
    )
    physics_cathedral = OrganizationalUnit.objects.create(
        name="Physics Cathedral",
        parent=mech_faculty,
        type="CATHEDRAL",
    )

    OrganizationalUnit.objects.create(
        name="C#",
        parent=it_cathedral,
        type="GROUP",
    )
    OrganizationalUnit.objects.create(
        name="Java",
        parent=it_cathedral,
        type="GROUP",
    )
    adm_and_man_it = OrganizationalUnit.objects.create(
        name="Administration and Management of IT Systems",
        parent=it_cathedral,
        type="GROUP",
    )
    OrganizationalUnit.objects.create(
        name="Linux Administration I",
        parent=adm_and_man_it,
        type="GROUP",
    )

    OrganizationalUnit.objects.create(
        name="Linux Administration II",
        parent=adm_and_man_it,
        type="GROUP",
    )
    OrganizationalUnit.objects.create(
        name="Mathematical Analysis",
        parent=math_cathedral,
        type="GROUP",
    )
    OrganizationalUnit.objects.create(
        name="Linear Algebra",
        parent=math_cathedral,
        type="GROUP",
    )
    OrganizationalUnit.objects.create(
        name="Mechanics",
        parent=mech_cathedral,
        type="GROUP",
    )
    OrganizationalUnit.objects.create(
        name="Physics",
        parent=physics_cathedral,
        type="GROUP",
    )


def seed_products():
    try:
        t_janek = User.objects.get(username="t_janek")
        csharp_ou = OrganizationalUnit.objects.get(name="C#")
        linux_ou = OrganizationalUnit.objects.get(name="Linux Administration I")
        linux_advanced_ou = OrganizationalUnit.objects.get(name="Linux Administration II")
        physics_ou = OrganizationalUnit.objects.get(name="Physics")
        java_ou = OrganizationalUnit.objects.get(name="Java")
    except ObjectDoesNotExist:
        print("⚠️ No organizational units found.")
        return
    Product.objects.create(parent=physics_ou, name="Physics", price=50.0)
    Product.objects.create(parent=linux_ou, name="Linux Basics", price=50.0)
    Product.objects.create(parent=linux_advanced_ou, name="Linux Advanced", price=75.0)
    Product.objects.create(parent=csharp_ou, name="CSharp", price=100.0)
    Product.objects.create(parent=java_ou, name="Java", price=80.0, owner=t_janek)


def seed_groups():
    group_permissions = {
        "Teacher": [
            {"model": Product, "codenames": ["view_product", "field_name_view_product"]},
        ],
        "Leading teacher": [
            {"model": Product,
             "codenames": ["view_product", "change_product", "owner_delete_product", "field_owner_view_product",
                           "field_name_change_product"]},
        ],
        "Mesh administrator": [
            {
                "model": Product,
                "codenames": ["view_product", "change_product", "delete_product", "field_id_view_product"],
            },
        ],
    }
    PermissionCreationService.add_permissions_to_permissions_groups(group_permissions)


def seed_user_groups():
    try:
        leading_teacher_group = Group.objects.get(name="Leading teacher")
        teacher_group = Group.objects.get(name="Teacher")
        mesh_administrator_group = Group.objects.get(name="Mesh administrator")

        teacher_janek = User.objects.get(username="t_janek")
        teacher_piotrek = User.objects.get(username="t_piotrek")
        teacher_franek = User.objects.get(username="t_franek")
        adm_maciek = User.objects.get(username="adm_maciek")

        csharp_ou = OrganizationalUnit.objects.get(name="C#")
        java_ou = OrganizationalUnit.objects.get(name="Java")
        it_cathedral_ou = OrganizationalUnit.objects.get(name="IT Cathedral")
        it_faculty_ou = OrganizationalUnit.objects.get(name="IT Faculty")
        physics_ou = OrganizationalUnit.objects.get(name="Physics")
    except ObjectDoesNotExist:
        print("⚠️ Something was not found")
        return
    csharp_user_group = UserGroup.objects.create()
    csharp_user_group.users.set((teacher_janek,))
    csharp_user_group.organizational_units.set((csharp_ou, java_ou))
    csharp_user_group.permission_groups.set((leading_teacher_group,))

    it_cathedral_user_group = UserGroup.objects.create()
    it_cathedral_user_group.users.set(
        (
            teacher_franek,
            teacher_janek,
        )
    )
    it_cathedral_user_group.organizational_units.set((it_cathedral_ou,))
    it_cathedral_user_group.permission_groups.set((teacher_group,))

    it_faculty_user_group = UserGroup.objects.create()
    it_faculty_user_group.users.set((adm_maciek,))
    it_faculty_user_group.organizational_units.set((it_faculty_ou,))
    it_faculty_user_group.permission_groups.set((mesh_administrator_group,))

    physical_cathedral_user_group = UserGroup.objects.create()
    physical_cathedral_user_group.users.set((teacher_piotrek, teacher_janek))
    physical_cathedral_user_group.organizational_units.set((physics_ou,))
    physical_cathedral_user_group.permission_groups.set((teacher_group,))
