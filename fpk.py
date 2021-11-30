#!/usr/bin/env python3

# Created by: Master
# On: 11/28/2021 at 11:12 PM CST

import struct

from io import BytesIO
from typing import List

MAGIC = b'\x4F\x46\x50\x4B'


class FPK_File:

    class Header:

        def __init__(self, sector: int, b: int, size: int, d: int, fn: str):
            self.sector: int = sector
            self.b: int = b
            self.size: int = size
            self.d: int = d
            self.fn: str = fn
            return
        pass

    # noinspection PyTypeChecker
    def __init__(self, header: Header):
        self.header: FPK_File.Header = header
        self.data: bytes = None
        return

    pass


class FPK_Folder:  # 32 byte block

    class Header:

        def __init__(self, offset: int, files: int, fp: str):
            self.offset: int = offset  # 4 bytes
            self.files: files = files  # 24 bytes
            self.fp: str = fp  # 24 bytes
            return

        pass

    def __init__(self, header: Header):
        self.header: FPK_Folder.Header = header
        self.files: List[FPK_File] = list()
        return

    pass


class FPK:

    class Header:

        def __init__(self,
                     size_fpk: int,
                     folders: int,
                     idk_1: int,
                     idk_2: int,
                     idk_3: int,
                     offset_data_block: int,
                     idk_5: int
                     ):
            self.size_fpk: int = size_fpk
            self.folders: int = folders
            self.idk_1: int = idk_1
            self.idk_2: int = idk_2
            self.idk_3: int = idk_3
            self.offset_data_block: int = offset_data_block
            self.idk_5: int = idk_5
            return
        pass

    def __init__(self,
                 header: Header,
                 folders: List[FPK_Folder]
                 ):
        self.header = header
        self.folders: List[FPK_Folder] = folders
        return

    pass


def read_fpk_files(bytes_fpk: BytesIO, fpk: FPK):
    for fpk_folder in fpk.folders:
        for fpk_file in fpk_folder.files:
            bytes_fpk.seek(fpk_file.header.sector * 2048)
            fpk_file.data = bytes_fpk.read(fpk_file.header.size)
            continue
        continue
    return


def read_fpk_folders(bytes_fpk: BytesIO, folders: int) -> list[FPK_Folder]:
    fpk_folders: list[FPK_Folder] = list()
    for i in range(folders):
        bytes_folder_entry_chunk: bytes = bytes_fpk.read(32)
        offset_files: int = struct.unpack('<I', bytes_folder_entry_chunk[0:4])[0]
        files: int = struct.unpack('<I', bytes_folder_entry_chunk[4:8])[0]
        fp_folder: str = bytes_folder_entry_chunk[8:32].rstrip(b'\x00').decode(encoding='ascii')
        fpk_folders.append(
            FPK_Folder(
                FPK_Folder.Header(offset_files, files, fp_folder)
            )
        )

        print(f'Found folder \"{fp_folder}\"')
        continue
    del bytes_folder_entry_chunk
    del offset_files
    del files
    del fp_folder
    del i

    print()

    for fpk_folder in fpk_folders:
        bytes_fpk.seek(fpk_folder.header.offset)
        for i in range(fpk_folder.header.files):
            bytes_fpk_file_header = bytes_fpk.read(32)

            sector: int = struct.unpack('<I', bytes_fpk_file_header[0:4])[0]
            b: int = struct.unpack('<I', bytes_fpk_file_header[4:8])[0]
            size: int = struct.unpack('<I', bytes_fpk_file_header[8:12])[0]
            d: int = struct.unpack('<I', bytes_fpk_file_header[12:16])[0]
            fn: str = bytes_fpk_file_header[16:32].rstrip(b'\x00').decode(encoding='ascii')

            fpk_folder.files.append(
                FPK_File(
                    FPK_File.Header(sector, b, size, d, fn)
                )
            )

            print(f'Found file \"{fn}\" for folder \"{fpk_folder.header.fp[:-1]}\"')
            continue
        del bytes_fpk_file_header
        del sector
        del b
        del size
        del d
        del fn
        del i

        print()
        continue
    del fpk_folder
    return fpk_folders


def read_fpk(bytes_fpk: BytesIO) -> FPK:
    bytes_magic = bytes_fpk.read(4)
    if bytes_magic != MAGIC:
        print('Failed magic check!')
        print(f'Expected \"{MAGIC}\", but got \"{bytes_magic}\"!')
        return
    else:
        print('Passed magic check\n')
        pass
    del bytes_magic

    size_fpk = struct.unpack('<I', bytes_fpk.read(4))[0]  # size of entire fpk file
    folders = struct.unpack('<I', bytes_fpk.read(4))[0]  # number of folders in this fpk
    idk_1 = struct.unpack('<I', bytes_fpk.read(4))[0]  # ???

    idk_2 = struct.unpack('<I', bytes_fpk.read(4))[0]  # first folder..?
    idk_3 = struct.unpack('<I', bytes_fpk.read(4))[0]  # first folder offset..?
    offset_data_block = struct.unpack('<I', bytes_fpk.read(4))[0]
    idk_5 = struct.unpack('<I', bytes_fpk.read(4))[0]  # ???

    fpk = FPK(
        FPK.Header(size_fpk, folders, idk_1, idk_2, idk_3, offset_data_block, idk_5),
        read_fpk_folders(bytes_fpk, folders)
    )
    read_fpk_files(bytes_fpk, fpk)
    return fpk
