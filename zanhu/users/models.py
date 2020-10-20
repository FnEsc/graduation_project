from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible # 为了让python2适应unicode兼容性
class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    """自定义模型"""
    # name = CharField(_("Name of User"), blank=True, max_length=255) # CharField后接下划线相当于别名

    nickname = models.CharField(null=True,blank=True,max_length=255,verbose_name="昵称") # null=True表示可以为空，verbose_name别名
    job_title = models.CharField(null=True,blank=True,max_length=50,verbose_name="职业")
    introduction = models.TextField(null=True,blank=True,verbose_name="简介")
    picture = models.ImageField(null=True,blank=True,verbose_name="头像",upload_to="profile_pics/")
    city = models.CharField(null=True,blank=True,max_length=50,verbose_name="城市")
    personal_url = models.URLField(null=True,blank=True,max_length=255,verbose_name="个人链接")
    weibo = models.URLField(null=True, blank=True, max_length=255, verbose_name="微博")
    zhihu = models.URLField(null=True, blank=True, max_length=255, verbose_name="知乎")
    github = models.URLField(null=True, blank=True, max_length=255, verbose_name="Github")
    Linkedin = models.URLField(null=True, blank=True, max_length=255, verbose_name="Linkedin")
    created_at = models.DateTimeField(auto_now_add=True,verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name_plural = verbose_name = "用户"

    def __str__(self):
        return self.username

    def get_absolute_url(self): # 返回用户详情页url
        return reverse("users:detail", kwargs={"username": self.username})

    def get_profile_name(self):
        return self.nickname if bool(self.nickname)==True else self.username
