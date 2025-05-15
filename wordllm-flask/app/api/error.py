from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES
from app.api import bp

def error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response

def bad_request(message):
    return error_response(400, message)

def unauthorized(message="Authentication required"):
    return error_response(401, message)

def forbidden(message="Access denied"):
    return error_response(403, message)

def not_found(message="Resource not found"):
    return error_response(404, message)

def internal_error(message="An unexpected error occurred"):
    return error_response(500, message)
