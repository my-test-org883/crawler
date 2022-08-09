import os
import re
import subprocess

from config import P4_AP_PORT, P4_CP_PORT, P4_URL
from P4 import P4, P4Exception


class HandlerP4:
    __session = None

    def __init__(self, username: str, password: str, conection_type: str):
        try:
            if not self.__session:
                self.__session = P4()
                self.address = P4_URL
                self.user = username
                self.password = password

                self.logged = False
                self.conection_type = conection_type

                if conection_type == "AP":
                    self.port = P4_AP_PORT
                elif conection_type == "CP":
                    self.port = P4_CP_PORT
                    self.user = os.environ.get("P4_CP_USER", "")
                    self.password = os.environ.get("P4_CP_PW", "")
                else:
                    raise Exception("Conection type is missing.")

                self.__session.port = f"{self.address}:{self.port}"
                self.__session.user = self.user
                self.__session.password = self.password
                self.__session.connect()

        except P4Exception as e:
            raise e

    def __del__(self):
        if self.__session.connected():
            self.__session.disconnect()

    def get_p4_session(self):
        return self.__session

    def ensure_login(func):
        def check_login(self, *args, **kwargs):
            if not self.logged:
                if self.login():
                    self.logged = True
                else:
                    raise Exception(
                        f"It was not possible to login to P4 {self.conection_type}"
                    )
            return func(self, *args, **kwargs)

        return check_login

    def login(self) -> bool:
        """
        Checks if user is logged in.
        """
        self.__session.run_login()
        p4ticket: [dict] = self.__session.run_login("-s")
        if p4ticket:
            return True
        else:
            return False

    @staticmethod
    def filter_cl_error(error_message: str) -> list:
        regex_cl_error = r"'(\d+)"
        result = re.findall(regex_cl_error, error_message)
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
        while cl_list_aux:
            subprocess_result = subprocess.run(
                describe_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

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

    @ensure_login
    def run_labels(self, arguments: list) -> list:
        labels_result = self.__session.run_labels(arguments)
        sorted_labels = sorted(list(labels_result), key=lambda k: -int(k["Access"]))
        return sorted_labels

    @ensure_login
    def run_client(self, arguments: list) -> list:
        result = self.__session.run_client(arguments)
        return result

    @ensure_login
    def run_changes(self, arguments: list) -> list:
        result = self.__session.run_changes(arguments)
        return result

    @ensure_login
    def run_filelog(self, arguments: list) -> list:
        result = self.__session.run_filelog(arguments)
        return result
