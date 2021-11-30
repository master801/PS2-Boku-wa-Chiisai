#!/usr/bin/env python3

# Created by: Master
# On: 11/28/2021 at 10:31 PM CST

import os
from io import BytesIO

import fpk

fp_fpk = 'PACKFILE.FPK'


def extract_fpk(fpk_packfile: fpk.FPK):
    for folder in fpk_packfile.folders:
        fp_folder = f'EXTRACTED/{folder.header.fp}'

        if not os.path.exists(fp_folder):
            os.makedirs(fp_folder)
            pass

        for file in folder.files:
            fp_file = f'{fp_folder}{file.header.fn}'

            if not os.path.exists(fp_file):
                io_file = open(fp_file, mode='xb')
                io_file.write(file.data)
                io_file.flush()
                io_file.close()
                pass
            continue
        continue
    return


def read_fpk() -> fpk.FPK:
    io_packfile = open(fp_fpk, mode='rb+')

    io_bytes_packfile = BytesIO(io_packfile.read())
    fpk_packfile: fpk.FPK = fpk.read_fpk(io_bytes_packfile)
    io_bytes_packfile.close()

    io_packfile.close()
    return fpk_packfile


def main():
    if not os.path.exists(fp_fpk):
        print(f'File \"{fp_fpk}\" does not exist!')
        return

    fpk_packfile: fpk.FPK = read_fpk()
    extract_fpk(fpk_packfile)
    return


if __name__ == '__main__':
    main()
    pass
