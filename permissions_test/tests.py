from django.contrib.auth.models import User, Group
from django.test import TestCase

from permissions.constants import Action
from permissions.models import OrganizationalUnit, UserGroup
from permissions.services import PermissionCreationService, PermissionService
from permissions_test.models import Product
from permissions_test.seed import seed_users, seed_user_groups, seed_groups, seed_products, seed_organizational_units


# Create your tests here.

class UserPermissionTest(TestCase):
    def setUp(self):
        self.setUpUsers()
        self.setUpGroups()
        self.setUpOrganizationalUnits()
        self.setUpUsersGroups()
        self.setUpProducts()
        self.setUpPermissionServices()

    def test_regular_model_permissions(self):
        # View
        self.assertTrue(self.admin_perm_service.has_perm_to_action(Product, Action.VIEW))
        self.assertTrue(self.maciek_perm_service.has_perm_to_action(Product, Action.VIEW))
        self.assertTrue(self.franek_perm_service.has_perm_to_action(Product, Action.VIEW))
        self.assertTrue(self.janek_perm_service.has_perm_to_action(Product, Action.VIEW))

        # Change
        self.assertTrue(self.admin_perm_service.has_perm_to_action(Product, Action.CHANGE))
        self.assertTrue(self.maciek_perm_service.has_perm_to_action(Product, Action.CHANGE))
        self.assertTrue(self.janek_perm_service.has_perm_to_action(Product, Action.CHANGE))
        self.assertFalse(self.franek_perm_service.has_perm_to_action(Product, Action.CHANGE))

        # Delete
        self.assertTrue(self.admin_perm_service.has_perm_to_action(Product, Action.DELETE))
        self.assertTrue(self.maciek_perm_service.has_perm_to_action(Product, Action.DELETE))
        self.assertFalse(self.janek_perm_service.has_perm_to_action(Product, Action.DELETE))
        self.assertFalse(self.franek_perm_service.has_perm_to_action(Product, Action.DELETE))

        # Add
        self.assertTrue(self.admin_perm_service.has_perm_to_action(Product, Action.ADD))
        self.assertFalse(self.maciek_perm_service.has_perm_to_action(Product, Action.ADD))
        self.assertFalse(self.janek_perm_service.has_perm_to_action(Product, Action.ADD))
        self.assertFalse(self.franek_perm_service.has_perm_to_action(Product, Action.ADD))

    def test_regular_object_permissions(self):
        pass

    def test_olp_object_permissions(self):
        pass

    def setUpUsers(self):
        self.teacher_janek = User.objects.create_user(
            username="t_janek", email="janek@example.com", password="admin", is_staff=True
        )
        self.teacher_franek = User.objects.create_user(
            username="t_franek", email="franek@example.com", password="admin", is_staff=True
        )
        self.teacher_piotrek = User.objects.create_user(
            username="t_piotrek",
            email="piotrek@example.com",
            password="admin",
            is_staff=True,
        )
        self.adm_maciek = User.objects.create_user(
            username="adm_maciek",
            email="maciek@example.com",
            password="admin",
            is_staff=True,
        )
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="admin",
            is_staff=True,
            is_superuser=True,
        )

    def setUpOrganizationalUnits(self):
        self.root_ou = OrganizationalUnit.objects.create(
            name="Root Unit",
            type="ROOT",
        )

        self.pb_ou = OrganizationalUnit.objects.create(
            name="Bialystok University of Technology",
            parent=self.root_ou,
            type="UNIVERSITY",
        )

        self.it_faculty_ou = OrganizationalUnit.objects.create(
            name="IT Faculty",
            parent=self.pb_ou,
            type="FACULTY",
        )

        self.mech_faculty_ou = OrganizationalUnit.objects.create(
            name="Mechanical Faculty",
            parent=self.pb_ou,
            type="FACULTY",
        )
        self.it_cathedral_ou = OrganizationalUnit.objects.create(
            name="IT Cathedral",
            parent=self.it_faculty_ou,
            type="CATHEDRAL",
        )
        self.math_cathedral_ou = OrganizationalUnit.objects.create(
            name="Math Cathedral",
            parent=self.it_faculty_ou,
            type="CATHEDRAL",
        )
        self.mech_cathedral_ou = OrganizationalUnit.objects.create(
            name="Mechanical Cathedral",
            parent=self.mech_faculty_ou,
            type="CATHEDRAL",
        )
        self.physics_cathedral_ou = OrganizationalUnit.objects.create(
            name="Physics Cathedral",
            parent=self.mech_faculty_ou,
            type="CATHEDRAL",
        )

        self.csharp_ou = OrganizationalUnit.objects.create(
            name="C#",
            parent=self.it_cathedral_ou,
            type="GROUP",
        )
        self.java_ou = OrganizationalUnit.objects.create(
            name="Java",
            parent=self.it_cathedral_ou,
            type="GROUP",
        )
        self.adm_and_man_it_ou = OrganizationalUnit.objects.create(
            name="Administration and Management of IT Systems",
            parent=self.it_cathedral_ou,
            type="GROUP",
        )
        self.linux_ou = OrganizationalUnit.objects.create(
            name="Linux Administration I",
            parent=self.adm_and_man_it_ou,
            type="GROUP",
        )

        self.linux_advanced_ou = OrganizationalUnit.objects.create(
            name="Linux Administration II",
            parent=self.adm_and_man_it_ou,
            type="GROUP",
        )
        self.math_analysis_ou = OrganizationalUnit.objects.create(
            name="Mathematical Analysis",
            parent=self.math_cathedral_ou,
            type="GROUP",
        )
        self.math_algebra_ou = OrganizationalUnit.objects.create(
            name="Linear Algebra",
            parent=self.math_cathedral_ou,
            type="GROUP",
        )
        self.mechanics_ou = OrganizationalUnit.objects.create(
            name="Mechanics",
            parent=self.mech_cathedral_ou,
            type="GROUP",
        )
        self.physics_ou = OrganizationalUnit.objects.create(
            name="Physics",
            parent=self.physics_cathedral_ou,
            type="GROUP",
        )

    def setUpGroups(self):
        self.group_permissions = {
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
        PermissionCreationService.add_permissions_to_permissions_groups(self.group_permissions)
        self.leading_teacher_group = Group.objects.get(name="Leading teacher")
        self.teacher_group = Group.objects.get(name="Teacher")
        self.mesh_administrator_group = Group.objects.get(name="Mesh administrator")

    def setUpUsersGroups(self):
        self.csharp_user_group = UserGroup.objects.create()
        self.csharp_user_group.users.set((self.teacher_janek,))
        self.csharp_user_group.organizational_units.set((self.csharp_ou, self.java_ou))
        self.csharp_user_group.permission_groups.set((self.leading_teacher_group,))

        self.it_cathedral_user_group = UserGroup.objects.create()
        self.it_cathedral_user_group.users.set(
            (
                self.teacher_franek,
                self.teacher_janek,
            )
        )
        self.it_cathedral_user_group.organizational_units.set((self.it_cathedral_ou,))
        self.it_cathedral_user_group.permission_groups.set((self.teacher_group,))

        self.it_faculty_user_group = UserGroup.objects.create()
        self.it_faculty_user_group.users.set((self.adm_maciek,))
        self.it_faculty_user_group.organizational_units.set((self.it_faculty_ou,))
        self.it_faculty_user_group.permission_groups.set((self.mesh_administrator_group,))

        self.physical_cathedral_user_group = UserGroup.objects.create()
        self.physical_cathedral_user_group.users.set((self.teacher_piotrek, self.teacher_janek))
        self.physical_cathedral_user_group.organizational_units.set((self.physics_ou,))
        self.physical_cathedral_user_group.permission_groups.set((self.teacher_group,))

    def setUpProducts(self):
        self.physics_product = Product.objects.create(parent=self.physics_ou, name="Physics", price=50.0)
        self.linux_product = Product.objects.create(parent=self.linux_ou, name="Linux Basics", price=50.0)
        self.linux_advanced_product = Product.objects.create(parent=self.linux_advanced_ou, name="Linux Advanced",
                                                             price=75.0)
        self.csharp_product = Product.objects.create(parent=self.csharp_ou, name="CSharp", price=100.0)
        self.java_product = Product.objects.create(parent=self.java_ou, name="Java", price=80.0,
                                                   owner=self.teacher_janek)

    def setUpPermissionServices(self):
        self.janek_perm_service = PermissionService(self.teacher_janek)
        self.franek_perm_service = PermissionService(self.teacher_franek)
        self.maciek_perm_service = PermissionService(self.adm_maciek)
        self.admin_perm_service = PermissionService(self.admin)
        self.piotrek_perm_service = PermissionService(self.teacher_piotrek)
