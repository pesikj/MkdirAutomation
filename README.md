# mkdir automation

This tools automatize running the Linux command `mkdir` and it can be used to automatize creation of directories.

## Usage

To use the mkdir automation, it needs to be imported

```py
from mkdir_automation.tester import MkdirAutomatizer
```

Create an instance of the `MkdirAutomatizer` class. It supports the following parameters.

### directory_list

`directory_list` contains a directory or directories that should be created. Supported datatypes are 
`str` and `list`. 

The following example creates a directory `test_x`.

```py
m = MkdirAutomatizer("test_x")
m.run_command()
```

The following example is invalid unless `p` (or `parent`) parameter is provided or unless the directory `test_x`
already exists.

```py
MkdirAutomatizer("test_x/test_y")
m.run_command()
```

If a nested list is given, the directories in the nested list are created as subdirectories
of the directory preceding the nested list.

The following command generates a tree of directories given in the list.

```py
MkdirAutomatizer(["test_x", ["test_x1", ["test_x11", "test_x12"], "test_x2"], "test_y", ["test_y1"]]
m.run_command()
```
            
### Valueless arguments

These arguments are provided only as names, without values. The `p` argument creates parent directories
if they do not exist. Also, an error is not triggered when directory already exists.

These commands create hierarchy structure.

```py
MkdirAutomatizer("test_x/test_y", "p")
m.run_command()
MkdirAutomatizer(["test_x", ["test_y/test_z"]], "p")
m.run_command()
```

The argument `v` generated the verbose output. The output can be read from the `standard_output` property.

The argument `--help` stores the text of help. The argument `version` stores value of the version output.

```py
MkdirAutomatizer("test_x/test_y", "p")
m.run_command()
print(m.standard_output)
```

The argument `z` sets SELinux security context of each created directory to the default type.

### Test scenarios

#### Scenario 1

Creates a `test_x` folder

```py
MkdirTester("test_x")
```

#### Scenario 2

Is not validated.

```py
MkdirTester("test_x/test_y")
```

#### Scenario 3

Creates a tree of directories.

```py
MkdirTester(["test_x", ["test_x1", ["test_x11", "test_x12"], "test_x2"], "test_y", ["test_y1"]]
```

#### Scenario 4

Creates a tree of directories with 777 permissions.

```py
MkdirTester(["test_x", ["test_x1", ["test_x11", "test_x12"], "test_x2"], "test_y", ["test_y1"]], mode=777)
```

#### Scenario 5

Creates directory with a subdirectory.

```py
MkdirTester("test_x/test_y", "p")
```

#### Scenario 6

Creates directory with a subdirectory and stores the verbose output.

```py
MkdirTester(["test_x", ["test_y/test_z"]], "p", "v")
```

#### Scenario 7

Not validated - the `--help` argument should be give with empty folder list.

```py
MkdirTester(["test_x", ["test_y/test_z"]], "--help")
```

#### Scenario 8

Not validated - the `mode` has incorrect length.

```py
MkdirTester(["test_x", ["test_y"]], mode="wr-")
```

#### Scenario 9

Not validated - the `mode` has invalid characters.

```py
MkdirTester(["test_x", ["test_y"]], mode="-wr-abcwr-")
```

#### Scenario 10

Valid - directories are created with the given permissions.

```py
MkdirTester(["test_x", ["test_y"]], mode="-rw-r--r--")
```