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

    @ensure_login
    def run_describe(self, cl_list: list) -> (list, str):

        regex_changelist = r"([0-9]+)[^ ]+\.{3} user"
        regex_branch = (
            r"\.{3} path /{0,2}[^/]*(//[^/.*\\]+/?[^/.*\\]+/?[^/.*\\]+/?[^/.*\\]+/?)"
        )

        describe_command = [
            "./misc/p4",
            "-p",
            f"{self.address}:{self.port}",
            "-u",
            f"{self.user}",
            "-P",
            f"{self.password}",
            "-ztag",
            "describe",
            "-m",
            "1",
            "-s",
        ]
        describe_command.extend(cl_list)
        result_dic = dict()
        cl_list_aux = cl_list.copy()
        # while cl_list_aux:
        #     subprocess_result = subprocess.run(
        #         describe_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        #     )

            result_str = subprocess_result.stdout.decode("cp1252", errors="ignore")
            error_str = subprocess_result.stderr.decode("cp1252", errors="ignore")

            if result_str:
                for cl_info in result_str.split("... change "):
                    cl_number_list = re.findall(regex_changelist, cl_info)
                    if cl_number_list:
                        branch_info = re.findall(regex_branch, cl_info)
                        result_dic[cl_number_list[0]] = {
                            "branch_info": branch_info[0] if branch_info else None,
                            "cl_description": cl_info,
                        }
                        describe_command.remove(cl_number_list[0])
                        cl_list_aux.remove(cl_number_list[0])
            elif not error_str:
                break

            if error_str:
                if "no such changelist" in error_str or "Invalid changelist" in error_str:
                    invalid_cls_found = re.findall(r"([0-9]+)", error_str)
                    for cl in invalid_cls_found:
                        describe_command.remove(cl)
                        cl_list_aux.remove(cl)
                else:
                    raise Exception(error_str)

        return result_dic, [i for i in cl_list if i not in result_dic.keys()]

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
