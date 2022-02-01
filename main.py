import glob
import re
import argparse
import zipfile
from typing import List
from shutil import rmtree
import os
from os.path import splitext, basename, join
import rarfile

rarfile.UNRAR_TOOL = "unrar";


def list_cbz_files(folder): #-> List:
    print(f"Listing files in {folder}");
    result = glob.glob(f"{folder}/*.cbz") + glob.glob(f"{folder}/*.cbr");
    print(f"Found {len(result)} files");
    return sorted(result);

def list_pages(folder) -> List:

    pre3_folder = (fr"{folder}")
    pre2_folder=re.sub('\]','[]]',pre3_folder,count=1);
    folderfix=re.sub('\[','[[]',pre2_folder,count=1);

    jpgs = glob.glob(f"{folderfix}/**/*.jpg", recursive=True);
    pngs = glob.glob(f"{folderfix}/**/*.png", recursive=True);
    return sorted(jpgs + pngs)




def unpack_single_file(cbz_file: str, cbz_folder: str):
    cbz_short_filename = basename(cbz_file);
    name, extension = splitext(cbz_short_filename);
    if extension == ".cbz":
        try:
            archive_file = zipfile.ZipFile(cbz_file);
        except zipfile.BadZipFile:
            print(f"Maybe {cbz_file} is RAR file in fact?");
            archive_file = rarfile.RarFile(cbz_file);
    elif extension == ".cbr":
        try:
            archive_file = rarfile.RarFile(cbz_file);
        except rarfile.BadRarFile:
            print(f"Maybe {cbz_file} is ZIP file in fact?");
            archive_file = zipfile.ZipFile(cbz_file);
    else:
        print(cbz_file);
        print(extension);
        raise ValueError("Another extension");

    temp_folder = f"temp_{name}"
    archive_file.extractall(temp_folder);
    print("Unpacking Successful!");
    print(f"Moving unpacked ' {cbz_file} ' files to the temp folder");


    for filename in list_pages(temp_folder):
        print(f"Moving {filename} to main folder");
        os.renames(filename, join(f"{cbz_folder}", name, basename(filename)));
    try:
        rmtree(temp_folder);
    except FileNotFoundError:
        pass

def unpack_files(cbzs: List, cbz_folder: str):
    for cbz_file in cbzs:
        try:
            print("Starting unpacking the file: '", cbz_file, "'");
            unpack_single_file(cbz_file, cbz_folder);
        except Exception as e:
            print(f"Failed on {cbz_file}");
            raise


def pack_files(result_filename: str, cbz_folder: str):
    pages = list_pages(cbz_folder)
    print(f"Packing {len(pages)} pages to {result_filename}");
    with zipfile.ZipFile(result_filename, "w") as zf:
        for page in pages:
            zf.write(page);


def remove_temp_folder(cbz_folder: str):
    print(f"Removing temp folder {cbz_folder}");
    rmtree(cbz_folder);


def merge(lder: str, result_filename: str):
    cbz_folder = "cbz_merger_temp";

    rfolder = (fr"{lder}");
    fixrfolder=re.sub('\]','[]]',rfolder,count=1);
    folder=re.sub('\[','[[]',fixrfolder,count=1);

    if result_filename is None:
        result_filename = "result.cbz";
    elif not result_filename.endswith(".cbz"):
        result_filename = f"{result_filename}.cbz";

    try:
        os.remove(result_filename);
    except FileNotFoundError:
        pass

    cbzs = list_cbz_files(folder);
    print("List of found files: ", cbzs);
    unpack_files(cbzs, cbz_folder);
    pack_files(result_filename, cbz_folder);
    remove_temp_folder(cbz_folder);

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", "-d", help="Directory to scan for CBZ/CBR files");
    parser.add_argument("--result_name", "-r", help="Result name of the CBZ file");
    args = parser.parse_args();

    merge(lder=args.folder, result_filename=args.result_name);
