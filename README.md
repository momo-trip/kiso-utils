# kiso-utils

Common utility package used across the C-to-Rust translation pipeline and test generation workflows.

## Package Structure

```
kiso-utils/
├── utils_api/
│   ├── __init__.py
│   ├── translate_utils.py # Translation-specific utilities
│   └── utils.py           # General-purpose utilities (file I/O, coverage, etc.)
└── README.md
```

---

## utils.py

Foundation functions used throughout the pipeline: file operations, directory management, code coverage measurement, and script execution.

### Dependencies

- Python standard library: `os`, `sys`, `json`, `shutil`, `subprocess`, `tempfile`, `pathlib`, `stat`, `re`, `time`, `signal`, `pty`, `select`, `termios`, `threading`, `datetime`, `collections`, `dataclasses`
- External: `clang.cindex` (libclang), `ijson`, `anthropic`, `openai`, `tiktoken`, `chardet`, `replicate`, `matplotlib`, `graphviz`, `watchdog`, `numpy`

### Key Features

#### File I/O

| Function | Description |
|----------|-------------|
| `read_json(file_path)` | Read a JSON file and return dict/list. Returns `None` on missing file or parse error. |
| `write_json(json_file_path, json_data)` | Write dict/list to a JSON file (UTF-8, indent=4). Auto-creates parent directories. |
| `append_json(file_path, new_data)` | Append data to an existing JSON array file. |
| `read_json_streaming(json_path)` | Stream-read a large JSON array using `ijson` (generator). |
| `read_file(filename)` | Read a text file. Falls back through multiple encodings on UTF-8 failure. |
| `write_file(target_path, content)` | Write text to a file with surrogate character error handling. |
| `append_file(file_path, code_to_append)` | Append text to the end of a file. |
| `read_specific_lines(filename, start_line, end_line)` | Extract text from a specified line range. Multi-encoding support. |
| `count_file_lines(file_path)` | Return the total number of lines in a file. |
| `get_line_from_file(file_path, line_number)` | Get the content of a specific line. |

#### File & Directory Management

| Function | Description |
|----------|-------------|
| `create_file(file_path)` | Create a file if it doesn't exist (auto-creates parent directories). |
| `recreate_file(file_path)` | Delete and recreate a file. |
| `delete_file(file_path)` | Delete a file (silently ignores if not found). |
| `copy_file(src, dst)` | Copy a file using `shutil.copy2`. |
| `create_permissioned_file(file_path)` | Create a file with execute permissions (755). |
| `create_directory(path)` | Recursively create a directory. |
| `delete_directory(dir_path)` | Recursively delete a directory. |
| `recreate_directory(dir_path)` | Delete then create a directory. |
| `copy_directory(src, dst)` | Recursive copy with permission preservation. Handles symlinks. |
| `rename_directory(old, new, overwrite=True)` | Rename a directory with optional overwrite. |
| `create_backup_directory(dir_name)` | Create a timestamped backup (max retained: 1). |
| `clone_directory(src, renamed)` | Create a backup and rename it. |
| `tmp_backup_directory(raw_dir)` | Create a temporary backup. |
| `restore_directory(raw_tmp, raw_dir)` | Restore from a backup. |
| `grant_permissions(target_dir)` | Grant write permission to read-only files. |
| `check_permission(raw_dir)` | Detect and fix read-only files. |

#### Script Execution

| Function | Description |
|----------|-------------|
| `run_script(script_path, timeout, dir_move_flag, execute_log_path, option, progress_queue, iteration_count, max_iterations, log_dir, mode)` | Execute a shell script with timeout, logging, and progress queue support. `option` accepts `"compile"` / `"run"` / `"both"`. |
| `run_script_wo_log(script_path, timeout, dir_move_flag, execute_log_path, option)` | Script execution without progress tracking. Includes automatic detection of argument-waiting state. |
| `run_script_pty(script_path, timeout)` | Execute with PTY for real-time output capture. |

**Return value (`run_script`):** `(error_output, std_output, iteration_count)`

#### Code Coverage Measurement

Coverage measurement based on `lcov` / `gcov`.

| Function | Description |
|----------|-------------|
| `get_coverage(cov_target, target_dir, database_dir, branch_path, line_path, function_path)` | Collect line, branch, and function coverage in one call. Returns: `(branch_cov, branch_max, line_cov, line_max, func_cov, func_max)` |
| `get_line_coverage(coverage_info_path, directory, line_path, order_path)` | Parse and output line coverage to JSON. |
| `get_branch_coverage(coverage_info_path, target_dir, branch_path)` | Parse and output branch coverage to JSON. |
| `get_function_coverage(coverage_info_path, target_dir, function_path, order_path)` | Parse and output function coverage to JSON. |
| `get_is_covered(target_entry, cov_path, target_dir, cov_type)` | Check whether a specific target (function/branch/line) is covered. |
| `get_is_increased(target_entry, database_dir, previous_coverage, current_coverage, cov_type)` | Determine if coverage increased from the previous run. Records results to `cov_increased.json`. |
| `run_cov_script(...)` | Main function that runs tests, measures coverage, and records results in one pass. |
| `run_branch_cov_script(...)` | Branch-coverage-specific variant. |

#### Path Operations & Normalization

| Function | Description |
|----------|-------------|
| `normalize_path(path_str, base_path)` | Convert an absolute path to a relative path based on `base_path`. |
| `denormalize_path(path_str, base_path)` | Convert a relative path to an absolute path. |
| `normalize_metadata(meta_dir, current_dir)` | Batch-convert paths in metadata JSON files to relative paths. |
| `denormalize_metadata(meta_dir, current_dir)` | Batch-convert paths in metadata JSON files to absolute paths. |
| `get_abs_path(path)` | Normalize to an absolute path. |
| `get_last_directory(path)` | Get the trailing directory name from a path. |
| `absolute_to_relative(absolute_path, base_path)` | Convert absolute to relative path. |
| `change_top_directory(original_path, new_top_directory)` | Replace the top-level directory in a path. |

#### Line Numbering

| Function | Description |
|----------|-------------|
| `add_line_numbers(input_file)` | Prepend `Line N [indent]: ...` format line numbers to a file (in-place). |
| `add_line_numbers_custom(input_file, fixed_number)` | Version with configurable starting line number. |
| `add_line_numbers_custom_new(input_file, fixed_number)` | Append `\|Line N` at the end of each line. |

#### Miscellaneous

| Function | Description |
|----------|-------------|
| `deduplicate_compile_commands(json_path)` | Remove duplicate entries from `compile_commands.json`. |
| `find_compile_commands_json(target_dir)` | Recursively search for `compile_commands.json` in a directory. |
| `merge_json(json1, json2)` | Recursively merge two dicts. |
| `merge_dicts(main_dict, new_dict)` | In-place dict merge (extends list values). |
| `get_all_files(directory)` | Recursively get all file paths in a directory. |
| `get_random(length)` | Generate a random alphanumeric string of specified length. |
| `get_timestamp()` | Get a timestamp in `YYYY-MM-DD-HH-MM-SS` format. |
| `save_to_output_dir(output, output_dir)` | Copy each path in a dict to an output directory. |

### Data Classes

```python
@dataclass
class LineCoverage:
    line_number: int
    is_covered: bool
    execution_count: int

class CoverageData:
    """Manages per-file line coverage data."""
    def __init__(self, file_path: str)
    def add_line(self, line_number: int, execution_count: int)
    def to_dict(self) -> dict
    @classmethod
    def from_dict(cls, data: dict) -> 'CoverageData'
```

---

## translate_utils.py

Translation-specific utilities for the C-to-Rust pipeline. Provides centralized path management, metadata normalization/denormalization, and code analysis helpers.

### Dependencies

- Functions from `utils.py` (imported via `.utils`)
- `clang.cindex` (libclang bindings)
- Various Python standard library modules

### Key Features

#### PathConfig — Centralized Path Management

A class that centrally manages all paths used in the translation pipeline.

```python
paths = create_path_config(
    user_id="0000",
    original_dir="/path/to/source",
    process_type="trans",    # "trans" | "s_repair" | "reformat"
    work_dir="my_workspace"
)
```

**Key attributes:**

| Category | Example Attributes | Description |
|----------|-------------------|-------------|
| Directories | `target_dir`, `work_dir`, `raw_dir` | Source and workspace paths |
| Rust output | `rust_output_dir`, `lib_path`, `cargo_path` | Rust project-related paths |
| Metadata | `meta_dir`, `div_meta_dir`, `database_dir` | Analysis data storage |
| Build | `build_path`, `run_test_path`, `run_all_path` | Build and test shell scripts |
| Macro analysis | `all_macros_path`, `taken_macros_path`, `guards_path` | Conditional compilation related |
| Logging | `log_dir`, `logging_path`, `chat_dir` | Logs and chat history |
| Dependencies | `dep_json_path`, `div_json_path`, `list_path` | File dependency information |

**Helper functions:**

| Function | Description |
|----------|-------------|
| `create_path_config(user_id, original_dir, process_type, work_dir)` | Create a `PathConfig` instance. |
| `extract_all_paths(paths)` | Return all paths as a tuple for individual variable unpacking. |

#### Log Management

| Function | Description |
|----------|-------------|
| `set_log(log_dir, llm_choice, target, logging_path, step, DEBUG_LLM)` | Redirect `sys.stdout` / `sys.stderr` to a log file. Generates filenames based on LLM type (gpt/claude/gemini/llama) and pipeline step (pre/div/conv/f_rep). |

#### Metadata Operations

| Function | Description |
|----------|-------------|
| `obtain_metadata(c_path, meta_dir, rust_flag, path_flag, signal)` | Generate or read a metadata file path from a source file path. |
| `reverse_meta_path(meta_path, meta_dir)` | Reverse-derive the original source file path from a metadata path. |

#### Path Normalization (Translation-Specific)

Functions for converting file paths inside metadata JSON between absolute and relative forms. Recursively processes `file_path`, `definition`, `usage_location`, `uses`, and `components` fields.

| Function | Target | Direction |
|----------|--------|-----------|
| `normalize_translation_metadata(meta_dir, target_dir)` | Dict-format metadata | Absolute → Relative |
| `denormalize_translation_metadata(meta_dir, target_dir, record_flag)` | Dict-format metadata | Relative → Absolute |
| `normalize_translation_div_metadata(meta_dir, current_dir)` | List-format metadata | Absolute → Relative |
| `denormalize_translation_div_metadata(meta_dir, current_dir)` | List-format metadata | Relative → Absolute |
| `normalize_metafiles(meta_dir, current_dir, all_macros_path, taken_macros_path, guards_path)` | Macro-related metafiles | Absolute → Relative |
| `denormalize_metafiles(...)` | Macro-related metafiles | Relative → Absolute |
| `normalize_dep_data(dep_json_path, base_dir)` | Dependency JSON | Absolute → Relative |
| `denormalize_dep_data(dep_json_path, original_dir, target_dir)` | Dependency JSON | Path replacement |

#### Path Mapping (C ↔ Rust)

| Function | Description |
|----------|-------------|
| `update_path_map(mapping_file, child_path, rust_child_path, parent_path, rust_parent_path)` | Register a C/Rust file mapping. Supports bidirectional lookup. |
| `get_path_map(mapping_file, file_path, option)` | Look up `"parent"` / `"rust"` / `"c"` / `"child"` from the mapping. |
| `obtain_c_path(rust_path, c_directory, rust_output_dir)` | Derive the corresponding C file path from a Rust file path. |

#### Code Segment Operations

| Function | Description |
|----------|-------------|
| `get_current_code(json_path)` | Read current code from source files and update the `current_code` field in metadata JSON entries. Includes automatic `#[attr]` macro attribute detection. |
| `find_other_intervals(rust_path, meta_dir)` | Detect code regions in a Rust file not covered by metadata and add them as "others" entries. |
| `get_unit_code(one_unit)` | Concatenate code from multiple segments. |
| `get_unit_code_with_location(one_unit, database_dir)` | Concatenate code with file path and line number annotations. |
| `get_lined_code(test_path, workspace_dir)` | Get entire file content with line numbers. |
| `get_specific_lined_code(database_dir, test_path, start_line, end_line)` | Get a specific line range with line numbers. |

#### Dependencies & References

| Function | Description |
|----------|-------------|
| `get_ref_files(c_path, dep_json_path)` | Get the list of include files from the dependency JSON. |
| `get_parent_path(c_path, map_path)` | Get the parent file path. |
| `get_child_path(c_path, map_path)` | Get the list of child file paths. |
| `update_parent_path(c_path, dep_json_path)` | Reverse-lookup the parent path from divided parts. |
| `get_list_path(dep_json_path, target_dir, list_path)` | Output all files in the dependency graph to a list file. |

#### Build & Configuration

| Function | Description |
|----------|-------------|
| `get_setting_data(data, target_dir)` | Extract build paths, test paths, and target functions from a settings JSON. |
| `add_tracing(rust_io_dir, toml_path)` | Add `tracing` / `tracing-subscriber` dependencies to `Cargo.toml`. |
| `get_llm_flag(llm_on)` | Convert `"on"` / `"off"` string to bool. |

#### Miscellaneous

| Function | Description |
|----------|-------------|
| `execute_command(command)` | Execute a shell command and return `(None, stderr)`. |
| `remove_git_directory(rust_directory)` | Remove the `.git` directory. |
| `find_highest_source(directory)` | Find the topmost directory containing `.c` / `.h` files. |
| `calculate_execution_time(chat_dir, output_path, trial_id, target)` | Calculate execution time from chat file timestamps. |
| `find_matching_path(workspace_dir, target_suffix)` | Search for a file matching a suffix within the workspace. |
| `update_modified_keys(c_key_set, meta_dir, rust_c_map, modified_lines)` | Identify C keys corresponding to modified lines. |
| `get_name_key(item)` | Generate a `name:file_path:start:end` format key from a metadata entry. |

---

## Requirements

- Python 3.8+
- libclang (LLVM 19 recommended)
- `lcov` / `gcov` (required for coverage measurement)
- External Python packages: `anthropic`, `openai`, `tiktoken`, `chardet`, `ijson`, `clang`, `pydantic`, `replicate`, `matplotlib`, `graphviz`, `watchdog`, `numpy`
