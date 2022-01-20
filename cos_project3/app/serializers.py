from rest_framework import serializers
from app.models import ImageUpload, Cos, CosReviewModel

class ImageUploadSerializer(serializers.ModelSerializer):
    pic = serializers.ImageField(use_url=True)
    class Meta:
        model = ImageUpload
        fields = ('title','pic')

class CosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cos
        fields = '__all__'

class RecommendSerializer(serializers.Serializer):
    prdname = serializers.CharField()
    ingredient = serializers.CharField()
    image = serializers.CharField()
    brand = serializers.CharField()
    price = serializers.CharField()
    cosine = serializers.CharField()

class CosReviewSerializer(serializers.Serializer):
    class Meta:
        model = CosReviewModel
        fields = ('reviewName', 'reviewImage', 'reviewContent', 'reviewUser', 'reviewCos')