from django.urls import path
from zanhu.news import views

app_name = "news" # 当前配置所在appname
urlpatterns = [
    path("", view=views.NewListView.as_view(), name="list"),
    path("post-news/", views.post_new, name="post_news"),
    path("delete/<str:pk>/", views.NewsDeleteView.as_view(), name="delete_news"),
    path("like/", views.like, name="post_like"),
    path("get-thread/",views.get_thread, name="get_thread"),
    path("post-comment/", views.post_comment, name="post_comment"),
    path("update-interactions/", views.update_interactions, name="update-interactions"),

]
