# 모델 설치
from app.models import Cos
# django_filters 설치
from django_filters import rest_framework as filters
from rest_framework.filters import BaseFilterBackend
from app.models import Cos

class CosFilter(filters.FilterSet):
    class Meta:
        model = Cos
        fields = ['id', 'brand', 'image', 'price', 'prdname', 'ingredient']

# class cos_list_filters(BaseFilterBackend):
#     def filter_queryset(self, request, queryset, view):
#         params_dict = {}
#         for i in request.query_params.lists():
#             params_dict[i[0]] = i[1][0]
#         return queryset.filter(**params_dict)
