from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Feat, Class


class FeatCreateTests(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pw")

    def test_login_required(self) -> None:
        response = self.client.get(reverse("core:feat_create"))
        self.assertEqual(response.status_code, 302)

    def test_create_feat_minimal(self) -> None:
        self.client.login(username="tester", password="pw")
        response = self.client.post(
            reverse("core:feat_create"),
            {"name": "Alert", "description": "Always on guard"},
        )
        self.assertEqual(response.status_code, 302)
        feat = Feat.objects.get(name="Alert")
        self.assertEqual(feat.description, "Always on guard")
        self.assertEqual(feat.data, {})

    def test_create_feat_with_options(self) -> None:
        self.client.login(username="tester", password="pw")
        prereq_class = Class.objects.create(name="Wizard")
        existing = Feat.objects.create(name="Existing", description="desc")
        payload = {
            "name": "Magic Adept",
            "description": "desc",
            "prerequisite_class": prereq_class.id,
            "prerequisite_class_level": 3,
            "charges": 2,
            "recharge_type": "long rest",
            "grants": f"[{{\"model\": \"feat\", \"id\": {existing.id}}}]",
        }
        response = self.client.post(reverse("core:feat_create"), payload)
        self.assertEqual(response.status_code, 302)
        feat = Feat.objects.get(name="Magic Adept")
        self.assertEqual(
            feat.data.get("prerequisites", {}).get("class"), prereq_class.id
        )
        self.assertEqual(
            feat.data.get("prerequisites", {}).get("class_level"), 3
        )
        self.assertEqual(feat.data.get("charges"), 2)
        self.assertEqual(feat.data.get("recharge_type"), "long rest")
        self.assertEqual(feat.data.get("grants"), [{"model": "feat", "id": existing.id}])
