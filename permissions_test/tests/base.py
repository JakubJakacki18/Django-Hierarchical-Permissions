from django.contrib.auth.models import User, Group
from django.test import TestCase

from permissions.constants import Action
from permissions.models import OrganizationalUnit, UserGroup
from permissions.services import PermissionCreationService, PermissionService
from permissions_test.models import Product


class SharedTestData(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.setUpUsers()
        cls.setUpGroups()
        cls.setUpOrganizationalUnits()
        cls.setUpUsersGroups()
        cls.setUpProducts()
        cls.setUpPermissionServices()

    @classmethod
    def setUpUsers(cls):
        cls.teacher_janek = User.objects.create_user(
            username="t_janek", email="janek@example.com", password="admin", is_staff=True
        )
        cls.teacher_franek = User.objects.create_user(
            username="t_franek", email="franek@example.com", password="admin", is_staff=True
        )
        cls.teacher_piotrek = User.objects.create_user(
            username="t_piotrek",
            email="piotrek@example.com",
            password="admin",
            is_staff=True,
        )
        cls.adm_maciek = User.objects.create_user(
            username="adm_maciek",
            email="maciek@example.com",
            password="admin",
            is_staff=True,
        )
        cls.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="admin",
            is_staff=True,
            is_superuser=True,
        )

    @classmethod
    def setUpOrganizationalUnits(cls):
        cls.root_ou = OrganizationalUnit.objects.create(
            name="Root Unit",
            type="ROOT",
        )

        cls.pb_ou = OrganizationalUnit.objects.create(
            name="Bialystok University of Technology",
            parent=cls.root_ou,
            type="UNIVERSITY",
        )

        cls.it_faculty_ou = OrganizationalUnit.objects.create(
            name="IT Faculty",
            parent=cls.pb_ou,
            type="FACULTY",
        )

        cls.mech_faculty_ou = OrganizationalUnit.objects.create(
            name="Mechanical Faculty",
            parent=cls.pb_ou,
            type="FACULTY",
        )
        cls.it_cathedral_ou = OrganizationalUnit.objects.create(
            name="IT Cathedral",
            parent=cls.it_faculty_ou,
            type="CATHEDRAL",
        )
        cls.math_cathedral_ou = OrganizationalUnit.objects.create(
            name="Math Cathedral",
            parent=cls.it_faculty_ou,
            type="CATHEDRAL",
        )
        cls.mech_cathedral_ou = OrganizationalUnit.objects.create(
            name="Mechanical Cathedral",
            parent=cls.mech_faculty_ou,
            type="CATHEDRAL",
        )
        cls.physics_cathedral_ou = OrganizationalUnit.objects.create(
            name="Physics Cathedral",
            parent=cls.mech_faculty_ou,
            type="CATHEDRAL",
        )

        cls.csharp_ou = OrganizationalUnit.objects.create(
            name="C#",
            parent=cls.it_cathedral_ou,
            type="GROUP",
        )
        cls.java_ou = OrganizationalUnit.objects.create(
            name="Java",
            parent=cls.it_cathedral_ou,
            type="GROUP",
        )
        cls.adm_and_man_it_ou = OrganizationalUnit.objects.create(
            name="Administration and Management of IT Systems",
            parent=cls.it_cathedral_ou,
            type="GROUP",
        )
        cls.linux_ou = OrganizationalUnit.objects.create(
            name="Linux Administration I",
            parent=cls.adm_and_man_it_ou,
            type="GROUP",
        )

        cls.linux_advanced_ou = OrganizationalUnit.objects.create(
            name="Linux Administration II",
            parent=cls.adm_and_man_it_ou,
            type="GROUP",
        )
        cls.math_analysis_ou = OrganizationalUnit.objects.create(
            name="Mathematical Analysis",
            parent=cls.math_cathedral_ou,
            type="GROUP",
        )
        cls.math_algebra_ou = OrganizationalUnit.objects.create(
            name="Linear Algebra",
            parent=cls.math_cathedral_ou,
            type="GROUP",
        )
        cls.mechanics_ou = OrganizationalUnit.objects.create(
            name="Mechanics",
            parent=cls.mech_cathedral_ou,
            type="GROUP",
        )
        cls.physics_ou = OrganizationalUnit.objects.create(
            name="Physics",
            parent=cls.physics_cathedral_ou,
            type="GROUP",
        )

    @classmethod
    def setUpGroups(cls):
        cls.group_permissions = {
            "Teacher": [
                {"model": Product, "codenames": ["view_product"]},
            ],
            "Leading teacher": [
                {"model": Product, "codenames": ["view_product", "change_product", "owner_delete_product"]},
            ],
            "Mesh administrator": [
                {
                    "model": Product,
                    "codenames": ["view_product", "change_product", "delete_product"],
                },
            ],
        }
        PermissionCreationService.add_permissions_to_permissions_groups(cls.group_permissions)
        cls.leading_teacher_group = Group.objects.get(name="Leading teacher")
        cls.teacher_group = Group.objects.get(name="Teacher")
        cls.mesh_administrator_group = Group.objects.get(name="Mesh administrator")

    @classmethod
    def setUpUsersGroups(cls):
        cls.csharp_user_group = UserGroup.objects.create()
        cls.csharp_user_group.users.set((cls.teacher_janek,))
        cls.csharp_user_group.organizational_units.set((cls.csharp_ou, cls.java_ou))
        cls.csharp_user_group.permission_groups.set((cls.leading_teacher_group,))

        cls.it_cathedral_user_group = UserGroup.objects.create()
        cls.it_cathedral_user_group.users.set(
            (
                cls.teacher_franek,
                cls.teacher_janek,
            )
        )
        cls.it_cathedral_user_group.organizational_units.set((cls.it_cathedral_ou,))
        cls.it_cathedral_user_group.permission_groups.set((cls.teacher_group,))

        cls.it_faculty_user_group = UserGroup.objects.create()
        cls.it_faculty_user_group.users.set((cls.adm_maciek,))
        cls.it_faculty_user_group.organizational_units.set((cls.it_faculty_ou,))
        cls.it_faculty_user_group.permission_groups.set((cls.mesh_administrator_group,))

        cls.physical_cathedral_user_group = UserGroup.objects.create()
        cls.physical_cathedral_user_group.users.set((cls.teacher_piotrek, cls.teacher_janek))
        cls.physical_cathedral_user_group.organizational_units.set((cls.physics_ou,))
        cls.physical_cathedral_user_group.permission_groups.set((cls.teacher_group,))

    @classmethod
    def setUpProducts(cls):
        cls.physics_product = Product.objects.create(parent=cls.physics_ou, name="Physics", price=50.0)
        cls.linux_product = Product.objects.create(parent=cls.linux_ou, name="Linux Basics", price=50.0)
        cls.linux_advanced_product = Product.objects.create(parent=cls.linux_advanced_ou, name="Linux Advanced",
                                                            price=75.0)
        cls.csharp_product = Product.objects.create(parent=cls.csharp_ou, name="CSharp", price=100.0)
        cls.java_product = Product.objects.create(parent=cls.java_ou, name="Java", price=80.0,
                                                  owner=cls.teacher_janek)

    @classmethod
    def setUpPermissionServices(cls):
        cls.janek_perm_service = PermissionService(cls.teacher_janek)
        cls.franek_perm_service = PermissionService(cls.teacher_franek)
        cls.maciek_perm_service = PermissionService(cls.adm_maciek)
        cls.admin_perm_service = PermissionService(cls.admin)
        cls.piotrek_perm_service = PermissionService(cls.teacher_piotrek)
