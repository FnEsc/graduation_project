from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views import defaults as default_views
from zanhu.news.views import NewListView

urlpatterns = [
                  # path("home/", TemplateView.as_view(template_name="pages/home.html"), name="home"),
                  # 此处重置Homepage到Newslist页面
                  path("", NewListView.as_view(), name="home"),
                  path("about/", TemplateView.as_view(template_name="pages/about.html"), name="about"),
                  # User management
                  path("users/", include("users.urls", namespace="users")),
                  path("accounts/", include("allauth.urls")),
                  # 第三方类url
                  path('markdownx/', include('markdownx.urls')),
                  path('comments/', include('django_comments.urls')),
                  # Your stuff: custom urls includes go here
                  path("news/", include("news.urls", namespace="news")),
                  path("article/", include("article.urls", namespace="article")),
                  path("question/", include("question.urls", namespace="question")),
                  path("messager/", include("messager.urls", namespace="messager")),
                  path("notifications/", include("notifications.urls", namespace="notifications")),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
