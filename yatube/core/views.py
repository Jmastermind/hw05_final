from http import HTTPStatus

from django.core import exceptions
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def csrf_failure(request: HttpRequest, reason: str = '') -> HttpResponse:
    del reason
    return render(request, 'core/403csrf.html')


def page_not_found(
    request: HttpRequest,
    exception: exceptions.ObjectDoesNotExist,
) -> HttpResponse:
    del exception
    return render(
        request,
        'core/404.html',
        {'path': request.path},
        status=HTTPStatus.NOT_FOUND,
    )


def permission_denied(
    request: HttpRequest,
    exception: exceptions.PermissionDenied,
) -> HttpResponse:
    del exception
    return render(request, 'core/403.html', status=HTTPStatus.FORBIDDEN)


def server_error(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        'core/500.html',
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
    )
