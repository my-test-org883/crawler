import re


def get_cls_from_string(cl_string: str) -> list:
    if cl_string:
        regex_cl_submit = r"([A-Za-z]?\d{7,})"
        cl_list = re.findall(regex_cl_submit, cl_string)
        return [i for i in cl_list if is_valid_int(i)]
    else:
        return []


def is_valid_int(number_str):
    try:
        int(number_str)
        return True
    except ValueError:
        return False


def create_cl_dict(tasks: list) -> dict:
    cl_dict = dict()
    for task in tasks:
        for cl in task["cls"]:
            if cl not in cl_dict.keys():
                cl_dict[cl] = {
                    "task": [task["task_info"]],
                    "carrier_list": task["carrier_list"],
                    "source": task["source"],
                }
            else:
                if task["task_info"] not in cl_dict[cl]["task"]:
                    cl_dict[cl]["task"].append(task["task_info"])
                for carrier in task["carrier_list"]:
                    if carrier not in cl_dict[cl]["carrier_list"]:
                        cl_dict[cl]["carrier_list"].append(carrier)
    return cl_dict


def merge_dict(dict1: dict, dict2: dict) -> dict:
    for key in dict2.keys():
        if key not in dict1.keys():
            dict1[key] = dict2[key].copy()
        else:
            dict1[key]["task"].extend(dict2[key]["task"].copy())
            dict1[key]["task"] = list(set(dict1[key]["task"]))
            dict1[key]["task"].sort()
    return dict1
