from functools import wraps

from rest_framework.serializers import ValidationError
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.views import Response


def wrap_exception(wrapped):
    """ Convenient decorator for required response structure """

    @wraps(wrapped)
    def inner(self, request):
        try:
            return wrapped(self, request)
        except ValidationError as e:
            return Response({"status": "error", "error_details": e.get_full_details()}, status=e.status_code)
        except AppException as e:
            return Response({"status": "error", "error_details": e.details}, status=e.status_code)
        except Exception:
            # log unexpected error to sentry or smth
            return Response(
                {"status": "error", "error_details": "Server error"}, status=HTTP_500_INTERNAL_SERVER_ERROR
            )

    return inner


class AppException(BaseException):
    pass


class RedisConnectionError(AppException):
    status_code = HTTP_500_INTERNAL_SERVER_ERROR
    details = "Redis connection error occurred"
