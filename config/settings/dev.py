import mimetypes

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = (
    "django-insecure-f-e6#p)-6(kyc8#j$0@ir+h56yg9+zr(^83etp=(s3sqlb#n_w"
)

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INSTALLED_APPS.append("debug_toolbar")
MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INTERNAL_IPS = ("127.0.0.1", "172.17.0.1")

# For django_toolbar
mimetypes.add_type("application/javascript", ".js", True)


try:
    from .local import *
except ImportError:
    pass
