from django.core.paginator import Page, Paginator
from django.db.models.query import QuerySet
from django.http import HttpRequest


def paginate(
    request: HttpRequest,
    queryset: QuerySet,
    count: int = 10,
) -> Page:
    return Paginator(queryset, count).get_page(request.GET.get('page'))


def truncate(text: str, count: int = 10) -> str:
    return text[:count] + '...' if len(text) > count else text
