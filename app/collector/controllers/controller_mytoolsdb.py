import logging
import os

import pymysql

logger = logging.getLogger(__name__)


class ControllerMytoolsDatabase:
    def __init__(self):
        self.host = os.environ.get("MYTOOLS_HOST", "")
        self.user = os.environ.get("MYTOOLS_USER", "")
        self.password = os.environ.get("MYTOOLS_PW", "")
        self.db = os.environ.get("MYTOOLS_DB", "")

    def get_smr_cl_by_branch(self, ap_branch: str) -> list:
        with pymysql.connect(
            host=self.host, user=self.user, password=self.password, db=self.db
        ) as connection:
            with connection.cursor() as cursor:
                sql = "SELECT cl,branch from SecurityPatch WHERE branch=%s"
                cursor.execute(sql, ap_branch)
                result = sorted(list(set(cursor.fetchall())))
                return result

    def get_security_changelists(self, ap_branch: list):
        smr_cls = self.get_smr_cl_by_branch(ap_branch)
        result = self.format_smr_cl_list(smr_cls)
        return result

    @staticmethod
    def format_smr_cl_list(smr_cl_list: list) -> dict:
        result_dict = {
            str(i[0]): {
                "branch": i[1],
                "port": "AP",
                "source": "SMR Database",
                "carrier_list": ["ALL"],
                "task": [],
                "is_smr": True,
            }
            for i in smr_cl_list
        }
        return result_dict
