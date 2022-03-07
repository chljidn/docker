from rest_framework.test import APITestCase, APIRequestFactory
from common.models import User
from common.serializers import UserSerializers

class user_serializer_test(APITestCase):
    def setUp(self):
        user = User.objects.create_user(username='test_serializer', password='userpasswd', email='user@test.com',
                                        birth='2021-09-09', sex='M')
        staff = User.objects.create_superuser(username='staff_serializer', password='staffpasswd', email='staff@test.com',
                                        birth='2021-09-09', sex='M')

    def test_user_serializer(self):
        user = User.objects.get(username="test_serializer")
        serializer = UserSerializers(user)
        data = serializer.data
        # username, email, birth, sex, like(related), cosreviewmodel_set(related) => 6
        self.assertEqual(len(data), 6)

        user = User.objects.all()
        serializer = UserSerializers(user, many=True)
        # queryset object => test_serializer, staff_serializer = 2
        self.assertEqual(len(serializer.data), 2)

class qa_serializer_test(APITestCase):

    def setUp(self):
        pass

    def test_qa_serializer(self):
        pass


