import rest_framework.exceptions
from common.models import User, Qa
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import make_password
from app.models import Cos, recommend_excel
from common.models import QaReple
from app.serializers import CosReviewSerializer, recommend_excel_serializer
from django.utils import timezone
from rest_framework.fields import empty

# cos 모델은 common의 CosSerializer와 app의 LikeSerializer. 총 두 개의 serializer를 갖는다.
# id와 prdname만 직력화하기 위해서 작성.
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cos
        fields = ('id', 'prdname', 'brand')


class SignUpSerializer(serializers.ModelSerializer):
    def save(self):
        user = User.objects.create_user(**self.validated_data)
        return user
    class Meta:
        model=User
        fields = ('username', 'sex', 'birth', 'email', 'password')

4
class QaRepleSerializer(serializers.ModelSerializer):
    repleUser = serializers.StringRelatedField()
    class Meta:
        model= QaReple
        fields = '__all__'


class QaSerializers(serializers.ModelSerializer):
    # StringRelateField로 설정하면 username만 가져온다
    # 즉 User 모델에서 def __str__ 로 설정한 필드값만 직렬화에 포함된다.
    qa_user = serializers.StringRelatedField()
    password = serializers.CharField(write_only=True, allow_null=True)
    qareple_set = QaRepleSerializer(read_only=True, many=True)
    qaDate = serializers.DateTimeField(default=timezone.now, format="%Y-%m-%d")

    class Meta:
        model = Qa
        fields = ('id', 'postname', 'content', 'password', 'qa_user', 'qaDate', 'qareple_set')

    def validate(self, attrs):
        if attrs.get("password", None):
            attrs["password"] = make_password(attrs["password"])
        return attrs


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    like = LikeSerializer(read_only = True, many=True)
    cosreviewmodel_set = CosReviewSerializer(read_only=True, many=True)
    qa_set = QaSerializers(read_only=True, many=True)
    recommend_excel_set = serializers.StringRelatedField(many=True)

    def update(self, instance, validated_data):
        if validated_data.get("password", None):
            validated_data["password"] = make_password(validated_data["password"])
        return super().update(instance, validated_data)

    class Meta:
        model=User
        fields = ('id', 'password', 'username', 'sex', 'birth', 'email', 'like', 'cosreviewmodel_set', 'recommend_excel_set', 'qa_set')


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['id'] = self.user.id
        return data
