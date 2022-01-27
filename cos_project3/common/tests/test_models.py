from django.test import TestCase
from common.models import User, Qa, QaReple

class UserModelTestCase(TestCase):
    def setUp(self):
        User.objects.create_user(username="modeltest",
                                 password="modeltest123",
                                 email="modeltest@test.com",
                                 birth="2002-02-02",
                                 sex="M"
                                 )
