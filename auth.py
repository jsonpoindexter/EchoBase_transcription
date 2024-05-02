from flask import request, jsonify


def check_api_key(FLASK_API_KEY):
    def wrapper(func):
        def inner(*args, **kwargs):
            api_key = request.headers.get('X-API-KEY')
            if not api_key or api_key != FLASK_API_KEY:
                return jsonify({'error': 'Invalid or missing API Key'}), 401
            return func(*args, **kwargs)

        inner.__name__ = func.__name__
        return inner

    return wrapper
