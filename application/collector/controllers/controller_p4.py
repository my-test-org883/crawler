import logging
import re

from application.collector.handlers.handler import Handler

logger = logging.getLogger(__name__)
CONTROLLER_API = "p4"


class ControllerP4:
    def __init__(self):
        handler_obj = Handler()
        self.handler_ap, self.handler_cp = handler_obj.get_handler(CONTROLLER_API)
        if not self.handler_ap or not self.handler_cp:
            raise Exception("It was not possible to create Perforce session.")
        self.ap_branch = None
        self.cp_branch = None
        self.csc_branch = None
        self.workspace_list_ap = None
        self.workspace_list_cp = None

    def find_cl_branch(self, cl_list: list, binary_type: str) -> dict:
        p4_argument = ["-df"]
        p4_argument.extend(cl_list)
        regex_branch = r"([^/]+/)([^/]+/)?([^/]+/)?"

        handler = self.__get_handler(binary_type)

        p4_cl_list, cl_error = handler.run_describe(p4_argument)

        cl_branch_dic = {
            i["change"]: i["path"] for i in p4_cl_list if i["status"] == "submitted"
        }

        for cl in cl_branch_dic:
            re_result = re.search(regex_branch, cl_branch_dic[cl])
            if re_result:
                re_groups = re_result.groups()
                branch = f'//{"".join([i for i in re_groups if i])}'
                cl_branch_dic[cl] = branch
            cl_branch_dic[cl] = cl_branch_dic[cl].replace("...", "")

        return cl_branch_dic

    def find_binary_version(self, branch: str, model_name: str, binary_type: str) -> list:
        regex_binary_version = rf"_({model_name.replace('SM-','')}[A-Z0-9]+)"
        p4_argument = ["-m", "100", "-E", f"*{model_name}_*", f"{branch}..."]
        handler = self.__get_handler(binary_type)

        label_list = handler.run_labels(p4_argument)

        binary_version_list = list()
        for label in label_list:
            re_binary_search = re.findall(regex_binary_version, label["label"])

            if len(re_binary_search) == 1:
                binary_version_list.append(re_binary_search[0])

        return binary_version_list

    def get_template_cls(self, template: str, template_type: str) -> list:
        if not template:
            raise Exception(f"{template_type} template not found.")

        if template_type in ["AP", "CSC"]:
            if not self.ap_branch:
                branch = self.get_branch_from_template(template, template_type)
                self.ap_branch = branch
            else:
                branch = self.ap_branch
        elif template_type == "CP":
            if not self.cp_branch:
                branch = self.get_branch_from_template(template, template_type)
                self.cp_branch = branch
            else:
                branch = self.cp_branch

        branch_cl_history = self.get_branch_cl_history(branch, template_type)
        return branch_cl_history

    @staticmethod
    def get_branch_from_view(workspace_list: list, template_type: str) -> str:
        template = workspace_list[0]["Client"]
        if template_type == "AP":
            regex_branch = r"(//\w+/\w+/[^\s/]+/)android/..."
        elif template_type == "CP":
            regex_branch = r"(//\w+/\w+/\w+/[^\s/]+/)[\S]+/code/..."
        elif template_type == "CSC":
            regex_branch = r"(//\w+_CSC/\w+/[^\s/]+/[^\s/]+)"

        view = "\n".join(workspace_list[0]["View"])
        branch_list = re.findall(regex_branch, view)
        if not branch_list:
            raise Exception(
                f"It was not possible to find the branch from template: {template}"
            )
        else:
            branch = branch_list[0]
        return branch

    def get_branch_cl_history(
        self, branch: str, template_type: str, cl_cync: str = None
    ) -> list:
        handler = self.__get_handler(template_type)
        if cl_cync:
            p4_argument = ["-e", cl_cync, "-s", "submitted", f"{branch}..."]
        else:
            p4_argument = ["-s", "submitted", f"{branch}..."]
        history_list = handler.run_changes(p4_argument)
        history_cl_list = [i["change"] for i in history_list]
        return history_cl_list

    def __get_handler(self, binary_type: str) -> Handler:
        if binary_type == "AP" or binary_type == "CSC":
            handler = self.handler_ap
        elif binary_type == "CP":
            handler = self.handler_cp
        else:
            raise Exception(f"Wrong binary type: {binary_type}")
        return handler

    def get_branch_from_template(self, template: str, template_type: str) -> str:
        handler = self.__get_handler(template_type)
        p4_argument = ["-o", template]
        workspace_list = handler.run_client(p4_argument)

        if template_type in ["AP", "CSC"]:
            self.workspace_list_ap = workspace_list
        elif template_type == "CP":
            self.workspace_list_cp = workspace_list

        branch = self.get_branch_from_view(workspace_list, template_type)
        return branch

    def find_cp_delivery_branch(self, ap_branch: str, template: str) -> str:
        if not self.workspace_list_ap:
            handler = self.__get_handler("AP")
            p4_argument = ["-o", template]
            self.workspace_list_ap = handler.run_client(p4_argument)

        view_str = "\n".join(self.workspace_list_ap[0]["View"])
        regex_cp_delivery_branch = fr"({ap_branch}cp/[^\s/]+/[^\s/]+)"

        cp_delivery_branch_list = re.findall(regex_cp_delivery_branch, view_str)
        if not cp_delivery_branch_list:
            raise Exception(
                f"It was not possible to find the cl delivery branch from template: {template}"
            )
        else:
            cp_delivery_branch = cp_delivery_branch_list[0]
        return cp_delivery_branch

    def get_file_history(self, file_path: str, p4_port: str, *args) -> dict:
        handler = self.__get_handler(p4_port)
        p4_argument = list()
        for arg in args:
            p4_argument.append(arg)

        p4_argument.append(file_path)
        file_history = handler.run_filelog(p4_argument)
        return file_history

    async def find_cp_delivery_cl(self, template: str) -> dict:
        logger.debug('P4 fetch "cp_delivery_cl" START')
        p4_port = "AP"
        if not self.ap_branch:
            self.ap_branch = self.get_branch_from_template(template, p4_port)
        cp_delivery_branch = self.find_cp_delivery_branch(self.ap_branch, template)
        file_path = f"{cp_delivery_branch}/prebuilts/modem.bin"
        file_history = self.get_file_history(file_path, p4_port, "-m", "1")
        cp_delivery_cl = str(file_history[0].revisions[0].change)
        result = {
            cp_delivery_cl: {
                "task": ["CP_delivery"],
                "carrier_list": [],
                "source": "P4 (CP delivery)",
            }
        }
        logger.debug('P4 fetch "cp_delivery_cl" END')
        return result

    def find_cls_info(self, cl_list: list, binary_type: str) -> (list, list):
        handler = self.__get_handler(binary_type)
        result, invalid_cl_list = handler.run_describe(cl_list)
        return result, invalid_cl_list
