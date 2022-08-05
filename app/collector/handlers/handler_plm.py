import json
import logging
from json.decoder import JSONDecodeError

import aiohttp
import requests
from aiohttp.client import ClientConnectorError

logger = logging.getLogger(__name__)


class HandlerPlm:

    __session = None

    def __init__(self, session_id: str):
        self.url = "http://my.website.com"
        self.cookies = {"WLSESSIONID": session_id}

    async def get_plm(self, rest_api: str, params: dict) -> dict:
        try:
            url = f"{self.url}/{rest_api}"
            session = aiohttp.ClientSession(trust_env=True)
            try:
                request_type = "aiohttp"
                resp = await session.get(url, cookies=self.cookies, params=params, timeout=60)
            except ClientConnectorError:
                logger.info("get_plm: aiohttp exception ClientConnectorError, using requests")
                request_type = "requests"
                resp = requests.get(url, cookies=self.cookies, params=params, timeout=60)
            except Exception as E:
                raise E
            result = await self.handle_requests(resp, request_type)
        finally:
            if session and not session.closed:
                await session.close()
        return result

    async def post_plm(self, rest_api: str, body: str, headers: dict) -> dict:
        try:
            url = f"{self.url}/{rest_api}"
            session = aiohttp.ClientSession(trust_env=True)
            try:
                request_type = "aiohttp"
                resp = await session.post(
                    url, headers=headers, cookies=self.cookies, data=body, timeout=60
                )
            except ClientConnectorError:
                logger.info("get_plm: aiohttp exception ClientConnectorError, using requests")
                request_type = "requests"
                resp = requests.post(
                    url, headers=headers, cookies=self.cookies, data=body, timeout=60
                )
            except Exception as E:
                raise E
            result = await self.handle_requests(resp, request_type)
        finally:
            if session and not session.closed:
                await session.close()
        return result

    @staticmethod
    async def handle_requests(request, request_type: str) -> dict:

        if request.ok and not request.history:
            if request_type == "requests":
                try:
                    result = json.loads(request.text)
                except JSONDecodeError:
                    result = request.content
                except Exception as E:
                    raise E
            elif request_type == "aiohttp":
                try:
                    result = json.loads(await request.text())
                except (UnicodeDecodeError, JSONDecodeError):
                    result = await request.read()
        elif request.history and request.history[0].status == 302:
            raise Exception("PLM Credential has expired.")
        else:
            raise Exception("Could not connect to PLM.")
        return result
