import hashlib
import hmac
import json

def sentry_evt(request):

    expected_digest = request.headers.get('sentry-hook-signature')  # returns None if header is missing
    print('expected_digest',expected_digest)
    body = json.dumps(request.body)

    digest = hmac.new(
        key="client_secret".encode('utf-8'),
        msg=body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not expected_digest:  # The signature is missing
        raise Exception

    if not hmac.compare_digest(digest, expected_digest):
        raise Exception

def sentry_setup(request):
    expected_digest = request.headers.get('sentry-hook-signature')  # returns None if header is missing
    print('expected_digest', expected_digest)
    body = json.dumps(request.body)

    digest = hmac.new(
        key="client_secret".encode('utf-8'),
        msg=body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not expected_digest:  # The signature is missing
        raise Exception

    if not hmac.compare_digest(digest, expected_digest):
        raise Exception