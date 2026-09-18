from django.test import TestCase

from .models import DormitoryRule


class RuleModelTests(TestCase):
    def test_rule_label(self):
        rule = DormitoryRule.objects.create(code="TEST", title="Test rule", category="Test", description="Description")
        self.assertEqual(str(rule), "TEST - Test rule")
