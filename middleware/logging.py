import json
import logging
import time

from django.http import JsonResponse

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s; %(message)s")
handler.formatter = formatter
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        request_data = {
            "method": request.method,
            'path': request.path,
        }

        logger.info(request_data)

        try:
            response = self.get_response(request)
        except Exception as e:
            error_data = {
                'exception_type': type(e).__name__,
                'exception_message': str(e),
                'path': request.path,
                'method': request.method,
            }
            logger.error(f"EXCEPTION: {json.dumps(error_data, ensure_ascii=False)}")
            logger.exception("Detailed exception traceback:")

            response = JsonResponse(
                {'error': 'Internal server error'},
                status=500
            )

        duration = time.time() - start_time
        response_data = {
            "status_code": response.status_code,
            "duration": round(duration, 2),
            "path": request.path,
            "content_type": response.get('Content-Type', ''),
            "content_length": response.get('Content-Length', '')
        }

        if response.status_code >= 400:
            try:
                if hasattr(response, 'data') and response.data:
                    response_data['response_body'] = response.data
            except Exception:
                pass

        logger.info(response_data)

        return response