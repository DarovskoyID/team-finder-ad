import re
from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


def validate_github_url(value):
    if not value:
        return
    URLValidator(schemes=["http", "https"])(value)
    url = urlsplit(value)
    if (
        url.hostname not in {"github.com", "www.github.com"}
        or url.username is not None
        or url.password is not None
        or url.port not in {None, 80, 443}
    ):
        raise ValidationError("Укажите ссылку на github.com.")


def normalize_phone(value):
    if not value:
        return None
    if not re.fullmatch(r"(?:8|\+7)[0-9]{10}", value):
        raise ValidationError(
            "Номер должен быть в формате 8XXXXXXXXXX "
            "или +7XXXXXXXXXX."
        )
    return "+7" + value[-10:]


def validate_phone(value):
    normalize_phone(value)
