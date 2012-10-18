# coding: utf-8
from __future__ import unicode_literals
import gzip
import io
import zipfile

class SparseZipFile(zipfile.ZipFile):
    def __init__(self, file, chunk_length=None):
        zipfile.ZipFile.__init__(self, file, mode="w",
                compression=zipfile.ZIP_STORED, allowZip64=True)
        self.chunk_length = chunk_length or 2 ** 10

    def write(self, filename, arcname=None, compress_type=None):
        raise NotImplemented

    def writestr(self, zinfo_or_arcname, bytes, compress_type=None):
        arcname = (zinfo_or_arcname.name
                if isinstance(zinfo_or_arcname, zipfile.ZipInfo)
                else zinfo_or_arcname)
        _, _, arcname = arcname.rpartition('.gz')
        gz = io.BytesIO()
        with gzip.GzipFile(filename=arcname.encode('utf-8'),
                mode='wb', fileobj=gz) as f:
            f.write(bytes)
        gz = gz.getvalue()
        arcname += '.gz'
        # TODO: len(ZipInfo.FileHeader(zinfo))
        header_len = 30 + len(arcname.encode('utf-8'))
        padding = b'\0' * (-(header_len + len(gz)) % self.chunk_length)
        zipfile.ZipFile.writestr(self, arcname, gz + padding,
                compress_type=zipfile.ZIP_STORED)
