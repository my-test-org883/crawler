from django.db import models


class AndroidOs(models.Model):
    os_version = models.CharField(max_length=25, blank=False, unique=True, primary_key=True)
    os_code = models.CharField(max_length=3, blank=False)

    def __str__(self):
        return self.os_version

    class Meta:
        verbose_name_plural = "Android Os DB"


class ModelInfo(models.Model):
    short_model_name = models.CharField(max_length=15, blank=False)
    project = models.CharField(max_length=50, blank=False, unique=True)
    model_name = models.CharField(max_length=50, blank=False)
    os = models.ForeignKey(AndroidOs, on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return self.project

    class Meta:
        verbose_name_plural = "Model Information"


class TasksInformation(models.Model):
    task_code = models.CharField(max_length=50, blank=False)
    model = models.ForeignKey(ModelInfo, on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return self.task_code

    class Meta:
        unique_together = ("task_code", "model")
        verbose_name_plural = "Tasks Information"


class CarrierInformation(models.Model):
    carrier_code = models.CharField(max_length=3, blank=False, primary_key=True)

    def __str__(self):
        return self.carrier_code

    class Meta:
        verbose_name_plural = "Carrier Database"


class Changelists(models.Model):
    cl_number = models.CharField(max_length=15, blank=False)
    task_list = models.ManyToManyField(TasksInformation)
    model = models.ForeignKey(ModelInfo, on_delete=models.CASCADE, blank=False)
    os = models.ForeignKey(AndroidOs, on_delete=models.CASCADE, blank=False)
    branch = models.CharField(max_length=100, blank=False)
    cl_source = models.CharField(max_length=50, blank=False)
    cl_type = models.CharField(max_length=5, blank=False)
    relevance = models.CharField(max_length=50, blank=True)
    is_smr = models.BooleanField(blank=False, default=False)
    carrier_info = models.ManyToManyField(CarrierInformation)
    comment = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.cl_number}"

    class Meta:
        unique_together = ("cl_number", "model", "cl_type")
        verbose_name_plural = "Changelists"


class QueryHistory(models.Model):
    model = models.ForeignKey(ModelInfo, on_delete=models.CASCADE, blank=False)
    os = models.ForeignKey(AndroidOs, on_delete=models.CASCADE, blank=False)
    date = models.DateField(blank=False)

    def __str__(self):
        return f"{self.model} {self.os} ({self.date})"

    class Meta:
        unique_together = ("model", "os")
        verbose_name_plural = "Query History"
