from datetime import datetime, timezone

from django.template.defaulttags import register


@register.simple_tag
def calculate_days(date):
    return (datetime.now(timezone.utc) - date).days
