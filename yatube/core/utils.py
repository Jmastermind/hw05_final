from django.conf import settings
from django.core.paginator import Page, Paginator
from django.db.models.query import QuerySet
from django.http import HttpRequest


def paginate(
    request: HttpRequest,
    queryset: QuerySet,
    count: int = settings.PAGINATION,
) -> Page:
    return Paginator(queryset, count).get_page(request.GET.get('page'))


def truncate(text: str, count: int = settings.TRUNCATION) -> str:
    return text[:count] + '...' if len(text) > count else text
