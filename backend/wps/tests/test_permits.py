from django.db.models import signals
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from user.models import User
from wps.models import NaceCode, Permit, WaterUseSector

from .setup import TEST_GEOM


class PermitTestCase(APITestCase):

    def setUp(self):
        self.nace = NaceCode.objects.create(code='A1', description='test')
        self.water_use_sector = WaterUseSector.objects.create(name='sector01', geom=TEST_GEOM)
        self.user01 = User.objects.create(
            username="test-user",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        self.user02 = User.objects.create(
            username="test-user2",
            email="test2@example.com",
            first_name="Test",
            last_name="User2"
        )
        self.obj = Permit.objects.create(
            submitted_by=self.user01,
            operator_name='Test',
            nace_code=self.nace,
            water_use_sector=self.water_use_sector,
            pdf='fake.pdf'
        )

        signals.post_save.receivers = []

    def test_unauthorized(self):
        url = reverse("permit-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_only_permits(self):
        url = reverse("permit-list")
        self.client.force_authenticate(self.user02)
        response = self.client.get(url, format="json")
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data["results"]), 0)

    def test_permit_validate_forbidden(self):
        url = reverse("permit-validate", kwargs={"uid": str(self.obj.uid)})
        self.client.force_authenticate(self.user01)
        data = {"status": "approved", "remark": "test", "send_email": False}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
