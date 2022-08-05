import asyncio
import logging
import re

from app.collector.handlers.handler import Handler
from app.common.utilities import create_cl_dict, get_cls_from_string

CONTROLLER_API = "jira"
logger = logging.getLogger(__name__)


class ControllerJira:
    def __init__(self):
        handler_obj = Handler()
        self.handler = handler_obj.get_handler(CONTROLLER_API)

        self.carrier = None
        self.date = None
        self.model_name_list = None
        self.os_version = None
        self.short_model_name = None

    async def find_jira_cls(
        self,
        model_name_list: str,
        short_model_name: str,
        os_version: str,
        date: str = None,
    ) -> dict:

        self.date = date
        self.model_name_list = [model_name_list[i] for i in model_name_list.keys()]
        self.os_version = os_version
        self.short_model_name = short_model_name

        task1 = asyncio.create_task(self.find_cls_by_task_type(""))
        task2 = asyncio.create_task(self.find_cls_by_task_type(""))
        task3 = asyncio.create_task(self.find_cls_by_task_type("task"))
        task4 = asyncio.create_task(self.find_cls_by_task_type("support_feedback"))

        async_result = list()
        async_result.append(await task1)
        async_result.append(await task2)
        async_result.append(await task3)
        async_result.append(await task4)

        cl_dict = dict(
            dict_item for dictionary in async_result for dict_item in dictionary.items()
        )
        return dict(sorted(cl_dict.items()))

    async def find_cls_by_task_type(self, task_type: str) -> dict:
        jql = await self.get_jql(task_type)
        fields = [
            "customfield_12601",
            "customfield_11910",
            "customfield_11907",
            "customfield_10322",
        ]

        logger.debug(f'Jira fetch "{task_type}" START')
        tasks = await self.handler.fetch_issues(jql, fields, task_type, max_results=5000)
        logger.debug(f'Jira fetch "{task_type}" END')

        result = self.parse_tasks(tasks, task_type)
        return result

    async def get_jql(self, jql_type: str) -> str:
        jql = await self.__init_jql()
        if jql_type == "":
            jql += ' and type = " TG"'
            jql += " and status = Closed"
            jql += " and resolution = Fixed"
        elif jql_type == "":
            jql += ' and issuetype in (" Issue", "Horizontal'
            jql += ' Deployment", "Requirement ")'
            jql += " and status in (Closed, Resolved)"
        elif jql_type == "task":
            jql += " and issuetype = Task"
            jql += " and status in (Closed, Resolved)"
        elif jql_type == "support_feedback":
            jql += ' and type = "Support Feedback"'
            jql += " and project = GA"
        return jql

    async def __init_jql(self) -> str:
        model_name_string = ",".join('"{0}"'.format(n) for n in self.model_name_list)

        result = f'("Model Name" in ({model_name_string})'
        result += f' OR summary ~ "{self.short_model_name}")'
        result += f' and "OS Version" = "{self.os_version}"'
        if self.carrier:
            result += f' and "Carrier Code" = {self.carrier}'
        if self.date:
            result += f' and updated >= "{self.date}"'
        return result

    def parse_tasks(self, tasks: list, task_type: str) -> dict:
        for task in tasks:
            all_cls = self.find_all_cls_from_task(task)
            task["cls"] = all_cls
            task["source"] = f"JIRA ({task_type})"
        cl_dict = create_cl_dict(tasks)
        return cl_dict

    def find_all_cls_from_task(self, task: dict) -> list:
        cls_string = task["cl_submit"]
        cl_list = get_cls_from_string(cls_string)
        return cl_list

    async def find_model_names(self, short_model_name: str, os_version: str) -> list:
        jql = (
            "issuetype = MODEL AND status NOT IN (CANCELLED, DROPPED) "
            f'and "Basic Model" = "{short_model_name.replace("-", "")}"  '
            f'and "OS Version" = "{os_version}"'
        )
        fields = [
            "customfield_10301",
            "customfield_12510",
            "customfield_12712",
            "customfield_13304",
        ]

        logger.debug('Jira fetch "Model Name" START')
        tasks = await self.handler.fetch_issues(jql, fields, "model_name", max_results=2000)
        logger.debug('Jira fetch "Model Name" END')

        result = list()
        for task in tasks:
            task_dic = dict()
            task_dic["short_model_name"] = short_model_name
            task_dic["project"] = task["plmDevModelName"]
            task_dic["model_name"] = list(set(task["modelName"]))[0]
            task_dic["os_id"] = os_version
            result.append(task_dic)
        if result:
            return result
        else:
            raise Exception(f"Model information not found: {short_model_name} - {os_version}")

    @staticmethod
    def remove_duplicates_from_list(list_item: list) -> list:
        result = list(set(list_item))
        result.sort()
        return result

    async def find_os_information(self) -> list:
        jira_filter = (
            'project = PTC AND type = task AND "OS Version" is not EMPTY ORDER BY key ASC'
        )
        tasks = await self.handler.fetch_issues(jira_filter, fields="", max_results=10)
        for task in tasks:
            jira_meta = await self.handler.jira.editmeta(task.key)
            if "customfield_13304" in jira_meta["fields"]:
                allowed_values_list = jira_meta["fields"]["customfield_13304"]["allowedValues"]
                break
        else:
            raise Exception("It was not possible to find OS possible values.")

        allowed_values_dic = self.parse_allowed_values(allowed_values_list)
        return allowed_values_dic

    def parse_allowed_values(self, allowed_values_list: list) -> list:

        result = [
            {"os_version": i["value"], "os_code": self.find_os_code(i["value"])}
            for i in allowed_values_list
        ]
        return result

    @staticmethod
    def find_os_code(os_string: str) -> str:
        regex_filter = r"\(([\S]+)\)"
        code_list = re.findall(regex_filter, os_string)
        result = "".join(code_list) or "N/A"
        return result
