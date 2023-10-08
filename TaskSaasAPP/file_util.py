import mimetypes

def get_file_type(file):
    file_type, _ = mimetypes.guess_type(file.name)
    return file_type