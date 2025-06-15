from permissions.constants import Action
from permissions_test.models import Product
from permissions_test.tests.base import SharedTestData


class RegularModelPermissionsTests(SharedTestData):
    def test_view_regular_model_permissions(self):
        self.assertTrue(self.admin_perm_service.has_perm_to_action(Product, Action.VIEW))
        self.assertTrue(self.maciek_perm_service.has_perm_to_action(Product, Action.VIEW))
        self.assertTrue(self.franek_perm_service.has_perm_to_action(Product, Action.VIEW))
        self.assertTrue(self.janek_perm_service.has_perm_to_action(Product, Action.VIEW))

    def test_change_regular_model_permissions(self):
        self.assertTrue(self.admin_perm_service.has_perm_to_action(Product, Action.CHANGE))
        self.assertTrue(self.maciek_perm_service.has_perm_to_action(Product, Action.CHANGE))
        self.assertTrue(self.janek_perm_service.has_perm_to_action(Product, Action.CHANGE))
        self.assertFalse(self.franek_perm_service.has_perm_to_action(Product, Action.CHANGE))

    def test_delete_regular_model_permissions(self):
        self.assertTrue(self.admin_perm_service.has_perm_to_action(Product, Action.DELETE))
        self.assertTrue(self.maciek_perm_service.has_perm_to_action(Product, Action.DELETE))
        self.assertFalse(self.janek_perm_service.has_perm_to_action(Product, Action.DELETE))
        self.assertFalse(self.franek_perm_service.has_perm_to_action(Product, Action.DELETE))

    def test_add_regular_model_permissions(self):
        self.assertTrue(self.admin_perm_service.has_perm_to_action(Product, Action.ADD))
        self.assertFalse(self.maciek_perm_service.has_perm_to_action(Product, Action.ADD))
        self.assertFalse(self.janek_perm_service.has_perm_to_action(Product, Action.ADD))
        self.assertFalse(self.franek_perm_service.has_perm_to_action(Product, Action.ADD))
