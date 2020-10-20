from django.http import HttpResponseBadRequest
from django.views.generic import View
from django.core.exceptions import PermissionDenied

from functools import wraps

def ajax_required(f):
    """验证是否为ajax请求"""

    @wraps(f)
    def wrap(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest("不是ajax请求！")
        return f(request, *args, **kwargs)
    return wrap

class AuthorRequiredMixin(View):
    """验证当前news为原作者，用于删除news或编辑news"""

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().user.username != self.request.user.username:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
