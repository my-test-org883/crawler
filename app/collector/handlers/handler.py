from app.collector.handlers.handler_jira import HandlerJira
from app.collector.handlers.handler_p4 import HandlerP4
from app.collector.handlers.handler_retriever import HandlerRetriver
from app.collector.handlers.handler_plm import HandlerPlm
from app.common.auth import get_credentials


class Handler:
    __handler_jira = None
    __handler_p4_ap = None
    __handler_p4_cp = None
    __handler_retriever = None
    __handler_plm = None
    headers = None

    def get_handler(self, auth_point: str):
        """
        get_handler returns the handler requested.

        :param auth_point: Input to select the desired Handler,
            it can be one of the following ('jira' or 'p4').
        :return: The desired Handler.
        """
        if not self.headers:
            return None

        auth_info = get_credentials(
            self.headers.get("Authorization"), auth_point, all_data=True
        )
        if auth_point == "jira":
            return self.__get_jira_handler(auth_info)
        elif auth_point == "p4":
            return self.__get_p4_handler(auth_info)
        elif auth_point == "sso":
            return self.__get__handler_retriever(auth_info)
        elif auth_point == "plm":
            return self.__get_plm_handler(auth_info)
        else:
            return None

    def __get_jira_handler(self, auth_info: dict) -> HandlerJira:
        credentials = auth_info["credentials"]
        if not self.__handler_jira:
            self.__handler_jira = HandlerJira(credentials["user_id"], credentials["password"])
        return self.__handler_jira

    def __get_p4_handler(self, auth_info: dict) -> HandlerP4:
        credentials = auth_info["credentials"]
        if not self.__handler_p4_ap:
            self.__handler_p4_ap = HandlerP4(
                credentials["user_id"], credentials["password"], "AP"
            )
        if not self.__handler_p4_cp:
            self.__handler_p4_cp = HandlerP4(
                credentials["user_id"], credentials["password"], "CP"
            )
        return self.__handler_p4_ap, self.__handler_p4_cp

    def __get__handler_retriever(self, auth_info: dict) -> HandlerRetriver:
        crowd_token = auth_info["authorization_cookie"]["value"]
        if not self.__handler_retriever:
            self.__handler_retriever = HandlerRetriver(crowd_token)
        return self.__handler_retriever

    def __get_plm_handler(self, auth_info: dict) -> HandlerRetriver:
        session_id = auth_info["authorization_cookie"]["value"]
        if not self.__handler_plm:
            self.__handler_plm = HandlerPlm(session_id)
        return self.__handler_plm
