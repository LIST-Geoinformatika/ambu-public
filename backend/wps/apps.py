import logging

from django.apps import AppConfig
from django.db.utils import ProgrammingError

logger = logging.getLogger(__name__)


class WpsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wps"

    def ready(self):
        try:
            import wps.signals  # noqa
        except ProgrammingError as e:
            custom_error_msg = "Error when importing wps signals. Make sure all migrations are applied"
            logger.critical("{}\nVerbose: {}".format(custom_error_msg, str(e)))
