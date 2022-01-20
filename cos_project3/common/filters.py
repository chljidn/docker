from common.models import Qa, User
from django_filters import rest_framework as filters

class QaFilter(filters.FilterSet):
    class Meta:
        model = Qa
        fields = ['id', 'postname', 'content']

class userFilter(filters.FilterSet):
    class Meta:
        model = User
        fields = '__all__'