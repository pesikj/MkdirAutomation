from mkdir_automation.tester import MkdirTester

def run_scenario(tester: MkdirTester, valid: bool):
    assert tester.automatizer.validation_passed == valid
    if valid:
        tester.run_test()
        assert tester.test_directories() == True
        tester.test_directories_details()

scenarios = {
    1: [MkdirTester("test_x"), True],
    2: [MkdirTester("test_x/test_y"), False],
    3: [MkdirTester(["test_x", ["test_x1", ["test_x11", "test_x12"], "test_x2"], "test_y", ["test_y1"]]), True],
    4: [MkdirTester(["test_x", ["test_x1", ["test_x11", "test_x12"], "test_x2"], "test_y", ["test_y1"]], mode=777), True],
    5: [MkdirTester("test_x/test_y", "p"), True],
    6: [MkdirTester(["test_x", ["test_y/test_z"]], "p", "v"), True],
    7: [MkdirTester(["test_x", ["test_y/test_z"]], "--help"), False],
    8: [MkdirTester(["test_x", ["test_y/test_z"]], mode="wr-"), False],
    9: [MkdirTester(["test_x", ["test_y"]], mode="-wr-abcwr-"), False],
    10: [MkdirTester(["test_x", ["test_y"]], mode="-rw-r--r--"), True],
}


for scenario_number, scenario in scenarios.items():
    print(f"Running scenario {scenario_number}.")
    run_scenario(*scenario)
    print(f"Scenario {scenario_number} finish.")
