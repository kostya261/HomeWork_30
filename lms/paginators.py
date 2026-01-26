from rest_framework.pagination import PageNumberPagination


class LessonPaginator(PageNumberPagination):
    """
    Пагинатор для уроков.
    """
    page_size = 10  # Количество элементов на странице по умолчанию
    page_size_query_param = 'page_size'  # Параметр для указания количества элементов на странице
    max_page_size = 50  # Максимальное количество элементов на странице


class CursePaginator(PageNumberPagination):
    """
    Пагинатор для курсов.
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 30
