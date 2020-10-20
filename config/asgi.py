import os, sys
import django
from channels.routing import get_default_application

# 从wsgi复制配置过来
app_path = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
)
sys.path.append(os.path.join(app_path, "zanhu"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()
application = get_default_application()
