from django.urls import reverse
from wps.models import WaterUseSector
from rest_framework import status
from rest_framework.test import APITestCase
from user.models import User
from .setup import TEST_GEOM


class WaterUseSectorTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            username="test-user",
            email="test@example.com",
            first_name="Test",
            last_name="User"
        )
        self.obj = WaterUseSector.objects.create(name='sector01', geom=TEST_GEOM)

    def test_water_use_sector_list_forbidden(self):
        url = reverse("water-use-sectors")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_water_use_sector_list_success(self):
        self.client.force_authenticate(self.user)
        url = reverse("water-use-sectors")
        response = self.client.get(url, format="json")
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data["results"]), 1)
