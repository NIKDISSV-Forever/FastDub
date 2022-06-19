try:
    from FastDub.YT.Upload import Uploader
    from FastDub.YT.Upload.UploadVideo import VALID_PRIVACY_STATUSES
except ImportError:
    SUPPORTED = False
else:
    SUPPORTED = True
