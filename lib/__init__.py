import hashlib
import time


def md5string(x):
    return hashlib.md5(x.encode()).hexdigest()

def timestamp_to_str(timestamp, format_str="%Y-%m-%d %H:%M:%S"):
    return time.strftime(format_str,
                         time.localtime(timestamp))