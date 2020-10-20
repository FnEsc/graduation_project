from django.urls import path
from zanhu.article import views

app_name = "article" # 当前配置所在appname
urlpatterns = [
    path("", view=views.ArticleListView.as_view(), name="list"),
    path("write-new-article/", view=views.ArticleCreateView.as_view(), name="write_new"),
    path("drafts/", view=views.DraftListView.as_view(), name="drafts"),
    path("<str:slug>/", view=views.ArticleDetailView.as_view(), name="article"), # 阅读全文用slug
    path("edit/<int:pk>/", view=views.ArticleEditView.as_view(), name="edit_article"), # 编辑文章用pk(id)
]
