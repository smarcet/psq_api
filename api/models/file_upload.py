from drf_chunked_upload.models import ChunkedUpload


class FileUpload(ChunkedUpload):
    pass
# Override the default ChunkedUpload to make the `user` field nullable
FileUpload._meta.get_field('user').null = True