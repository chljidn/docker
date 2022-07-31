from rest_framework import serializers
from app.models import ImageUpload, Cos, CosReviewModel, recommend_excel

class ImageUploadSerializer(serializers.ModelSerializer):
    pic = serializers.ImageField(use_url=True)
    class Meta:
        model = ImageUpload
        fields = ('title','pic')

class CosReviewSerializer(serializers.ModelSerializer):
    reviewCos = serializers.StringRelatedField()
    reviewUser = serializers.StringRelatedField()
    class Meta:
        model = CosReviewModel
        fields = ('id', 'reviewName', 'reviewImage', 'reviewContent', 'reviewUser', 'reviewCos')

class CosSerializer(serializers.ModelSerializer):
    cosreviewmodel_set = CosReviewSerializer(read_only=True, many=True)
    class Meta:
        model = Cos
        fields = ('id', 'brand', 'image', 'ingredient', 'prdname', 'price', 'category', 'like', 'cosreviewmodel_set')

class RecommendSerializer(serializers.Serializer):
    prdname = serializers.CharField()
    ingredient = serializers.CharField()
    image = serializers.CharField()
    brand = serializers.CharField()
    price = serializers.CharField()
    cosine = serializers.FloatField()

class recommend_excel_serializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d")
    class Meta:
        model = recommend_excel
        fields = "__all__"