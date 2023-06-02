from io import StringIO
import paramiko


def generate_keys():
    key = paramiko.RSAKey.generate(2048)
    privateString = StringIO()
    key.write_private_key(privateString)
    return f"{key.get_name()} {key.get_base64()}", privateString.getvalue()
