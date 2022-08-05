import asyncio
import logging
import time

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from app.collector.controllers.controller import Controller
from app.collector.handlers.handler import Handler
from app.common.apiresponse import ApiResponse
from app.common.auth import has_token

logger = logging.getLogger(__name__)


def check_arguments(required_inputs, arguments: list) -> None:
    missing_field = [i for i in required_inputs if i not in arguments]
    if missing_field:
        raise AttributeError(f"The following fields are missing:{missing_field}")


def generate_base_cls_dic(arguments: dict) -> dict:
    base_cls_dic = {
        "ap_sync_cl": arguments["ap_sync_cl"],
        "ap_max_cl": arguments["ap_max_cl"],
        "cp_sync_cl": arguments["cp_sync_cl"],
        "cp_max_cl": arguments["cp_max_cl"],
    }
    return base_cls_dic


class UpdateChangelists(APIView):
    permission_classes = (permissions.AllowAny,)

    @has_token
    def get(self, request):
        response = ApiResponse()
        try:
            required_input = [
                "model_name",
                "os_version",
                "ap_template",
            ]
            arguments = request.GET
            check_arguments(required_input, arguments)

            response.model_name = model_name = arguments["model_name"]
            response.os_version = os_version = arguments["os_version"]
            ap_template = arguments["ap_template"]

            logger.info("Request update_changelists START")
            time_init = time.time()

            Handler.headers = request.headers
            controller_obj = Controller(model_name, os_version, ap_template, True)
            response.result_list = asyncio.run(controller_obj.update_cl_database())
            response.ready = True

            logger.info(f"Request update_changelists END - time:[{time.time() - time_init}]")
            return Response(*response.serialize("success"))
        except AttributeError as E:
            msg = f"Request data invalid. Please, check them and try again. {str(E)}"
            response.error_message = msg
            error_type = "fail"
            return Response(*response.serialize(error_type))
        except Exception as E:
            msg = str(E)
            error_type = "error"
            response.error_message = msg
            return Response(*response.serialize(error_type))


class GetChangelists(APIView):
    permission_classes = (permissions.AllowAny,)

    @has_token
    def get(self, request):
        response = ApiResponse()
        try:
            required_input = [
                "model_name",
                "os_version",
            ]
            arguments = request.GET
            check_arguments(required_input, arguments)

            response.model_name = model_name = arguments["model_name"]
            response.os_version = os_version = arguments["os_version"]

            logger.info("Request get_changelists START")
            time_init = time.time()

            Handler.headers = request.headers
            controller_obj = Controller(model_name, os_version)
            response.result_list = asyncio.run(controller_obj.get_model_cl_database())
            response.ready = True

            logger.info(f"Request get_changelists END - time:[{time.time() - time_init}]")
            return Response(*response.serialize("success"))
        except AttributeError as E:
            msg = f"Request data invalid. Please, check them and try again. {str(E)}"
            response.error_message = msg
            error_type = "fail"
            return Response(*response.serialize(error_type))
        except Exception as E:
            msg = str(E)
            error_type = "error"
            response.error_message = msg
            return Response(*response.serialize(error_type))


class GetOsList(APIView):
    permission_classes = (permissions.AllowAny,)

    @has_token
    def get(self, request):
        response = ApiResponse()
        try:
            logger.info("Request get_changelists START")
            time_init = time.time()

            Handler.headers = request.headers
            controller_obj = Controller()
            response.result_list = asyncio.run(controller_obj.get_os_list_database())
            response.result_list.sort()
            response.ready = True

            logger.info(f"Request get_changelists END - time:[{time.time() - time_init}]")
            return Response(*response.serialize("success"))
        except AttributeError as E:
            msg = f"Request data invalid. Please, check them and try again. {str(E)}"
            response.error_message = msg
            error_type = "fail"
            return Response(*response.serialize(error_type))
        except Exception as E:
            msg = str(E)
            error_type = "error"
            response.error_message = msg
            return Response(*response.serialize(error_type))
