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
import time
import anthropic
import json
import base64
import tiktoken
from collections import defaultdict, deque
import chardet
from pycparser import c_parser, c_ast
import replicate
from typing import List, Any
from anthropic import InternalServerError
from collections import defaultdict
import subprocess
from typing import Union, Dict
from clang.cindex import CompilationDatabase, Index
from datetime import datetime, timedelta
from pathlib import Path
import math
from clang.cindex import Index, CursorKind, TokenKind
from clang.cindex import CompilationDatabase, Index
from clang.cindex import CompilationDatabase, CompilationDatabaseError
import stat
from openai import AzureOpenAI
from openai import OpenAI
import sys
# import google.generativeai as genai  
# from openai import RateLimitError, APIError
# from testGen.main import print_hello
# from google.generativeai.protos import Content, Part

from .utils import (
    # normal
    read_json,
    write_json,
    read_file,
    write_file,
    create_file,
    delete_file,
    copy_file,
    create_directory,
    delete_directory,
    copy_directory,
    run_script,
    #get_compile_commands,
    find_compile_commands_json,
    deduplicate_compile_commands,
    normalize_path,
    denormalize_path,
    get_abs_path,
    get_last_directory,
    read_specific_lines,
)

# from llm_api import (
#     RepairConfig,
#     LLMInterface,
#     init_prompt_count, 
#     set_exp_data,
#     repair_test,
#     repair_branch,
#     occupy_llm,
#     shutdown_llm,
#     save_coverage_report
# )

MACRO_PARSER_HOME = "/root/kiso-parser-macro"

class Logger:
    def __init__(self, file_path):
        self.terminal = sys.stdout
        self.log = open(file_path, "a", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()  # This writes to the file in real time

    def flush(self):
        pass


def set_log(log_dir, llm_choice, target, logging_path, step, DEBUG_LLM):
    if step == 'pre_processing':
        prefix = 'pre'
    elif step == 'divide':
        prefix = 'div'
    elif step == 'convert':
        prefix = 'conv'
    elif step == 's_repair':
        prefix = 'f_rep'
    else:
        prefix = step
        #raise ValueError("Invalid step value. Use 'pre_processing' or 'convert'.")

    if llm_choice == 'gpt':
        llm_type = 'gpt'
    elif llm_choice == 'claude':
        llm_type = 'claude'
    elif llm_choice == 'claude_azure':
        llm_type = 'claude_azure'
    elif llm_choice == 'gemini':
        llm_type = 'gemini'
    elif llm_choice == 'llama':
        llm_type = 'llama'
    else:
        raise ValueError("Invalid step value. Use an approproate llm_choice.")
    
    
    data = {}
    if os.path.exists(logging_path):
        data = read_json(logging_path)
        #num = data.get(target, None)
        if target in data and 'log_count' in data[target]:
            num = data[target]['log_count']
        else:
            num = 1
        #if num is None:
        #    num = 1
    else:
        num = 1
    
    log_file_path = f'{log_dir}/{target}/{num}_{target}_{prefix}_{llm_type}.log'

    if DEBUG_LLM:
        log_file_path = f'{log_dir}/{target}/{num}_{target}_{prefix}_{llm_type}_see.log'

    num += 1  # Fixed increment
    if target not in data:
        data[target] = {}
    data[target]['log_count'] = num
    write_json(logging_path, data)

    # Create the directory if it does not exist
    log_directory = os.path.dirname(log_file_path)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    sys.stdout = Logger(log_file_path)
    sys.stderr = Logger(log_file_path)  # Also log error messages to the file

    return log_file_path


class PathConfig:
    """Class for managing path settings"""
    
    def __init__(self, user_id, original_dir, process_type, work_dir):
        """
        Args:
            user_id: User ID
            target: Source directory name
            target: Target command name
            raw_dir: Path to the raw directory (default: "trans_c")
            work_dir: Working directory (default: "my_workspace")
        """

        target = get_last_directory(original_dir)  # Which one should we use?

        self.user_id = user_id
        self.target = target
        #self.target = target
        
        # Base directories
        if process_type in ['reformat']:
            self.raw_dir=f"trans_re_{user_id}"
        else:
            self.raw_dir=f"trans_c_{user_id}" #'raw'
    
        #self.raw_dir="trans_c"

        if process_type != "s_repair":
            self.work_dir=f"workspace_{user_id}_{target}"
            work_dir = self.work_dir

        else:
            self.work_dir=f"workspace_{process_type}_{user_id}_{target}"

            # work_dir = get_last_directory(work_dir)
            # self.work_dir=work_dir

        self.c_code_dir = f'c_code_{user_id}'

        self.meta_dir = f'metadata_{user_id}/{target}'
        self.div_meta_dir = f'div_metadata_{user_id}/{target}'
        self.chat_dir = f'chats_{user_id}_{process_type}/{target}' # self.chat_dir = f'chats/{target}'
        self.chat_macro_dir = f'chat_macro_{process_type}/{target}'
        self.log_dir = f'logs_{user_id}/{target}'
        self.exp_dir = f'exp_{user_id}/{target}'
        self.archive_dir = f'archive_{user_id}/{target}'
        self.database_dir = f'database_{user_id}/{target}'
        self.output_dir = f'output_{user_id}/{target}'

        #self.root_dir = 'root'
        self.c_output_dir = 'modified_c'
        self.testcase_dir = 'testcase'
        self.test_m_dir = 'test_makefiles'
        self.unity_dir = 'unity_code'
        
        
        # Tools
        self.macro_finder = f"{MACRO_PARSER_HOME}/macro_finder/build/macro-finder"
        self.marker = f'/* Genifai: here is one target function!: target_line */'

        # Target / Database
        if process_type in ["s_repair", "trans"]:
            self.target_dir = f"{self.work_dir}/{target}"  #self.target_dir = f"{self.work_dir}/{target}"

        else:
            self.target_dir = f"{self.raw_dir}/{target}"  # target_dir = f"{work_dir}/{target}"
            

        self.execute_path = None
        self.run_all_path = None
        
        if self.work_dir is not None:
            self.execute_path = f"{self.work_dir}/execute.sh"
            self.run_all_path = f"{self.work_dir}/run_all.sh"  # self.run_all_path = f"{self.target_dir}/run_all.sh"
        
        # print(self.run_all_path)

        self.build_path = f"{self.target_dir}/c_build.sh"  #f"{self.rust_output_dir}/src/build.rs"
        self.run_test_path = f"{self.target_dir}/run_test.sh"

        self.c_rust_path = f"{self.database_dir}/c_rust.json"
        self.rust_c_path = f"{self.database_dir}/rust_c.json"
        self.block_path = f"{self.database_dir}/block_output.txt"
        self.block_group_path = f"{self.database_dir}/block_group_output.json" #txt"
        
        self.taken_macros_path = f"{self.database_dir}/taken_macros.json"
        self.all_macros_path = f"{self.database_dir}/all_macros.json"

        self.taken_directive_path = f"{self.database_dir}/taken_directive.json"
        self.all_directive_path = f"{self.database_dir}/all_directive.json"

        self.guards_path = f"{self.database_dir}/guards.json"
        self.guarded_macros_path = f"{self.database_dir}/guarded_macros.json"

        self.custom_headers_dir = f"{self.target_dir}/custom_macros"
        self.custom_json_path = f"{self.database_dir}/custom_header.json"
        self.custom_header_path = f"{self.target_dir}/custom_macros.h"
        #self.taken_json_path = f"{self.database_dir}/output_def.json"

        self.cfg_path = f"{self.database_dir}/cfg.json"
        self.independent_path = f"{self.database_dir}/independent.json"
        self.flag_path = f"{self.database_dir}/flag.json"
        self.const_path = f"{self.database_dir}/const.json"
        self.conflict_path = f"{self.database_dir}/conflict.json"
        self.global_path = f"{self.database_dir}/globals.json"
        self.is_program_path = f"{self.database_dir}/is_program.json"

        self.independent_const_build_path = f"{self.database_dir}/const_macros.json"
        self.flag_build_path = f"{self.database_dir}/flag_macros.json"

        self.history_path = f'{self.database_dir}/chat_history.json'
        self.insertion_path = f"{self.database_dir}/insertion.json"

        # Rust output related
        self.rust_output_dir = f"{self.work_dir}/trans_rust"
        self.lib_path = f"{self.rust_output_dir}/src/lib.rs"
        self.build_rs_path = f"{self.rust_output_dir}/build.rs" #f'{self.database_dir}/build.rs'
        self.cargo_path = f"{self.rust_output_dir}/Cargo.toml"
        self.rust_build_path = f"{self.rust_output_dir}/rust_build.sh"
        
        self.build_config_path = f"{self.rust_output_dir}/build_config.txt"   # = os.path.join(rust_output_dir, "build_config.txt")
        # C related
        self.c_lib_path = None
        self.c_cargo_path = None
        self.c_build_path = f"{self.target_dir}/c_build.sh"
        self.rust_lib_h_path = f"{self.target_dir}/rust_lib.h"

        # Dependency / Order related
        self.dep_json_path = f'{self.database_dir}/dependencies.json'
        self.initial_dep_json_path = f'{self.database_dir}/dependencies_initial.json'
        self.div_json_path = f'{self.database_dir}/divisions.json'
        
        self.list_path = f'{self.database_dir}/order.txt'
        self.initial_list_path = f'{self.database_dir}/order_initial.txt'
        self.io_list_path = f'{self.database_dir}/order_io.txt'
        self.beg_list_path = f'{self.database_dir}/beg_order.txt'
        
        # Log / Result related
        self.compile_log_path = f'{self.database_dir}/compile.log'
        self.testcase_json_path = f'{self.database_dir}/testcase.json'
        self.result_path = f"{self.database_dir}/result.json"
        self.moment_path = f"{self.database_dir}/moment.json"
        self.line_path = f"{self.database_dir}/segment.json"
        self.logging_path = f'{self.database_dir}/log_manager.json'
        
        # Macro related
        self.macro_path = f'{self.database_dir}/all_output_used.json' # all_conds.json
        self.initial_macro_path = f'{self.database_dir}/all_conds_initial.json'
        self.all_macro_path = f'{self.database_dir}/all_macros.json'
        self.build_list_path = f'{self.database_dir}/build_list.json'
        self.flag_json_path = f'{self.database_dir}/flag_map.json'
        self.macro_list_path = f'{self.database_dir}/macro_list.txt'
        self.modified_macro_path = f'{self.database_dir}/modified_macro.txt'
        self.matched_macro_path = f'{self.database_dir}/matched_macro_4.txt'
        #self.def_json_path = f'{self.def_json_path}'
        
        # Conditional compilation related
        self.conds_status_path = f"{self.database_dir}/conds_status.json"
        self.picked_path = f"{self.database_dir}/picked_conds.json"
        self.classified_path = f"{self.database_dir}/classify_data.json"
        self.defined_path = f"{self.database_dir}/cfgs_defined.json"
        self.undefined_path = f"{self.database_dir}/cfgs_undefined.json"
        self.cmd_line_path = f"{self.database_dir}/cfgs_cmd_line.json"
        self.namespace_path = f"{self.database_dir}/macro_namespace.json"
        
        
        # Others
        self.map_path = f"{self.database_dir}/path_mappings.json"
        self.call_path = ""
        self.persistent_dir = 'persistent'
        self.c_bank_dir = 'bank_c'
        self.rust_bank_dir = 'bank_rust'
        self.translation_dir = ''

        self.token_path = f"{self.database_dir}/token_{process_type}.json"
        self.history_path = f'{self.database_dir}/history_{process_type}.json'
        self.count_path = f'{self.database_dir}/count_{process_type}.json'
        self.time_path = f'{self.database_dir}/time_{process_type}.json'  # time_path = f"{database_dir}/time.json"


    
    def to_dict(self):
        """Return all paths as a dictionary"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    def __repr__(self):
        return f"PathConfig(user_id={self.user_id}, target={self.target}, target={self.target})"


def create_path_config(user_id, original_dir, process_type, work_dir):
    """
    Helper function to create a PathConfig instance
    
    Args:
        user_id: User ID (e.g., "0000")
        target: Source directory name (e.g., "mini")
        target: Target command name (e.g., "mini")
        raw_dir: Raw directory (default: "trans_c")
        work_dir: Working directory (default: "my_workspace")
    
    Usage example:
        paths = create_path_config(
            user_id="0000",
            target="mini",
            process_type=process_type,
        )
    """
    return PathConfig(user_id, original_dir, process_type, work_dir)


def extract_all_paths(paths):
    """
    Return all paths from PathConfig as individual variables
    
    Returns:
        tuple: A tuple of all path variables
    
    Usage example:
        paths = create_path_config("0000", "mini", "mini")
        (raw_dir, meta_dir, chat_dir, chat_macro_dir, log_dir, exp_dir,
         testcase_dir, test_m_dir, unity_dir, archive_dir, root_dir,
         macro_finder, target_dir, database_dir, history_path, insertion_path,
         c_output_dir, work_dir, rust_output_dir, lib_path, build_path, cargo_path,
         c_lib_path, c_cargo_path, c_build_path,
         dep_json_path, initial_dep_json_path, div_json_path,
         list_path, initial_list_path, io_list_path, beg_list_path,
         compile_log_path, testcase_json_path, result_path, moment_path,
         line_path, logging_path,
         macro_path, initial_macro_path, all_macro_path, build_list_path,
         flag_json_path, macro_list_path, modified_macro_path, matched_macro_path,
         conds_status_path, token_path, picked_path, classified_path,
         defined_path, undefined_path, cmd_line_path, namespace_path,
         guards_path, taken_json_path,
         map_path, call_path, persistent_dir, c_bank_dir, rust_bank_dir,
         translation_dir, build_rs_path, chat_dir) = extract_all_paths(paths)
    """

    return (
        paths.target,
        paths.build_path, 
        paths.rust_build_path,
        paths.rust_lib_h_path,
        paths.run_test_path,
        paths.run_all_path,
        paths.raw_dir, #
        paths.target_dir,
        paths.work_dir,
        paths.c_code_dir,
        paths.rust_output_dir,
        paths.execute_path,
        paths.marker,

        paths.meta_dir,
        paths.div_meta_dir,
        paths.chat_dir,
        paths.chat_macro_dir,
        paths.log_dir,
        paths.exp_dir,
        paths.archive_dir,
        
        paths.macro_finder,
        paths.database_dir,
        #paths.lib_path,
        
        paths.dep_json_path,
        paths.list_path,
        paths.result_path,
        paths.moment_path,
        paths.line_path,
        paths.logging_path,
        
        paths.guards_path,
        paths.guarded_macros_path,
        paths.taken_macros_path,
        paths.all_macros_path,
        paths.taken_directive_path,
        paths.all_directive_path,
        paths.cfg_path,
        paths.independent_path,
        paths.flag_path,
        paths.const_path,
        paths.conflict_path,
        paths.global_path,
        paths.is_program_path,
        paths.build_config_path,

        paths.custom_headers_dir,
        paths.custom_json_path,
        paths.custom_header_path,

        paths.block_path, 
        paths.block_group_path,
        paths.rust_c_path,
        paths.c_rust_path,
        
        paths.map_path,
        paths.call_path,
        paths.persistent_dir,
        #paths.build_rs_path,

        paths.chat_dir,
        paths.history_path,
        paths.token_path,
        paths.count_path,
        paths.time_path,
        paths.output_dir,

        paths.independent_const_build_path,
        paths.flag_build_path,
    )



def execute_command(command): # -> Tuple[None, str]:  # (command: str) -> Tuple[None, str]:
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:  # If the command succeeded
        return (None, None)  #(None, '')  # Succeeded, so no error
    else:  # If the command failed
        return (None, result.stderr)  # Failed, so return stderr output



def remove_git_directory(rust_directory):
    """
    Remove the .git directory within the specified Rust project directory
    
    Parameters:
    -----------
    rust_directory : str
        Path to the Rust project directory
    """
    git_path = os.path.join(rust_directory, '.git')
    
    try:
        if os.path.exists(git_path):
            # Recursively delete the .git directory
            shutil.rmtree(git_path)
            print(f"Removed .git directory from {rust_directory}")
        else:
            print(f"No .git directory found in {rust_directory}")
    except Exception as e:
        print(f"Error removing .git directory: {e}")


def remove_base_path(full_path, base_path):
    base_path = os.path.normpath(base_path) # Normalize the base path
    full_path = os.path.normpath(full_path) # Normalize the full path
    
    base_length = len(base_path) # Get the length of the base path
    
    if full_path.startswith(base_path): # If the full path starts with the base path, strip that part
        return full_path[base_length:].strip(os.path.sep)
    else:
        return full_path


def obtain_c_path(rust_path, c_directory, rust_output_dir):

    source_flag = False
    file_name = os.path.basename(rust_path)
    if file_name[:-3].endswith("c"):
        suffix = ".c"
        source_flag = True
    elif file_name[:-3].endswith("h"):
        suffix = ".h"
        source_flag = True
    else:
        suffix = ".c" # Temporary location for build.rs
        print(file_name[:-3])
        print(file_name)
        #raise ValueError("The end of the rust_path is somehow wrong.")
    
    base_path = find_highest_source(c_directory)
    lowest_dir = os.path.basename(os.path.normpath(base_path)) # Name of the lowest directory in base_path
    rust_dir = rust_output_dir + "/" + "src"  + "/" + lowest_dir
    initial_path = remove_base_path(rust_path, rust_dir)

    if source_flag:
        c_path = base_path + "/" + initial_path[:-5] + suffix
    else:
        c_path = base_path + "/" + initial_path[:-3] + suffix

    # print(base_path)
    # print(c_path)
    return c_path



def obtain_metadata(c_path, given_meta_dir, rust_flag, path_flag, signal):
    """
    Generate or read a metadata file path from a file path
    
    Supports any file extension (uses the extension as-is to generate the metadata path)
    
    Args:
        c_path: Path to the source file
        given_meta_dir: Metadata directory
        rust_flag: Whether to add a Rust suffix
        path_flag: True=return path only, False=load data, None=return both
        signal: "def" or "use"
    
    Returns:
        Path, data, or both depending on path_flag
    """
    if c_path is None:
        return (None, None) if path_flag is None else None

    # Get the file extension (with dot)
    base_path, ext = os.path.splitext(c_path)
    
    # If there is no extension
    if not ext:
        file_suffix = "_noext"
        # print(f"No file extension found: {c_path}")
        # return (None, None) if path_flag is None else None
    
    # Remove the dot from the extension and convert to an underscore-prefixed suffix
    # e.g.: ".c" -> "_c", ".def" -> "_def", ".cpp" -> "_cpp"
    file_suffix = ext.replace('.', '_')
    
    # Build the suffix
    rust_suffix = "_rust" if rust_flag else ""
    signal_suffix = "_use" if signal == "use" else ""
    
    # Build the metadata file path
    meta_path = f"{given_meta_dir}/{base_path}{file_suffix}{rust_suffix}{signal_suffix}.json"
    
    # Handle return value
    if path_flag is False:
        # Load and return data only
        meta_data = read_json(meta_path)
        return meta_data
    elif path_flag is True:
        # Return path only
        return meta_path
    else:
        # Return both (path_flag is None)
        meta_data = read_json(meta_path)
        return meta_data, meta_path


def reverse_meta_path(meta_path, given_meta_dir):
    """
    Restore the original source file path from a metadata file path
    
    Args:
        meta_path: Path to the metadata file
        given_meta_dir: Metadata directory
    
    Returns:
        Absolute path of the original source file
    """
    # Remove the meta directory part
    rel_path = meta_path.replace(given_meta_dir + "/", "")
    
    # Remove .json
    rel_path = rel_path.replace(".json", "")
    
    # Remove suffixes (from the end)
    if rel_path.endswith("_use"):
        rel_path = rel_path[:-4]
    
    if rel_path.endswith("_rust"):
        rel_path = rel_path[:-5]
    
    # Find the last underscore+extension and convert back to dot format
    last_underscore = rel_path.rfind("_")
    if last_underscore != -1:
        base = rel_path[:last_underscore]
        ext = rel_path[last_underscore + 1:]
        
        if ext == "noext":
            result = base
        else:
            result = f"{base}.{ext}"
    else:
        result = rel_path
    
    # result = os.path.abspath(result)

    # cwd = os.getcwd()
    # if result.startswith(cwd):
    #     result = result[len(cwd):]
    #     if result.startswith("/"):
    #         result = result[1:]

    if not result.startswith("/"):
        result = "/" + result
        
    return result
    

def find_adjusted_start(file_path, original_start_line):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        
    current_line = original_start_line - 1  # Convert to 0-indexed
    
    # Regex pattern to find macro attributes
    macro_pattern = r'^\s*#\[.+\]'
    
    first_macro_line = None
    
    while current_line > 0:
        current_line -= 1
        if re.match(macro_pattern, lines[current_line]):
            # If a macro attribute is found, record that line
            first_macro_line = current_line
        elif not lines[current_line].strip():
            # Skip empty lines
            continue
        else:
            # If a non-macro-attribute line is found, break out of the loop
            break
    
    # If a macro attribute was found, return the line of the first macro attribute;
    # otherwise, return the original start line
    return (first_macro_line + 1) if first_macro_line is not None else original_start_line


def load_code_segment(file_path, start_line, end_line):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        return ''.join(lines[start_line-1:end_line])
    
def get_current_code(json_path): #def adjust_for_cfg(json_path):
    data = read_json(json_path)
    #data = json.loads(json_data)
    
    for item in data:
        file_path = item['file_path']
        original_start_line = item['start_line']
        item['start_line'] = find_adjusted_start(file_path, original_start_line)

    
    for item in data:
        file_path = item['file_path']
        start_line = item['start_line']
        end_line = item.get('end_line', start_line)  # Use start_line if end_line is not specified
        
        try:
            current_code = load_code_segment(file_path, start_line, end_line)
            item['current_code'] = current_code.rstrip()  # Remove trailing newlines
        except FileNotFoundError:
            item['current_code'] = f"Error: File not found - {file_path}"
        except IOError:
            item['current_code'] = f"Error: Unable to read file - {file_path}"

    
    write_json(json_path, data)
    #return json.dumps(data, ensure_ascii=False, indent=2)

    # For rust_code, set current_code for anything that is not a function
    data = read_json(json_path)
    for item in data:
        if item['category'] != "function" and item['rust_code'] is None:
            item['rust_code'] = item['current_code']
    
    write_json(json_path, data)


def is_blank_line(line):
    return len(line.strip()) == 0

def find_other_intervals(rust_path, meta_dir): # c_path, 
    meta_data, meta_path = obtain_metadata(rust_path, meta_dir, True, None, "def")
    
    # Exclude items where end_line is None
    meta_data = [item for item in meta_data if item['end_line'] is not None]

    # Get the ranges of existing blocks
    existing_blocks = [(item['start_line'], item['end_line']) for item in meta_data]
    existing_blocks.sort(key=lambda x: x[0])

    # Read the file
    with open(rust_path, 'r') as file:
        lines = file.readlines()

    new_blocks = []
    current_line = 1
    
    # Scan the entire file and detect new blocks
    for start, end in existing_blocks:
        if current_line < start:
            block_start = current_line
            while block_start < start and is_blank_line(lines[block_start - 1]):
                block_start += 1
            
            block_end = start - 1
            while block_end > block_start and is_blank_line(lines[block_end - 1]):
                block_end -= 1
            
            current_code = read_specific_lines(rust_path, block_start, block_end)

            if block_start < block_end:
                new_blocks.append({
                    "category": "others",
                    "name": "others",
                    "file_path": rust_path,
                    "start_line": block_start,
                    "end_line": block_end,
                    "current_code" : current_code,
                    "rust_code" : None, 
                })
        current_line = end + 1

    # If there are undetected blocks remaining until the end of the file
    if current_line <= len(lines):
        block_start = current_line
        while block_start <= len(lines) and is_blank_line(lines[block_start - 1]):
            block_start += 1
        
        block_end = len(lines)
        while block_end >= block_start and is_blank_line(lines[block_end - 1]):
            block_end -= 1
        
        current_code = read_specific_lines(rust_path, block_start, block_end)

        if block_start <= block_end:
            new_blocks.append({
                "category": "others",
                "name": "others",
                "file_path": rust_path,
                "start_line": block_start,
                "end_line": block_end,
                "current_code" : current_code,
                "rust_code" : None, 
            })

    # Add new blocks to meta_data
    meta_data.extend(new_blocks)

    # Sort by line number
    meta_data.sort(key=lambda x: x['start_line'])

    write_json(meta_path, meta_data)

    return json.dumps(meta_data, indent=4)



def add_tracing(rust_io_dir, toml_path):    
    # Read Cargo.toml
    with open(toml_path, 'r') as f:
        content = f.read()
    
    # Add [lib] section
    if '[lib]' not in content:
        # Add [lib] section if it does not exist
        lib_section = '\n[lib]\nname = "trans_rust"\ncrate-type = ["cdylib"]\n'
        # Add [lib] section after the package section
        if '[package]' in content:
            parts = content.split('[package]')
            package_parts = parts[1].split('[', 1)
            content = '[package]' + package_parts[0] + lib_section + ('[' + package_parts[1] if len(package_parts) > 1 else '')

    # Find the [dependencies] section
    if '[dependencies]' not in content:
        # Add [dependencies] section if it does not exist
        content += '\n[dependencies]\n'

    dependency_line = f'''tracing = "0.1"
tracing-subscriber = {{ version = "0.3", features = ["env-filter", "json"] }}'''

    # Check if the dependency has already been added
    #if f'{lib_name}' not in content:
        # Add after the [dependencies] section
    parts = content.split('[dependencies]')
    content = parts[0] + '[dependencies]\n' + dependency_line + (parts[1] if len(parts) > 1 else '')

    # Write the changes back
    with open(toml_path, 'w') as f:
        f.write(content)


def find_highest_source(targetectory):
    for root, dirs, files in os.walk(targetectory):
        for file in files:
            if file.endswith('.c') or file.endswith('.h'):
                return root
    return None

def update_path_map(
    mapping_file: str,
    child_path: str,
    rust_child_path: str,
    parent_path: str,
    rust_parent_path: str):

    if not os.path.exists(mapping_file):
        mapping_data = {}
    else:
        mapping_data = read_json(mapping_file)

    # Update mapping
    if child_path not in mapping_data:
        mapping_data[child_path] = {}

    mapping_data[child_path] = {
        "rust_path": rust_child_path,
        "parent_path": parent_path
    }

    if parent_path is not None:
        if parent_path not in mapping_data:
            mapping_data[parent_path] = {}
        
        mapping_data[parent_path]["rust_path"] = rust_parent_path
        if "child_path" not in mapping_data[parent_path]:
            mapping_data[parent_path]["child_path"] = []

        mapping_data[parent_path]["child_path"].append(child_path)
        
    #write_json(mapping_file, mapping_data)
    
    # After this, we'll make it so that it can also be searched using the rust_path key.
    if rust_child_path not in mapping_data:
        mapping_data[rust_child_path] = {}
    mapping_data[rust_child_path]["c_path"] = child_path
    mapping_data[rust_child_path]["parent_path"] = rust_parent_path

    if rust_parent_path is not None:
        if rust_parent_path not in mapping_data:
            mapping_data[rust_parent_path] = {}
        
        mapping_data[rust_parent_path]["c_path"] = parent_path
        if "child_path" not in mapping_data[rust_parent_path]:
            mapping_data[rust_parent_path]["child_path"] = []
        mapping_data[rust_parent_path]["child_path"].append(rust_child_path)

    write_json(mapping_file, mapping_data)

    return mapping_data


def get_path_map(mapping_file: str, file_path: str, option: str):
    print(f"get_path_map() for {file_path}")
    answer_path = None

    if not os.path.exists(mapping_file):
        mapping_data = {}
    else:
        mapping_data = read_json(mapping_file)

    c_path = None
    rust_path = None

    if file_path not in mapping_data:
        return answer_path

    if file_path.endswith(".c") or file_path.endswith(".h"):
        c_path = file_path
    elif file_path.endswith(".rs"):
        rust_path = file_path

    if file_path.endswith(".c") or file_path.endswith(".h"):
        if option == "parent" and 'parent_path' in mapping_data[c_path]:
            answer_path = mapping_data[c_path]['parent_path']
        elif option == "rust" and 'rust_path' in mapping_data[c_path]:
            answer_path = mapping_data[c_path]['rust_path'] 
        elif option == "child" and 'child_path' in mapping_data[c_path]:
            # This should be a list
            # answer_path =  []
            answer_path = mapping_data[c_path]['child_path']  

    elif file_path.endswith(".rs"):
        if rust_path in mapping_data:
            if option == "parent" and 'parent_path' in mapping_data[rust_path]:
                answer_path = mapping_data[rust_path]['parent_path']
            elif option == "c" and 'c_path' in mapping_data[rust_path]:
                answer_path = mapping_data[rust_path]['c_path'] 
            elif option == "child" and 'child_path' in mapping_data[rust_path]:
                answer_path = mapping_data[rust_path]['child_path'] 

            """
            elif option == "c":
                rust_path = c_path
                #mapping_data[c_path]['child_path']  
                for file_path, entry in mapping_data.items():
                    if entry['rust_path'] == rust_path:
                        answer_path = file_path
                        break
            """
    print(f"Get in get_path_map(): {answer_path} for {file_path}")
    return answer_path



def get_setting_data(data, target_dir):  # , target # translation_dir, 
    # dst_dir = f"{translation_dir}/{target}"
    # print(dst_dir)
    # config_path = f"{dst_dir}/setting.json"

    created_paths = [] #data['created_paths']  # This is dangerous
    if data is None:
        data = {}

    build_path = data['build_path']
    run_test_path = data['run_test_path']
    run_all_path = data['run_all_path']
    target_funcs = data['target_funcs']

    print(f"created_paths: {created_paths}")
    print(f"build_path: {build_path}")
    print(f"run_test_path: {run_test_path}")
    print(f"run_all_path: {run_all_path}")

    # filetered_created_paths = []
    # print(f"file_paths in created_paths")
    # for file_path in created_paths:
    #     file_path = f"{target_dir}/{file_path}"
    #     filetered_created_paths.append(file_path)
    #     print(f"{file_path}")

    filetered_target_funcs = []
    print(f"file_paths in target_funcs")
    for item in target_funcs:
        file_path = item['def_file_path']
        item['def_file_path'] = f"{target_dir}/{file_path}"
        filetered_target_funcs.append(item)
        print(f"{file_path}")


    build_path = f"{target_dir}/{build_path}"
    run_test_path = f"{target_dir}/{run_test_path}"
    run_all_path = f"{target_dir}/{run_all_path}"

    #write_json(config_path, data)
    return build_path, run_test_path, run_all_path, filetered_target_funcs # filetered_created_paths,  # , run_all_path #created_paths



def calculate_execution_time(chat_dir, output_path, trial_id, target):

    files = os.listdir(chat_dir)
    chat_files = [f for f in files if re.match(r'chat\d+_(user|llm)\.txt', f)] # Filter files matching the pattern chat{number}_{user/llm}.txt
    
    if not chat_files:
        return "Error: No chat files found"

    def extract_number(filename): # Function to extract the number from a filename
        match = re.search(r'chat(\d+)_', filename)
        if match:
            return int(match.group(1))
        return -1
    
    chat_files.sort(key=extract_number) # Sort by number and get the first and last files from chat0000 onward
    first_file = None
    for f in chat_files:
        num = extract_number(f)
        if num >= 0:  # Files from chat0000 onward
            first_file = f
            break
            
    if not first_file:
        return "Error: No valid chat files found"
        
    last_file = chat_files[-1]
    
    # Create full paths
    file1_path = os.path.join(chat_dir, first_file)
    file2_path = os.path.join(chat_dir, last_file)
    
    print(f"First file: {first_file}")
    print(f"Last file: {last_file}")

    try:
        # Get creation time using the appropriate method for the platform
        if platform.system() == 'Windows':
            birth_time1 = os.path.getctime(file1_path)
            birth_time2 = os.path.getctime(file2_path)
        else:  # macOS/Linux
            stat_info1 = os.stat(file1_path)
            stat_info2 = os.stat(file2_path)
            
            # st_birthtime is available on macOS
            if hasattr(stat_info1, 'st_birthtime'):
                birth_time1 = stat_info1.st_birthtime
                birth_time2 = stat_info2.st_birthtime
            else:
                # Birth time is not available on some Linux systems, so use change time instead of creation time
                birth_time1 = stat_info1.st_ctime
                birth_time2 = stat_info2.st_ctime
        
        # Calculate time difference (in seconds)
        execution_time = birth_time2 - birth_time1
        
        # Format into a human-readable form
        time_delta = datetime.timedelta(seconds=execution_time)
        
        result =  {
            'target' : target,
            'trial_id' : trial_id, 
            'seconds': execution_time,
            'formatted': str(time_delta),
            'start_time': str(datetime.datetime.fromtimestamp(birth_time1)),
            'end_time': str(datetime.datetime.fromtimestamp(birth_time2)),
            'start_file' : file1_path,
            'end_file' : file2_path,
        }

        print(f"execution time: {result['formatted']} ({result['seconds']} seconds)")
        print(f"start time: {result['start_time']}")
        print(f"end time: {result['end_time']}")
        
        write_json(output_path, {})
        write_json(output_path, result)

    except FileNotFoundError as e:
        return f"Error: File not found - {e}"
    except Exception as e:
        return f"Error: {e}"


def find_matching_path(workspace_dir, target_suffix):

    matching_paths = []
    matching_path = target_suffix
    for root, _, files in os.walk(workspace_dir):
        for file in files:
            full_path = os.path.join(root, file)
            if full_path.endswith(target_suffix):
                matching_paths.append(full_path)
                matching_path = full_path
                break
    
    return matching_path


def add_line_numbers(input_file):
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as temp_file:
            with open(input_file, 'r', encoding='utf-8') as infile:
                # Read all lines and get the maximum indent level and line count
                lines = list(infile)
                if not lines:
                    #print(f"File {input_file} is empty.")
                    return

                max_line_num = len(lines)
                max_indent = max((len(line) - len(line.lstrip())) // 4 for line in lines)
                
                # Calculate the maximum digit count for line numbers and indent levels
                line_num_width = len(str(max_line_num))
                indent_width = len(str(max_indent))
                
                # Create the format string (fix the position of the colon)
                format_str = f"Line {{:{line_num_width}d}} [{{:{indent_width}d}}]: {{}}"
                
                # Process each line
                for line_number, line in enumerate(lines, start=1):
                    indent_level = (len(line) - len(line.lstrip())) // 4
                    numbered_line = format_str.format(line_number, indent_level, line)
                    temp_file.write(numbered_line)
                
        # Overwrite the original file with the contents of the temporary file
        os.replace(temp_file.name, input_file)
        #print(f"Wrote file with line numbers and indent levels to {input_file}.")

    except UnicodeDecodeError:
        print(f"Warning: Skipping binary file: {input_file}")
        return
        
    except IOError as e:
        #print(f"An error occurred: {e}")
        print(f"An error occurred: {e}")



def add_line_numbers_custom(input_file, fixed_number):
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as temp_file:
            with open(input_file, 'r', encoding='utf-8') as infile:
                # Read all lines and get the maximum indent level and line count
                lines = list(infile)
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
                for line_number, line in enumerate(lines, start=fixed_number):
                    indent_level = (len(line) - len(line.lstrip())) // 4
                    numbered_line = format_str.format(line_number, indent_level, line)
                    temp_file.write(numbered_line)
                
        # Overwrite the original file with the temporary file contents
        os.replace(temp_file.name, input_file)
        #print(f"Wrote file with line numbers and indent levels to {input_file}.")
    except IOError as e:
        #print(f"An error occurred: {e}")
        print(f"An error occurred: {e}")


def get_unit_code(one_unit):  # , original_dir, target_dir
    c_code_parts = []
    
    for item in one_unit:
        #target_file_path = item['file_path'].replace(os.path.abspath(target_dir), os.path.abspath(original_dir))
        #print(target_file_path)
        code = read_specific_lines(item['file_path'], item['start_line'], item['end_line'])
        #c_code_parts.append("=========")
        c_code_parts.append(code)
    
    # Join the list with newlines into a single string
    return '\n'.join(c_code_parts)


def get_unit_code_with_location(one_unit, database_dir):  # , original_dir, target_dir
    c_code_parts = []
    
    for item in one_unit:
        #target_file_path = item['file_path'].replace(os.path.abspath(target_dir), os.path.abspath(original_dir))
        #print(target_file_path)
        c_code_parts.append(f"*** {item['file_path']} ***")
        #code = read_specific_lines(item['file_path'], item['start_line'], item['end_line'])
        code = get_lined_specific_code(database_dir, item['file_path'], item['start_line'], item['end_line'])
        c_code_parts.append("******************************\n")
        #c_code_parts.append("=========")
        c_code_parts.append(code)
    
    # Join the list with newlines into a single string
    return '\n'.join(c_code_parts)



def get_lined_code(test_path, workspace_dir):
    if not os.path.exists(test_path):
        test_path = find_matching_path(workspace_dir, test_path)

    test_code = None
    if os.path.exists(test_path):
        lined_test_path = "lined.txt" #"lined.c"
        copy_file(test_path, lined_test_path)
        add_line_numbers(lined_test_path)
        #add_line_numbers_custom(test_path, fixed_number)
        test_code = read_file(lined_test_path)

        delete_file(lined_test_path)

    if test_code is None:
        test_code = "" # If the file does not exist, avoid a None error in the prompt.
    return test_code



def get_lined_specific_code(database_dir, test_path, start_line, end_line, work_dir=None):
    
    if test_path is None:
        return ""

    if work_dir is not None:
        if not os.path.exists(test_path):
            test_path = find_matching_path(work_dir, test_path)

    target_code = read_specific_lines(test_path, start_line, end_line)
    
    lined_test_path = f"{database_dir}/lined.txt" #"lined.c"
    write_file(lined_test_path, target_code)
    add_line_numbers_custom(lined_test_path, int(start_line)) #add_line_numbers(lined_test_path)
    test_code = read_file(lined_test_path)

    delete_file(lined_test_path)

    return test_code


def get_list_path(dep_json_path, target_dir, list_path):
    all_files = set()
    data = read_json(dep_json_path)
    for item in data:
        if target_dir in item['source']:
            all_files.add(item['source'])
        if target_dir in item['include']:
            all_files.add(item['include'])

    with open(list_path, 'w') as f:
        for filename in list(all_files):
            f.write(f"{filename}\n")


def parse_def_loc(def_loc):
    """Parse def_loc and return file_path, line, column"""
    # if def_loc == "undefined":
    #     return None, None, None
    
    # Split "file_path:line:column" from the right
    parts = def_loc.rsplit(':', 2)
    if len(parts) == 3:
        return parts[0], int(parts[1]), int(parts[2])
    else:
        # If parsing fails, treat the entire string as file_path
        return def_loc, None, None #def_loc, None, None


def normalize_translation_div_metadata(meta_dir, current_dir):
    """
    Convert absolute paths in metadata to relative paths
    
    Args:
        meta_dir: Metadata directory
        current_dir: Base directory (reference for absolute paths)
    """
    print("normalize metadata...")
    
    meta_path = Path(meta_dir)
    current_path = Path(current_dir).resolve()
    
    # Recursively retrieve .json files
    meta_paths = list(meta_path.rglob("*.json"))
    
    print(f"Found {len(meta_paths)} JSON files")
    
    for json_file in meta_paths:
        print(f"Processing: {json_file.relative_to(meta_path)}")
        
        # Read the JSON file
        meta_data = read_json(json_file)
        
        # Process metadata
        for item in meta_data:
            # Convert def_file_path to a relative path
            if 'file_path' in item:
                item['file_path'] = normalize_path(
                    item['file_path'], 
                    current_path
                )

            if 'definition' in item:
                def_path, def_line, def_column = parse_def_loc(item['definition'])
                def_path = normalize_path(
                    def_path, 
                    current_path
                )

                if def_line is not None:
                    item['definition'] = f"{def_path}:{def_line}:{def_column}"
                else:
                    item['definition'] = f"{def_path}"

            if 'usage_location' in item:
                use_path, use_line, use_column = parse_def_loc(item['usage_location'])
                use_path = normalize_path(
                    use_path, 
                    current_path
                )

                if use_line is not None:
                    item['usage_location'] = f"{use_path}:{use_line}:{use_column}"
                else:
                    item['usage_location'] = f"{use_path}"
            
            # Process callees
            if 'uses' in item:
                callees = item['uses']
                for callee_item in callees:
                    # Convert call_file_path to a relative path
                    if 'file_path' in callee_item:
                        callee_item['file_path'] = normalize_path(
                            callee_item['file_path'], 
                            current_path
                        )

                    if 'definition' in callee_item:
                        def_path, def_line, def_column = parse_def_loc(callee_item['definition'])
                        def_path = normalize_path(
                            def_path, 
                            current_path
                        )

                        if def_line is not None:
                            callee_item['definition'] = f"{def_path}:{def_line}:{def_column}"
                        else:
                            callee_item['definition'] = f"{def_path}"

                    if 'usage_location' in callee_item:
                        use_path, use_line, use_column = parse_def_loc(callee_item['usage_location'])
                        use_path = normalize_path(
                            use_path, 
                            current_path
                        )

                        if use_line is not None:
                            callee_item['usage_location'] = f"{use_path}:{use_line}:{use_column}"
                        else:
                            callee_item['usage_location'] = f"{use_path}"
            ##
            if 'components' in item:
                for each_item in item['components']: #.items():
                    if 'file_path' in each_item:
                        each_item['file_path'] = normalize_path(
                            each_item['file_path'], 
                            current_dir
                        )

                    if 'definition' in each_item:
                        def_path, def_line, def_column = parse_def_loc(each_item['definition'])
                        def_path = normalize_path(
                            def_path, 
                            current_path
                        )

                        if def_line is not None:
                            each_item['definition'] = f"{def_path}:{def_line}:{def_column}"
                        else:
                            each_item['definition'] = f"{def_path}"

                    if 'usage_location' in each_item:
                        use_path, use_line, use_column = parse_def_loc(each_item['usage_location'])
                        use_path = normalize_path(
                            use_path, 
                            current_path
                        )

                        if use_line is not None:
                            each_item['usage_location'] = f"{use_path}:{use_line}:{use_column}"
                        else:
                            each_item['usage_location'] = f"{use_path}"
                    
                    if 'uses' in each_item:
                        callees = each_item['uses']
                        for callee_item in callees:
                            # Convert call_file_path to an absolute path
                            if 'file_path' in callee_item:
                                callee_item['file_path'] = normalize_path(
                                    callee_item['file_path'], 
                                    current_dir
                                )
                            if 'definition' in callee_item:
                                def_path, def_line, def_column = parse_def_loc(callee_item['definition'])
                                def_path = normalize_path(
                                    def_path, 
                                    current_path
                                )

                                if def_line is not None:
                                    callee_item['definition'] = f"{def_path}:{def_line}:{def_column}"
                                else:
                                    callee_item['definition'] = f"{def_path}"

                            if 'usage_location' in callee_item:
                                use_path, use_line, use_column = parse_def_loc(callee_item['usage_location'])
                                use_path = normalize_path(
                                    use_path, 
                                    current_path
                                )

                                if use_line is not None:
                                    callee_item['usage_location'] = f"{use_path}:{use_line}:{use_column}"
                                else:
                                    callee_item['usage_location'] = f"{use_path}"
        
        # Save changes
        write_json(json_file, meta_data)
    
    print(f"Normalization complete: {len(meta_paths)} files processed")


def normalize_key_path(key, base_path):
    """
    Convert file paths within a key to relative paths
    
    Example: "test3_3:{TRANS_HOME}/trans_c_0000/mini2/test_1.c:3"
         -> "test3_3:test_1.c:3"
    """
    # Assumes "name:path:line" format
    parts = key.split(':')
    
    if len(parts) >= 3:
        # Extract the path portion (from the 2nd element to the one before the last)
        # e.g.: ["test3_3", "/root/.../test_1.c", "3"]
        name = parts[0]
        line = parts[-1]
        # The path is the middle part separated by : (also considering Windows paths)
        path_str = ':'.join(parts[1:-1])
        
        # Normalize the path
        normalized_path = normalize_path(path_str, base_path)
        
        return f"{name}:{normalized_path}:{line}"
    
    return key


def normalize_translation_metadata(meta_dir, target_dir):
    """
    Convert absolute paths in metadata to relative paths
    
    Args:
        meta_dir: Metadata directory
        target_dir: Base directory (reference for absolute paths)
    """
    print("normalize metadata...")
    
    meta_path = Path(meta_dir)
    current_path = Path(target_dir).resolve()
    
    # Recursively retrieve .json files
    meta_paths = list(meta_path.rglob("*.json"))
    
    print(f"Found {len(meta_paths)} JSON files")
    
    for json_file in meta_paths:
        #print(f"Processing: {json_file.relative_to(meta_path)}")
        # Read the JSON file
        meta_data = read_json(json_file)
        
        # Create a new dictionary (to transform the keys)
        new_meta_data = {}
        
        # Process metadata
        for name_key, item in meta_data.items():
            # Convert the key's path
            new_key = normalize_key_path(name_key, current_path)
            
            # Convert def_file_path to a relative path
            if 'file_path' in item:
                item['file_path'] = normalize_path(
                    item['file_path'], 
                    current_path
                )
            
            # Convert definition to a relative path
            if 'definition' in item:
                def_path, def_line, def_column = parse_def_loc(item['definition'])
                def_path = normalize_path(
                    def_path, 
                    current_path
                )

                if def_line is not None:
                    item['definition'] = f"{def_path}:{def_line}:{def_column}"
                else:
                    item['definition'] = f"{def_path}"

            if 'usage_location' in item:
                use_path, use_line, use_column = parse_def_loc(item['usage_location'])
                use_path = normalize_path(
                    use_path, 
                    current_path
                )

                if use_line is not None:
                    item['usage_location'] = f"{use_path}:{use_line}:{use_column}"
                else:
                    item['usage_location'] = f"{use_path}"


            # Process callees
            if 'uses' in item:
                callees = item['uses']
                for callee_item in callees:
                    if 'file_path' in callee_item:
                        callee_item['file_path'] = normalize_path(
                            callee_item['file_path'], 
                            current_path
                        )

                    if 'definition' in callee_item:
                        def_path, def_line, def_column = parse_def_loc(callee_item['definition'])
                        def_path = normalize_path(
                            def_path, 
                            current_path
                        )

                        if def_line is not None:
                            callee_item['definition'] = f"{def_path}:{def_line}:{def_column}"
                        else:
                            callee_item['definition'] = f"{def_path}"

                    if 'usage_location' in callee_item:
                        use_path, use_line, use_column = parse_def_loc(callee_item['usage_location'])
                        use_path = normalize_path(
                            use_path, 
                            current_path
                        )

                        if use_line is not None:
                            callee_item['usage_location'] = f"{use_path}:{use_line}:{use_column}"
                        else:
                            callee_item['usage_location'] = f"{use_path}"
            
            # Process components
            if 'components' in item:
                new_components = {}
                for each_key, each_item in item['components'].items():
                    # Also convert the component's key
                    new_each_key = normalize_key_path(each_key, current_path)
                    
                    if 'file_path' in each_item:
                        each_item['file_path'] = normalize_path(
                            each_item['file_path'], 
                            current_path
                        )
                    
                    if 'definition' in each_item:
                        def_path, def_line, def_column = parse_def_loc(each_item['definition'])
                        def_path = normalize_path(
                            def_path, 
                            current_path
                        )

                        if def_line is not None:
                            each_item['definition'] = f"{def_path}:{def_line}:{def_column}"
                        else:
                            each_item['definition'] = f"{def_path}"

                    if 'usage_location' in each_item:
                        use_path, use_line, use_column = parse_def_loc(each_item['usage_location'])
                        use_path = normalize_path(
                            use_path, 
                            current_path
                        )

                        if use_line is not None:
                            each_item['usage_location'] = f"{use_path}:{use_line}:{use_column}"
                        else:
                            each_item['usage_location'] = f"{use_path}"
                    
                    if 'uses' in each_item:
                        callees = each_item['uses']
                        for callee_item in callees:
                            if 'file_path' in callee_item:
                                callee_item['file_path'] = normalize_path(
                                    callee_item['file_path'], 
                                    current_path
                                )

                            if 'definition' in callee_item:
                                def_path, def_line, def_column = parse_def_loc(callee_item['definition'])
                                def_path = normalize_path(
                                    def_path, 
                                    current_path
                                )

                                if def_line is not None:
                                    callee_item['definition'] = f"{def_path}:{def_line}:{def_column}"
                                else:
                                    callee_item['definition'] = f"{def_path}"

                            if 'usage_location' in callee_item:
                                use_path, use_line, use_column = parse_def_loc(callee_item['usage_location'])
                                use_path = normalize_path(
                                    use_path, 
                                    current_path
                                )

                                if use_line is not None:
                                    callee_item['usage_location'] = f"{use_path}:{use_line}:{use_column}"
                                else:
                                    callee_item['usage_location'] = f"{use_path}"
                    
                    new_components[new_each_key] = each_item
                
                item['components'] = new_components
            
            new_meta_data[new_key] = item
        
        # Save changes
        current_dir = os.getcwd()
        # print(target_dir)
        # print(meta_dir)
        # print(json_file)

        if str(target_dir) in str(json_file):
            relative_part = str(json_file).split(str(target_dir))[-1].lstrip('/')
            new_json_file = Path(current_dir) / Path(os.path.dirname(meta_dir)) / relative_part
            print(f"{json_file} -> {new_json_file}")
            os.makedirs(new_json_file.parent, exist_ok=True)
            # print(new_json_file)
            delete_file(json_file)

            # Recursively delete directories that have become empty
            parent = json_file.parent
            while parent != meta_path and parent.exists():
                if not any(parent.iterdir()):
                    parent.rmdir()
                    parent = parent.parent
                else:
                    break
                    
            write_json(new_json_file, new_meta_data)

        else:
            write_json(json_file, new_meta_data)
        
    print(f"Normalization complete: {len(meta_paths)} files processed")

def denormalize_key_path(key, base_path):
    """
    Convert relative paths within a key to absolute paths
    
    Example: "test3_3:test_1.c:3"
         -> "test3_3:{TRANS_HOME}/trans_c_0000/mini2/test_1.c:3"
    """
    parts = key.split(':')
    
    if len(parts) >= 3:
        name = parts[0]
        line = parts[-1]
        path_str = ':'.join(parts[1:-1])
        
        # Convert the path to an absolute path
        denormalized_path = denormalize_path(path_str, base_path)
        
        return f"{name}:{denormalized_path}:{line}"
    
    return key


def is_already_denormalized(meta_data):
    """Check if the metadata has already been denormalized"""
    for name_key, item in meta_data.items():
        if '__meta__' in item and item['__meta__'] is True:
            return True
    return False


def denormalize_translation_metadata(meta_dir, target_dir, record_flag):
    print("denormalize metadata...")
    if not os.path.exists(meta_dir):
        return

    work_dir = os.path.dirname(target_dir)
    meta_path = Path(meta_dir)
    current_path = Path(work_dir).resolve()
    meta_paths = list(meta_path.rglob("*.json"))

    for json_file in meta_paths:
        meta_data = read_json(json_file)
        
        if record_flag is True and is_already_denormalized(meta_data):
            print(f"skip (already denormalized): {json_file}")
            continue

        # Create a new dictionary (to transform the keys)
        new_meta_data = {}
        
        # Process metadata
        first = True
        for name_key, item in meta_data.items():
            # Convert the key's path
            new_key = denormalize_key_path(name_key, current_path)
            
            # Convert file_path to an absolute path
            if 'file_path' in item:
                item['file_path'] = denormalize_path(
                    item['file_path'], 
                    work_dir
                )
            
            # Convert definition to an absolute path
            if 'definition' in item:
                def_path, def_line, def_column = parse_def_loc(item['definition'])
                def_path = denormalize_path(
                    def_path, 
                    current_path
                )

                if def_line is not None:
                    item['definition'] = f"{def_path}:{def_line}:{def_column}"
                else:
                    item['definition'] = f"{def_path}"

            if 'usage_location' in item:
                use_path, use_line, use_column = parse_def_loc(item['usage_location'])
                use_path = denormalize_path(
                    use_path, 
                    current_path
                )

                if use_line is not None:
                    item['usage_location'] = f"{use_path}:{use_line}:{use_column}"
                else:
                    item['usage_location'] = f"{use_path}"
            
            # Process uses
            if 'uses' in item:
                callees = item['uses']
                for callee_item in callees:
                    if 'file_path' in callee_item:
                        callee_item['file_path'] = denormalize_path(
                            callee_item['file_path'], 
                            work_dir
                        )

                    if 'definition' in callee_item:
                        def_path, def_line, def_column = parse_def_loc(callee_item['definition'])
                        def_path = denormalize_path(
                            def_path, 
                            current_path
                        )

                        if def_line is not None:
                            callee_item['definition'] = f"{def_path}:{def_line}:{def_column}"
                        else:
                            callee_item['definition'] = f"{def_path}"

                    if 'usage_location' in callee_item:
                        use_path, use_line, use_column = parse_def_loc(callee_item['usage_location'])
                        use_path = denormalize_path(
                            use_path, 
                            current_path
                        )

                        if use_line is not None:
                            callee_item['usage_location'] = f"{use_path}:{use_line}:{use_column}"
                        else:
                            callee_item['usage_location'] = f"{use_path}"

            # Process components
            if 'components' in item:
                new_components = {}
                for each_key, each_item in item['components'].items():
                    # Also convert the component's key
                    new_each_key = denormalize_key_path(each_key, current_path)
                    
                    if 'file_path' in each_item:
                        each_item['file_path'] = denormalize_path(
                            each_item['file_path'], 
                            work_dir
                        )
                    
                    if 'definition' in each_item:
                        def_path, def_line, def_column = parse_def_loc(each_item['definition'])
                        def_path = denormalize_path(
                            def_path, 
                            current_path
                        )

                        if def_line is not None:
                            each_item['definition'] = f"{def_path}:{def_line}:{def_column}"
                        else:
                            each_item['definition'] = f"{def_path}"

                    if 'usage_location' in each_item:
                        use_path, use_line, use_column = parse_def_loc(each_item['usage_location'])
                        use_path = denormalize_path(
                            use_path, 
                            current_path
                        )

                        if use_line is not None:
                            each_item['usage_location'] = f"{use_path}:{use_line}:{use_column}"
                        else:
                            each_item['usage_location'] = f"{use_path}"

                    if 'uses' in each_item:
                        callees = each_item['uses']
                        for callee_item in callees:
                            if 'file_path' in callee_item:
                                callee_item['file_path'] = denormalize_path(
                                    callee_item['file_path'], 
                                    work_dir
                                )

                            if 'definition' in callee_item:
                                def_path, def_line, def_column = parse_def_loc(callee_item['definition'])
                                def_path = denormalize_path(
                                    def_path, 
                                    current_path
                                )

                                if def_line is not None:
                                    callee_item['definition'] = f"{def_path}:{def_line}:{def_column}"
                                else:
                                    callee_item['definition'] = f"{def_path}"

                            if 'usage_location' in callee_item:
                                use_path, use_line, use_column = parse_def_loc(callee_item['usage_location'])
                                use_path = denormalize_path(
                                    use_path, 
                                    current_path
                                )

                                if use_line is not None:
                                    callee_item['usage_location'] = f"{use_path}:{use_line}:{use_column}"
                                else:
                                    callee_item['usage_location'] = f"{use_path}"
                                    
                    
                    new_components[new_each_key] = each_item
                
                item['components'] = new_components
            
            if first is True:  # if record_flag is True and first is True:
                if record_flag is True:
                    item['__meta__'] = True
                else:
                    item['__meta__'] = False
                first = False
        
            new_meta_data[new_key] = item

        new_json_file = os.path.abspath(json_file)
        relative_target_dir = Path(target_dir).relative_to(Path.cwd())
        new_json_file = new_json_file.replace(meta_dir, f"{meta_dir}/{target_dir}")
        #current_dir = os.path.dirname(meta_dir)
        # print(new_json_file)
 
        #new_json_file = Path(target_dir) / Path(json_file.name)
        new_json_file = Path(new_json_file) 
        os.makedirs(new_json_file.parent, exist_ok=True)

        #write_json(json_file, new_meta_data)
        delete_file(json_file)

        # print(f"meta_dir: {meta_dir}")
        # print(f"json_file: {json_file}")
        # print(f"new_json_file: {new_json_file}")
        # print(f"same? {str(json_file) == str(new_json_file)}")

        write_json(new_json_file, new_meta_data)

def denormalize_translation_div_metadata(meta_dir, current_dir):
    print("denormalize metadata...")
    if not os.path.exists(meta_dir):
        return

    meta_path = Path(meta_dir)
    meta_paths = list(meta_path.rglob("*.json"))

    for json_file in meta_paths:
        meta_data = read_json(json_file)
        # Process metadata
        for item in meta_data: #.items():
            # Convert def_file_path to an absolute path
            if 'file_path' in item:
                item['file_path'] = denormalize_path(
                    item['file_path'], 
                    current_dir
                )

            if 'definition' in item:
                def_path, def_line, def_column = parse_def_loc(item['definition'])
                def_path = denormalize_path(
                    def_path, 
                    current_path
                )

                if def_line is not None:
                    item['definition'] = f"{def_path}:{def_line}:{def_column}"
                else:
                    item['definition'] = f"{def_path}"

            if 'usage_location' in item:
                use_path, use_line, use_column = parse_def_loc(item['usage_location'])
                use_path = denormalize_path(
                    use_path, 
                    current_path
                )

                if use_line is not None:
                    item['usage_location'] = f"{use_path}:{use_line}:{use_column}"
                else:
                    item['usage_location'] = f"{use_path}"
            
            # Process callees
            if 'uses' in item:
                callees = item['uses']
                for callee_item in callees:
                    # Convert call_file_path to an absolute path
                    if 'file_path' in callee_item:
                        callee_item['file_path'] = denormalize_path(
                            callee_item['file_path'], 
                            current_dir
                        )

                    if 'definition' in callee_item:
                        def_path, def_line, def_column = parse_def_loc(callee_item['definition'])
                        def_path = denormalize_path(
                            def_path, 
                            current_path
                        )

                        if def_line is not None:
                            callee_item['definition'] = f"{def_path}:{def_line}:{def_column}"
                        else:
                            callee_item['definition'] = f"{def_path}"

                    if 'usage_location' in callee_item:
                        use_path, use_line, use_column = parse_def_loc(callee_item['usage_location'])
                        use_path = denormalize_path(
                            use_path, 
                            current_path
                        )

                        if use_line is not None:
                            callee_item['usage_location'] = f"{use_path}:{use_line}:{use_column}"
                        else:
                            callee_item['usage_location'] = f"{use_path}"

            if 'components' in item:
                for each_item in item['components']: #.items():
                    if 'file_path' in each_item:
                        each_item['file_path'] = denormalize_path(
                            each_item['file_path'], 
                            current_dir
                        )

                    if 'definition' in each_item:
                        def_path, def_line, def_column = parse_def_loc(each_item['definition'])
                        def_path = denormalize_path(
                            def_path, 
                            current_path
                        )

                        if def_line is not None:
                            each_item['definition'] = f"{def_path}:{def_line}:{def_column}"
                        else:
                            each_item['definition'] = f"{def_path}"

                    if 'usage_location' in each_item:
                        use_path, use_line, use_column = parse_def_loc(each_item['usage_location'])
                        use_path = denormalize_path(
                            use_path, 
                            current_path
                        )

                        if use_line is not None:
                            each_item['usage_location'] = f"{use_path}:{use_line}:{use_column}"
                        else:
                            each_item['usage_location'] = f"{use_path}"

                    
                    if 'uses' in each_item:
                        callees = each_item['uses']
                        for callee_item in callees:
                            # Convert call_file_path to an absolute path
                            if 'file_path' in callee_item:
                                callee_item['file_path'] = denormalize_path(
                                    callee_item['file_path'], 
                                    current_dir
                                )
                            
                            if 'definition' in callee_item:
                                def_path, def_line, def_column = parse_def_loc(callee_item['definition'])
                                def_path = denormalize_path(
                                    def_path, 
                                    current_path
                                )

                                if def_line is not None:
                                    callee_item['definition'] = f"{def_path}:{def_line}:{def_column}"
                                else:
                                    callee_item['definition'] = f"{def_path}"

                            if 'usage_location' in callee_item:
                                use_path, use_line, use_column = parse_def_loc(callee_item['usage_location'])
                                use_path = denormalize_path(
                                    use_path, 
                                    current_path
                                )

                                if use_line is not None:
                                    callee_item['usage_location'] = f"{use_path}:{use_line}:{use_column}"
                                else:
                                    callee_item['usage_location'] = f"{use_path}"

        """
        for nema_key, item in meta_data.items():
            if 'name' in item and item['name'] in consts: # Sometimes raises KeyError: 'name', maybe it's better to separate macros?
                item['is_const'] = True

            if 'components' in item:
                for each_key, each_item in item['components'].items():
                    if 'name' in each_item and each_item['name'] in consts:
                        each_item['is_const'] = True

        """

        write_json(json_file, meta_data)





def normalize_metafiles(meta_dir, current_dir, all_macros_path, taken_macros_path, guards_path):
    """
    Convert absolute paths in metadata to relative paths
    
    Args:
        meta_dir: Metadata directory
        current_dir: Base directory (reference for absolute paths)
        all_macros_path: Path to all_conditions.json (corresponds to data["files"])
        taken_macros_path: Path to taken_conditions.json (corresponds to data["macros"])
        guards_path: Path to guards.json
    """
    print("normalize metadata...")
    
    print(f"all_conds: {all_macros_path}")
    print(f"taken_conds: {taken_macros_path}") 
    print(f"guards: {guards_path}")
    
    current_path = Path(current_dir).resolve()
    
    # 1. Process all_conditions.json (data["files"])
    if all_macros_path and Path(all_macros_path).exists():
        print(f"\nProcessing: {all_macros_path}")
        all_conds = read_json(all_macros_path)
        
        # Create a new dictionary (also converting keys)
        normalized_all_conds = {}
        
        for file_path, conditions_dict in all_conds.items():
            # Convert the key to a relative path
            normalized_key = normalize_path(file_path, current_path)
            
            if isinstance(conditions_dict, dict):
                # Process each category: defined, ifdef, ifndef, if, elif, endif
                for cond_type, cond_list in conditions_dict.items():
                    if isinstance(cond_list, list):
                        for item in cond_list:
                            if isinstance(item, dict):
                                normalize_condition_item(item, current_path)
            
            # Save with the new key
            normalized_all_conds[normalized_key] = conditions_dict
        
        write_json(all_macros_path, normalized_all_conds)
        print(f"  ✓ Normalized {len(normalized_all_conds)} file groups")

    
    # 2. Process taken_conditions.json (data["macros"])
    if taken_macros_path and Path(taken_macros_path).exists():
        print(f"\nProcessing: {taken_macros_path}")
        taken_conds = read_json(taken_macros_path)
        
        # Create a new dictionary (also converting keys)
        normalized_taken_conds = {}
        
        for macro_key, macro_info in taken_conds.items():
            # Convert macro_key to a relative path
            normalized_macro_key = normalize_macro_key(macro_key, current_path)
            
            if isinstance(macro_info, dict):
                # Leave name as-is
                
                # Process definition
                if 'definition' in macro_info and isinstance(macro_info['definition'], dict):
                    def_obj = macro_info['definition']
                    
                    # Handle both location info strings and regular paths in file_path
                    if 'file_path' in def_obj and def_obj['file_path']:
                        # Check if it's a location info string like "mini/main.c:6:9" or a regular path
                        fp = def_obj['file_path']
                        if ':' in fp and fp.count(':') >= 2:
                            # Location info string
                            def_obj['file_path'] = normalize_location_string(fp, current_path)
                        else:
                            # Regular path
                            def_obj['file_path'] = normalize_path(fp, current_path)
                
                # Process uses
                if 'uses' in macro_info and isinstance(macro_info['uses'], list):
                    for use_item in macro_info['uses']:
                        if isinstance(use_item, dict):
                            # file_path
                            if 'file_path' in use_item:
                                use_item['file_path'] = normalize_path(
                                    use_item['file_path'], current_path
                                )
                            
                            # macro_key
                            if 'macro_key' in use_item:
                                use_item['macro_key'] = normalize_macro_key(
                                    use_item['macro_key'], current_path
                                )
                            
                            # endif
                            if 'endif' in use_item and isinstance(use_item['endif'], dict):
                                if 'file_path' in use_item['endif']:
                                    use_item['endif']['file_path'] = normalize_path(
                                        use_item['endif']['file_path'], current_path
                                    )
            
            # Save with the new key
            normalized_taken_conds[normalized_macro_key] = macro_info
        
        write_json(taken_macros_path, normalized_taken_conds)
        print(f"  ✓ Normalized {len(normalized_taken_conds)} macro definitions")
    
    
    # 3. Process guards.json
    if guards_path and Path(guards_path).exists():
        print(f"\nProcessing: {guards_path}")
        guards_data = read_json(guards_path)
        
        if 'guards' in guards_data and isinstance(guards_data['guards'], list):
            for guard in guards_data['guards']:
                if isinstance(guard, dict) and 'file_path' in guard:
                    guard['file_path'] = normalize_path(guard['file_path'], current_path)
            
            write_json(guards_path, guards_data)
            print(f"  ✓ Normalized {len(guards_data['guards'])} include guards")
        else:
            print("  ! Unexpected guards.json format, skipping")
    
    print("\nNormalization complete!")

    print(f"all_conds: {all_macros_path}")
    print(f"taken_conds: {taken_macros_path}") 
    print(f"guards: {guards_path}")


def normalize_location_string(location_str, base_path):
    """
    Convert file paths within a location string to relative paths
    Example: f"{MACRO_HOME}/trans_c/mini/main.c:6:9"
          -> "mini/main.c:6:9"
    
    Args:
        location_str: Location string
        base_path: Base path for reference
    
    Returns:
        str: Normalized location string
    """
    if not location_str or ':' not in location_str:
        return location_str
    
    # The last two colons are line:column, so everything before them is file_path
    parts = location_str.rsplit(':', 2)
    
    if len(parts) == 3:
        file_path = parts[0]
        line = parts[1]
        column = parts[2]
        
        # Normalize file_path
        normalized_file_path = normalize_path(file_path, base_path)
        
        return f"{normalized_file_path}:{line}:{column}"
    
    return location_str


def normalize_macro_key(macro_key, base_path):
    """
    Convert file paths within a macro_key to relative paths
    Example: "DEBUG:{MACRO_HOME}/trans_c/mini/main.c:6:9"
          -> "DEBUG:mini/main.c:6:9"
    
    Args:
        macro_key: Macro key string
        base_path: Base path for reference
    
    Returns:
        str: Normalized macro key
    """
    if not macro_key or ':' not in macro_key:
        return macro_key
    
    # Decompose macro key: macro_name:file_path:line:column
    parts = macro_key.split(':', 1)  # Split at the first colon
    
    if len(parts) == 2:
        macro_name = parts[0]
        rest = parts[1]  # file_path:line:column
        
        # Normalize the location info from rest
        normalized_location = normalize_location_string(rest, base_path)
        
        return f"{macro_name}:{normalized_location}"
    
    return macro_key


def normalize_condition_item(item, base_path):
    """
    Normalize all paths within a condition item
    Corresponds to entries created by save_all_macros
    
    Args:
        item: Condition item (dictionary)
        base_path: Base path for reference
    """
    # file_path
    if 'file_path' in item:
        item['file_path'] = normalize_path(item['file_path'], base_path)
    
    # macro_key (e.g.: "DEBUG:/root/.../main.c:6:9")
    if 'macro_key' in item:
        item['macro_key'] = normalize_macro_key(item['macro_key'], base_path)
    
    # defined_at (e.g.: "/root/.../main.c:6:9")
    if 'defined_at' in item:
        item['defined_at'] = normalize_location_string(item['defined_at'], base_path)
    
    # endif object
    if 'endif' in item and isinstance(item['endif'], dict):
        if 'file_path' in item['endif']:
            item['endif']['file_path'] = normalize_path(item['endif']['file_path'], base_path)
    
    # else object (if present)
    if 'else' in item and isinstance(item['else'], dict):
        if 'file_path' in item['else']:
            item['else']['file_path'] = normalize_path(item['else']['file_path'], base_path)
    
    # macros array (for IF and ELIF cases)
    if 'macros' in item and isinstance(item['macros'], list):
        for macro_info in item['macros']:
            if isinstance(macro_info, dict):
                # defined_at
                if 'defined_at' in macro_info:
                    macro_info['defined_at'] = normalize_location_string(
                        macro_info['defined_at'], base_path
                    )
                # macro_key
                if 'macro_key' in macro_info:
                    macro_info['macro_key'] = normalize_macro_key(
                        macro_info['macro_key'], base_path
                    )
    
    # closes object (for ENDIF case)
    if 'closes' in item and isinstance(item['closes'], dict):
        if 'file_path' in item['closes']:
            item['closes']['file_path'] = normalize_path(item['closes']['file_path'], base_path)




def denormalize_metafiles(meta_dir, current_dir, all_macros_path, taken_macros_path, guards_path):
    """
    Convert relative paths in metadata to absolute paths
    
    Args:
        meta_dir: Metadata directory
        current_dir: Base directory (reference for absolute paths)
        all_macros_path: Path to all_conditions.json (corresponds to data["files"])
        taken_macros_path: Path to taken_conditions.json (corresponds to data["macros"])
        guards_path: Path to guards.json
    """
    print("denormalize metadata...")
    
    print(f"all_conds: {all_macros_path}")
    print(f"taken_conds: {taken_macros_path}") 
    print(f"guards: {guards_path}")
    
    current_path = Path(current_dir).resolve()
    
    # 1. Process all_conditions.json (data["files"])
    if all_macros_path and Path(all_macros_path).exists():
        print(f"\nProcessing: {all_macros_path}")
        all_conds = read_json(all_macros_path)
        
        # Create a new dictionary (also converting keys)
        denormalized_all_conds = {}
        
        for file_path, conditions_dict in all_conds.items():
            # Convert the key to an absolute path
            denormalized_key = denormalize_path(file_path, current_path)
            
            if isinstance(conditions_dict, dict):
                # Process each category: defined, ifdef, ifndef, if, elif, endif
                for cond_type, cond_list in conditions_dict.items():
                    if isinstance(cond_list, list):
                        for item in cond_list:
                            if isinstance(item, dict):
                                denormalize_condition_item(item, current_path)
            
            # Save with the new key
            denormalized_all_conds[denormalized_key] = conditions_dict
        
        write_json(all_macros_path, denormalized_all_conds)
        print(f"  ✓ Denormalized {len(denormalized_all_conds)} file groups")

    
    # 2. Process taken_conditions.json (data["macros"])
    if taken_macros_path and Path(taken_macros_path).exists():
        print(f"\nProcessing: {taken_macros_path}")
        taken_conds = read_json(taken_macros_path)
        
        # Create a new dictionary (also converting keys)
        denormalized_taken_conds = {}
        
        for macro_key, macro_info in taken_conds.items():
            # Convert macro_key to an absolute path
            denormalized_macro_key = denormalize_macro_key(macro_key, current_path)
            
            if isinstance(macro_info, dict):
                # Leave name as-is
                
                # Process definition
                if 'definition' in macro_info and isinstance(macro_info['definition'], dict):
                    def_obj = macro_info['definition']
                    
                    # Handle both location info strings and regular paths in file_path
                    if 'file_path' in def_obj and def_obj['file_path']:
                        fp = def_obj['file_path']
                        if ':' in fp and fp.count(':') >= 2:
                            # Location info string
                            def_obj['file_path'] = denormalize_location_string(fp, current_path)
                        else:
                            # Regular path
                            def_obj['file_path'] = denormalize_path(fp, current_path)
                
                # Process uses
                if 'uses' in macro_info and isinstance(macro_info['uses'], list):
                    for use_item in macro_info['uses']:
                        if isinstance(use_item, dict):
                            # file_path
                            if 'file_path' in use_item:
                                use_item['file_path'] = denormalize_path(
                                    use_item['file_path'], current_path
                                )
                            
                            # macro_key
                            if 'macro_key' in use_item:
                                use_item['macro_key'] = denormalize_macro_key(
                                    use_item['macro_key'], current_path
                                )
                            
                            # endif
                            if 'endif' in use_item and isinstance(use_item['endif'], dict):
                                if 'file_path' in use_item['endif']:
                                    use_item['endif']['file_path'] = denormalize_path(
                                        use_item['endif']['file_path'], current_path
                                    )
            
            # Save with the new key
            denormalized_taken_conds[denormalized_macro_key] = macro_info
        
        write_json(taken_macros_path, denormalized_taken_conds)
        print(f"  ✓ Denormalized {len(denormalized_taken_conds)} macro definitions")
    
    
    # 3. Process guards.json
    if guards_path and Path(guards_path).exists():
        print(f"\nProcessing: {guards_path}")
        guards_data = read_json(guards_path)
        
        if 'guards' in guards_data and isinstance(guards_data['guards'], list):
            for guard in guards_data['guards']:
                if isinstance(guard, dict) and 'file_path' in guard:
                    guard['file_path'] = denormalize_path(guard['file_path'], current_path)
            
            write_json(guards_path, guards_data)
            print(f"  ✓ Denormalized {len(guards_data['guards'])} include guards")
        else:
            print("  ! Unexpected guards.json format, skipping")
    
    print("\nDenormalization complete!")

    print(f"all_conds: {all_macros_path}")
    print(f"taken_conds: {taken_macros_path}") 
    print(f"guards: {guards_path}")


def denormalize_condition_item(item, base_path):
    """
    Convert all paths within a condition item to absolute paths
    
    Args:
        item: Condition item (dictionary)
        base_path: Base path for reference
    """
    # file_path
    if 'file_path' in item:
        item['file_path'] = denormalize_path(item['file_path'], base_path)
    
    # macro_key
    if 'macro_key' in item:
        item['macro_key'] = denormalize_macro_key(item['macro_key'], base_path)
    
    # defined_at
    if 'defined_at' in item:
        item['defined_at'] = denormalize_location_string(item['defined_at'], base_path)
    
    # endif object
    if 'endif' in item and isinstance(item['endif'], dict):
        if 'file_path' in item['endif']:
            item['endif']['file_path'] = denormalize_path(item['endif']['file_path'], base_path)
    
    # else object
    if 'else' in item and isinstance(item['else'], dict):
        if 'file_path' in item['else']:
            item['else']['file_path'] = denormalize_path(item['else']['file_path'], base_path)
    
    # macros array
    if 'macros' in item and isinstance(item['macros'], list):
        for macro_info in item['macros']:
            if isinstance(macro_info, dict):
                # defined_at
                if 'defined_at' in macro_info:
                    macro_info['defined_at'] = denormalize_location_string(
                        macro_info['defined_at'], base_path
                    )
                # macro_key
                if 'macro_key' in macro_info:
                    macro_info['macro_key'] = denormalize_macro_key(
                        macro_info['macro_key'], base_path
                    )
    
    # closes object
    if 'closes' in item and isinstance(item['closes'], dict):
        if 'file_path' in item['closes']:
            item['closes']['file_path'] = denormalize_path(item['closes']['file_path'], base_path)


def denormalize_location_string(location_str, base_path):
    """
    Convert file paths within a location string to absolute paths
    Example: "mini/main.c:6:9"
          -> f"{MACRO_HOME}/trans_c/mini/main.c:6:9"
    
    Args:
        location_str: Location string
        base_path: Base path for reference
    
    Returns:
        str: Location string with absolute paths
    """
    if not location_str or ':' not in location_str:
        return location_str
    
    # Special cases such as "undefined"
    if location_str == "undefined" or location_str.startswith('/'):
        return location_str
    
    # The last two colons are line:column
    parts = location_str.rsplit(':', 2)
    
    if len(parts) == 3:
        file_path = parts[0]
        line = parts[1]
        column = parts[2]
        
        # Convert file_path to an absolute path
        absolute_file_path = denormalize_path(file_path, base_path)
        
        return f"{absolute_file_path}:{line}:{column}"
    
    return location_str


def denormalize_macro_key(macro_key, base_path):
    """
    Convert file paths within a macro_key to absolute paths
    Example: "DEBUG:mini/main.c:6:9"
          -> "DEBUG:{MACRO_HOME}/trans_c/mini/main.c:6:9"
    
    Args:
        macro_key: Macro key string
        base_path: Base path for reference
    
    Returns:
        str: Macro key with absolute paths
    """
    if not macro_key or ':' not in macro_key:
        return macro_key
    
    # Decompose macro key: macro_name:file_path:line:column
    parts = macro_key.split(':', 1)  # Split at the first colon
    
    if len(parts) == 2:
        macro_name = parts[0]
        rest = parts[1]  # file_path:line:column
        
        # Convert location info from rest to absolute paths
        absolute_location = denormalize_location_string(rest, base_path)
        
        return f"{macro_name}:{absolute_location}"
    
    return macro_key




def denormalize_dep_data(dep_json_path, original_dir, target_dir):
    """
    Replace the original_dir portion with target_dir for all paths in the dep_data JSON
    
    Args:
        dep_json_path: Path to the dependency JSON file
        original_dir: Source directory path to replace
        target_dir: Destination directory path to replace with
    """
    print("Denormalize dep_data ...")
    
    # Convert to absolute paths
    original_dir_abs = os.path.abspath(original_dir)
    target_dir_abs = os.path.abspath(target_dir)
    
    # Unify trailing slashes
    if not original_dir_abs.endswith('/'):
        original_dir_abs += '/'
    if not target_dir_abs.endswith('/'):
        target_dir_abs += '/'
    
    with open(dep_json_path, 'r') as f:
        data = json.load(f)
    
    def replace_path(path):
        """Replace original_dir with target_dir in the path"""
        if path.startswith(original_dir_abs):
            return path.replace(original_dir_abs, target_dir_abs, 1)
        # Also handle the case without trailing slash
        original_no_slash = original_dir_abs.rstrip('/')
        target_no_slash = target_dir_abs.rstrip('/')
        if path.startswith(original_no_slash):
            return path.replace(original_no_slash, target_no_slash, 1)
        return path
    
    # Process all entries
    for item in data:
        # Replace source
        if 'source' in item:
            item['source'] = replace_path(item['source'])
        
        # Replace include list
        if 'include' in item:
            item['include'] = [replace_path(p) for p in item['include']]
        
        # Replace included_by list
        if 'included_by' in item:
            item['included_by'] = [replace_path(p) for p in item['included_by']]
    
    # Write the results back
    with open(dep_json_path, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"Replaced paths: {original_dir_abs} -> {target_dir_abs}")
    print(f"Updated: {dep_json_path}")



def normalize_dep_data(dep_json_path, base_dir):
    """
    Convert all absolute paths in the dep_data JSON to relative paths by removing the base_dir portion
    
    Args:
        dep_json_path: Path to the dependency JSON file
        base_dir: Base directory path (this portion will be removed)
    """
    print("Normalize dep_data ...")
    
    # Convert to absolute path
    base_dir_abs = os.path.abspath(base_dir)
    
    # Unify trailing slash
    if not base_dir_abs.endswith('/'):
        base_dir_abs += '/'
    
    with open(dep_json_path, 'r') as f:
        data = json.load(f)
    
    def normalize_path(path):
        """Remove base_dir from the path and convert to a relative path"""
        if path.startswith(base_dir_abs):
            return path[len(base_dir_abs):]
        # Also handle the case without trailing slash
        base_no_slash = base_dir_abs.rstrip('/')
        if path == base_no_slash:
            return '.'
        if path.startswith(base_no_slash + '/'):
            return path[len(base_no_slash) + 1:]
        return path
    
    # Process all entries
    for item in data:
        # Replace source
        if 'source' in item:
            item['source'] = normalize_path(item['source'])
        
        # Replace include list
        if 'include' in item:
            item['include'] = [normalize_path(p) for p in item['include']]
        
        # Replace included_by list
        if 'included_by' in item:
            item['included_by'] = [normalize_path(p) for p in item['included_by']]
    
    # Write the results back
    with open(dep_json_path, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"Normalized paths relative to: {base_dir_abs}")
    print(f"Updated: {dep_json_path}")

    
def denormalize_target_path(target_path, original_dir, target_dir):
    with open(target_path, 'r') as f:
        content = f.read()

    # Convert to absolute paths
    content = content.replace(original_dir, target_dir)

    with open(target_path, 'w') as f:
        f.write(content)


def denormalize_block_group_path(block_group_path, original_dir, target_dir):
    """Replace file_path in the block_group JSON file"""
    with open(block_group_path, 'r') as f:
        data = json.load(f)

    for group in data:
        if 'components' in group:
            for component in group['components']:
                if 'file_path' in component:
                    component['file_path'] = component['file_path'].replace(
                        original_dir, target_dir
                    )

    with open(block_group_path, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def denormalize_block_path(block_path, original_dir, target_dir):
    """Replace paths in a block file (NAME:PATH:START:END format)"""
    with open(block_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        new_lines.append(line.replace(original_dir, target_dir))

    with open(block_path, 'w') as f:
        f.writelines(new_lines)
        


def get_parent_path(c_path, map_path):
    return get_path_map(map_path, c_path, "parent")


def update_parent_path(c_path, dep_json_path):
    dep_json = read_json(dep_json_path)
    found_parent_path = None
    for dep in dep_json:
        c_parent_path = dep['source']

        if 'div_parts' in dep:
            for dep_item in dep['div_parts']:
                div_path = dep_item['source']
                if div_path == c_path:
                    found_parent_path = c_parent_path
                    break

    # if found_parent_path is None:
    #     print(f"found_parent_path was not found for {c_path}.")
    # else:
    #     print(f"found_parent_path was found for {c_path}.")
    return found_parent_path



def get_child_path(c_path, map_path):
    return get_path_map(map_path, c_path, "child")


def get_ref_files(c_path, dep_json_path):
    include_files = []
    dep_json = read_json(dep_json_path)

    found = False
    for dep_item in dep_json:
        source_path = dep_item['source']
        if c_path == source_path:
            include_files = dep_item['indirect_include']
            found = True
        else:
            if 'div_parts' in dep_item:
                div_parts = dep_item['div_parts']
                for part in div_parts:
                    if c_path == part['source']:
                        found = True
                        include_files = part['include']
        if found:
            break

    # include_files.append(c_lib_path)
    # include_files.append(c_build_path)
    # include_files.append(c_cargo_path)

    return include_files


def append_rust_path(target_path, content):
    directory = os.path.dirname(target_path) # Get the directory path from the file path
    if directory and not os.path.exists(directory): # Create the directory if it does not exist
        os.makedirs(directory)
    with open(target_path, 'a') as file: # Write the content to the file
        file.write('\n') # Ensure a newline
        #file.write('\n') # Ensure a newline
        file.write(content)


def get_llm_flag(llm_on):
    if llm_on == "on":
        llm_on = True
    else:
        llm_on = False
    
    return llm_on



# Identify c_key elements that should have been at the modified locations
def update_modified_keys(c_key_set, meta_dir, rust_c_map, modified_lines):
    print("update_modified_keys...")
    
    # Process each file in modified_lines
    for rust_file_path, mods in modified_lines.items():
        # mods is a list (to handle cases with multiple modifications)
        if not isinstance(mods, list):
            mods = [mods]  # Convert to a list if it is not one
        
        # Process each modification
        for mod in mods:
            start_line = mod['start_line']
            end_line = mod['end_line']
            
            print(f"Checking {rust_file_path}: lines {start_line}-{end_line}")
            
            # Check each entry in rust_c_map
            for rust_key, c_key in rust_c_map.items():
                parts = rust_key.split(':')
                if len(parts) >= 4:
                    rust_name = parts[0]
                    rust_path = parts[1]
                    rust_start = int(parts[2])
                    rust_end = int(parts[3])
                    
                    if rust_path == rust_file_path:
                        if rust_start <= end_line and rust_end >= start_line:
                            print(f"  Found overlap: {rust_name} ({rust_start}-{rust_end}) -> adding {c_key}")
                            c_key_set.add(c_key)
    
    print(f"Updated c_key_set: {len(c_key_set)} keys")
    return c_key_set


def get_name_key(item):
    if 'name' in item:
        name_key = f"{item['name']}:{item['file_path']}:{item['start_line']}:{item['end_line']}"
    
    if 'macro_name' in item and 'start_line' in item:
        name_key = f"{item['macro_name']}:{item['file_path']}:{item['start_line']}:{item['end_line']}"
    
    if 'macro_name' in item and 'line' in item:
        name_key = f"{item['macro_name']}:{item['file_path']}:{item['line']}"
    
    return name_key

