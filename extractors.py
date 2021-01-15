"""
Functions to extract layer files from 7zip files
"""

import re
import subprocess
import os

try:
    from py7zr import SevenZipFile
except ImportError:
    pass


class ProgramNotFoundError(Exception):
    pass


filter_pattern = re.compile(r'BDTOPO_\d-\d_TOUSTHEMES_SHP_LAMB93_[DR]\d+_\d{4}-\d\d-\d\d/BDTOPO/'
                + r'1_DONNEES_LIVRAISON_\d{4}-\d\d-\d+/'
                + r'BDT_\d-\d_SHP_LAMB93_[DR]\d+-ED\d{4}-\d\d-\d\d/'
                + r'([A-Z_]+)/([A-Z_]+)\.\w\w\w$')


def _test_file(f):
    rep = f.replace('\\', '/')
    return filter_pattern.search(rep)


def py7zr_available():
    try:
        import py7zr
    except ImportError:
        return False
    return True


def extract_py7zr(archive_path, theme, layer_name, target_dir):
    """
        Extraction using py7zr package
    """
    with SevenZipFile(archive_path, 'r') as archive:
        # Extracts the compressed shapefile
        to_extract = []
        for f in archive.getnames():
            match = _test_file(f)
            if match and theme == match.group(1) and layer_name == match.group(2):
                to_extract.append(f)
        archive.extract(targets=to_extract, path=target_dir)
    return os.path.join(target_dir, layer_name + '.shp')


def extract_7zip(archive_path, theme, layer_name, target_dir, 
                 executable='7z', callback=None):
    """
    Extraction using the 7z program.
    It must be installed on the sytem.
    """
    if not executable:
        raise ProgramNotFoundError()
    args = [executable, 'l', archive_path, '-sccUTF-8']
    # get file list
    try:
        completed = subprocess.run(args, capture_output=True, text=True)
    except FileNotFoundError:
        raise ProgramNotFoundError("The 7zip program was not found")
    completed.check_returncode()
    output = completed.stdout

    shape_files = []
    for li in output.split("\n"):
        if re.match(r'^\d\d\d\d-\d\d-\d\d', li):
            parts = re.split(r'\s+', li)
            subpath = parts[-1]
            match = _test_file(subpath)
            if match and theme == match.group(1) \
                    and layer_name == match.group(2):
                shape_files.append(subpath)
    for i, f in enumerate(shape_files):
        completed = subprocess.run([executable, 'e',
                    '-o' + target_dir, '-y', archive_path, f],
                    capture_output=True)
        completed.check_returncode()
        if callback:
            callback(i, len(shape_files))
    return os.path.join(target_dir, layer_name + '.shp')


def get_folder(folder_path, theme, layer_name):
    """
    Searches for the layer file in the data folder
    """
    for dirpath, _, filenames in os.walk(folder_path):
        for f in filenames:
            fpath = os.path.join(dirpath, f)
            ext = os.path.splitext(f)[1]
            match = _test_file(fpath)
            if match and ext == '.shp' and theme == match.group(1) \
                    and layer_name == match.group(2):
                return fpath
