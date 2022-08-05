import json
import logging

import aiohttp
import requests
from aiohttp.client import ClientConnectorError

logger = logging.getLogger(__name__)


class HandlerRetriver:

    __session = None

    def __init__(self, token: str):
        self.url = "http://my.website.com/rest/"
        self.cookies = {"crowd.token_key": token}

    async def search_for_binary(self, query: dict) -> dict:
        try:
            session = aiohttp.ClientSession(trust_env=True)
            rest_api = "grid/srbinary/?q="
            url = f"{self.url}{rest_api}{json.dumps(query)}"
            try:
                request_type = "aiohttp"
                resp = await session.get(url, cookies=self.cookies, timeout=60)
            except ClientConnectorError:
                request_type = "requests"
                logger.info("retriever: aiohttp exception ClientConnectorError")
                resp = requests.get(url, cookies=self.cookies)
            result = await self.handle_requests(resp, request_type)
        finally:
            if session and not session.closed:
                await session.close()
        return result

    @staticmethod
    async def handle_requests(request, request_type: str) -> dict:
        if request.ok:
            if request_type == "requests":
                result = json.loads(request.text)
            elif request_type == "aiohttp":
                result = json.loads(await request.text())
        else:
            raise Exception("Could not connect to Retriever.")
        return result
