import hashlib
import os
import time
from concurrent.futures.thread import ThreadPoolExecutor


class file_info:
    def __init__(self, name):
        self.name = name
        self.size = os.path.getsize(name)
        self.sum = '0'

    def __str__(self):
        return 'name:{} size:{}'.format(self.name, self.size)


def get_sum(finfo):
    try:
        with open(finfo.name, 'rb') as fd:
            data = fd.read()
            finfo.sum = hashlib.blake2b(data).hexdigest()
    except (PermissionError, IOError) as err:
        print('{}: {}'.format(finfo.name, err))


def get_file_list(dirname, ext, files):
    try:
        for f in os.scandir(dirname):
            if f.is_dir():
                get_file_list(f.path, ext, files)
            elif f.is_file():
                if ext == '' or f.path.endswith(ext):
                    files.append(file_info(f.path))
    except PermissionError as err:
        print('{}'.format(err))


def by_size(finfo):
    return finfo.size


def print_timing(start, msg):
    duration = time.perf_counter_ns() - start
    out = 'time to {} was {:.2f} secs'.format(msg, duration / 1000000000.0)
    print(out)


def get_file_infos(dir, ext):
    print('starting at ' + dir)
    files = []
    start = time.perf_counter_ns()
    get_file_list(dir, ext, files)
    files.sort(key=by_size)
    print_timing(start, 'find files')

    start = time.perf_counter_ns()
    with ThreadPoolExecutor(max_workers=3) as executor:
        for i in range(0, len(files) - 1):
            if files[i].size == files[i+1].size:
                executor.submit(get_sum, (files[i]))
    print_timing(start, 'compute sums')
    return files


def show_dupes(finfos):
    dupes = []
    for i in range(0, len(finfos) - 1):
        finfo = finfos[i]
        if finfo.sum != '0' and finfo.sum == finfos[i+1].sum:
            dupes.append(finfo)
    return dupes