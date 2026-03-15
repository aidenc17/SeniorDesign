import hashlib

# returns the md5 checksum of specified file
def md5_file(filename):

    md5 = hashlib.md5()

    with open(filename, "rb") as file:
        while True:
            data = file.read(4096)
            if not data:
                break
            md5.update(data)

    return md5.hexdigest()


