# uploads.py
'''Upload user and project pictures'''

from app import s3


def upload_to_s3(bucket=None, file=None, user_id=None, project_id=None,
                 file_name=None):
    '''
    Main function to S3 uploading, depends on properly placed .aws folder at
    home directory

    Args:
        bucket (str): Bucket which the incoming file should be placed
        file (file): Incoming file
        user_id (int): User id for indentification purposes
        project_id (int): Project_id for indentifications purposes
        file_name (str): Name string that will be placed on upload

    Raises:
        Custom Exception when can't properly connect to AWS bucket.

    Returns:
        void
    '''
    if s3.buckets.all() is None:
        raise Exception("No s3 bucket found")
    if user_id:
        s3.Bucket(bucket).put_object(
            Key='profile_pictures/'+str(user_id)+'_profile_pic.'+file.mimetype.split('image/')[1],
            Body=file, ACL='public-read')
    if project_id:
        s3.Bucket(bucket).put_object(
            Key='projects/'+str(project_id)+'_'+file_name+'_arrang_pic.'+file.mimetype.split('image/')[1],
            Body=file, ACL='public-read')
