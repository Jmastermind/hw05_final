from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def get_image(name: str = 'giffy.gif') -> SimpleUploadedFile:
    file = BytesIO()
    Image.new('RGBA', size=(1, 1), color=(155, 0, 0)).save(file, 'gif')
    file.name = name
    file.seek(0)
    return SimpleUploadedFile(
        name=name,
        content=file.read(),
        content_type='image/gif',
    )
