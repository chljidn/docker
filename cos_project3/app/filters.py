# 모델 설치
from app.models import Cos

# django_filters 설치
from django_filters import rest_framework as filters

class CosFilter(filters.FilterSet):
    #min_id = filters.NumberFilter(field_name="id", lookup_expr='gte')
    #max_id = filters.NumberFilter(field_name="id", lookup_expr='lte')

    class Meta:
        model = Cos
        fields = ['id', 'brand', 'image', 'price', 'prdname', 'ingredient']