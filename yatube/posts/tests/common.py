from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def create_test_image(name: str = 'giffy.gif') -> bytes:
    file = BytesIO()
    image = Image.new('RGBA', size=(50, 50), color=(155, 0, 0))
    image.save(file, 'gif')
    file.name = name
    file.seek(0)
    return file.read()


def get_image(name: str = 'giffy.gif') -> SimpleUploadedFile:
    return SimpleUploadedFile(
        name=name,
        content=create_test_image(name),
        content_type='image/gif',
    )
