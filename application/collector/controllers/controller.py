import asyncio
import copy
import re
import time

from application.collector.controllers.controller_database import \
    ControllerDatabase
from application.collector.controllers.controller_jira import ControllerJira
from application.collector.controllers.controller_mytoolsdb import \
    ControllerMytoolsDatabase
from application.collector.controllers.controller_p4 import ControllerP4
from application.collector.controllers.controller_plm import ControllerPlm
from application.common.utilities import merge_dict


class Controller:
    def __init__(
        self,
        model_name: str = None,
        os_version: str = None,
        ap_template: str = None,
        do_authentication: bool = False,
    ):
        self.model_name = model_name
        self.os_version = os_version

        self.short_model_name = self.__get_short_model_name(model_name) if model_name else ""
        if do_authentication:
            self.controller_jira = ControllerJira()
        else:
            self.controller_jira = None
        self.controller_p4 = None
        self.controller_retriever = None
        self.controller_plm = None
        self.controller_database = ControllerDatabase()
        self.controller_mytools = None

        self.ap_template = ap_template
        self.ap_branch = ""

        self.date = ""
        self.os_version_info = None
        self.carrier_db = None
        self.model_info_list = None

    async def set_model_info(self):
        if not self.controller_jira:
            self.controller_jira = ControllerJira()
        self.controller_p4 = ControllerP4()
        self.controller_plm = ControllerPlm()
        self.controller_mytools = ControllerMytoolsDatabase()

        self.os_version_info = await self.get_os_version_info(self.os_version)
        self.carrier_db = await self.controller_database.get_carrier_info()

        self.model_info_list = await self.get_model_info(
            self.os_version_info.os_version, self.short_model_name
        )
        self.ap_branch = self.controller_p4.get_branch_from_template(self.ap_template, "AP")
        if self.ap_branch:
            self.security_cl_dict = self.controller_mytools.get_security_changelists(
                self.ap_branch
            )
        else:
            raise Exception(f"Wrong workspace provided: '{self.ap_template}'")

    async def update_cl_database(self) -> None:
        await self.set_model_info()
        project_dict = {i.project: i.model_name for i in self.model_info_list}

        short_model_name = self.short_model_name
        os_version = self.os_version_info.os_version
        date = self.date

        if not date:
            date = await self.get_last_query_date()
        #  Executing Jira, PLM and CP Delivery routines in pseudo parallel way using asyncio
        result = asyncio.gather(
            self.controller_jira.find_jira_cls(
                project_dict, short_model_name, os_version, date
            ),
            *[
                self.controller_plm.find_plm_cls(self.short_model_name, project)
                for project in project_dict.keys()
            ],
            self.controller_p4.find_cp_delivery_cl(self.ap_template),
        )
        await result
        cl_dict = dict()
        for dic_item in result.result():
            if dic_item:
                cl_dict = merge_dict(cl_dict, dic_item)
        cl_dict = await self.filter_changelists(cl_dict)

        # Merging CL result with SMR Cls
        cl_dict = self.merge_smr_cls(cl_dict)

        # Updating database
        await self.__update_cl_database(cl_dict)
        await self.set_query_date()
        cl_info_result = await self.controller_database.get_cl_database(
            self.short_model_name, self.os_version
        )
        return cl_info_result

    async def get_model_cl_database(self):
        cl_info_result = await self.controller_database.get_cl_database(
            self.short_model_name, self.os_version
        )
        return cl_info_result

    async def get_os_list_database(self):
        os_version_list = await self.controller_database.get_os_version_list()
        return os_version_list

    async def filter_changelists(self, cl_dict: dict) -> dict:
        await self.update_tasks_database(cl_dict)
        cl_database_list = await self.controller_database.get_cl_database_list(
            self.short_model_name
        )
        cl_list = sorted([cl for cl in cl_dict if cl not in cl_database_list], key=int)

        cl_info_dict_cp, non_cp_cls = self.controller_p4.find_cls_info(cl_list, "CP")
        cl_info_dict_ap, __ = self.controller_p4.find_cls_info(non_cp_cls, "AP")

        for cl in cl_dict.copy().keys():
            await self.update_carrier_database(cl_dict, cl)
            if cl in cl_info_dict_ap and cl_info_dict_ap[cl]["branch_info"]:
                branch = cl_info_dict_ap[cl]["branch_info"]
                cl_dict[cl]["branch"] = self.get_branch_info(
                    cl_info_dict_ap[cl]["branch_info"]
                )
                if "_CSC" in branch:
                    cl_dict[cl]["port"] = "CSC"
                else:
                    cl_dict[cl]["port"] = "AP"

            elif cl in cl_info_dict_cp and cl_info_dict_cp[cl]["branch_info"]:
                cl_dict[cl]["port"] = "CP"
                cl_dict[cl]["branch"] = cl_info_dict_cp[cl]["branch_info"]

            else:
                cl_dict[cl]["port"] = "N/R"
                cl_dict[cl]["branch"] = "N/R"

        return cl_dict

    async def update_carrier_database(self, cl_dict: dict, current_cl: str):
        if cl_dict[current_cl]["carrier_list"]:
            for carrier_code in cl_dict[current_cl]["carrier_list"].copy():
                if carrier_code not in self.carrier_db and len(carrier_code) == 3:
                    await self.controller_database.update_carrier_info(carrier_code)
                    self.carrier_db.append(carrier_code)
                elif len(carrier_code) != 3:
                    cl_dict[current_cl]["carrier_list"].remove(carrier_code)
        else:
            cl_dict[current_cl]["carrier_list"].append("ALL")
            if "ALL" not in self.carrier_db:
                await self.controller_database.update_carrier_info("ALL")
                self.carrier_db.append("ALL")

    async def update_tasks_database(self, cl_dict: dict):
        filter_dic = {"model_name": self.short_model_name}
        task_list = await self.controller_database.get_task_information(filter_dic)
        for task in [
            item for list_item in [cl_dict[i]["task"] for i in cl_dict] for item in list_item
        ]:
            if task not in task_list:
                task_list.append(task)
                await self.controller_database.update_task_information(
                    task, self.model_info_list
                )

    async def __update_cl_database(self, cl_dict: dict):
        formmated_cl_list = list()
        for cl, cl_info in cl_dict.items():
            formmated_cl_list.append(
                {
                    "cl_number": cl,
                    "task_list": cl_info["task"],
                    "os": self.os_version_info,
                    "cl_source": cl_info["source"],
                    "cl_type": cl_info["port"],
                    "branch": cl_info["branch"],
                    "relevance": "",
                    "is_smr": cl_info["is_smr"],
                    "carrier_info": cl_info["carrier_list"],
                    "comment": "",
                }
            )

        await self.controller_database.update_changelist_information(
            formmated_cl_list, self.model_info_list
        )

    @staticmethod
    def __get_short_model_name(model_name: str) -> str:
        regex_model = r"SM-[a-zA-Z0-9]*"
        short_model_name = re.findall(regex_model, model_name)
        if short_model_name:
            return short_model_name[0]
        else:
            return ""

    async def get_os_version_info(self, os_version: str) -> dict:
        dic_info = await self.controller_database.get_os_version_info(os_version)
        if not dic_info:
            os_list = await self.controller_jira.find_os_information()
            await self.controller_database.update_os_version_db(os_list)
            dic_info = await self.controller_database.get_os_version_info(os_version)
        if dic_info:
            return dic_info
        else:
            raise Exception(f"Invalid OS version: {os_version}")

    async def get_model_info(self, os_version: str, short_model_name: str) -> dict:
        model_info_obj_list = await self.controller_database.get_model_info(
            short_model_name, os_version
        )
        if not model_info_obj_list:
            model_info_list = await self.controller_jira.find_model_names(
                short_model_name, os_version
            )
            await self.controller_database.update_model_info_db(model_info_list)
            model_info_obj_list = await self.controller_database.get_model_info(
                short_model_name, os_version
            )
        if model_info_obj_list:
            for model_info_obj in model_info_obj_list:
                model_info_obj.project = model_info_obj.project.strip()
            return model_info_obj_list
        else:
            raise Exception(f"Model information not found: {short_model_name} - {os_version}")

    async def get_last_query_date(self) -> time:
        date = await self.controller_database.get_date_information(
            self.short_model_name, self.os_version_info
        )
        return date

    async def set_query_date(self):
        date = time.strftime("%Y-%m-%d")
        await self.controller_database.set_date_information(
            self.model_info_list, self.os_version_info, date
        )
        return date

    def merge_smr_cls(self, cl_dict):
        cl_dict_copy = copy.deepcopy(cl_dict)
        for cl, cl_info in cl_dict_copy.items():
            if cl in self.security_cl_dict.keys():
                cl_info["is_smr"] = True
                self.security_cl_dict.pop(cl)
            else:
                cl_info["is_smr"] = False
        cl_dict_copy.update(self.security_cl_dict)
        return cl_dict_copy

    def get_branch_info(self, branch_string):
        if self.ap_branch in branch_string or branch_string in self.ap_branch:
            return self.ap_branch
        else:
            return branch_string
