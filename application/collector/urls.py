from django.conf.urls import url

from . import view

urlpatterns = [
    url(r"^update_changelists$", view.UpdateChangelists.as_view()),
    url(r"^get_changelists$", view.GetChangelists.as_view()),
    url(r"^get_os_version_list", view.GetOsList.as_view()),
]
