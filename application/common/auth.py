from functools import wraps
from os import getenv
from django.http import HttpResponseBadRequest

import jwt
import requests

__AUTH_SERVICE = getenv("AUTH_SERVICE", "105.112.171.112:7101")
__TOKEN_TYPE = "Bearer"


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, verify=False)
    except jwt.ExpiredSignatureError:
        return None


def fetch_credentials(username: str, authpoint: str, headers=None) -> dict:
    url = f"http://{__AUTH_SERVICE}/v1/{authpoint}/get?session_id={username}"
    cust_headers = {}
    if headers:
        cust_headers["Authorization"] = headers
    response = requests.get(url, headers=cust_headers)
    if response.ok:
        data = {}
        if response.status_code != 204:
            data = response.json()
        if "credentials" not in data:
            if authpoint in data:
                return data[authpoint]
            raise Exception(f"User not logged at {authpoint}")
        return data
    raise Exception(
        "Could not load credentials ",
        f"http://{__AUTH_SERVICE}/v1/{authpoint}/get?session_id={username}",
    )


def get_credentials(headers: str, authpoint: str, all_data=False) -> dict:
    token = get_token_only(headers)
    token = decode_token(token)
    credentials = fetch_credentials(token["username"], authpoint, headers)
    if not all_data:
        return credentials["credentials"]
    return credentials


def get_token_only(headers: str) -> str:
    splited = headers.split(f"{__TOKEN_TYPE} ")
    if len(splited) == 2:
        return splited[1]
    return None


def has_token(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        token = get_token_only(args[1].headers.get("Authorization") or "")
        if not token:
            return HttpResponseBadRequest(
                "<h1>400 Bad Request!</h1><h2>Authentication Token not found</h2>"
            )
        return func(*args, **kwargs)

    return wrap
