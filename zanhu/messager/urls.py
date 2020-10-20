from django.urls import path
from zanhu.messager import views

app_name = "messager"  # 当前配置所在appname
urlpatterns = [
    path("", view=views.MessagesListView.as_view(), name="messages_list"),

    path("send-message/", view=views.send_message, name="send_message"),
    path("<str:username>/", view=views.MessagesConversationListView.as_view(), name="messages_conversation_detail"),
]
