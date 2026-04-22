import os
import networkx as nx
import matplotlib.pyplot as plt
import re
from typing import Dict, List, Tuple, Set, Any
import openai # check version
import copy           
from copy import deepcopy
from collections import defaultdict, deque
import shutil
import subprocess
from functools import reduce
import clang.cindex
clang.cindex.Config.set_library_file('/usr/lib/llvm-19/lib/libclang.so.1')
#clang.cindex.Config.set_library_file('/opt/homebrew/opt/llvm/lib/libclang.dylib') # for mac os
from clang.cindex import CursorKind
import tempfile
from pydantic import BaseModel
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import anthropic
from anthropic import InternalServerError #, BadRequestError
from openai import BadRequestError
import base64
import tiktoken
import chardet
#from pycparser import c_parser, c_ast
import replicate
#import google.generativeai as genai  
from typing import List, Any
#from google.generativeai.protos import Content, Part
import json
import requests
from datetime import datetime # import datetime
from clang.cindex import Index, CursorKind, TypeKind
from pathlib import Path
import threading
from typing import Dict, List, Set, Tuple
from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple, NamedTuple
import http.server
import socketserver
from functools import partial
import atexit
import traceback
import signal
import logging
from functools import partial
from typing import Optional, Union
import time
from threading import Timer
from datetime import datetime, timedelta
import select
import matplotlib.pyplot as plt
import platform
import matplotlib.image as mpimg
from graphviz import Digraph
import webbrowser
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import random
from typing import List, Optional
import pwd
import grp
from pathlib import Path
import glob
from threading import Thread
from collections import defaultdict
from typing import Dict, List, Set, Tuple
import clang.cindex
from pathlib import Path
from typing import List, Set, Dict, Optional, Tuple
from clang.cindex import Index, CursorKind, TranslationUnit
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Set, Tuple
from pathlib import Path
import subprocess
from clang.cindex import Index, CursorKind, Config
from threading import Thread
import argparse
from clang.cindex import CompilationDatabase, Index
from datetime import datetime, timedelta
from typing import Optional
import subprocess
from typing import Dict, List, Tuple, Any
import threading
from datetime import datetime
import string
from openai import AzureOpenAI
from collections import Counter
from clang.cindex import Index, CursorKind, TokenKind
from clang.cindex import CompilationDatabase, Index
from clang.cindex import CompilationDatabase, CompilationDatabaseError
#import datetime
from collections import defaultdict
from openai import OpenAI
import numpy as np
import random
from anthropic import AnthropicBedrock
import sys
import subprocess
import fcntl
import select
from typing import Tuple
import pty
import subprocess
import termios
import tty
from pathlib import Path
import stat
import ijson
from pathlib import Path
import random
import string



@dataclass
class LineCoverage:
    line_number: int
    is_covered: bool
    execution_count: int

class CoverageData:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.lines: Dict[int, LineCoverage] = {}
    
    def add_line(self, line_number: int, execution_count: int):
        self.lines[line_number] = LineCoverage(
            line_number=line_number,
            is_covered=execution_count > 0,
            execution_count=execution_count
        )
    
    def to_dict(self):
        return {
            'file_path': self.file_path,
            'lines': {
                str(line_num): {
                    'line_number': line.line_number,
                    'is_covered': line.is_covered,
                    'execution_count': line.execution_count
                }
                for line_num, line in self.lines.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        coverage = cls(data['file_path'])
        for line_num, line_data in data['lines'].items():
            coverage.add_line(
                int(line_data['line_number']),
                line_data['execution_count']
            )
        return coverage



def count_file_lines(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        try:
            create_file(file_path)
        except Exception as create_error:
            print(f"Failed to create file: {create_error}")
        return 0
        
    if not os.path.isfile(file_path):
        #print(f"Not a file: {file_path}")
        return 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            total_lines = len(lines)
            #print(f"The total number of lines in the file is: {total_lines}")
            return total_lines
    except UnicodeDecodeError:
        try:
            with open(file_path, 'rb') as file:
                total_lines = sum(1 for _ in file)
                #print(f"The total number of lines in the file is: {total_lines} (counted in binary mode)")
                return total_lines
        except Exception as binary_error:
            print(f"Binary mode counting failed: {binary_error}")
            return 0
    except PermissionError:
        print(f"Permission denied: {file_path}")
        return 0
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        try:
            create_file(file_path)
        except Exception as create_error:
            print(f"Failed to create file: {create_error}")
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0


def read_json_streaming(json_path):
    """Stream-read a JSON array one element at a time"""
    with open(json_path, 'rb') as f:
        for entry in ijson.items(f, 'item'):
            yield entry


def read_json(file_path): # Specifying encoding='utf-8' makes it environment-independent
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error occurred while parsing JSON data in {file_path}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error reading {file_path}: {e}")
        return None


def write_json(json_file_path, json_data):
    dir_name = os.path.dirname(json_file_path)
    
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, ensure_ascii=False, indent=4)



def delete_file(file_path):
    try: # Check if the specified file exists, and delete it if it does
        if os.path.isfile(file_path):
            os.remove(file_path)
            #print(f"File '{file_path}' has been successfully deleted.")
        #else:
        #    print(f"File {file_path} does not exist. Skipping removal.")
    except Exception as e:
        print(f"Error deleting file: {e}")


def read_file(filename):
    try:
        # First try to read as UTF-8 text
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                code_content = file.read()
            return code_content
        except UnicodeDecodeError:
            # If UTF-8 fails, try reading as binary
            with open(filename, 'rb') as file:
                binary_content = file.read()
            
            # You can try different encodings here
            for encoding in ['latin-1', 'cp1252', 'shift-jis']:
                try:
                    return binary_content.decode(encoding)
                except UnicodeDecodeError:
                    continue
            
            # If all text decodings fail, return binary data
            return binary_content
    except FileNotFoundError:
        print(f"Error: {filename} does not exist")
        return None


def write_file(target_path, content):
    directory = os.path.dirname(target_path)  # Get the directory path from the file path
    if directory and not os.path.exists(directory):  # Create the directory if it does not exist
        os.makedirs(directory)
    
    try:
        # Handle surrogate characters
        if isinstance(content, str):
            # Replace surrogate characters with safe characters
            content = content.encode('utf-8', errors='replace').decode('utf-8')
        
        with open(target_path, 'w', encoding='utf-8', errors='replace') as file:  # Write content to the file
            file.write(content)
            
    except UnicodeEncodeError as e:
        print(f"Unicode encoding error for {target_path}: {e}")
        # Fallback: remove problematic characters and retry
        try:
            # Remove surrogate characters
            cleaned_content = ''.join(char for char in content if not (0xD800 <= ord(char) <= 0xDFFF))
            with open(target_path, 'w', encoding='utf-8', errors='ignore') as file:
                file.write(cleaned_content)
        except Exception as fallback_error:
            print(f"Fallback write failed for {target_path}: {fallback_error}")
            
    except Exception as e:
        print(f"Error writing file {target_path}: {e}")


def copy_file(source_path, destination_path):
    try: # Copy the source file to the destination path
        shutil.copy2(source_path, destination_path)
        print("The file was copied successfully.")
    except IOError as e:
        print(f"An error occurred while copying the file: {e}")
    except Exception as e:
        print(f"An unexpected error has occurred: {e}")


def create_file(file_path):
    if os.path.exists(file_path):
        return
    
    try: # Create the directory if it does not exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Create the file (if it does not exist)
        with open(file_path, 'x') as file:
            pass
        #print(f"File '{file_path}' created successfully.")
    #except FileExistsError:
    #    print(f"File '{file_path}' already exists.")
    except Exception as e:
        print(f"An error occurred: {e}")


def recreate_file(file_path):
    delete_file(file_path)
    create_file(file_path)



def append_file(file_path, code_to_append):
    try:
        directory = os.path.dirname(file_path) # Get the directory path of the file
        if directory: # If the directory exists and is not empty
            os.makedirs(directory, exist_ok=True) # Create the directory if it does not exist

        with open(file_path, 'a') as file: # Open the file in append mode
            file.write(code_to_append)
            
    except IOError as e:
        print(f"An error occurred while writing to file '{file_path}': {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")



def create_permissioned_file(file_path):
    if os.path.exists(file_path):
        return
    
    try:
        # Create the directory if it does not exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Create the file (if it does not exist)
        with open(file_path, 'x') as file:
            pass
        
        # Grant execute permission (755 = rwxr-xr-x)
        os.chmod(file_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

        #print(f"File '{file_path}' created successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")


def create_directory(path):
    try:
        os.makedirs(path, exist_ok=True)
        #print(f"Directory '{path}' created successfully.")
    except OSError as error:
        print(f"Failed to create directory '{path}'. Error: {error}")
        raise



def delete_directory(dir_path):
    try: # Check if the specified directory exists, and delete it if it does
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
            print(f"Directory '{dir_path}' has been successfully deleted.")
        #else:
        #    print(f"No such directory: '{dir_path}'")
    except Exception as e:
        print(f"Error deleting directory: {e}")       



def rename_directory(old_path, new_path, overwrite=True):
    """
    Rename a directory
    
    Args:
        old_path: Directory path before renaming
        new_path: Directory path after renaming
        overwrite: Whether to allow overwriting (default: False)
    
    Returns:
        The new directory path
    """
    old_dir = Path(old_path).resolve()
    new_dir = Path(new_path).resolve()
    
    # Check existence
    if not old_dir.exists():
        raise FileNotFoundError(f"Directory not found: {old_path}")
    
    if not old_dir.is_dir():
        raise NotADirectoryError(f"Not a directory: {old_path}")
    
    # Do nothing if the paths are the same
    if old_dir == new_dir:
        print(f"Source and destination are the same: {old_path}")
        return str(new_dir)
    
    # If the new path already exists
    if new_dir.exists():
        if overwrite:
            print(f"Removing existing directory: {new_path}")
            shutil.rmtree(new_dir)
        else:
            raise FileExistsError(f"Destination already exists: {new_path}. Use overwrite=True to replace.")
    
    # Create the parent directory if it does not exist
    new_dir.parent.mkdir(parents=True, exist_ok=True)
    
    # Rename
    old_dir.rename(new_dir)
    # print(f"✓ Renamed: {old_path} -> {new_path}")
    
    return str(new_dir)


def copy_directory(source_directory, destination_root):
    """
    Copy directory with exact permissions preservation.
    """
    try:
        source_directory_name = os.path.basename(os.path.normpath(source_directory))
        final_destination = os.path.join(destination_root, source_directory_name)
        
        # Remove if the destination is a file
        if os.path.exists(final_destination) and not os.path.isdir(final_destination):
            print(f"Warning: Removing file {final_destination} to create directory")
            os.remove(final_destination)
        
        # Create the root directory and copy permissions
        os.makedirs(final_destination, exist_ok=True)
        src_stat = os.stat(source_directory)
        os.chmod(final_destination, src_stat.st_mode)
        
        # Recursively copy manually
        for root, dirs, files in os.walk(source_directory):
            rel_path = os.path.relpath(root, source_directory)
            dest_dir = os.path.join(final_destination, rel_path)
            
            # Create the directory and copy the original permissions
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
                try:
                    src_dir_stat = os.stat(root)
                    os.chmod(dest_dir, src_dir_stat.st_mode)
                except Exception as e:
                    print(f"Warning: Failed to copy permissions for {dest_dir}: {e}")
            
            # Copy files
            for file in files:
                try:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(dest_dir, file)
                    
                    # Remove if the destination is a directory
                    if os.path.isdir(dst_file):
                        print(f"Warning: Removing directory {dst_file} to create file")
                        shutil.rmtree(dst_file)
                    
                    # If it is a symbolic link
                    if os.path.islink(src_file):
                        link_to = os.readlink(src_file)
                        if os.path.exists(dst_file) or os.path.islink(dst_file):
                            os.remove(dst_file)
                        os.symlink(link_to, dst_file)
                        # Copy the permissions of the symbolic link itself (if possible)
                        try:
                            src_link_stat = os.lstat(src_file)
                            os.lchmod(dst_file, src_link_stat.st_mode)
                        except (AttributeError, OSError):
                            # Ignore if lchmod is not available in the environment
                            pass
                        print(f"Created symlink from {dst_file} to {link_to}")
                    # If it is a regular file
                    elif os.path.isfile(src_file):
                        shutil.copy2(src_file, dst_file)  # copy2 also preserves permissions
                except Exception as file_error:
                    print(f"Warning: Failed to copy {src_file}: {file_error}")
        
        print(f"Copied {source_directory} to {final_destination}")
        
    except Exception as e:
        print(f"Error during copy from {source_directory} to {destination_root}: {e}")
        import traceback
        traceback.print_exc()

def create_backup_directory(dir_name):
    max_backups=1

    try:
        # Generate a directory name for backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{dir_name}_backup_{timestamp}"
        
        # Search for existing backups
        backups = [d for d in os.listdir('.') if d.startswith(f"{dir_name}_backup_")]
        
        # Delete backups exceeding the maximum count, starting from the oldest
        if len(backups) >= max_backups:
            backups.sort()
            for old_backup in backups[:len(backups) - max_backups + 1]:
                shutil.rmtree(old_backup)
                # print(f'Removed old backup: {old_backup}')
                print(f'Removed old backup: {old_backup}')
        
        # Create a new backup
        shutil.copytree(dir_name, backup_name)
        #print(f'Created backup: {backup_name}')
        print(f'Created backup: {backup_name}')

        return backup_name
        
    except FileNotFoundError:
        #print(f'Directory {dir_name} not found')
        print(f'Directory {dir_name} not found')
    except PermissionError:
        #print('Permission denied: cannot create backup')
        print('Permission denied: cannot create backup')
    except shutil.Error as e:
        #print(f'Error occurred during backup creation: {e}')
        print(f'Error occurred during backup creation: {e}')
    except OSError as e:
        #print(f'An error occurred: {e}')
        print(f'An error occurred: {e}')
    
    return None



def clone_directory(src_dir, renamed_dir):
    copied_dir = create_backup_directory(src_dir)
    rename_directory(copied_dir, renamed_dir)



def restore_directory(raw_tmp, raw_dir):
    delete_directory(raw_dir)
    rename_directory(raw_tmp, raw_dir)


def tmp_backup_directory(raw_dir):
    raw_tmp = f"{raw_dir}_tmp_parse"
    delete_directory(raw_tmp)
    copied_dir = create_backup_directory(raw_dir)
    rename_directory(copied_dir, raw_tmp)

    return raw_tmp



def delete_lines(file_path, start_line, end_line):
    try:
        # Read the contents of the file
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        # Check the range to delete
        if start_line < 1 or end_line > len(lines) or start_line > end_line:
            print("Invalid line range.")
            return
        
        # Delete the specified lines
        del lines[start_line - 1:end_line]
        
        # Remove the newline from the last line (to prevent the file from ending with a newline)
        if lines and lines[-1].endswith('\n'):
            lines[-1] = lines[-1].rstrip('\n')
        
        # Write the updated contents to the file
        with open(file_path, 'w') as file:
            file.writelines(lines)
        
        #print(f"Deleted lines {start_line} through {end_line}.")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except IOError:
        print(f"An error occurred while processing file '{file_path}'.")



def load_toml_file(file_path):
    try:
        with open(file_path, 'r') as file:
            toml_data = toml.load(file)
    except FileNotFoundError:
        toml_data = {}
    return toml_data

def write_toml_file(toml_data, file_path):
    with open(file_path, 'w') as file:
        file.write(toml_data)

def write_toml(toml_data, file_path):
    with open(file_path, 'w') as file:
        toml_string = toml.dumps(toml_data)
        file.write(toml_string)

def json_to_toml(json_data):
    return toml.dumps(json_data)

def merge_toml_json(dict1, dict2):
    for key in dict2:
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            merge_toml_json(dict1[key], dict2[key])
        else:
            dict1[key] = dict2[key]

def grant_permissions(target_dir): #: str, dry_run: bool = False) -> list:
    """
    List read-only files in the target directory and
    grant write permissions
    
    Args:
        target_dir: Path to the target directory
        dry_run: If True, only list without changing permissions
    
    Returns:
        List of files that were read-only
    """
    dry_run = False #True
    target_path = Path(target_dir).resolve()
    
    if not target_path.exists():
        #print(f"Error: Directory does not exist: {target_path}")
        print(f"Error: Directory does not exist: {target_path}")
        return []
    
    readonly_files = []
    
    # Recursively scan all files in the directory
    for file_path in target_path.rglob('*'):
        if file_path.is_file():
            # Get the current permissions
            current_mode = file_path.stat().st_mode
            
            # If the user does not have write permission
            if not (current_mode & stat.S_IWUSR):
                readonly_files.append(str(file_path))
    
    # Display results
    if readonly_files:
        #print(f"Read-only files found: {len(readonly_files)}")
        print(f"Read-only files found: {len(readonly_files)}")
        print("-" * 60)
        for f in readonly_files:
            print(f"  {f}")
        print("-" * 60)
        
        if not dry_run:
            #print(f"\nGranting write permissions...")
            print(f"\nGranting write permissions...")
            for f in readonly_files:
                file_path = Path(f)
                current_mode = file_path.stat().st_mode
                # Add write permission for the user
                new_mode = current_mode | stat.S_IWUSR
                os.chmod(f, new_mode)
            #print(f"Done: Granted write permission to {len(readonly_files)} files")
            print(f"Done: Granted write permission to {len(readonly_files)} files")
        else:
            #print(f"\ndry_run=True: Skipped permission changes")
            print(f"\ndry_run=True: Skipped permission changes")
    else:
        #print(f"No read-only files found in: {target_path}")
        print(f"No read-only files found in: {target_path}")
    
    return readonly_files


def check_permission(raw_dir):
    """Display read-only files and grant write permissions"""
    read_only_files = []
    for root, dirs, files in os.walk(raw_dir):
        for fname in files:
            fpath = os.path.join(root, fname)
            if not os.access(fpath, os.W_OK):
                read_only_files.append(fpath)
    
    if read_only_files:
        print(f"Found {len(read_only_files)} read-only files in {raw_dir}:")
        for fpath in read_only_files:
            mode = oct(os.stat(fpath).st_mode)[-3:]
            print(f"  [{mode}] {fpath}")
            os.chmod(fpath, os.stat(fpath).st_mode | stat.S_IWUSR)
        print(f"Granted write permission to {len(read_only_files)} files.")
    else:
        print(f"No read-only files found in {raw_dir}")
    
    return read_only_files



def read_specific_lines(filename, start_line, end_line):
    if end_line is None:
        return ""

    start_line = int(start_line)
    end_line = int(end_line)
    
    # List of encodings to try
    encodings = ['utf-8', 'latin-1', 'cp932', 'shift_jis', 'euc-jp', 'iso-2022-jp']
    
    # Check if the file exists
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return ""
    
    # Check file type (optional)
    is_binary = False
    try:
        with open(filename, 'rb') as test_file:
            sample = test_file.read(1024)
            is_binary = b'\0' in sample  # Determine as binary if NULL bytes are present
    except Exception:
        pass
    
    # Attempt to process as a text file
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as file:
                lines = file.readlines()
                if start_line <= 0 or end_line > len(lines):
                    print("Error: Invalid start or end line number.")
                    return ""
                return ''.join(lines[start_line-1:end_line])
        except UnicodeDecodeError:
            continue  # Try the next encoding
        except Exception as e:
            print(f"Error while reading file with {encoding}: {e}")
            continue
    
    # If all encodings fail, read in binary mode
    try:
        with open(filename, 'rb') as file:
            all_bytes = file.read()
            # Forcefully convert binary to string and split into lines
            text = all_bytes.decode('utf-8', errors='replace')
            lines = text.splitlines(True)
            
            if start_line <= 0 or end_line > len(lines):
                print("Error: Invalid start or end line number.")
                return ""
            
            return ''.join(lines[start_line-1:end_line])
    except Exception as e:
        print(f"Error processing binary file: {e}")
    
    return ""  # If all methods fail



def get_last_directory(path: str) -> str:
    # Method 1: Using os.path.basename
    if path is None:
        return None
    return os.path.basename(os.path.normpath(path))


#############################################

# from coverage instrument
def get_line_coverage(coverage_info_path, directory, line_path, order_path) -> Dict[str, CoverageData]:
    # Generate info using lcov
    # if not hasattr(thread_local, 'uuid'):
    #     thread_local.uuid = str(uuid.uuid4())
    # thread_id = threading.get_ident()
    # unique_id = f"{thread_id}_{thread_local.uuid}"

    line_percent = 0

    """
    random = get_random_void()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    timestamp = f"{timestamp}_{random}"

    coverage_info_path = f"{database_dir}/coverage_{timestamp}.info"
    #coverage_info_path = f"{database_dir}/coverage.info"

    try:
        subprocess.run(
            ["lcov", "--capture", "--directory", directory, "--output-file", f"{coverage_info_path}"],
            check=True,
            stderr=subprocess.PIPE,
            timeout=10
        )
    except subprocess.TimeoutExpired:
        print(f"WARNING: gcov command timed out")
        # If timed out, skip this file and move to the next
    except subprocess.CalledProcessError as e:
        print(f"Error running lcov: {e.stderr.decode()}")
        sys.exit(1)

    """

    coverage_data: Dict[str, CoverageData] = {}

    # if not hasattr(thread_local, 'uuid'):
    #     thread_local.uuid = str(uuid.uuid4())
    # thread_id = threading.get_ident()
    # unique_id = f"{thread_id}_{thread_local.uuid}"

    if not os.path.exists(coverage_info_path):
        return 

    with open(f"{coverage_info_path}", 'r') as f:
        current_file = None
        for line in f:
            line = line.strip()
            if line.startswith('SF:'):
                current_file = line[3:]
                coverage_data[current_file] = CoverageData(current_file)
            elif line.startswith('DA:'):
                try:
                    # Handle special format cases like "DA:6TN:"
                    da_part = line[3:]
                    if ',' in da_part:
                        line_num_str, count_str = da_part.split(',')
                        line_num = int(line_num_str)
                        count = int(count_str)
                        if coverage_data is not None and current_file is not None:
                            coverage_data[current_file].add_line(line_num, count)
                    else:
                        # Log and skip if there is no comma
                        print(f"WARNING: Skipping malformed line data: {line}")
                except ValueError as e:
                    # Log and skip if a conversion error occurs
                    print(f"WARNING: Could not parse line data: {line}, Error: {e}")
                    continue
        
            # elif line.startswith('DA:'):
            #     line_num, count = map(int, line[3:].split(','))
            #     coverage_data[current_file].add_line(line_num, count)

    
    # Save to JSON file and Print summary
    print("Save coverage data to JSON file")
    print(coverage_data)

    # if os.path.exists(output_file):
    #     existing_data = read_json(output_file)
    # else:
    # existing_data = {}
    existing_data = {
        "total_lines" : None,
        "covered_lines" : None,
        "files" : {}
    }

    for file_path, coverage in coverage_data.items():
        if file_path not in existing_data:
            existing_data["files"][file_path] = {
                "file_path": file_path,
                "total_lines" : None,
                "covered_lines" : None,
                "coverage_percent" : None,
                "lines": {}
            }

        for line_num, line_coverage in coverage.lines.items():
            line_info = {
                'line_number': line_coverage.line_number,
                'is_covered': line_coverage.is_covered,
                'execution_count': line_coverage.execution_count
            }
            
            if str(line_num) not in existing_data["files"][file_path]["lines"]:
                existing_data["files"][file_path]["lines"][str(line_num)] = []
            #existing_data["files"][file_path]["lines"][str(line_num)].append(line_info)
            existing_data["files"][file_path]["lines"][str(line_num)] = line_info

    # print
    """Print coverage information for all files and average coverage"""
    total_lines = 0
    total_covered_lines = 0
    
    #order = read_compile_order(order_path)
    # absolute_order = []
    # for path in order:
    #     absolute_path = os.path.abspath(os.path.join(os.path.dirname(order_path), path))
    #     absolute_order.append(absolute_path)

    for file_path, coverage in coverage_data.items():
        # if file_path not in absolute_order:
        #     continue

        print(f"\nFile: {file_path}")
        
        file_total_lines = 0
        file_covered_lines = 0
        
        for line_num in sorted(coverage.lines.keys()):
            line = coverage.lines[line_num]
            status = "covered" if line.is_covered else "uncovered"
            #print(f"Line {line_num}: {status} (execution count: {line.execution_count})")
            
            file_total_lines += 1
            if line.is_covered:
                file_covered_lines += 1
        
        # Calculate coverage rate for each file
        if file_total_lines > 0:
            file_coverage_percent = (file_covered_lines / file_total_lines) * 100
            print(f"\nCoverage rate for {file_path}: {file_coverage_percent:.2f}%")
        
        existing_data["files"][file_path]["total_lines"] = file_total_lines
        existing_data["files"][file_path]["covered_lines"] = file_covered_lines
        existing_data["files"][file_path]["coverage_percent"] = file_coverage_percent

        # Add to overall statistics

        # if file_path in order: # added
        total_lines += file_total_lines
        total_covered_lines += file_covered_lines
    
    # Calculate overall coverage rate
    average_coverage = 0
    if total_lines > 0:
        average_coverage = (total_covered_lines / total_lines) * 100
        print(f"\nAverage coverage rate for all files: {average_coverage:.2f}%")
        print(f"Total lines: {total_lines}, Covered lines: {total_covered_lines}")

    existing_data["total_lines"] = total_lines
    existing_data["covered_lines"] = total_covered_lines

    with open(line_path, 'w') as f:
        json.dump(existing_data, f, indent=4)

    return total_covered_lines, total_lines #average_coverage  #average_coverage / 100

    
def get_branch_coverage(coverage_info_path, target_dir, branch_path): #, order_path):
    #order = read_compile_order(order_path)

    """
    random = get_random_void()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    timestamp = f"{timestamp}_{random}"

    # Generate coverage info including branch coverage with lcov
    coverage_info_path = f"{database_dir}/coverage_{timestamp}.info" 
    #coverage_info_path = f"{database_dir}/coverage.info" 
    try:
        subprocess.run(
            [
                "lcov", "--capture", "--directory", target_dir,
                "--output-file", coverage_info_path,
                "--rc", "lcov_branch_coverage=1"  # Enable branch coverage
            ],
            check=True,
            stderr=subprocess.PIPE,
            timeout=30
        )
    except subprocess.TimeoutExpired:
        print(f"WARNING: lcov command timed out")
        return {"error": "lcov command timed out", "total_branches": 0, "covered_branches": 0, "files": {}}
    except subprocess.CalledProcessError as e:
        print(f"Error running lcov: {e.stderr.decode()}")
        return {"error": f"lcov command error: {e.stderr.decode()}", "total_branches": 0, "covered_branches": 0, "files": {}}
    """

    branch_data: Dict[str, Any] = {
        "total_branches": 0,
        "covered_branches": 0,
        "coverage_percent": None,
        "files": {}
    }
    
    current_file = None
    
    with open(coverage_info_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Get file name
            if line.startswith('SF:'):
                current_file = line[3:]
                branch_data["files"][current_file] = {
                    "file_path" : current_file,
                    "total_branches": 0,
                    "covered_branches": 0,
                    "coverage_percent": None,
                    "branches": []
                }
            
            # Parse branch coverage information
            # BRDA:line_number,block_number,branch_number,execution_count or -
            # Parse branch coverage information
            elif line.startswith('BRDA:'):
                branch_data["total_branches"] += 1  # branch_total will be recalculated later
                
                parts = line[5:].split(',')
                
                # Check if parts has enough elements
                if len(parts) < 4:
                    print(f"Warning: Invalid BRDA line format: {line}")
                    continue  # Skip this line and move to the next
                
                try:
                    line_number = int(parts[0])
                    block_number = int(parts[1])
                    branch_number = int(parts[2])
                    
                    if parts[3] == '-':
                        execution_count = 0
                        taken = False
                    else:
                        try:
                            execution_count = int(parts[3])
                            taken = execution_count > 0
                        except ValueError:
                            # For special values (e.g.: '1TN:')
                            print(f"Warning: Special branch value found: {parts[3]} (line: {line})")
                            # If it contains TN:, consider it as executed (adjust as needed)
                            if 'TN:' in parts[3]:
                                execution_count = 1  # Temporary value
                                taken = True
                            else:
                                execution_count = 0
                                taken = False
                                
                    if taken:
                        branch_data["covered_branches"] += 1
                            
                    if current_file:
                        branch_data["files"][current_file]["total_branches"] += 1
                        if taken:
                            branch_data["files"][current_file]["covered_branches"] += 1
                                
                        branch_info = {
                            "line_number": line_number,
                            "block": block_number,
                            "branch": branch_number,
                            "taken": taken,
                            "count": execution_count
                        }
                                
                        branch_data["files"][current_file]["branches"].append(branch_info)
                except (ValueError, IndexError) as e:
                    print(f"Error: While processing BRDA line: {line}, Error details: {e}")
                    # Increment an error counter or log the error for analysis as needed
                    continue  # Skip this line and move to the next

            """
            elif line.startswith('BRDA:'):
                branch_data["total_branches"] += 1 # branch_total will be recalculated later
                
                parts = line[5:].split(',')
                line_number = int(parts[0])
                block_number = int(parts[1])
                branch_number = int(parts[2])  #branch_number = int(parts[2])
                
                if parts[3] == '-':
                    execution_count = 0
                    taken = False
                else:
                    try:
                        execution_count = int(parts[3])
                        taken = execution_count > 0
                    except ValueError:
                        # For special values (e.g.: '1TN:')
                        print(f"WARNING: Special branch value found: {parts[3]} in line: {line}")
                        # If it contains TN:, consider it as executed (adjust as needed)
                        if 'TN:' in parts[3]:
                            execution_count = 1  # Temporary value
                            taken = True
                        else:
                            execution_count = 0
                            taken = False
                
                if taken:
                    branch_data["covered_branches"] += 1

                # else:
                #     execution_count = int(parts[3])
                #     taken = execution_count > 0
                #     if taken:
                #         branch_data["covered_branches"] += 1
                
                if current_file:
                    branch_data["files"][current_file]["total_branches"] += 1
                    if taken:
                        branch_data["files"][current_file]["covered_branches"] += 1
                    
                    branch_info = {
                        "line_number": line_number,
                        "block": block_number,
                        "branch": branch_number,
                        "taken": taken,
                        "count": execution_count
                    }
                    
                    branch_data["files"][current_file]["branches"].append(branch_info)

            """

    # Calculate coverage rate for each file
    branch_total = 0
    covered_total = 0
    for file_path, file_data in branch_data["files"].items():
        ## if file_path in order:
        branch_total += file_data["total_branches"]
        covered_total += file_data["covered_branches"]
        ##

        total = file_data["total_branches"]
        covered = file_data["covered_branches"]
        if total > 0:
            file_data["coverage_percent"] = round((covered / total) * 100, 2)
        else:
            file_data["coverage_percent"] = 0
    
    # Calculate overall coverage rate
    branch_data["total_branches"] = branch_total
    branch_data["covered_branches"] = covered_total

    if branch_data["total_branches"] > 0:
        branch_data["coverage_percent"] = round(
            (branch_data["covered_branches"] / branch_data["total_branches"]) * 100, 2
        )
    else:
        branch_data["coverage_percent"] = 0
    
    # Collect information on uncovered branches
    """
    branch_data["uncovered_branches"] = []
    for file_path, file_data in branch_data["files"].items():
        for branch in file_data["branches"]:
            if not branch["taken"]:
                branch_data["uncovered_branches"].append({
                    "file": file_path,
                    "line_number": branch["line_number"],
                    "block": branch["block"],
                    "branch": branch["branch"]
                })
    """
    

    with open(branch_path, "w") as f:
        json.dump(branch_data, f, indent=4)
    
    # Display results
    print(f"Branch Coverage: {branch_data['coverage_percent']}%")
    print(f"Total Branches: {branch_data['total_branches']}")
    print(f"Covered Branches: {branch_data['covered_branches']}")
    #print(f"Uncovered Branches: {len(branch_data['uncovered_branches'])}")
    
    average_coverage = branch_data['coverage_percent'] / 100

    return covered_total, branch_total #branch_data["coverage_percent"]  #average_coverage #branch_data
    

# related_main is not being added
def get_function_coverage(coverage_info_path, target_dir, function_path, order_path):
    #order = read_compile_order(order_path)

    """
    random = get_random_void()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    timestamp = f"{timestamp}_{random}"

    # Generate coverage info including function coverage with lcov
    coverage_info_path = f"{database_dir}/coverage_{timestamp}.info" 
    try:
        subprocess.run(
            [
                "lcov",
                "--capture",
                "--directory", target_dir,
                "--output-file", coverage_info_path,
                "--rc", "lcov_branch_coverage=1"  # Also enable branch coverage
            ],
            check=True,
            stderr=subprocess.PIPE,
            timeout=30
        )
    except subprocess.TimeoutExpired:
        print(f"WARNING: lcov command timed out")
        return {"error": "lcov command timed out", "total_functions": 0, "covered_functions": 0, "files": {}}
    except subprocess.CalledProcessError as e:
        print(f"Error running lcov: {e.stderr.decode()}")
        return {"error": f"lcov command error: {e.stderr.decode()}", "total_functions": 0, "covered_functions": 0, "files": {}}
    """

    function_data = {
        "total_functions": 0,
        "covered_functions": 0,
        "coverage_percent": None,
        "files": {}
    }
    
    current_file = None
    
    with open(coverage_info_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Get file name
            if line.startswith('SF:'):
                current_file = line[3:]
                function_data["files"][current_file] = {
                    "file_path": current_file,
                    "total_functions": 0,
                    "covered_functions": 0,
                    "coverage_percent": None,
                    "functions": []
                }
            
            # Parse function definition (FN:line_number,function_name)
            elif line.startswith('FN:'):
                parts = line[3:].split(',')
                if len(parts) >= 2:
                    try:
                        line_number = int(parts[0])
                        function_name = parts[1]
                        
                        if current_file:
                            function_data["files"][current_file]["functions"].append({
                                "name": function_name,
                                "line_number": line_number,
                                "called": False,
                                "count": 0
                            })
                    except (ValueError, IndexError) as e:
                        print(f"Error: While processing FN line: {line}, Error details: {e}")
                        continue
            
            # Parse function execution (FNDA:execution_count,function_name)
            elif line.startswith('FNDA:'):
                parts = line[5:].split(',')
                if len(parts) >= 2:
                    try:
                        execution_count = int(parts[0])
                        function_name = parts[1]
                        
                        if current_file:
                            for func in function_data["files"][current_file]["functions"]:
                                if func["name"] == function_name:
                                    func["called"] = execution_count > 0
                                    func["count"] = execution_count
                                    break
                    except (ValueError, IndexError) as e:
                        print(f"Error: While processing FNDA line: {line}, Error details: {e}")
                        continue
    
    # # Recalculate the number of functions and called functions for each file from the functions list
    # for file_path, file_data in function_data["files"].items():
    #     file_data["total_functions"] = len(file_data["functions"])
    #     file_data["covered_functions"] = sum(1 for func in file_data["functions"] if func["called"])
    
    # Recalculate the number of functions and called functions for each file from the functions list
    function_total = 0
    covered_total = 0

    #related_ids = get_related_data(callee_main_path)
    #callee_data = read_json(callee_path)

    for file_path, file_data in function_data["files"].items():
        def_file_path = file_path
            
        for func_item in file_data['functions']:
            """
            def_start_line = get_def_start_line(callee_data, target_cmd, func_item['name'], file_path, func_item['line_number'], meta_dir)
            key = f"{func_item['name']}@{def_file_path}:{def_start_line}"
            if key in related_ids:
                file_data["total_functions"] += 1

                if func_item['called'] is True:
                    #file_data["covered_functions"] = sum(1 for func in file_data["functions"] if func["called"])
                    file_data["covered_functions"] += 1
            """

            file_data["total_functions"] += 1
            if func_item['called'] is True:
                #file_data["covered_functions"] = sum(1 for func in file_data["functions"] if func["called"])
                file_data["covered_functions"] += 1


        function_total += file_data["total_functions"]
        covered_total += file_data["covered_functions"]

    # # Calculate coverage rate for each file
    # for file_path, file_data in function_data["files"].items():
        
    #     # function_total_each = 0
    #     # covered_total_each = 0

    #     # related_ids = get_related_data_by_file(callee_main_path, file_path)
    #     # for func in function_data["files"][file_path]["functions"]:
    #     #     if func["name"] in related_funcs:
    #     #         function_total_each += 1
    #     #         if func["called"] > 0:
    #     #             covered_total_each += 1
        
    #     # file_data["total_functions"] += function_total_each
    #     # file_data["covered_functions"] += covered_total_each
        
    #     if file_path in order:
    #         function_total += file_data["total_functions"]
    #         covered_total += file_data["covered_functions"]

    #     total = file_data["total_functions"]
    #     covered = file_data["covered_functions"]
    #     if total > 0:
    #         file_data["coverage_percent"] = round((covered / total) * 100, 2)
    #     else:
    #         file_data["coverage_percent"] = 0
    
    # Calculate overall coverage rate
    function_data["total_functions"] = function_total
    function_data["covered_functions"] = covered_total

    if function_data["total_functions"] > 0:
        function_data["coverage_percent"] = round(
            (function_data["covered_functions"] / function_data["total_functions"]) * 100, 2
        )
    else:
        function_data["coverage_percent"] = 0
    

    # Create the directory if it does not exist
    os.makedirs(os.path.dirname(function_path), exist_ok=True)
    
    # Save function coverage data as a JSON file
    with open(function_path, 'w') as f:
        json.dump(function_data, f, indent=4)
    
    # Display coverage summary
    total_functions = function_data["total_functions"]
    covered_functions = function_data["covered_functions"]
    coverage_percent = function_data["coverage_percent"]
    
    print(f"Function Coverage Summary:")
    print(f"  Total Functions: {total_functions}")
    print(f"  Covered Functions: {covered_functions}")
    print(f"  Coverage: {coverage_percent}%")

    coverage_percent = function_data["coverage_percent"]


    return covered_total, total_functions #coverage_percent



def get_random_void():
    #return random.random()
    return f"0000000000000"



def get_coverage(cov_target, target_dir, database_dir, branch_path, line_path, function_path): #, order_path): # , taregt_json ############
    
    delete_file(line_path) #get_file_coverage(target_dir)
    delete_file(branch_path)

    random = get_random_void()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    timestamp = f"{timestamp}_{random}"

    # Generate coverage info including branch coverage with lcov
    coverage_info_path = f"{database_dir}/coverage_{timestamp}.info" 
    #coverage_info_path = f"{database_dir}/coverage.info" 
    
    ###
    """  
    # Get directories containing .gcda files
    gcda_dirs = get_gcda_directories(target_dir)

    if not gcda_dirs:
        print("No .gcda files found")
        #return False
        return branch_coverage, line_coverage, function_coverage

    print(f"Found {len(gcda_dirs)} directories with .gcda files")
    
    # Create a temporary directory
    max_workers = 10
    with tempfile.TemporaryDirectory() as temp_dir:
        # Parallel processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_lcov, d, temp_dir) for d in gcda_dirs]
            info_files = []
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result and os.path.exists(result):
                    info_files.append(result)
        
        if not info_files:
            print("No coverage files generated")
            #return False
        
        print(f"Generated {len(info_files)} coverage files, merging...")
        
        # Merge the results
        merge_cmd = ["lcov"]
        for info_file in info_files:
            merge_cmd.extend(["-a", info_file])
        merge_cmd.extend(["-o", coverage_info_path])
        
        try:
            subprocess.run(merge_cmd, check=True, timeout=600)
            print(f"Coverage merged to {coverage_info_path}")
            #return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            print(f"Failed to merge coverage: {e}")
            #return False

    """  
    ###
    #"""    
    try:
        subprocess.run(
            [
                "lcov", "--capture", "--directory", target_dir,
                "--output-file", coverage_info_path,
                "--rc", "lcov_branch_coverage=1"  # Enable branch coverage
            ],
            check=True,
            #stderr=subprocess.PIPE,
            stderr=subprocess.DEVNULL,    # Added
            stdout=subprocess.DEVNULL,    # Added
            timeout=None #600 #240 # 30
        )
    except subprocess.TimeoutExpired:
        print(f"WARNING: lcov command timed out")
        return 0, 0, 0  # {"error": "lcov command timed out", "total_branches": 0, "covered_branches": 0, "files": {}}
    except subprocess.CalledProcessError as e:
        print(f"Error running lcov: {e.stderr.decode()}")
        #return {"error": f"lcov command error: {e.stderr.decode()}", "total_branches": 0, "covered_branches": 0, "files": {}}
        return 0, 0, 0  # Fixed return value

    #"""    

    # line coverage # coverage_data will be the latest one. # Parse coverage data
    order_path = "tmp_order.txt"
    # line_coverage, line_percent
    line_coverage, line_max = get_line_coverage(coverage_info_path, target_dir, line_path, order_path)
    
    # branch coverage
    # branch_percent
    branch_coverage, branch_max = get_branch_coverage(coverage_info_path, target_dir, branch_path) #, order_path)

    # function coverage
    # coverage_percent
    function_coverage, function_max = get_function_coverage(coverage_info_path, target_dir, function_path, order_path) 

    # Update here
    current_coverage_info_path = f"{database_dir}/current_cov_info.info"
    if os.path.exists(coverage_info_path):
        copy_file(coverage_info_path, current_coverage_info_path)
    
    delete_file(coverage_info_path)


    # global current_coverage
    # if cov_target == "function":
    #     current_coverage = coverage_percent #function_coverage
    # elif cov_target == "branch":
    #     current_coverage = branch_coverage

    branch_percent = round((branch_coverage / branch_max) * 100, 2) if branch_max > 0 else 0.0
    line_percent = round((line_coverage / line_max) * 100, 2) if line_max > 0 else 0.0
    function_percent = round((function_coverage / function_max) * 100, 2) if function_max > 0 else 0.0

    print("++++++++++++++++++++")
    print(f'Branch cov: {branch_coverage} ({branch_percent} %)')
    print(f'Line cov: {line_coverage} ({line_percent:.2f} %)')
    print(f'Function cov: {function_coverage} ({function_percent} %)')
    print("++++++++++++++++++++")

    return branch_coverage, branch_max, line_coverage, line_max, function_coverage, function_max


def get_branch_covered(target_file, target_function, start_line, end_line):
    is_full_branch_covered = False
    
    try:
        target_file_path = target_file
        
        if not os.path.exists(target_file_path):
            return False #, f"Error: File not found: {target_file_path}"
        
        # Run lcov to generate .info file
        target_dir = os.path.dirname(target_file_path)
        
        cmd = ['lcov', '--capture', '--directory', target_dir, '--output-file', '-']
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=None #60
        )
        
        if result.returncode != 0:
            return False #, f"lcov error: {result.stderr}"
        
        # Parse the .info file
        lines = result.stdout.split('\n')
        line_data = {}
        branch_data = {}
        function_data = {}
        current_file = None
        
        for line in lines:
            line = line.strip()
            
            # File information
            if line.startswith('SF:'):
                current_file = line[3:]
            
            elif current_file == target_file_path:
                # Line coverage: DA:line_number,execution_count
                if line.startswith('DA:'):
                    parts = line[3:].split(',')
                    line_num = int(parts[0])
                    count = int(parts[1])
                    line_data[line_num] = count
                
                # Function coverage: FN:line_number,function_name
                elif line.startswith('FN:'):
                    parts = line[3:].split(',', 1)
                    line_num = int(parts[0])
                    func_name = parts[1]
                    function_data[line_num] = func_name
                
                # Branch coverage: BRDA:line_number,block,branch,execution_count
                elif line.startswith('BRDA:'):
                    parts = line[5:].split(',')
                    line_num = int(parts[0])
                    count = 0 if parts[3] == '-' else int(parts[3])
                    if line_num not in branch_data:
                        branch_data[line_num] = []
                    branch_data[line_num].append(count)
        
        # start_line and end_line are the function's start and end lines
        if start_line is None or end_line is None:
            return False #, "Function start and end lines are not specified"
        
        function_start_line = start_line
        function_end_line = end_line
        
        # Check branches within the specified function
        uncovered_branches = []
        total_branches = 0
        
        for line_num, branches in branch_data.items():
            # Check if within the function range
            if function_start_line <= line_num <= function_end_line:
                for i, branch_count in enumerate(branches):
                    total_branches += 1
                    if branch_count == 0:
                        uncovered_branches.append((line_num, i))
        
        # Check if all branches are covered
        is_full_branch_covered = len(uncovered_branches) == 0 and total_branches > 0
        
        # In case debug information is also returned
        debug_info = {
            'total_branches': total_branches,
            'uncovered_branches': uncovered_branches,
            'function_range': (function_start_line, function_end_line)
        }
        
        return is_full_branch_covered #, debug_info
    
    except Exception as e:
        return False #, f"Error: {str(e)}"


#############################################

def run_script_pty(script_path, timeout):
    print("Start: run_script_pty()")
    script_dir = os.path.dirname(script_path)
    script_name = os.path.basename(script_path)
    
    master_fd, slave_fd = pty.openpty()
    
    # Keep the setting to turn off echo
    slave_attrs = termios.tcgetattr(slave_fd)
    new_attrs = list(slave_attrs)
    new_attrs[3] = new_attrs[3] & ~termios.ECHO
    termios.tcsetattr(slave_fd, termios.TCSANOW, new_attrs)
    
    # Set environment variables
    env = os.environ.copy()
    env['TERM'] = 'dumb'  # Use 'dumb' terminal to suppress ANSI escape sequences
    
    """
    if target == "yank":
        env['TERM'] = 'xterm'
    """
    process = subprocess.Popen(
        ["/bin/bash", script_name],
        env=env,
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        close_fds=True,
        preexec_fn=os.setsid,
        cwd=script_dir
    )
    
    os.close(slave_fd)
    
    output_lines = []
    buffer = ""
    
    # Start time for timeout management
    start_time = time.time()
    timed_out = False

    try:
        while True:
            try:
                ##
                # Timeout check
                if timeout and (time.time() - start_time) > timeout:
                    timed_out = True
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    break
                
                # Execute read with timeout
                ready_to_read, _, _ = select.select([master_fd], [], [], 0.1)
                if not ready_to_read:
                    continue

                ##

                data = os.read(master_fd, 1024)
                if not data:
                    break
                
                text = data.decode('utf-8', errors='replace')
                buffer += text
                
                # Process complete lines
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    clean_line = line.strip('\r')  # Remove carriage returns
                    if clean_line:  # Exclude empty lines
                        output_lines.append(clean_line)
                
            except OSError:
                break
            
            if process.poll() is not None:
                break
                
    finally:
        os.close(master_fd)
    
    # Process the last line remaining in the buffer
    if buffer.strip():
        output_lines.append(buffer.strip())
    
    return_code = process.wait()

    print(f"run_script_pty: {script_path}")

    # If a timeout occurred, return an error message
    if timed_out:
        output_text = '\n'.join(output_lines)
        #return f"ERROR: Script execution of {script_path} timed out after {timeout} seconds"
        return f"ERROR: Script execution of {script_path} timed out after {timeout} seconds\n\n=== Execution results (up to timeout) ===\n{output_text}"
    
    #prompt.extend(['\n'.join(std_out)])  # Join list elements with newline characters
    return '\n'.join(output_lines) #, return_code  #output_lines, return_code



#sudo ln -s $(pwd)/shell_runner/target/release/shell_runner /usr/local/bin/
def run_script(script_path, timeout, dir_move_flag, execute_log_path, option, progress_queue, iteration_count, max_iterations, log_dir, mode): # -> Union[str, None]:
    
    error_output = None
    std_output = None
    result = None
    
    # Iteration start
    if progress_queue:
        progress_queue.put(json.dumps({
            "type": "iteration_start",
            "iteration": iteration_count, #i + 1,
            "total": max_iterations
        }))
        
    try:
        # Check if file exists
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script not found: {script_path}")
            
        # Check if file is executable
        if not os.access(script_path, os.X_OK):
            # Try to make it executable
            try:
                os.chmod(script_path, 0o755)
            except Exception as e:
                raise PermissionError(f"Cannot make script executable: {e}")
        
        if dir_move_flag is True:
            execute_dir = os.path.dirname(os.path.normpath(script_path))
            script_path = os.path.basename(os.path.normpath(script_path))
        else:
            execute_dir = None

        """
        # Check permission information and output detailed logs
        file_stat = os.stat(script_path)
        current_user = os.getlogin()
        
        try:
            owner = pwd.getpwuid(file_stat.st_uid).pw_name
            group = grp.getgrgid(file_stat.st_gid).gr_name
        except KeyError:
            owner = str(file_stat.st_uid)
            group = str(file_stat.st_gid)
            
        print(f"File permissions: {oct(file_stat.st_mode)}")
        print(f"File owner: {owner}, group: {group}")
        print(f"Current user: {current_user}")

        # Check and set execute permission
        if not os.access(script_path, os.X_OK):
            print("Script is not executable. Attempting to set execute permission...")
            
            try:
                # Change permission using sudo (if needed)
                if owner != current_user:
                    result = subprocess.run(['sudo', 'chmod', '+x', script_path], 
                                            capture_output=True, text=True)
                    if result.returncode != 0:
                        print(f"sudo chmod failed: {result.stderr}")
                        # If sudo fails, try regular chmod
                        os.chmod(script_path, 
                                file_stat.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                else:
                    # If the owner is the current user, chmod directly
                    os.chmod(script_path, 
                            file_stat.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                
                print("Execute permission set successfully")
            except Exception as e:
                print(f"Failed to set execute permission: {e}")
                # Still attempt to run the script even if permission setting fails
        """

        """
        if option == "compile":
            script_path = f"./{script_path} --build"
        elif option == "run":
            script_path = f"./{script_path} --run"
        else:
            script_path = f"./{script_path}"

        """
        cmd = ["bash"]
        
        if script_path.startswith("./"):
            cmd.append(script_path)
        else:
            cmd.append(f"./{script_path}")

        if option == "compile":
            cmd.append("--build")
        elif option == "run":
            cmd.append("--run")
        
        print(f"Execute run_script: {script_path} at {execute_dir}")

        # Copy current environment variables
        env = os.environ.copy()
        env["GCOV_CHECK_STAMP"] = "0" # Add GCOV_CHECK_STAMP=0

        # Execute the script
        if execute_dir is None:
            print("Run with None execute_dir")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False, #shell=True  # Required for shell scripts
                env=env
            )
        else:
            #print("Run with some execute_dir")
            result = subprocess.run(
                cmd,
                capture_output=True,
                cwd=execute_dir,
                text=True,
                timeout=timeout,
                shell=False, #shell=True  # Required for shell scripts
                env=env
            )

    except subprocess.TimeoutExpired:
        std_output = f"Script execution timed out after {timeout} seconds" #, std_output, iteration_count
        
    except subprocess.SubprocessError as e:
        std_output = f"Failed to execute script: {str(e)}" #, std_output, iteration_count
        
    except Exception as e:
        std_output = f"Unexpected error: {str(e)}" #, std_output, iteration_count


    finally:

        if result is not None:
            # Write execution results to log
            if execute_log_path is not None:
                print(f"before ({execute_log_path})")
                create_file(execute_log_path)
                with open(execute_log_path, 'w', encoding='utf-8') as f:
                    if result.stdout:
                        f.write(result.stdout)
                        #print(result.stdout)
                    if result.stderr:
                        f.write(result.stderr)
                        #print(result.stderr)
                print(f"Wrote log file ({execute_log_path})")

            # else:
            #     if result.stdout:
            #         print(result.stdout)
            #     if result.stderr:
            #         print(result.stderr)
            #     print("Without log file")
            # print(f"execute_log_path: {execute_log_path}")


            # Check for errors
            std_output = result.stdout if result.stdout is not None and result.stdout != "" else None
            error_output = result.stderr if result.stderr is not None and result.stderr != "" else None
            return_code = result.returncode  # Get return_code here

            print(f"type(result.stdout): {type(result.stdout)}") 
            print(f"type(result.stderr): {type(result.stderr)}") 
            print(f"return_code: {return_code}") 
            
            # if result.stdout:
            #     std_output = result.stdout
            # if result.stdout:
            #     error_output = result.stderr

            # added the realtime output
            # pty_output = run_script_pty(script_path)
            #std_output = pty_output
            # print(pty_output)

            """
            if result.stdout.strip():
                std_output = f"{result.stdout.strip()}"
            if result.stdout: #result.returncode != 0:
                # Combine stderr and stdout if there's an error
                error_output = result.stderr.strip()
                # if result.stdout.strip():
                    #error_output += f"\nStdout: {result.stdout.strip()}"
                    #std_output += f"\nStdout: {result.stdout.strip()}"

                print("-------- error_output start ---------")
                print(result.stderr)
                print("-------- error_output end ---------")
                #return error_output
                return error_output, std_output

            return None, None
            """

            
            if error_output and return_code == 0:
                #print("\nBuild information:")
                if std_output is None:
                    std_output = error_output
                else:
                    std_output += "\n" + error_output  # Append with a newline
                error_output = None
            
            if error_output is None and return_code == 1: # Mainly for "initial_testcase"
                #error_output = "Return code is 1, abnormal termination."
                error_output = "Return code 1: abnormal termination."
            
            # if std_output is not None and isinstance(std_output, str):
            #     std_output = std_output.split('\n') if std_output else None
            
            # if error_output is not None and isinstance(error_output, str):
            #     error_output = error_output.split('\n') if error_output else None


            if progress_queue: # and log_dir:
                if error_output:
                    if log_dir:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        os.makedirs(log_dir, exist_ok=True)
                        log_file = os.path.join(log_dir, f"generation_{timestamp}.log")

                        # logging.basicConfig(
                        #     filename=log_file,
                        #     level=logging.DEBUG,
                        #     format='%(asctime)s - %(levelname)s - %(message)s'
                        # )
                        # logging.info(f"Script execution started: {script_path}")
                        # if error_output:
                        #     logging.error(f"Error occurred: {error_output}")
                        # if std_output:
                        #     logging.info(f"Output: {std_output}")
                    

                        # Create log content
                        log_content = f"=== Execution Log - {timestamp} ===\n\n"
                        log_content += f"Script: {script_path}\n\n"
                        
                        if error_output:
                            log_content += "=== ERROR OUTPUT ===\n"
                            log_content += error_output
                            log_content += "\n\n"
                        
                        if std_output:
                            log_content += "=== STANDARD OUTPUT ===\n"
                            log_content += std_output
                            log_content += "\n\n"

                        with open(log_file, 'w', encoding='utf-8') as f:
                            f.write(log_content)


                        progress_queue.put(json.dumps({
                            "type": "error_retry",
                            "message": "Test execution failed", 
                            #"error_summary": error_summary,
                            "log_file": str(log_file),
                            "log_content": log_content
                            #"retry": retry_count
                        }))
            
                else:
                    # Success
                    progress_queue.put(json.dumps({
                        "type": "execution_success",
                        "message": "Test execution succeeded",
                        "iteration": iteration_count
                    }))
        if mode == "modify_data":
            iteration_count += 1

        # print(iteration_count)
        # print(max_iterations)
    
    return error_output, std_output, iteration_count



def check_script_state(script_path: str, timeout: int = 5) -> Tuple[bool, str]:
    absolute_path = os.path.abspath(script_path)
    # print(f"Absolute path of the script: {absolute_path}")

    if not os.path.exists(absolute_path):
        return False, f"Script does not exist: {absolute_path}"

    if not os.access(absolute_path, os.X_OK):
        return False, f"Script does not have execute permission: {absolute_path}"

    try:
        # Execute the script
        process = subprocess.Popen(
            [absolute_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            # Execute through shell
            shell=True
        )

        # Monitor the process state
        psutil_process = psutil.Process(process.pid)
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check the process state
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                return False, f"Script has terminated. Exit code: {process.returncode}"

            # Get process state (output more detailed information)
            status = psutil_process.status()
            cpu_percent = psutil_process.cpu_percent(interval=0.1)
            #print(f"Status: {status}, CPU: {cpu_percent}%")  # Debug output

            # Check characteristics of waiting-for-input state
            if (status == 'sleeping' and 
                cpu_percent < 0.1):
                
                # Terminate the process
                process.terminate()
                return True, "Likely in a waiting-for-arguments state"

            time.sleep(0.1)

        # If timed out
        process.terminate()
        return False, "Processing in progress or unknown state (timed out)"

    except Exception as e:
        return False, f"An error occurred: {str(e)}"




#sudo ln -s $(pwd)/shell_runner/target/release/shell_runner /usr/local/bin/
def run_script_wo_log(script_path, timeout, dir_move_flag, execute_log_path, option): # -> Union[str, None]:
    
    error_output = None
    std_output = None

    is_waiting, message = check_script_state(script_path)

    if is_waiting is True:
        print("Does it require arguments?")
        print(f"Dynamic verification result: {is_waiting}, {message}")

        timeout = 20 # How many seconds is this exactly?

    try:
        # Check if file exists
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script not found: {script_path}")
            
        # Check if file is executable
        if not os.access(script_path, os.X_OK):
            # Try to make it executable
            try:
                os.chmod(script_path, 0o755)
            except Exception as e:
                raise PermissionError(f"Cannot make script executable: {e}")
        
        if dir_move_flag is True:
            execute_dir = os.path.dirname(os.path.normpath(script_path))
            script_path = os.path.basename(os.path.normpath(script_path))
        else:
            execute_dir = None

        cmd = ["bash"]
        
        if script_path.startswith("./"):
            cmd.append(script_path)
        else:
            cmd.append(f"./{script_path}")

        if option == "init":
            cmd.append("init")

        #print(cmd)

        """
        if option == "compile":
            cmd.append("--build")
        elif option == "run":
            cmd.append("--run")
        """
        
        
        print(f"Execute run_script: {script_path} at {execute_dir}")

        env = os.environ.copy()

        # Execute the script
        if execute_dir is None:
            print("Run with None execute_dir")
            result = subprocess.run(
                cmd,
                #env=env,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False #shell=True  # Required for shell scripts
            )
        else:
            #print("Run with some execute_dir")
            result = subprocess.run(
                cmd,
                #env=env,
                capture_output=True,
                cwd=execute_dir,
                text=True,
                timeout=timeout,
                shell=False #shell=True  # Required for shell scripts
            )

        # Write execution results to log
        if execute_log_path is not None:
            print(f"before ({execute_log_path})")
            create_file(execute_log_path)
            with open(execute_log_path, 'w', encoding='utf-8') as f:
                if result.stdout:
                    f.write(result.stdout)
                    #print(result.stdout)
                if result.stderr:
                    f.write(result.stderr)
                    #print(result.stderr)
            print(f"Wrote log file ({execute_log_path})")

        # else:
        #     if result.stdout:
        #         print(result.stdout)
        #     if result.stderr:
        #         print(result.stderr)
        #     print("Without log file")
        # print(f"execute_log_path: {execute_log_path}")


        # Check for errors
        std_output = result.stdout if result.stdout is not None and result.stdout != "" else None
        error_output = result.stderr if result.stderr is not None and result.stderr != "" else None
        return_code = result.returncode  # Get return_code here

        #if std_output:
        # print("---------- std_output ----------")
        # print(std_output)
        # #if error_output:
        # print("---------- error_output ----------")
        # print(error_output) # = result.stderr

        #"""

        # print("---------- error_output ----------")
        # print(error_output) # = result.stderr
        # print("----------------------------------")

        # Judging by return code is not a good approach.
        #"""
        if error_output and return_code == 0:
            #print("\nBuild information:")
            if std_output is None:
                std_output = error_output
            else:
                std_output += "\n" + error_output  # Append with a newline
            error_output = None
        #"""
        """
        if error_output: # and return_code == 0:
            if not is_rust_error(error_output): # If an error pattern is found
                std_output += "\n" + error_output  # Append with a newline
        """

        if is_waiting is True:
            error_output += f"Timed out because arguments are required. Please fix the shell script ({script_path}) with the argument content."

        print("---------- std_output ----------")
        print(std_output)
        #if error_output:
        print("---------- error_output ----------")
        print(error_output) # = result.stderr
        print("----------------------------------")


        # if result.stdout:
        #     std_output = result.stdout
        # if result.stdout:
        #     error_output = result.stderr
        

        return error_output, std_output

    except subprocess.TimeoutExpired:
        return f"Script execution timed out after {timeout} seconds", std_output
        
    except subprocess.SubprocessError as e:
        return f"Failed to execute script: {str(e)}", std_output
        
    except Exception as e:
        return f"Unexpected error: {str(e)}", std_output



def get_timestamp():
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S') # datetime.now().strftime("%Y%m%d_%H%M%S") # #
    return timestamp


def get_is_covered(target_entry, cov_path, target_dir, cov_type): #def find_first_uncovered_line(target_entry, cov_path) -> Optional[int]:

    print(f"target_entry: {target_entry}")
    file_path = target_entry['target_path']
    target_function = target_entry['target_function']
    target_line = target_entry['target_line']
    target_branch = target_entry['target_branch']
    target_uncovered_ratio = target_entry['target_uncovered_ratio']
    abs_path = os.path.abspath(file_path)

    is_covered = None
    if cov_type == "function":
        if os.path.exists(cov_path):
            with open(cov_path, 'r') as f:
                coverage_data = json.load(f)
            
            if abs_path not in coverage_data['files']:
                print(f"Error: No coverage data found for {abs_path}")
                return None
                
            file_coverage = coverage_data['files'][abs_path]
            
            # Check function coverage
            for function in file_coverage['functions']:
                if function['name'] == target_function:
                    is_covered = function['called']
                    return is_covered
            
            print(f"Error: Function {target_function} not found in coverage data")
            return False
            
        return None


    elif cov_type == "branch":
        try:
            with open(cov_path, 'r') as f:
                coverage_data = json.load(f)
            
            if abs_path not in coverage_data['files']:
                print(f"Error: No coverage data found for {abs_path}")
                return None
                
            file_coverage = coverage_data['files'][abs_path]

            total_branches = [] #len(file_coverage['branches'])
            uncovered_branches = []

            for branch in file_coverage['branches']:
                if branch['line_number'] == target_line: # and branch['branch'] == target_branch: #branch['block'] == target_branch:
                    total_branches.append(branch)
                    if not branch["taken"]:
                        uncovered_branches.append(branch)
                    """
                    is_covered = branch['taken']
                    return is_covered
                    """
        
            uncovered_ratio = len(uncovered_branches) / len(total_branches) if len(total_branches) > 0 else 0
            if uncovered_ratio < target_uncovered_ratio:
                is_covered = True
            else:
                is_covered = False

            return is_covered

            
        except FileNotFoundError:
            print("Error: coverage_details.json not found")
            return None
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in coverage_details.json")
            return None
        except Exception as e:
            print(f"Error while finding uncovered line: {str(e)}")
            return None
        
    elif cov_type == "line":
        print(f"target_entry: {target_entry}")
        file_path = target_entry['target_path']
        target_line = target_entry['target_line']

        try:
            with open(cov_path, 'r') as f:
                coverage_data = json.load(f)
            
            abs_path = os.path.abspath(file_path)
            
            if abs_path not in coverage_data['files']:
                print(f"Error: No coverage data found for {abs_path}")
                return None
                
            file_coverage = coverage_data['files'][abs_path]
            
            # Check the coverage status of a specific line
            line_key = str(target_line)  # JSON keys are strings
            if line_key in file_coverage['lines']:
                coverage_dict = file_coverage['lines'][line_key]
                #if coverage_list:  # Make sure the list is not empty
                return coverage_dict['is_covered']  # Return is_covered of the last element in the list
                # return file_coverage['lines'][line_key]['is_covered']
            return None

            
        except FileNotFoundError:
            print("Error: coverage_details.json not found")
            return None
        except json.JSONDecodeError:
            print("Error: Invalid JSON format in coverage_details.json")
            return None
        except Exception as e:
            print(f"Error while finding uncovered line: {str(e)}")
            return None


def get_is_increased(target_entry, database_dir, previous_coverage, current_coverage, cov_type):

    # if TARGET == "function":
    #     current_coverage = function_coverage

    # elif TARGET == "branch":
    #     current_coverage = branch_coverage

    print(f"target_entry: {target_entry}")
    file_path = target_entry['target_path']
    target_line = target_entry['target_line']
    target_branch = target_entry['target_branch']
    target_function = target_entry['target_function']

    # current_coverage, line_coverage = get_coverage(target_dir, branch_path, line_path, order_path)

    is_increased = False

    print()
    if previous_coverage is None or current_coverage is None: # added
        print(f"previous_coverage: {previous_coverage}")
        print(f"current_coverage: {current_coverage}")
        raise ValueError("Error in get_is_increased()")
        #return is_increased, 0
    
    print(f"previous_coverage: {previous_coverage}")
    print(f"current_coverage: {current_coverage}")

    is_increased = None
    diff = None
    #"""
    # Putting this on hold since it causes an error here
    if previous_coverage < current_coverage:
        is_increased = True
        diff = current_coverage - previous_coverage
    else:
        diff = 0

    #previous_coverage = current_coverage
    #"""

    increased = []
    if os.path.exists(f"{database_dir}/cov_increased.json"):
        increased = read_json(f"{database_dir}/cov_increased.json")

    timestamp = get_timestamp()
    increased.append({
        "timestamp" : timestamp,
        "file_path" : file_path,
        "target_function" : target_function,
        "line_number" : target_line,
        "cov_type" : cov_type, 
        #"branch" : target_branch,
        "is_increased" : is_increased,
        "previous_coverage" : previous_coverage,
        "current_coverage" : current_coverage,
        "diff" : diff
    })

    write_json(f"{database_dir}/cov_increased.json", increased)

    return is_increased, diff



def write_testcase(snap_dir, saved_tests, timestamp): #run_test_path, timestamp):
    for run_test_path in saved_tests:
        ext = Path(run_test_path).suffix  # E.g., ".sh", ".py", ".c"
        #timestamp = get_timestamp() #datetime.now().strftime("%Y%m%d_%H%M%S")
        #file_path = f"{snap_dir}/{timestamp}.sh"

        """
        if ext in [".sh", ".c"]:
            file_path = f"{snap_dir}/{timestamp}{ext}"
            copy_file(run_test_path, file_path)
        """

        if ext == ".sh":
            file_path = f"{snap_dir}/{timestamp}{ext}"
            copy_file(run_test_path, file_path)
        
        elif ext == ".c":
            #file_path = f"{snap_dir}/{timestamp}{ext}"
            copy_file(run_test_path, snap_dir)
    return file_path
    

def run_cov_script(test_type, cov_target, database_dir, snap_dir, tmp_dir, 
                   run_test_path, test_src_path, entry, 
                   branch_path, line_path, function_path, target_dir, initial_coverage, 
                   function_branch_path, progress_queue, iteration_count, max_iterations,
                   log_dir, mode
                   ): # option # timeout, dir_move_flag, option, 

    print("run cov_script...")

    # setup cov file
    if cov_target == "function":
        cov_type_path = function_path
    if cov_target == "branch":
        cov_type_path = branch_path
    if cov_target == "line":
        cov_type_path = line_path

    delete_file(cov_type_path)

    error, std_out, iteration_count = run_script(run_test_path, 30, True, None, "both", progress_queue, iteration_count, max_iterations, log_dir, mode)  # , 10000

    branch_coverage, branch_max, line_coverage, line_max, function_coverage, function_max = get_coverage(cov_target, target_dir, database_dir, branch_path, line_path, function_path) #, order_path)
    # branch_coverage, branch_max, line_coverage, line_max, function_coverage, function_max

    if cov_target == "function":
        current_coverage = function_coverage

    elif cov_target == "branch":
        current_coverage = branch_coverage

    #error, std_out = run_script(run_path, 10, True, None, "both")
    is_covered = None

    is_covered = get_is_covered(entry, cov_type_path, target_dir, cov_target) #(entry, line_path, target_dir) # target_lineがカバーされているかどうかを検知する
    if is_covered is None:
        print("cov_type_path")
        print(cov_type_path)

    #is_increased, diff = get_is_increased(entry, previous_coverage, current_coverage)
    is_increased, diff = get_is_increased(entry, database_dir, initial_coverage, current_coverage, "function")

    timestamp = get_timestamp()
    saved_tests = [run_test_path]
    if "unit" in test_type:
        saved_tests.append(test_src_path)
    
    original_run_test_path = None
    if mode == "modify_data":
        original_run_test_path = write_testcase(snap_dir, saved_tests, timestamp)

    delete_file(function_branch_path)
    copy_file(function_path, function_branch_path)


    write_json(f"{tmp_dir}/target_{timestamp}.json", entry)
    #copy_file(f"{tmp_dir}/target_{timestamp}.json", snap_dir)

    copy_file(branch_path, f"{tmp_dir}/cov_branch_{timestamp}.json")
    copy_file(line_path, f"{tmp_dir}/cov_line_{timestamp}.json")
    copy_file(function_path, f"{tmp_dir}/cov_function_{timestamp}.json")

    #copy_file(f"{tmp_dir}/cov_branch_{timestamp}.json", snap_dir)
    #copy_file(f"{tmp_dir}/cov_line_{timestamp}.json", snap_dir)
    #copy_file(f"{tmp_dir}/cov_function_{timestamp}.json", snap_dir)

    delete_file(f"{tmp_dir}/target_{timestamp}.json")

    delete_file(f"{tmp_dir}/cov_branch_{timestamp}.json")
    delete_file(f"{tmp_dir}/cov_line_{timestamp}.json")
    delete_file(f"{tmp_dir}/cov_function_{timestamp}.json")

    if progress_queue:
        progress_queue.put(json.dumps({
            "type": "iteration_result",
            "iteration": iteration_count,
            "result": {
                "func": function_coverage,
                "func_max": function_max,
                "branch": branch_coverage,
                "branch_max": branch_max,
                "line": line_coverage,
                "line_max": line_max
                # "coverage": current_coverage,
                #"coverage_improvement": 100 #improvement,
                #"new_tests": "", #new_tests,
                #"test_count": 1, #test_count
            }
        }))

    return error, std_out, iteration_count, is_covered, is_increased, diff, current_coverage, branch_coverage, line_coverage, function_coverage, timestamp, original_run_test_path  #, is_covered
    

def run_branch_cov_script(test_type, database_dir, snap_dir, tmp_dir, run_test_path, test_src_path, 
                          entry, branch_path, line_path, function_path, target_dir, initial_coverage, 
                          function_branch_path, progress_queue, iteration_count, max_iterations, log_dir, mode): # option # timeout, dir_move_flag, option, 
    print("run_branch_cov_script...")

    branch_coverage = None
    line_coverage = None
    function_coverage = None

    # clear gcda and gcov files
    cov_type_path = branch_path
    # if TARGET == "function":
    #     cov_type_path = function_path
    # if TARGET == "branch":
    #     cov_type_path = branch_path
    # if TARGET == "line":
    #     cov_type_path = line_path

    delete_file(cov_type_path)

    error, std_out, iteration_count = run_script(run_test_path, 30, True, None, "both", progress_queue, iteration_count, max_iterations, log_dir, mode)  # , 10000

    #branch_coverage, line_coverage, function_coverage = get_coverage(target_dir, branch_path, line_path, function_path, order_path)

    delete_file(branch_path)

    random = get_random_void()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    timestamp = f"{timestamp}_{random}"

    # Generate coverage info including branch coverage with lcov
    coverage_info_path = f"{database_dir}/coverage_{timestamp}.info" 
    #coverage_info_path = f"{database_dir}/coverage.info" 
    try:
        subprocess.run(
            [
                "lcov", "--capture", "--directory", target_dir,
                "--output-file", coverage_info_path,
                "--rc", "lcov_branch_coverage=1"  # Enable branch coverage
            ],
            check=True,
            #stderr=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=None #600 #240 # 30
        )
    except subprocess.TimeoutExpired:
        print(f"WARNING: lcov command timed out")
        #return {"error": "lcov command timed out", "total_branches": 0, "covered_branches": 0, "files": {}}
    except subprocess.CalledProcessError as e:
        #print(f"Error running lcov: {e.stderr.decode()}")
        print(f"Error running lcov: -")
        #return {"error": f"lcov command error: {e.stderr.decode()}", "total_branches": 0, "covered_branches": 0, "files": {}}

    # branch coverage
    branch_coverage, branch_percent = get_branch_coverage(coverage_info_path, target_dir, branch_path) #, order_path)

    print("++++++++++++++++++++")
    print(f'{branch_coverage} ({branch_percent} %)')
    #print(f'{line_coverage} ({line_percent:.2f} %)')
    #print(f'{function_coverage} ({coverage_percent} %)')
    print("++++++++++++++++++++")


    # if TARGET == "function":
    #     current_coverage = function_coverage
    # elif TARGET == "branch":
    current_coverage = branch_coverage

    #error, std_out = run_script(run_path, 10, True, None, "both")
    is_covered = None

    is_covered = get_is_covered(entry, cov_type_path, target_dir, "branch") #(entry, line_path, target_dir) # Detect whether the target_line is covered
    if is_covered is None:
        print("cov_type_path")
        print(cov_type_path)

    #is_increased, diff = get_is_increased(entry, previous_coverage, current_coverage)
    is_increased, diff = get_is_increased(entry, database_dir, initial_coverage, current_coverage, "branch")

    timestamp = get_timestamp()
    saved_tests = [run_test_path]
    if "unit" in test_type:
        saved_tests.append(test_src_path)

    original_run_test_path = write_testcase(snap_dir, saved_tests, timestamp)

    delete_file(function_branch_path)
    copy_file(function_path, function_branch_path)


    write_json(f"{tmp_dir}/target_{timestamp}.json", entry)
    copy_file(f"{tmp_dir}/target_{timestamp}.json", snap_dir)

    copy_file(branch_path, f"{tmp_dir}/cov_branch_{timestamp}.json")
    # copy_file(line_path, f"{tmp_dir}/cov_line_{timestamp}.json")
    # copy_file(function_path, f"{tmp_dir}/cov_function_{timestamp}.json")

    copy_file(f"{tmp_dir}/cov_branch_{timestamp}.json", snap_dir)
    # copy_file(f"{tmp_dir}/cov_line_{timestamp}.json", snap_dir)
    # copy_file(f"{tmp_dir}/cov_function_{timestamp}.json", snap_dir)

    delete_file(f"{tmp_dir}/target_{timestamp}.json")

    delete_file(f"{tmp_dir}/cov_branch_{timestamp}.json")
    # delete_file(f"{tmp_dir}/cov_line_{timestamp}.json")
    # delete_file(f"{tmp_dir}/cov_function_{timestamp}.json")


    ####### added

    # target_file_path = "src/main.c"  # Change to the actual path
    
    # # Get and display the annotated code
    # annotated_code = get_annotated_source_code(target_file_path)
    # print("=== Annotated source code ===")
    # print(annotated_code)
    
    # # Save to file
    # saved_file = save_annotated_code_to_file(target_file_path)
    # print(f"\nSaved annotated code: {saved_file}")

    delete_file(coverage_info_path)

    return error, std_out, iteration_count, is_covered, is_increased, diff, current_coverage, branch_coverage, line_coverage, function_coverage, timestamp  #, is_covered



def deduplicate_compile_commands(json_path):
    """
    Remove duplicate entries from a compile_commands.json file
    
    Args:
        json_path (str): Path to compile_commands.json
        
    Returns:
        list: Command list with duplicates removed
    """
    # Read the JSON file
    with open(json_path, 'r') as f:
        compile_commands = json.load(f)
    
    # Dictionary for grouping by file path
    unique_commands = {}
    
    # Display progress
    total = len(compile_commands)
    #print(f"Number of entries before processing: {total}")
    
    # Process each command
    for cmd in compile_commands:
        file_path = cmd.get('file')
        if not file_path:
            continue
        
        output_path = cmd.get('output', '')
        key = (file_path, output_path, cmd.get('directory', ''))

        # If an entry for the same file already exists, select the command with higher priority
        if key in unique_commands: #if file_path in unique_commands:
            # Criteria for priority (in this example, prefer commands with fewer arguments)
            # This varies by project, so modify as needed
            current_args = len(cmd.get('arguments', []))
            existing_args = len(unique_commands[key].get('arguments', [])) #len(unique_commands[file_path].get('arguments', []))
            
            # Prefer simpler commands (fewer arguments)
            # *The following condition needs to be adjusted per project
            if current_args < existing_args:
                unique_commands[key] = cmd   #[file_path] = cmd
                
            # Example of prioritizing AFL fuzzing commands
            # elif any("__AFL_" in arg for arg in cmd.get('arguments', [])):
            #     unique_commands[file_path] = cmd
        else:
            # Add if this is the first time seeing this file
            unique_commands[key] = cmd   #[file_path] = cmd
    
    # Command list after deduplication
    deduplicated_commands = list(unique_commands.values())
    #print(f"Number of entries after processing: {len(deduplicated_commands)}")
    
    write_json(json_path, deduplicated_commands)
    return deduplicated_commands


def find_compile_commands_json(target_dir): #def get_compile_commands(target_dir):
    
    #"""
    # Check within the specified directory
    compile_commands_path = os.path.join(target_dir, "compile_commands.json")
    #print(compile_commands_path)

    #if os.path.isfile(compile_commands_path):
    if os.path.exists(compile_commands_path):
        compile_commands = read_json(compile_commands_path)
        if compile_commands is not None:
            #if process_type == "gcno":
            deduplicate_compile_commands(f"{target_dir}/compile_commands.json")

            return target_dir
    #"""

    # Recursively search all subdirectories
    for root, dirs, files in os.walk(target_dir):
        if "compile_commands.json" in files:
            print(f"{root}/compile_commands.json")
            
            #if process_type == "gcno":
            deduplicate_compile_commands(f"{root}/compile_commands.json")

            return root
    
    # If not found
    #raise ValueError("Did not find compile_commands.json")
    return None


def recreate_directory(dir_path):
    """Delete and recreate a directory"""
    delete_directory(dir_path)
    create_directory(dir_path)


def get_abs_path(path):
    """Normalize a path to an absolute path"""
    return os.path.abspath(path)


def append_json(file_path, new_data):
    """Append data to a JSON file (concatenate as an array)"""
    
    # Read existing data if the file exists
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            # Initialize with an empty list if the file is empty or corrupted
            existing_data = []
    else:
        existing_data = []
    
    # Convert to a list if existing data is not a list
    if not isinstance(existing_data, list):
        existing_data = [existing_data]
    
    # Add the new data
    if isinstance(new_data, list):
        existing_data.extend(new_data)
    else:
        existing_data.append(new_data)
    
    # Write to file
    with open(file_path, 'w') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)


##

def normalize_path(path_str, base_path):

    if not path_str:
        return path_str
    
    try:
        path = Path(path_str)
        
        # If not an absolute path, return as-is
        if not path.is_absolute():
            return path_str
        
        # Convert absolute path to relative path
        path = path.resolve()
        rel_path = path.relative_to(base_path)
        return str(rel_path)
    
    except (ValueError, Exception) as e:
        # Return as-is if the path is outside base_path, etc.
        # print(f"Warning: Failed to normalize path '{path_str}': {e}")
        return path_str



def normalize_metadata(meta_dir, current_dir):
    """
    Convert absolute paths in metadata to relative paths
    
    Args:
        meta_dir: Metadata directory
        current_dir: Base directory (reference for absolute paths)
    """
    print("normalize metadata...")
    
    meta_path = Path(meta_dir)
    current_path = Path(current_dir).resolve()
    
    # Recursively get .json files
    meta_paths = list(meta_path.rglob("*.json"))
    
    print(f"Found {len(meta_paths)} JSON files")
    
    for json_file in meta_paths:
        print(f"Processing: {json_file.relative_to(meta_path)}")
        
        # Read the JSON file
        meta_data = read_json(json_file)
        
        # Process metadata
        for item in meta_data:
            # Convert def_file_path to relative path
            if 'def_file_path' in item:
                item['def_file_path'] = normalize_path(
                    item['def_file_path'], 
                    current_path
                )
            
            # Process callees
            if 'callees' in item:
                callees = item['callees']
                for callee_item in callees:
                    # Convert call_file_path to relative path
                    if 'call_file_path' in callee_item:
                        callee_item['call_file_path'] = normalize_path(
                            callee_item['call_file_path'], 
                            current_path
                        )
                    
                    # Convert def_file_path to relative path
                    if 'def_file_path' in callee_item:
                        callee_item['def_file_path'] = normalize_path(
                            callee_item['def_file_path'], 
                            current_path
                        )
        
        # Save changes
        write_json(json_file, meta_data)
    
    print(f"Normalization complete: {len(meta_paths)} files processed")


def denormalize_path(path_str, base_path):
    if not path_str:
        return path_str
    
    try:
        path = Path(path_str)
        
        # If already an absolute path, return as-is
        if path.is_absolute():
            return str(path)
        
        # Convert relative path to absolute path
        abs_path = (base_path / path).resolve()
        return str(abs_path)
    
    except Exception as e:
        print(f"Warning: Failed to denormalize path '{path_str}': {e}")
        return path_str




def denormalize_metadata(meta_dir, current_dir):
    print("denormalize metadata...")
    if not os.path.exists(meta_dir):
        return

    meta_path = Path(meta_dir)
    meta_paths = list(meta_path.rglob("*.json"))

    for json_file in meta_paths:
        meta_data = read_json(json_file)
        # Process metadata
        for item in meta_data:
            # Convert def_file_path to absolute path
            if 'def_file_path' in item:
                item['def_file_path'] = denormalize_path(
                    item['def_file_path'], 
                    current_dir
                )
            
            # Process callees
            if 'callees' in item:
                callees = item['callees']
                for callee_item in callees:
                    # Convert call_file_path to absolute path
                    if 'call_file_path' in callee_item:
                        callee_item['call_file_path'] = denormalize_path(
                            callee_item['call_file_path'], 
                            current_dir
                        )
                    
                    # Convert def_file_path to absolute path
                    if 'def_file_path' in callee_item:
                        callee_item['def_file_path'] = denormalize_path(
                            callee_item['def_file_path'], 
                            current_dir
                        )

        write_json(json_file, meta_data)



def merge_json(json1, json2):
    merged_json = json1.copy()  # Create a copy of json1

    for key, value in json2.items():
        if key in merged_json:
            if isinstance(merged_json[key], dict) and isinstance(value, dict):
                # If both values are dicts, merge recursively
                merged_json[key] = merge_json(merged_json[key], value)
            elif isinstance(merged_json[key], list) and isinstance(value, list):
                # If both values are lists, concatenate the lists
                merged_json[key].extend(value)
            else:
                # Otherwise, overwrite with json2's value
                merged_json[key] = value
        else:
            # If the key does not exist, add it as new
            merged_json[key] = value

    return merged_json


# # Add handling for when the top level is a list
# if isinstance(json1, list) and isinstance(json2, list):
#     return json1 + json2  # Or json1.extend(json2); return json1

# if isinstance(json1, list) or isinstance(json2, list):
#     # If only one is a list (type mismatch)
#     raise TypeError(f"Cannot merge list with dict: json1={type(json1)}, json2={type(json2)}")


def merge_list(json1, json2):
    # Add handling for when the top level is a list
    #if isinstance(json1, list) and isinstance(json2, list):
    json1.extend(json2)

    # return json1 + json2  # Or json1.extend(json2); return json1


def get_all_files(directory):
    """
    Recursively get all files in a directory
    
    Args:
        directory: Directory to search
        
    Returns:
        list: List of file paths
    """
    all_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append(file_path)

    return all_files



def get_last_directory(path: str) -> str:
    # Method 1: Using os.path.basename
    return os.path.basename(os.path.normpath(path))


def add_line_numbers(input_file):
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as temp_file:
            with open(input_file, 'r', encoding='utf-8') as infile:
                # Read all lines and get the maximum indent level and line count
                lines = list(infile)
                # Handle the case where the file is empty
                if not lines:
                    #print(f"File {input_file} is empty.")
                    return

                max_line_num = len(lines)
                max_indent = max((len(line) - len(line.lstrip())) // 4 for line in lines)
                
                # Calculate the maximum number of digits for line numbers and indent levels
                line_num_width = len(str(max_line_num))
                indent_width = len(str(max_indent))
                
                # Create the format string (fix the position of :)
                format_str = f"Line {{:{line_num_width}d}} [{{:{indent_width}d}}]: {{}}"
                
                # Process each line
                for line_number, line in enumerate(lines, start=1):
                    indent_level = (len(line) - len(line.lstrip())) // 4
                    numbered_line = format_str.format(line_number, indent_level, line)
                    temp_file.write(numbered_line)
                
        # Overwrite the original file with the temporary file contents
        os.replace(temp_file.name, input_file)
        #print(f"Wrote file with line numbers and indent levels to {input_file}.")
    except IOError as e:
        #print(f"An error occurred: {e}")
        print(f"An error occurred: {e}")



def add_line_numbers_custom_new(input_file, fixed_number):
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as temp_file:
            with open(input_file, 'r', encoding='utf-8') as infile:
                # Read all lines from the file (convert tabs to 4 spaces)
                lines = [line.expandtabs(4).rstrip('\n') for line in infile]
                max_line_number = len(lines)
                number_width = len(str(max_line_number))  # Number of digits for line numbers
                if lines:
                    max_line_length = max(len(line) for line in lines)  # Maximum line length
                else:
                    max_line_length = 0
                
                # Calculate the position of `|` (line length + margin + line number digits)
                vertical_bar_position = max_line_length + 4  # `4` is added as margin

                # Write processing
                for line_number, line in enumerate(lines, start=fixed_number):
                    line_number_str = str(line_number).rjust(number_width)  # Right-align the line number
                    padding = ' ' * (vertical_bar_position - len(line))  # Spaces to align `|`
                    numbered_line = f"{line}{padding}|Line {line_number_str}\n"
                    temp_file.write(numbered_line)

        # Overwrite the original file with the temporary file contents
        os.replace(temp_file.name, input_file)
        print(f"Wrote file with line numbers to {input_file}.")

    except IOError as e:
        print(f"An error occurred: {e}")


def merge_dicts(main_dict, new_dict):
    for key, value in new_dict.items():
        if key in main_dict:
            if isinstance(main_dict[key], dict) and isinstance(value, dict):
                merge_dicts(main_dict[key], value)
            elif isinstance(main_dict[key], list) and isinstance(value, list):
                main_dict[key].extend(value)
            elif isinstance(main_dict[key], list):
                main_dict[key].append(value)
            elif isinstance(value, list):
                main_dict[key] = [main_dict[key]] + value
            else:
                main_dict[key] = [main_dict[key], value]
        else:
            main_dict[key] = value


def count_lines(file_path):
    line_count = 0
    with open(file_path, 'r') as file:
        for _ in file:
            line_count += 1
    return line_count


def get_line_from_file(file_path, line_number):
    if line_number < 1:
        raise ValueError("Line number must be greater than 0")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for current_line, line_content in enumerate(f, 1):
                if current_line == line_number:
                    return line_content.rstrip('\n')
            return ""  # If the specified line is not found
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")



def absolute_to_relative(absolute_path, base_path):

    abs_path = Path(absolute_path).resolve() # Convert to PathLib object
    base = Path(base_path).resolve()

    relative_path = os.path.relpath(abs_path, base)
    print(f"From abs to rel: {absolute_path} -> {relative_path}")
    return str(relative_path)


def change_top_directory(original_path, new_top_directory):
    # Split the path
    path_parts = original_path.split(os.sep)

    # If no new top directory is specified, exclude the first part
    if new_top_directory is None:
        path_parts = path_parts[1:]  # Exclude the first element
    else:
        # Replace the first part with the new top directory
        path_parts[0] = new_top_directory
    
    new_path = os.sep.join(path_parts)
    print(f"original is {original_path}, new_path is {new_path}")
    # Join and return the updated path parts
    return new_path


def get_random(length):
    """
    Generate a random alphanumeric string of the specified length
    
    Args:
        length (int): Length of the string to generate
    
    Returns:
        str: Random alphanumeric string
    """
    characters = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    return ''.join(random.choice(characters) for _ in range(length))



def save_to_output_dir(output: dict, output_dir: str):
    """
    Duplicate and save each path (file or directory) in the output dict
    to output_dir.
    Also save the output dict itself as metadata.json.
    """
    os.makedirs(output_dir, exist_ok=True)

    copied = {}
    for key, src_path in output.items():
        if src_path is None:
            #print(f"[skip] {key}: path is None")
            continue
        if not os.path.exists(src_path):
            #print(f"[warn] {key}: {src_path} does not exist, skipping")
            continue

        basename = os.path.basename(src_path)
        dst_path = os.path.join(output_dir, basename)

        # If a file with the same name already exists, prefix with the key name
        if os.path.exists(dst_path):
            dst_path = os.path.join(output_dir, f"{key}_{basename}")

        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            #print(f"[copy dir]  {key}: {src_path} -> {dst_path}")
        else:
            shutil.copy2(src_path, dst_path)
            #print(f"[copy file] {key}: {src_path} -> {dst_path}")

        copied[key] = dst_path

    """
    # Save the original path information and copy destinations as metadata
    metadata = {
        "original": output,
        "copied": copied,
    }
    meta_path = os.path.join(output_dir, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"[saved] metadata -> {meta_path}")
    """

    return copied