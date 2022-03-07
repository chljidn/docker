from rest_framework.pagination import PageNumberPagination

class QaPagination(PageNumberPagination):
    page_size = 15