import argparse
import hashlib
import logging
import os
import schedule
import time
from collections import OrderedDict
from distutils.dir_util import copy_tree
import shutil


"""4 command line arguments created"""
args = argparse.ArgumentParser(description="Veeam back-up service")
args.add_argument("-s", "--sourcepath", required=True, help="Path of the source folder to be backed-up")
args.add_argument("-r", "--replicapath", required=True, help="Path of the replica folder")
args.add_argument('-l','--logfilepath', required=True ,help="Path of the log file")
args.add_argument('-t','--timeinterval', required=True, type=int, help="Back-up time interval in seconds")
arguments = args.parse_args()


"""Setting up the log file"""
logfile_path = os.path.join(arguments.logfilepath, "synclog.log")
logging.basicConfig(filename=logfile_path, level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s")


def md5(fname,size=4096):
    """This function is used to calculate the hash of the file. If you modify a file,
    then the name remains the same, but the hash gets changed"""
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(size), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def copy_dir(src, dst):
    """The function copies the whole directory with all subdirectories 
    and files"""
    copy_tree(src, dst)


def copy_file(file, dst):
    """The function copies one file to the destination directory"""
    shutil.copy(file, dst)


def del_file(file):
    """the function deletes one file from the destination folder"""
    os.remove(file)


def sourcepath_files(src):
    """The function creates ordered directory containing the file names with
    the hash of the files for all files from the source directory and its subdirectories; 
    keys == (hash, rel_path), items: file_path"""
    source_dict = OrderedDict()
    for root, dir, files in os.walk(src, topdown=True):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, start=arguments.sourcepath)
            hash1 = md5(file_path)
            source_dict[(hash1, rel_path)] = file_path
    return source_dict


def replicapath_files(dst):
    """The function creates ordered directory containing the file names with
    the hash of the files for all the files from replica directory and its subdirectories; 
    keys == (hash, rel_path), items: file_path"""
    replica_dict = OrderedDict()
    for root, dir, files in os.walk(dst, topdown=True):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, start=arguments.replicapath)
            hash1 = md5(file_path)
            replica_dict[(hash1, rel_path)] = file_path
    return replica_dict


def main(dst):
    """main function that sync the source folder into replica folder"""
    if not os.path.isdir(dst):
        """copies the whole source directory with all subfolders and files in case that
        the replica folder does not exist"""
        copy_dir(arguments.sourcepath, arguments.replicapath)
        print("FILES COPIED FROM THE SOURCE FOLDER TO THE REPLICA FOLDER:")
        logging.debug("FILES COPIED FROM THE SOURCE FOLDER TO THE REPLICA FOLDER:")
        for root, dir, files in os.walk(dst, topdown=True):
            for file in files:
                file_path = os.path.join(root, file)
                print(file_path)
                logging.debug(file_path)
    
    else:
        source_dict = sourcepath_files(arguments.sourcepath)
        replica_dict = replicapath_files(arguments.replicapath)

        """Creating an ordered directory of all the files from the source directory 
        that have been newly created or changed"""
        remaining_files = set(source_dict.keys()) - set(replica_dict.keys())
        remaining_files= [source_dict.get(k) for k in remaining_files]

        for file_path in remaining_files: 
            """every newly created or changed file in source directory is copied to the 
            replica directory including newly created subfolders"""
            os.path.split(file_path)
            rel_dir = os.path.relpath(file_path, arguments.sourcepath)
            file = os.path.split(file_path)[1]
            to_directory = os.path.join(arguments.replicapath, rel_dir)
            to_directory = os.path.split(to_directory)[0]
            if not os.path.isdir(to_directory):
                os.makedirs(to_directory)
            copy_file(file_path, to_directory)
            print("NEW FILE COPIED:")
            logging.debug("NEW FILE COPIED:")
            print(file_path)
            logging.debug(file_path)
            
        source_dict = sourcepath_files(arguments.sourcepath)
        replica_dict = replicapath_files(arguments.replicapath)

        """Creating an ordered directory of all the files from the source directory 
        that has been deleted"""
        excessive_files = set(replica_dict.keys()) - set(source_dict.keys())
        excessive_files= [replica_dict.get(k) for k in excessive_files]

        for file_path in excessive_files: 
            """every deleted file in source directory is as well deleted in replica directory"""
            os.path.split(file_path)
            rel_dir = os.path.relpath(file_path, arguments.replicapath)
            file = os.path.split(file_path)[1]
            from_directory = os.path.join(arguments.replicapath, rel_dir)
            from_directory = os.path.split(from_directory)[0]
            del_file(file_path)
            print("FILE DELETED:")
            logging.debug("FILE DELETED:")
            print(file_path)
            logging.debug(file_path)
           

if __name__ == "__main__":  
    schedule.every(arguments.timeinterval).seconds.do(main, dst=arguments.replicapath)
    while True:
        # Checks whether a scheduled task
        # is pending to run or not
        schedule.run_pending()
        time.sleep(1)
    



















