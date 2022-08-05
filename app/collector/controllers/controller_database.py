import copy
import logging

from app.collector.models import (
    AndroidOs,
    CarrierInformation,
    Changelists,
    ModelInfo,
    QueryHistory,
    TasksInformation,
)
from asgiref.sync import sync_to_async

CONTROLLER_API = "database"
logger = logging.getLogger(__name__)


class ControllerDatabase:
    def __init__(self):
        self.android_os_model = AndroidOs
        self.carrier_information_model = CarrierInformation
        self.changelists_model = Changelists
        self.model_info_model = ModelInfo
        self.query_history_model = QueryHistory
        self.tasks_information_model = TasksInformation

    @sync_to_async
    def get_os_version_info(self, os_version: str) -> dict:
        os_info_list = [i for i in self.android_os_model.objects.filter(pk=os_version)]
        return os_info_list[0] if os_info_list else None

    @sync_to_async
    def get_os_version_list(self) -> dict:
        os_info_list = [
            i for i in self.android_os_model.objects.all().values_list("pk", flat=True)
        ]
        return os_info_list

    @sync_to_async
    def update_os_version_db(self, os_list: list):
        for os in os_list:
            self.android_os_model.objects.get_or_create(**os)

    @sync_to_async
    def get_model_info(self, short_model_name: str, os_version: str) -> list:
        result = self.model_info_model.objects.filter(
            short_model_name=short_model_name, os_id=os_version
        )
        result_list = [i for i in result]
        return result_list

    @sync_to_async
    def update_model_info_db(self, model_info_list: list):
        for model_info in model_info_list:
            self.model_info_model.objects.get_or_create(**model_info)

    @sync_to_async
    def get_carrier_info(self) -> list:
        carrier_list = [i.carrier_code for i in self.carrier_information_model.objects.all()]
        return sorted(carrier_list)

    @sync_to_async
    def update_carrier_info(self, carrier_code: str):
        self.carrier_information_model.objects.get_or_create(carrier_code=carrier_code)

    @sync_to_async
    def get_task_information(self, short_model_name: dict) -> list:
        result = self.tasks_information_model.objects.filter(
            model__short_model_name=short_model_name
        )
        return [i for i in result]

    @sync_to_async
    def update_task_information(self, task_code: str, model_list: list):
        for model in model_list:
            self.tasks_information_model.objects.get_or_create(
                task_code=task_code, model=model
            )

    @sync_to_async
    def update_changelist_information(self, changelist_list: list, model_list: list):
        existing_cl_list = [
            i
            for i in self.changelists_model.objects.filter(
                model__project__in=[model.project for model in model_list]
            ).values_list("cl_number", flat=True)
        ]

        bulk_list = list()
        mtom_fields_dic = dict()
        for model in model_list:
            task_dict = {
                i[0]: i[1]
                for i in self.tasks_information_model.objects.filter(model=model).values_list(
                    "task_code", "id"
                )
            }
            mtom_fields_dic[model.project] = dict()
            for cl_info in changelist_list:
                cl_info_copy = copy.deepcopy(cl_info)
                carrier_info = cl_info_copy.pop("carrier_info")
                task_info = cl_info_copy.pop("task_list")

                mtom_fields_dic[model.project][cl_info["cl_number"]] = {
                    "task_ids": [task_dict[task] for task in task_info],
                    "carrier_ids": [carrier for carrier in carrier_info],
                }

                if cl_info_copy["cl_number"] not in existing_cl_list:
                    cl_info_copy["model"] = model
                    bulk_list.append(Changelists(**cl_info_copy))

        self.changelists_model.objects.bulk_create(bulk_list, ignore_conflicts=True)

        through_task = Changelists.task_list.through
        through_carrier = Changelists.carrier_info.through

        bulk_tasks = list()
        bulk_carriers = list()

        for model in model_list:
            changelis_ids_dict = {
                i[0]: i[1]
                for i in self.changelists_model.objects.filter(
                    model=model, cl_number__in=[j["cl_number"] for j in changelist_list]
                ).values_list("cl_number", "id")
            }

            for changelist in [j["cl_number"] for j in changelist_list]:
                task_id_list = mtom_fields_dic[model.project][changelist]["task_ids"]
                carrier_id_list = mtom_fields_dic[model.project][changelist]["carrier_ids"]
                for task_id in task_id_list:
                    bulk_tasks.append(
                        through_task(
                            **{
                                "changelists_id": changelis_ids_dict[changelist],
                                "tasksinformation_id": task_id,
                            }
                        )
                    )

                for carrier_id in carrier_id_list:
                    bulk_carriers.append(
                        through_carrier(
                            **{
                                "changelists_id": changelis_ids_dict[changelist],
                                "carrierinformation_id": carrier_id,
                            }
                        )
                    )

        through_task.objects.bulk_create(bulk_tasks, ignore_conflicts=True)
        through_carrier.objects.bulk_create(bulk_carriers, ignore_conflicts=True)

    @sync_to_async
    def get_date_information(self, short_model_name: str, os_version: AndroidOs) -> list:
        date_list = self.query_history_model.objects.filter(
            model__short_model_name=short_model_name, os=os_version
        ).all()

        if date_list.count():
            return date_list[0].date.strftime("%Y/%m/%d")
        else:
            return ""

    @sync_to_async
    def set_date_information(self, model_list: list, os_version: AndroidOs, date: str) -> list:
        for model in model_list:
            is_updated = self.query_history_model.objects.filter(
                model=model, os=os_version
            ).update(date=date)
            if not is_updated:
                self.query_history_model.objects.create(model=model, os=os_version, date=date)

    @sync_to_async
    def get_cl_database_list(self, short_model_name: list) -> list:
        cl_info = self.changelists_model.objects.filter(
            model__short_model_name=short_model_name
        ).values_list("cl_number", flat=True)
        return [cl for cl in cl_info]

    @sync_to_async
    def get_cl_database(self, short_model_name: str, os_version: str) -> list:
        database_list = list(
            self.changelists_model.objects.filter(
                model__short_model_name=short_model_name, os_id=os_version
            ).values(
                "branch",
                "carrier_info",
                "cl_number",
                "cl_source",
                "cl_type",
                "comment",
                "is_smr",
                "model__short_model_name",
                "os_id",
                "relevance",
                "task_list__task_code",
            )
        )
        cl_dict = dict()
        for cl_info in database_list:
            cl_number = cl_info["cl_number"]
            if cl_number not in cl_dict:
                cl_dict[cl_number] = dict()
                cl_dict[cl_number]["task_list"] = set()
                cl_dict[cl_number]["carrier_info"] = set()

            cl_dict[cl_number]["task_list"].add(cl_info["task_list__task_code"])
            cl_dict[cl_number]["carrier_info"].add(cl_info["carrier_info"])

        result_list = list()
        for cl_info in database_list:
            changelist = cl_info["cl_number"]
            if changelist in cl_dict.keys():
                carriers_and_tasks = cl_dict.pop(changelist)
                result_item = cl_info.copy()
                result_item.pop("task_list__task_code")
                result_item.pop("carrier_info")
                result_item["model_name"] = result_item.pop("model__short_model_name")
                result_item["task_code"] = list(carriers_and_tasks["task_list"])
                result_item["carrier_info"] = list(carriers_and_tasks["carrier_info"])

                result_item["task_code"].sort()
                result_item["carrier_info"].sort()

                result_list.append(result_item)

        return sorted(result_list, key=lambda a: int(a["cl_number"]))
