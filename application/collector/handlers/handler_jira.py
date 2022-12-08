import asyncio

from aiojira import JIRA, JIRAError

from config import JIRA_URL


class ExceptionJiraLoginError(Exception):
    pass


class HandlerJira:
    def __init__(self, user, password):
        self.url = JIRA_URL
        self.user = user
        self.password = password
        self.jira = None

    async def fetch_issues(
        self,
        jql: str,
        fields: list,
        issue_type: str = None,
        expand: str = None,
        max_results: int = 1000,
    ) -> list:
        if not self.jira:
            await self.__authenticate()
        issues = asyncio.create_task(
            self.jira.search_issues(jql, expand=expand, maxResults=max_results, fields=fields)
        )
        await issues
        if issue_type:
            issues_mp = list()
            for issue in issues.result():
                issues_mp.append(self.parse_issue(issue, issue_type))
            return issues_mp
        else:
            return issues.result()

    async def __authenticate(self):
        try:
            self.jira = await JIRA.create(
                server=self.url,
                basic_auth=(self.user, self.password),
                max_retries=0,
                timeout=120,
            )

        except JIRAError:
            raise ExceptionJiraLoginError()

    def __get_jql_model(self) -> str:
        return "issuetype = MODEL AND status NOT IN (CANCELLED, DROPPED) "

    def __merge_issues(self, lhs: list, rhs: list, key: str, targets: list) -> list:
        for la in lhs:
            for r in rhs:
                if la[key] == r[key]:
                    for t in targets:
                        if r[t]:
                            la[t] = r[t].strip()
        return lhs

    def __parse_spec_info(self, info: list) -> (list, str):
        carriers = ""
        specs = []
        if not info:
            return specs
        rows = info[0]["specs"].split("\r\n")
        for r in rows:
            cols = r.split(",")
            carriers = carriers + '"' + cols[0] + '",'
            specs.append({"carrier_code": cols[0], "fms_id": cols[1], "mps_id": cols[2]})
        carriers = carriers[0:-1]
        return specs, carriers

    def __unique(self, data: list) -> list:
        return [dict(t) for t in {tuple(d.items()) for d in data}]

    def parse_issue(self, issue: JIRA, mapping_type: str) -> dict:
        if mapping_type == "model_name":
            return {
                "modelName": [
                    issue.fields.customfield_10301.value
                    if issue.fields.customfield_10301
                    else issue.fields.customfield_12510
                ],
                "plmDevModelName": issue.fields.customfield_12712,
                "os_version": issue.fields.customfield_13304.value,
            }
        else:
            carrier_list = set()
            if issue.fields.customfield_11910 and issue.fields.customfield_11910.value:
                carrier_list.add(issue.fields.customfield_11910.value)

            if issue.fields.customfield_11907:
                for carrier in [i.value for i in issue.fields.customfield_11907]:
                    if carrier:
                        carrier_list.add(carrier)

            if issue.fields.customfield_10322 and issue.fields.customfield_10322.value:
                carrier_list.add(issue.fields.customfield_10322.value)
            return {
                "cl_submit": issue.fields.customfield_12601,
                "task_info": issue.key,
                "carrier_list": sorted(list(carrier_list)),
            }
