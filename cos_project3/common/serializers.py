import rest_framework.exceptions
from common.models import User, Qa
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import make_password
from app.models import Cos, recommend_excel
from common.models import QaReple
from app.serializers import CosReviewSerializer, recommend_excel_serializer

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


class UserSerializer(serializers.ModelSerializer):
    like = LikeSerializer(read_only = True, many=True)
    cosreviewmodel_set = CosReviewSerializer(read_only=True, many=True)
    recommend_excel_set = serializers.StringRelatedField(many=True)
    # recommend_excel_set = recommend_excel_serializer(read_only=True, many=True)

    class Meta:
        model=User
        fields = ('id','username', 'sex', 'birth', 'email', 'like', 'cosreviewmodel_set', 'recommend_excel_set')


class QaRepleSerializer(serializers.ModelSerializer):
    repleUser = serializers.StringRelatedField()
    class Meta:
        model= QaReple
        fields = '__all__'


class QaSerializers(serializers.ModelSerializer):
    # StringRelateField로 설정하면 username만 가져온다
    # 즉 User 모델에서 def __str__ 로 설정한 필드값만 직렬화에 포함된다.
    qa_user = serializers.StringRelatedField()
    qareple_set = QaRepleSerializer(read_only=True, many=True)
    qaDate = serializers.DateTimeField(format="%Y-%m-%d")

    class Meta:
        model = Qa
        fields = ('id', 'postname', 'content', 'qa_user', 'qaDate', 'qareple_set')

    # def validate(self, attrs):
    #     data = super().validate(attrs)
    #     # 요청받은 패스워드를 암호화(해쉬)
    #     data['password'] = make_password(data['password'])
    #     return data


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['id'] = self.user.id
        return data
