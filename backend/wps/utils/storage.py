import os

from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.utils.deconstruct import deconstructible


@deconstructible
class DataStorage(FileSystemStorage):
    def __init__(self, base_url=settings.DATA_URL,
                 location=settings.DATA_DIR, subdir=''):

        self.location = location
        self.subdir = subdir
        self.base_url = base_url

        super().__init__(location=os.path.join(self.location, self.subdir), base_url=self.base_url)

    def __eq__(self, other):
        return self.subdir == other.subdir
