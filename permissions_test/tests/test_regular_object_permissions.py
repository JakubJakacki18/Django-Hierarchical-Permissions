from permissions.constants import Action
from permissions_test.models import Product
from permissions_test.tests.base import SharedTestData


class RegularObjectPermissionsTests(SharedTestData):
    def setUp(self):
        super().setUp()
        self.users = [
            self.admin_perm_service,
            self.maciek_perm_service,
            self.franek_perm_service,
            self.janek_perm_service,
        ]

    def test_view_regular_object_permissions(self):
        # csharp
        self.assertFunction(Product, Action.VIEW, self.csharp_product, self.users, [True, True, True, True])

        # linux
        self.assertFunction(Product, Action.VIEW, self.linux_product, self.users, [True, True, True, True])

        # physics
        self.assertFunction(Product, Action.VIEW, self.physics_product, self.users, [True, False, False, True])

    def test_change_regular_object_permissions(self):
        # csharp
        self.assertFunction(Product, Action.CHANGE, self.csharp_product, self.users, [True, True, False, True])

        # linux
        self.assertFunction(Product, Action.CHANGE, self.linux_product, self.users, [True, True, False, False])

        # physics
        self.assertFunction(Product, Action.CHANGE, self.physics_product, self.users, [True, False, False, False])

    def test_delete_regular_object_permissions(self):
        # csharp
        self.assertFunction(Product, Action.DELETE, self.csharp_product, self.users, [True, True, False, False])

        # linux
        self.assertFunction(Product, Action.DELETE, self.linux_product, self.users, [True, True, False, False])

        # physics
        self.assertFunction(Product, Action.DELETE, self.physics_product, self.users, [True, False, False, False])

    def assertFunction(self, model, action, obj, users, truth_array):
        for user, truth_value in zip(users, truth_array):
            self.assertTrue(user.has_perm_to_action(model, action, obj)) if truth_value else self.assertFalse(
                user.has_perm_to_action(model, action, obj))
