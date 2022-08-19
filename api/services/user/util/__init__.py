def encode_password(password:str):
    from hashlib import md5
    return md5(bytes(password,'utf-8')).hexdigest()