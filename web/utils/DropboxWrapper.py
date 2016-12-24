import dropbox
import os
import traceback

token = os.environ.get('DROPBOX_ACCESS_TOKEN')
if not token:
    import config
    token = os.environ.get('DROPBOX_ACCESS_TOKEN')

box = dropbox.Dropbox(token)

def delete_submission(submission_id):
    try:
        box.files_delete('/{}.stl.gz'.format(submission_id))
        return True
    except:
        traceback.print_exc()
        return False

def add_submission(submission_id, file_data):
    try:
        box.files_upload(file_data, '/{}.stl.gz'.format(submission_id))
        return True
    except:
        traceback.print_exc()
        return False

def get_submission(submission_id, path):
    name = '{}.stl.gz'.format(submission_id)
    try:
        box.files_download_to_file(path, '/' + name)
        return True
    except:
        traceback.print_exc()
        return False
