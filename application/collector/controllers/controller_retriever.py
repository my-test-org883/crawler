import logging
import re

from application.collector.handlers.handler import Handler

logger = logging.getLogger(__name__)
CONTROLLER_API = "sso"


class ControllerRetriever:
    def __init__(self):
        handler_obj = Handler()
        self.handler = handler_obj.get_handler(CONTROLLER_API)
        if not self.handler:
            logger.debug("It was not possible to create Retriver session.")

    async def find_template(self, model_name: str, os_version: str) -> (str, str):
        query_dict = {"search": f"{model_name}_LA"}
        os_number = self.get_os_number(os_version)
        logger.debug("Retriever search for binary START")
        bin_dic_list = await self.handler.search_for_binary(query_dict)
        logger.debug("Retriever search for binary END")

        for bin_dic in bin_dic_list["data"]:
            if (
                bin_dic["model_nm"].startswith(f"{model_name}_")
                and bin_dic["os_version"] == os_number
            ):
                ap_template = bin_dic["ap_ver"]["build_workspace"]
                cp_template = bin_dic["cp_ver"]["build_workspace"]
                break
        else:
            raise Exception(f'Template not found for "{model_name}"')

        return ap_template, cp_template

    @staticmethod
    def get_os_number(os_version: str) -> str:
        regex_os_number = r"(\d+)\."
        os_number_list = re.findall(regex_os_number, os_version)
        if os_number_list:
            os_number = os_number_list[0]
        else:
            raise Exception(f'Error getting os_number "os_version: {os_version}"')
        return os_number
