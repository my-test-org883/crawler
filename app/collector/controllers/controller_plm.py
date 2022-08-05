from app.collector.handlers.handler import Handler
import asyncio
import pandas
from app.common.utilities import create_cl_dict, get_cls_from_string
import logging

logger = logging.getLogger(__name__)
CONTROLLER_API = "plm"


class ControllerPlm:
    def __init__(self):
        handler_obj = Handler()
        self.handler = handler_obj.get_handler(CONTROLLER_API)
        self.config_id = None
        self.headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"}

        if not self.handler:
            raise Exception("It was not possible to create PLM session.")

    async def find_plm_cls(self, model_name: str, dev_model_name: str):
        project_dic = await self.find_project_dic(model_name, dev_model_name)
        project_id = project_dic[dev_model_name]["id"]
        folder_dict = await self.find_folders(project_id)
        if await self.set_config_id():
            await self.select_configuration()
            await self.save_configuration_cl_only()
            cl_dict = await self.get_plm_cls(project_dic, folder_dict)
            await self.save_default_configuration()

        return cl_dict

    async def find_project_dic(self, model_name: str, dev_model_name: str) -> dict:
        project_region = dev_model_name.split("_")[1]
        api = "wl/tqm/defect/getLeftMenuProjectIframe.do"
        params = {
            "leftMenuVO.searchSet": "DEVNM",
            "leftMenuVO.searchText": f"{model_name}_{project_region}",
        }
        logger.debug("PLM: find_project START")
        get_result = await self.handler.get_plm(api, params)
        logger.debug("PLM: find_project END")
        result = {
            i["devName"]: {
                "id": i["devId"],
                "testPlanId": i["testPlanId"],
            }
            for i in get_result["list"]
            if i["devName"] == dev_model_name
        }
        if not result:
            raise Exception(f"Project {dev_model_name} not found in PLM.")
        return result

    async def find_folders(self, project_id: str) -> dict:
        api = "wl/tqm/defect/getLeftMenuMfgModel.do"
        params = {
            "defectLink": "Y",
            "devId": project_id,
        }
        logger.debug("PLM: find folders START")
        get_result = await self.handler.get_plm(api, params)
        logger.debug("PLM: find folders END")
        result = {
            i["mfgCode"]: {
                "id": i["mfgId"],
                "testPlanId": i["testPlanId"],
            }
            for i in get_result
        }
        return result

    async def save_configuration_cl_only(self) -> bool:
        api = "wl/tqm/defect/defectreg/getDefectExcelTitleInsert.do"
        body_list = [
            "defectExcelVO.caseDiv=ETC",
            "defectExcelVO.deleteTab=N",
            f"defectExcelVO.mainId={self.config_id}",
            "defectExcelVO.title=Basic",
            "defectExcelVO.lastSelectedYn=Y",
            "defectExcelVO.ddValue=BASIS%E2%86%95CASE_CODE",
            "defectExcelVO.ddValue=RESOLVE%E2%86%95CL_NUMBER",
            "title=",
        ]
        body = "&".join(body_list)

        logger.debug("PLM: save_configuration_cl_only START")
        post_result = await self.handler.post_plm(api, body, self.headers)
        logger.debug("PLM: save_configuration_cl_only END")
        if post_result["result"] == "OK":
            return True
        else:
            return False

    async def save_default_configuration(self) -> bool:
        api = "wl/tqm/defect/defectreg/getDefectExcelTitleInsert.do"
        body_list = [
            "defectExcelVO.caseDiv=ETC",
            "defectExcelVO.deleteTab=N",
            f"defectExcelVO.mainId={self.config_id}",
            "defectExcelVO.title=Basic",
            "defectExcelVO.lastSelectedYn=Y",
            "defectExcelVO.ddValue=BASIS%E2%86%95CASE_CODE",
            "defectExcelVO.ddValue=BASIS%E2%86%95PROJECT_NAME",
            "defectExcelVO.ddValue=BASIS%E2%86%95MKT_PROJECT_NAME",
            "defectExcelVO.ddValue=REGIST%E2%86%95CREATE_USER_ID",
            "defectExcelVO.ddValue=REGIST%E2%86%95TITLE",
            "defectExcelVO.ddValue=REGIST%E2%86%95REJECT_CNT",
            "defectExcelVO.ddValue=REGIST%E2%86%95RETURN_REASON",
            "defectExcelVO.ddValue=RESOLVE%E2%86%95DECISION_USER",
            "defectExcelVO.ddValue=RESOLVE%E2%86%95CL_NUMBER",
            "defectExcelVO.ddValue=RESOLVE%E2%86%95COMMENT",
            "defectExcelVO.ddValue=LT%E2%86%95PPT",
            "defectExcelVO.ddValue=LT%E2%86%95PRT",
            "defectExcelVO.ddValue=LT%E2%86%95RPT",
            "defectExcelVO.ddValue=LT%E2%86%95RCT",
            "defectExcelVO.ddValue=LT%E2%86%95PCT",
            "defectExcelVO.ddValue=LT%E2%86%95INGEST_TAT",
            "title=",
        ]
        body = "&".join(body_list)

        logger.debug("PLM: save_default_configuration START")
        post_result = await self.handler.post_plm(api, body, self.headers)
        logger.debug("PLM: save_default_configuration END")
        if post_result["result"] == "OK":
            return True
        else:
            return False

    async def set_config_id(self) -> None:
        api = "wl/tqm/defect/defectreg/getDefectExcelTitleAjax.do"
        body_list = ["defectExcelVO.caseDiv=ETC", "defectExcelVO.deleteTab=", "title="]
        body = "&".join(body_list)

        logger.debug("PLM: set_config_id START")
        post_result = await self.handler.post_plm(api, body, self.headers)
        logger.debug("PLM: set_config_id END")
        if post_result:
            self.config_id = post_result["excelConfigMainList"][0]["id"]
            return True
        else:
            return False

    async def select_configuration(self) -> None:
        api = "wl/tqm/defect/defectreg/getDefectExcelTitleAjax.do"
        if not self.config_id:
            raise Exception("PLM: configuration id not set.")
        body_list = [
            "defectExcelVO.caseDiv=ETC",
            "defectExcelVO.deleteTab=",
            f"defectExcelVO.mainId={self.config_id}",
            "defectExcelVO.title=Basic",
            "defectExcelVO.lastSelectedYn=Y",
            "title=",
        ]
        body = "&".join(body_list)

        logger.debug("PLM: select_configuration START")
        post_result = await self.handler.post_plm(api, body, self.headers)
        logger.debug("PLM: select_configuration END")
        if post_result:
            return True
        else:
            return False

    async def get_plm_cls(self, project_dic: dict, folder_dict: dict) -> dict:
        loop_dic = dict()
        task_list = list()
        loop_dic.update(project_dic)
        loop_dic.update(folder_dict)
        for item in loop_dic:
            task_list.append(asyncio.create_task(self.download_xls(loop_dic[item]["id"])))
        xls_list = [await task_item for task_item in task_list]

        result = self.parse_xls_list(xls_list)
        return result

    async def download_xls(self, id: str):
        api = "wl/tqm/defect/defectreg/getDefectCombinedExcel.do"

        body_list = [
            "projectModelType=ETC",
            f"objectId={id}",
            "isDevVerify=",
            "excelMaxCount=50000",
            "pjtProjectClass=",
        ]
        body = "&".join(body_list)
        logger.debug(f"PLM: download_xls {id} START")
        post_result = await self.handler.post_plm(api, body, self.headers)
        logger.debug(f"PLM: download_xls {id} END")

        return post_result

    @staticmethod
    def parse_xls_list(xls_list: list) -> dict:
        result_list = list()
        for xls_item in xls_list:
            if "b'<!DOCTYPE html PUBLIC" not in str(xls_item):
                xls_pandas = pandas.read_excel(xls_item)
                xls_dict = xls_pandas.to_dict()
                key_0, key_1 = xls_dict.keys()
                for key in xls_dict[key_0]:
                    if str(xls_dict[key_0][key]).startswith("P"):
                        result_list.append(
                            {
                                "task_info": xls_dict[key_0][key],
                                "source": "PLM",
                                "cls": get_cls_from_string(str(xls_dict[key_1][key])),
                                "carrier_list": [],
                            }
                        )

        result = create_cl_dict(result_list)
        return result
