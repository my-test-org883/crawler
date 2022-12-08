import asyncio
import json
from unittest import mock

from django.db import connections
from django.db.utils import OperationalError
from django.test import TestCase
from fixtures.auth_info import auth_json, header, params
from fixtures.jira_info import get_jira_side_effect, jira_meta_return_value
from fixtures.p4_info import p4_changes_side_effect, p4_client_side_effect
from fixtures.plm.plm_info import (find_folders_result,
                                   find_project_dic_response,
                                   save_configuration_cl_only_response,
                                   save_default_configuration_response,
                                   select_configuration_response,
                                   set_config_id_response, xml1_response,
                                   xml2_response, xml3_response, xml4_response)
from fixtures.retriever_info import retriever_dict
from fixtures.subprocess_info import (subprocess_error_side_effect,
                                      subprocess_result_side_effect)
from fixtures.test_info import expected_os_list, expected_result
from rest_framework.test import APIClient

from application.collector.controllers import controller_mytoolsdb
from application.collector.handlers import (handler_jira, handler_p4,
                                            handler_plm, handler_retriever)
from application.common import auth


@asyncio.coroutine
def async_result(result: any = "async_result"):
    return result


class CollectorTestCase(TestCase):
    @classmethod
    def tearDownClass(cls):
        def close_sessions(conn):
            close_sessions_query = """
                SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE
                    datname = current_database() AND
                    pid <> pg_backend_pid();
            """
            with conn.cursor() as cursor:
                try:
                    cursor.execute(close_sessions_query)
                except OperationalError:
                    pass

        for alias in connections:
            close_sessions(connections[alias])
            connections[alias].close()
        print("Forcefully closed database connections.")

    @mock.patch.object(controller_mytoolsdb, "pymysql")
    @mock.patch.object(handler_plm, "aiohttp")
    @mock.patch.object(auth, "requests")
    @mock.patch.object(handler_retriever, "aiohttp")
    @mock.patch.object(handler_jira, "JIRA")
    @mock.patch.object(handler_p4, "P4")
    @mock.patch.object(handler_p4, "subprocess")
    def test_1_update_changelist_endpoint(
        self,
        mock_subprocess,
        mock_p4,
        mock_jira,
        mock_retriever,
        mock_auth,
        mock_plm,
        mock_pymysql,
    ):

        client = APIClient()

        mock_auth.get().ok = True
        mock_auth.get().status_code = 200
        mock_auth.get().json.return_value = auth_json

        mock_jira.create.return_value = async_result(mock_jira)
        mock_jira.search_issues.side_effect = [async_result(i) for i in get_jira_side_effect()]
        mock_jira.editmeta.return_value = async_result(jira_meta_return_value)

        mock_p4().run_login.return_value = True
        mock_p4().run_client.side_effect = p4_client_side_effect
        mock_p4().run_changes.side_effect = p4_changes_side_effect
        mock_p4().run_filelog()[0].revisions[0].change = 12345678

        mock_retriever.ClientSession.return_value = mock_retriever
        mock_retriever.get.return_value = async_result(mock_retriever)
        mock_retriever.text.return_value = async_result(json.dumps(retriever_dict))
        mock_retriever.close.return_value = async_result()

        mock_plm.ClientSession().get.side_effect = [async_result(mock_plm) for i in range(4)]
        mock_plm.ClientSession().post.side_effect = [async_result(mock_plm) for i in range(16)]
        mock_plm.close.return_value = async_result()
        mock_plm.history = False
        mock_plm.text.side_effect = [
            async_result(find_project_dic_response),
            async_result(find_folders_result),
            async_result(set_config_id_response),
            async_result(select_configuration_response),
            async_result(save_configuration_cl_only_response),
            async_result(find_project_dic_response),
            async_result(find_folders_result),
            async_result(set_config_id_response),
            async_result(select_configuration_response),
            async_result(save_configuration_cl_only_response),
            async_result(xml1_response),
            async_result(xml2_response),
            async_result(xml3_response),
            async_result(xml4_response),
            async_result(xml1_response),
            async_result(xml2_response),
            async_result(xml3_response),
            async_result(xml4_response),
            async_result(save_default_configuration_response),
            async_result(save_default_configuration_response),
        ]
        mock_plm.read.side_effect = [
            async_result(xml1_response),
            async_result(xml2_response),
            async_result(xml3_response),
            async_result(xml4_response),
            async_result(xml1_response),
            async_result(xml2_response),
            async_result(xml3_response),
            async_result(xml4_response),
        ]

        mock_subprocess.run().stdout.decode.side_effect = subprocess_result_side_effect
        mock_subprocess.run().stderr.decode.side_effect = subprocess_error_side_effect

        mock_pymysql.connect().__enter__().cursor().__enter__().fetchall.return_value = (
            ("201324273862", "//"),
            ("197425334567", "//"),
            ("188764643367", "//"),
        )
        client.credentials(HTTP_AUTHORIZATION=header["Authorization"])
        request_result = client.get(
            "/collector/update_changelists", params, content_type="application/json"
        )
        result = request_result.json()

        assert request_result.status_code == 200
        assert request_result.status_text == "OK"
        assert result == expected_result

    @mock.patch.object(handler_plm, "aiohttp")
    @mock.patch.object(auth, "requests")
    @mock.patch.object(handler_retriever, "aiohttp")
    @mock.patch.object(handler_jira, "JIRA")
    @mock.patch.object(handler_p4, "P4")
    @mock.patch.object(handler_p4, "subprocess")
    def test_2_get_changelist_endpoint(
        self, mock_subprocess, mock_p4, mock_jira, mock_retriever, mock_auth, mock_plm
    ):

        mock_auth.get().ok = True
        mock_auth.get().status_code = 200
        mock_auth.get().json.return_value = auth_json

        client = APIClient()

        client.credentials(HTTP_AUTHORIZATION=header["Authorization"])
        request_result = client.get(
            "/collector/get_changelists", params, content_type="application/json"
        )
        result = request_result.json()

        assert request_result.status_code == 200
        assert request_result.status_text == "OK"
        assert result == expected_result

    @mock.patch.object(handler_plm, "aiohttp")
    @mock.patch.object(auth, "requests")
    @mock.patch.object(handler_retriever, "aiohttp")
    @mock.patch.object(handler_jira, "JIRA")
    @mock.patch.object(handler_p4, "P4")
    @mock.patch.object(handler_p4, "subprocess")
    def test_3_get_os_list_endpoint(
        self, mock_subprocess, mock_p4, mock_jira, mock_retriever, mock_auth, mock_plm
    ):

        mock_auth.get().ok = True
        mock_auth.get().status_code = 200
        mock_auth.get().json.return_value = auth_json

        client = APIClient()

        client.credentials(HTTP_AUTHORIZATION=header["Authorization"])
        request_result = client.get(
            "/collector/get_os_version_list", content_type="application/json"
        )
        result = request_result.json()

        assert request_result.status_code == 200
        assert request_result.status_text == "OK"
        assert result == expected_os_list
