class ApiResponse:
    def __init__(self):
        self.status_code = {"success": 200, "fail": 400, "error": 500}
        self.error_message = ""
        self.ready = False
        self.result_list = []
        self.model_name = ""
        self.os_version = ""

    def serialize(self, status_code: str) -> dict:
        mapped_object = {
            "has_error": True if self.error_message else False,
            "error_message": self.error_message,
            "is_ready": True if self.error_message else self.ready,
            "result_list": self.result_list if not self.error_message and self.ready else "",
        }
        if self.model_name:
            mapped_object["model_name"] = self.model_name
        if self.os_version:
            mapped_object["os_version"] = self.os_version
        return mapped_object, self.status_code[status_code]
