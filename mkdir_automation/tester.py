import os
import subprocess

from mkdir_automation.automation import MkdirAutomatizer


TEST_PATH = "test"


class MkdirTester:
    def __init__(self, directories, *args, **kwargs):
        self.automatizer = MkdirAutomatizer(directories, *args, **kwargs)

    def __test_setup(self):
        test_setup_automatizer = MkdirAutomatizer([TEST_PATH])
        test_setup_automatizer.run_command()
        os.chdir(TEST_PATH)
        self.automatizer.run_command()

    @staticmethod
    def __test_cleanup():
        if os.path.exists(TEST_PATH):
            os.chdir(".")
            cmd = f"rm -rf {TEST_PATH}"
            os.system(cmd)

    def run_test(self):
        self.__test_cleanup()
        self.__test_setup()

    def test_directories(self):
        directory_list = self.automatizer.get_final_structure()
        for path in directory_list.split():
            if not os.path.exists(path):
                return False
        return True

    def test_directories_details(self):
        directory_list = self.automatizer.get_final_structure().split()
        for item in directory_list:
            item = item.split("/")
            dir_name = item[-1]
            if len(item) == 0:
                command = f"ls -la | grep '\s{dir_name}$'"
            else:
                command = f"ls -la {'/'.join(item[:-1])} | grep '\s{dir_name}$'"
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
            stdout = result.stdout.split("\n")
            if len(stdout) == 0:
                return False
            stdout = stdout[0].split()
            if not stdout[0].startswith("d"):
                return False
            if self.automatizer.mode:
                mode = stdout[0]
                if mode[-9:] != self.automatizer.mode[-9:]:
                    return False

