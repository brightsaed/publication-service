import logging
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed

logger = logging.getLogger(__name__)


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_authentication = JWTAuthentication()

        self.exempt_path = [
            '/admin/',
            '/api/docs/',
            '/api/account/register/',
        ]

    def __call__(self, request):
        if any(request.path.startswith(path) for path in self.exempt_path):
            return self.get_response(request)

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if auth_header.startswith('Bearer '):
            try:
                auth_result = self.jwt_authentication.authenticate(request)
                if auth_result is not None:
                    user, token = auth_result
                    request.user = user
                    request.auth = token
                    logger.info(f'JWT Auth successful for user: {user.username}')
                else:
                    logger.warning(f'JWT Auth failed for path: {request.path}')
            except (InvalidToken, AuthenticationFailed) as error:
                error_data = {
                    'error_type': type(error).__name__,
                    'path': request.path,
                    'method': request.method,
                }
                logger.warning(f"JWT Authentication failed: {error_data}")

                return JsonResponse(
                    {
                        'error': 'Authentication failed',
                        'detail': str(error)
                    },
                    status=401
                )
            except Exception as error:
                logger.error(f"Unexpected error in JWT middleware: {str(error)}")
                return JsonResponse(
                    {'error': 'Internal authentication error'},
                    status=500)
        else:
            return JsonResponse(
                {
                    'error': 'Authentication required',
                    'detail': 'Bearer token missing'
                },
                status=401
            )
        return self.get_response(request)