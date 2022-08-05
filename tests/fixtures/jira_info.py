jira_task_list = [
    {
        "key": "BSC-2297418",
        "fields": {
            "customfield_12601": "1716:19111111",
            "customfield_10301.value": "SM-A505G Galaxy-A50 SS/DS LTE",
            "customfield_12510": "SM-A505G Galaxy-A50 SS/DS LTE",
            "customfield_12712": "SM-A505G_LA_QQ_TPA",
            "customfield_13304.value": "Android 10.0 (QQ)",
            "customfield_11910.value": "ZTO",
            "customfield_11907": [],
            "customfield_10322.value": "",
        },
        "comment": [],
    },
    {
        "key": "MODEL-1963",
        "fields": {
            "customfield_12601": "",
            "customfield_10301.value": "SM-A505G Galaxy-A50 SS/DS LTE",
            "customfield_12510": "SM-A505G Galaxy-A50 SS/DS LTE",
            "customfield_12712": "SM-A505G_LA_QQ_TPA",
            "customfield_13304.value": "Android 10.0 (QQ)",
            "customfield_11910.value": "ZTM",
            "customfield_11907": [],
            "customfield_10322.value": "",
        },
        "comment": [],
    },
    {
        "key": "MODEL-1626",
        "fields": {
            "customfield_12601": "19333333",
            "customfield_10301.value": "SM-A505G Galaxy-A50 SS/DS LTE",
            "customfield_12510": "SM-A505G Galaxy-A50 SS/DS LTE",
            "customfield_12712": "SM-A505G_LA_QQ_TPA",
            "customfield_13304.value": "Android 11.0 (RR)",
            "customfield_11910.value": "ZTR",
            "customfield_11907": [],
            "customfield_10322.value": "",
        },
        "comment": [],
    },
    {
        "key": "PTC-472632",
        "fields": {
            "customfield_12601": "1716:19333333",
            "customfield_10301.value": "SM-A505G Galaxy-A50 SS/DS LTE",
            "customfield_12510": "SM-A505G Galaxy-A50 SS/DS LTE",
            "customfield_12712": "SM-A505G_LA_QQ_TPA",
            "customfield_13304.value": "Android 11.0 (RR)",
            "customfield_11910.value": "",
            "customfield_11907": ["ZTA", "ZTR"],
            "customfield_10322.value": "",
        },
        "comment": [],
    },
    {
        "key": "PTC-254324",
        "fields": {
            "customfield_12601": "1716:19734567",
            "customfield_10301.value": "SM-A505G Galaxy-A50 SS/DS LTE",
            "customfield_12510": "SM-A505G Galaxy-A50 SS/DS LTE",
            "customfield_12712": "SM-A505G_LA_QQ_TTT",
            "customfield_13304.value": "Android 11.0 (RR)",
            "customfield_11910.value": "",
            "customfield_11907": [],
            "customfield_10322.value": "ZVV",
        },
        "comment": [],
    },
    {
        "key": "IMS-35089",
        "fields": {
            "customfield_12601": "MS23456789, MF98765432",
            "customfield_10301.value": "SM-A505G Galaxy-A50 SS/DS LTE",
            "customfield_12510": "SM-A505G Galaxy-A50 SS/DS LTE",
            "customfield_12712": "SM-A505G_LA_QQ_TPA",
            "customfield_13304.value": "Android 11.0 (RR)",
            "customfield_11910.value": "",
            "customfield_11907": [],
            "customfield_10322.value": "",
        },
        "comment": [],
    },
]


class Attribute(object):
    def __init__(self, attr=None, value=None, is_not_null=False):
        if attr and is_not_null:
            self.__dict__[attr] = value


class Jira_obj(object):
    def __init__(self, key: str, fields: dict, comments: list):

        self.set_fields(fields)
        self.key = key
        self.raw = {"fields": {"comment": {"comments": comments}}}

    def set_fields(self, fields: dict):
        self.fields = Attribute()
        for item in fields:
            key_fields = item.split(".")
            first_key = True
            current_item = None
            while len(key_fields) > 1:
                key = key_fields.pop(-1)
                if first_key:
                    first_key = False
                    if isinstance(fields[item], list):
                        current_item = Attribute(key, self.get_list_of_att(fields[item]), True)
                    else:
                        current_item = Attribute(key, fields[item], True)
                else:
                    current_item = Attribute(key, current_item, True)
            if current_item:
                self.fields.__dict__[key_fields[0]] = current_item
            else:
                if isinstance(fields[item], list):
                    self.fields.__dict__[key_fields[0]] = self.get_list_of_att(fields[item])
                else:
                    self.fields.__dict__[key_fields[0]] = fields[item]

    def get_list_of_att(self, itens_list):
        if itens_list:
            return [Attribute("value", i, True) for i in itens_list]
        else:
            return []


jira_meta_return_value = {
    "fields": {
        "customfield_13304": {
            "allowedValues": [
                {
                    "value": "Tizen 2.2",
                    "id": "16954",
                },
                {
                    "value": "Tizen 2.4",
                    "id": "24129",
                },
                {
                    "value": "Android 2.3.6",
                    "id": "16953",
                },
                {
                    "value": "Android 4.1 (JB)",
                    "id": "16951",
                },
                {
                    "value": "Android 4.1.2 (JB)",
                    "id": "16952",
                },
                {
                    "value": "Android 4.2 (JB)",
                    "id": "16949",
                },
                {
                    "value": "Android 4.2.2 (JB)",
                    "id": "16950",
                },
                {
                    "value": "Android 4.3 (JB)",
                    "id": "16946",
                },
                {
                    "value": "Android 4.3 (JBP)",
                    "id": "16956",
                },
                {
                    "value": "Android 4.4 (KK)",
                    "id": "16944",
                },
                {
                    "value": "Android 4.4.2 (KK)",
                    "id": "16947",
                },
                {
                    "value": "Android 4.4.4 (KK)",
                    "id": "16955",
                },
                {
                    "value": "Android 5.0 (LL)",
                    "id": "16943",
                },
                {
                    "value": "Android 5.1 (LL)",
                    "id": "16948",
                },
                {
                    "value": "Android 6.0 (MM)",
                    "id": "17400",
                },
                {
                    "value": "Android 7.0 (NN)",
                    "id": "19802",
                },
                {
                    "value": "Android 7.1 (NN)",
                    "id": "21000",
                },
                {
                    "value": "Android 8.0 (OO)",
                    "id": "21351",
                },
                {
                    "value": "Android 8.1 (GO)",
                    "id": "22100",
                },
                {
                    "value": "Android 8.1 (OO)",
                    "id": "21716",
                },
                {
                    "value": "Android 9.0 (GO)",
                    "id": "23408",
                },
                {
                    "value": "Android 9.0 (PP)",
                    "id": "22601",
                },
                {
                    "value": "Android 10.0 (QQ)",
                    "id": "24120",
                },
                {
                    "value": "Android 10.0 (GO)",
                    "id": "25500",
                },
                {
                    "value": "Android 11.0 (RR)",
                    "id": "26900",
                },
                {
                    "value": "N/A",
                    "id": "16957",
                },
                {
                    "value": "Non-Android",
                    "id": "16945",
                },
                {
                    "value": "Windows 10/Pro",
                    "id": "24319",
                },
            ]
        }
    }
}


def get_jira_side_effect():
    result = list()
    result.extend(
        [
            [Jira_obj(i["key"], i["fields"], i["comment"]) for i in jira_task_list]
            for _ in range(10)
        ]
    )

    return result
