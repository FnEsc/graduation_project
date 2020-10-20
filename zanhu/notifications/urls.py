from django.urls import path
from zanhu.notifications import views

app_name = "notifitions"  # 当前配置所在appname
urlpatterns = [
    path("", view=views.NotificationUnreadListView.as_view(), name="unread"),
    path("latest-notifications/", view=views.get_latest_notifications, name="latest_notifications"),
    path("mark-as-read/<str:slug>/", view=views.mark_as_read, name="mark_as_read"),
    path("mark-all-as-read/", view=views.mark_all_as_read, name="mark_all_as_read"),

]
