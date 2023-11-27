from dataclasses import dataclass
from enum import Enum
import subprocess


class PermissionModeType(Enum):
    NUMBER = 0
    STRING = 1


class DirectoryListParameterType(Enum):
    STR = 0
    LIST_OF_STR = 1
    NONE = 2

class ValidationResult(Enum):
    PASSED = 1
    FAILED = 2


@dataclass
class ValidationMessage:
    state: ValidationResult
    parameter: str
    message: str = None


class MkdirAutomatizer:
    def __init__(self, directory_list, *args, mode=None, context_ctx=None):
        self.directory_list = directory_list
        self.valueless_arguments = args
        self.mode = mode
        self.context_ctx = context_ctx
        self.validation_passed = self.validate_parameters()
        self.result = None
        self.command = None

    def run_command(self):
        if self.validation_passed:
            self.__run_command()

    def validate_parameters(self):
        validation_results = [
            self._process_valueless_arguments(), self._validate_directory_list(),
            self._validate_mode() if self.mode is not None else None,
            self._validate_context_ctx()
        ]
        validation_passed = True
        for item in validation_results:
            if item is None:
                continue
            item: ValidationMessage
            if item.state == ValidationResult.PASSED:
                print(f"Parameter {item.parameter} validation PASSED")
            else:
                print(f"Parameter {item.parameter} validation FAILED, error message: \n{item.message}")
                validation_passed = False
        return validation_passed

    def _validate_directory_list(self):
        if self.version or self.help:
            if len(self.directory_list) == 0:
                self.directory_list = ""
                self.directory_list_parameter_type = DirectoryListParameterType.NONE
                return ValidationMessage(ValidationResult.PASSED, "directory_list")
            else:
                self.directory_list_parameter_type = DirectoryListParameterType.LIST_OF_STR
                return ValidationMessage(ValidationResult.FAILED, "directory_list",
                                         f"No directories should be provided when {'help' * self.help}"\
                                         f"{'version' * self.version} parametr is provided.")
        if len(self.directory_list) == 0:
            self.directory_list_parameter_type = DirectoryListParameterType.NONE
            return ValidationMessage(ValidationResult.FAILED, "directory_list", "directory_list contains no values")
        if isinstance(self.directory_list, str):
            if not self.parents and "/" in self.directory_list:
                self.directory_list_parameter_type = None
                return ValidationMessage(ValidationResult.FAILED, "directory_list",
                                         "Directory names cannot contain slash when parameter parent is not used")
            else:
                self.directory_list_parameter_type = DirectoryListParameterType.STR
        elif isinstance(self.directory_list, list):
            def list_of_strings_only(item):
                if isinstance(item, str):
                    return True
                if isinstance(item, list):
                    string_only = True
                    for inner_item in item:
                        string_only = string_only and list_of_strings_only(inner_item)
                    return string_only
                return False

            def check_slashes(item):
                if isinstance(item, str):
                    return "/" in item
                if isinstance(item, list):
                    slash_found = False
                    for inner_item in item:
                        slash_found = slash_found or check_slashes(inner_item)
                    return slash_found
                return False

            list_of_strings_only_passed = list_of_strings_only(self.directory_list)
            if list_of_strings_only_passed:
                self.directory_list_parameter_type = DirectoryListParameterType.LIST_OF_STR
                if not self.parents:
                    slash = check_slashes(self.directory_list)
                    if slash:
                        return ValidationMessage(ValidationResult.FAILED, "directory_list",
                                                 "Directory names cannot contain slash when parameter parent is not "
                                                 "used")
                    final_directory_structure = self.get_final_structure()
                    if len(final_directory_structure.split()) != len(set(final_directory_structure.split())):
                        return ValidationMessage(ValidationResult.FAILED, "directory_list",
                                                 "Directory names must be unique when parameter parent is not used")
                    return ValidationMessage(ValidationResult.PASSED, "directory_list")
            else:
                return ValidationMessage(ValidationResult.FAILED, "directory_list",
                                         "directory_list must be a list or a string")
        else:
            return ValidationMessage(ValidationResult.FAILED, "directory_list",
                                     "directory_list must be a list or a string")
        return ValidationMessage(ValidationResult.PASSED, "directory_list")

    @staticmethod
    def chmod_numeric_to_letter(numeric_str):
        mapping = {
            '0': '---',
            '1': '--x',
            '2': '-w-',
            '3': '-wx',
            '4': 'r--',
            '5': 'r-x',
            '6': 'rw-',
            '7': 'rwx'
        }
        return f"-{''.join(mapping[digit] for digit in numeric_str)}"

    def _validate_mode(self):
        if isinstance(self.mode, int):
            self.mode = self.chmod_numeric_to_letter(str(self.mode))
        if isinstance(self.mode, str):
            if self.mode.isdigit():
                if len(self.mode) > 4:
                    return ValidationMessage(ValidationResult.FAILED, "mod",
                                             "Numeric mode cannot contain more than 4 digits")
                if "8" in self.mode or "9" in self.mode:
                    return ValidationMessage(ValidationResult.FAILED, "mod",
                                             "Numeric mode cannot contain 8 or 9")
                return ValidationMessage(ValidationResult.PASSED, "mod")
            else:
                self.mode = self.mode.lower()
                characters = set(self.mode)
                allowed_characters = set()
                allowed_characters.add("w")
                allowed_characters.add("r")
                allowed_characters.add("x")
                allowed_characters.add("-")
                if not characters.issubset(allowed_characters):
                    return ValidationMessage(ValidationResult.FAILED, "mod",
                                             "Mode contains invalid characters!")
                if len(self.mode) not in (9, 10):
                    return ValidationMessage(ValidationResult.FAILED, "mod",
                                             "Mode needs to have 9 or 10 characters or four digits")
                if len(self.mode) == 9:
                    self.mode = f"-{self.mode}"
                first = set(self.mode[1::3])
                allowed_characters = set()
                allowed_characters.add("r")
                allowed_characters.add("-")
                if not first.issubset(allowed_characters):
                    return ValidationMessage(ValidationResult.FAILED, "mod", "r or - must be on position 1, 4 and 7")
                second = set(self.mode[2::3])
                allowed_characters = set()
                allowed_characters.add("w")
                allowed_characters.add("-")
                if not second.issubset(allowed_characters):
                    return ValidationMessage(ValidationResult.FAILED, "mod", "w or - must be on position 2, 5 and 8")
                third = set(self.mode[3::3])
                allowed_characters = set()
                allowed_characters.add("x")
                allowed_characters.add("-")
                if not third.issubset(allowed_characters):
                    return ValidationMessage(ValidationResult.FAILED, "mod", "x or - must be on position 3, 6 and 9")
                return ValidationMessage(ValidationResult.PASSED, "mod")
        return ValidationMessage(ValidationResult.FAILED, "mod",
                                 "Mode needs to be str or int")

    def _validate_context_ctx(self):
        if self.context_ctx is None:
            return ValidationMessage(ValidationResult.PASSED, "context_ctx")
        if not isinstance(self.context_ctx, str):
            return ValidationMessage(ValidationResult.FAILED, "context_ctx", "context_ctx must be str")
        result = subprocess.run("sestatus", stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        if result.stderr:
            return ValidationMessage(ValidationResult.FAILED, "context_ctx", "context_ctx is defined but SELinux"
                                                                             " is not active")
        return ValidationMessage(ValidationResult.PASSED, "context_ctx")

    def _process_valueless_arguments(self):
        if isinstance(self.valueless_arguments, tuple):
            if len(self.valueless_arguments) == 0:
                self.parents = False
                self.verbose = False
                self.help = False
                self.version = False
                self.z = False
                self.context = False
            for item in self.valueless_arguments:
                if not isinstance(item, str):
                    return ValidationMessage(ValidationResult.FAILED, "valueless_arguments",
                                             "Valueless arguments must be string or list of strings")
                valueless_arguments = [x.replace("-", "") for x in self.valueless_arguments]
                valueless_arguments = set(valueless_arguments)
                allowed_valueless_arguments = set()
                allowed_valueless_arguments.add("p")
                allowed_valueless_arguments.add("v")
                allowed_valueless_arguments.add("z")
                allowed_valueless_arguments.add("parents")
                allowed_valueless_arguments.add("verbose")
                allowed_valueless_arguments.add("help")
                allowed_valueless_arguments.add("version")
                allowed_valueless_arguments.add("context")
                if not valueless_arguments.issubset(allowed_valueless_arguments):
                    self.parents = False
                    self.verbose = False
                    self.help = False
                    self.version = False
                    self.z = False
                    self.context = False
                    return ValidationMessage(ValidationResult.FAILED, "valueless_arguments",
                                             "Invalided valueless argument provided")
                self.parents = "p" in valueless_arguments or "parents" in valueless_arguments
                self.verbose = "v" in valueless_arguments or "verbose" in valueless_arguments
                self.help = "help" in valueless_arguments
                self.z = "z" in valueless_arguments
                self.version = "version" in valueless_arguments
                self.context = "context" in valueless_arguments
                return ValidationMessage(ValidationResult.PASSED, "valueless_arguments")
        else:
            return ValidationMessage(ValidationResult.FAILED, "valueless_arguments",
                                     "Valueless arguments must be string or list of strings")

    def get_final_structure(self):
        final_directory_structure = []
        def create_directories(path, directory_list):
            for item in directory_list:
                if isinstance(item, str):
                    new_path = f"{path}/{item}" if path else item
                    final_directory_structure.append(new_path)
                    next_index = directory_list.index(item) + 1
                    if next_index < len(directory_list) and isinstance(directory_list[next_index], list):
                        create_directories(new_path, directory_list[next_index])
        if self.directory_list_parameter_type == DirectoryListParameterType.LIST_OF_STR:
            directory_structure = self.directory_list
            create_directories("", directory_structure)
            final_directory_structure = " ".join(final_directory_structure)
        elif self.directory_list_parameter_type == DirectoryListParameterType.STR:
            final_directory_structure = self.directory_list
        else:
            final_directory_structure = ""
        return final_directory_structure

    def __run_command(self):
        final_directory_structure = self.get_final_structure()
        self.command = f"mkdir {final_directory_structure} {'-v' * self.verbose} {'--version' * self.version}" \
                       f"{'-p' * self.parents} {'-Z' * self.z} {'--context'}"
        self.result = subprocess.run(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

    @property
    def standard_output(self):
        if self.result is not None and isinstance(self.result, subprocess.CompletedProcess):
            return self.result.stdout

    @property
    def returncode(self):
        if self.result is not None and isinstance(self.result, subprocess.CompletedProcess):
            return self.result.returncode
