"""Settings for the Corner Shop backend (demo, deliberately insecure)."""

DEBUG = True
ALLOWED_HOSTS = ["*"]
SECRET_KEY = "demo-django-insecure-9x!k2m#q7w@e5r8t-not-a-real-key"

INSTALLED_APPS = ["django.contrib.auth", "django.contrib.contenttypes", "shop"]
ROOT_URLCONF = "shop.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "cornershop",
        "USER": "cornershop",
        "PASSWORD": "Sup3rS3cretPassw0rd9x",
        "HOST": "db.internal",
    }
}

# Third-party payment gateway (demo values, not real credentials).
PAYMENT_API_KEY = "Zq8Lm2Xv9TnR4wKb7YcDp3Hs6Jf1Ga"
