from rest_framework.pagination import PageNumberPagination


class CustomPaginator(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'


class LimitPageNumberPaginator(PageNumberPagination):
    page_size_query_param = 'limit'