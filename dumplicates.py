import hashlib
import os
import pathlib
import time
from multiprocessing import Pool
from typing import List, Any


class file_info:
    def __init__(self, name):
        self.name = name
        self.sum = ''
        self.size = 0

    def __str__(self):
        return 'name:{} size:{}'.format(self.name, self.size)

    def set(self, sum, size):
        self.sum = sum
        self.size = size


def get_file_data(file):
    finfo = file_info(file)
    try:
        with open(file, 'rb') as fd:
            data = fd.read()
            finfo.set(hashlib.blake2b(data).hexdigest(), os.path.getsize(file))
    except (PermissionError, IOError) as err:
        print('{}: {}'.format(file, err))
        pass
    return finfo


def size_sort(elem):
    return elem.size


def sum_sort(elem):
    return elem.sum


def get_file_list(dirname, ext, files):
    try:
        for f in os.scandir(dirname):
            if f.is_dir():
                get_file_list(f.path, ext, files)
            elif f.is_file():
                if ext == '' or f.path.endswith(ext):
                    files.append(f.path)
    except PermissionError as err:
        print('{}'.format(err))


def do_work(dir, ext, threads):
    files = []
    start = time.perf_counter_ns()
    get_file_list(dir, ext, files)
    duration = time.perf_counter_ns() - start
    msg = 'time to find {} files was {:.2f} secs'.format(len(files), duration / 1000000000.0)
    print(msg)

    with Pool(processes=threads) as pool:
        finfos = pool.map(get_file_data, files)
        pool.close()
        pool.join()
        finfos.sort(key=sum_sort)
    return finfos


def show_finfos(finfos):
    dupes = []
    for i in range(0, len(finfos) - 1):
        finfo = finfos[i]
        if finfo.sum == finfos[i + 1].sum:
            dupes.append(finfo)
    return dupes


def get_file_infos(dir, ext):
    print('starting at ' + dir)
    finfos = do_work(dir, ext, 8)
    return finfos