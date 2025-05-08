# diag-tool

Utility for updating, combining, filtering, or summarizing a YAML-format diag table

## Synopsis

```
diag-tool [options] subcommand [table1.yaml [table2.yaml …]]
```

`diag-tool` consists of various subcommands:
* `edit`: Edit a table interactively, then merge the changes back in
* `filter`: Apply file or variable filters to a table
* `list`: List the files and variables in a table
* `pick`: Pick a single file or variable from a table
* `merge`: Symmetrically merge tables, failing if any conflicts occur
* `update`: Update a table, replacing the table's original data if any conflicts occur

The `edit`, `filter`, `list`, and `pick` subcommands expect one YAML as input, and will
read from standard input if none is provided. `merge` and `update` expect at least two
YAMLs as input; if only one is provided, they will attempt to read the lefthand YAML from
standard input.

All subcommands write to standard output by default. If the `-i` (`--in-place`) option is
used, the YAML file is overwritten instead. In the case of `update` or `merge`,
`--in-place` causes the most righthand YAML to be overwritten.  diag-tool will ask for
confirmation before overwriting the old YAML; this can be bypassed using the `-F`
(`--force`) option.

Options:
* `-i` (`--in-place`): Overwrite existing table, rather than write to standard output
* `-F` (`--force`): Bypass the confirmation prompt when overwriting an existing table
* `-f FILE_FILTER` (`--file=FILE_FILTER`): Apply a file filter. `FILE_FILTER` must be of
  the form `[~]FILE`, where `FILE` may be an individual file name, a comma-separated list
  thereof, or `*`. In the case of a comma-separated list, the filter will match any of the
  filenames listed. The `~` prefix, if provided, inverts the filter so that matches are
  excluded rather than included.
* `-v VAR_FILTER` (`--var=VAR_FILTER`): Apply a variable filter. `VAR_FILTER` must be of
  the form `[~][FILE:[MODULE:]]VAR`, where `FILE`, `MODULE`, and `VAR` may be individual
  file/module/variable names, comma-separated lists thereof, or `*`. If comma-separated
  lists are provided, the filter will match the union of the Cartesian product of the lists.
  The `~` prefix, if provided, inverts the filter so that matches are excluded rather than
  included.
* `-p` (`--prune`): Prune files which have no variables remaining after filters are
  applied.
* `-a [~]table|file|var` (`--abstract=[~]table|file|var`): Exclude table-level,
  file-level, or variable-level attributes from the output. Multiple `--abstract` options
  may be provided. A `~` prefix disables the respective abstract option (i.e., causes
  attributes at the respective level to be included in the output).  Specifically, the
  following values have the following effects:
  - `table`: Hide `title` and `base_date`
  - `file`: Hide all file attributes except `file_name` and `varlist`
  - `var`: Hide all variable attributes except `var_name`
* `-h` (`--help`): Print help message and exit
* `-V` (`--version`): Print version number and exit

## Quickstart

To modify an existing variable, or to add a new variable by using an existing variable as
a template:

```
$ diag-tool -i --var=existing_file:existing_var -p -a table -a file edit diag_table.yaml
```

The above command applies a filter to pick out a variable called `existing_var` (in
`existing_file`) from `diag_table.yaml`, hides table and file attributes, drops you into
your editor of choice (customizable via the `VISUAL` or `EDITOR` env variables) to make
modifications, checks your input for validity, and merges the updates back into the
original `diag_table.yaml`. If you do not modify `file_name` or `var_name` while editing,
then the original variable will be updated; otherwise, a new variable (and a new file, if
needed) will be added.

The command shown above can be broken down into the following pipeline:

```
$ diag-tool --var=existing_file:existing_var -p -a table -a file filter diag_table.yaml | diag-tool edit | diag-tool -i update diag_table.yaml
```

* `diag-tool filter` picks out the variable `existing_var` and prints it to standard
  output.
* `diag-tool edit` drops the user into an editor in which `existing_var` can be modified.
* `diag-tool update` merges the changes back into the original table.

In the above example, notice that the `filter` and `edit` subcommands were invoked without
the `-i` (`--in-place`) option, causing them to print their results to standard output.
The `--in-place` option provided to the `update` subcommand instructs diag-tool to
overwrite the original YAML file, rather than write the merged table to standard output.

An alternative workflow could involve using `diag-tool filter` to create a template file:
```
$ diag-tool --var=existing_file:existing_var -p -a table -a file filter diag_table.yaml >~/templates/example_var.yaml
```

This template could then be used as the input for a subsequent pair of edit-update
commands, which could perhaps be run via a shell alias:
```
$ alias ADDVAR="diag-tool edit ~/templates/example_var.yaml | diag-tool -i update"
$ ADDVAR my_table.yaml
```

To combine three tables for which no conflicts are expected:
```
$ diag-tool merge table1.yaml table2.yaml table3.yaml >combined.yaml
```


To see a summary of the files and variables contained in a table:
```
$ diag-tool list table.yaml
```


To see a summary of the variables in `example_file`:
```
$ diag-tool --file=example_file list table.yaml
```


To see a list of the files with all variables excluded:
```
$ diag-tool --var=~* list table.yaml
```


To remove `unwanted_var` (in `the_file`) from `table.yaml`:
```
$ diag-tool -i --var=~the_file:unwanted_var filter table.yaml
```

Notice the `~` prefix in the variable filter string; this causes the filter to include all
variables except the match (namely, `unwanted_var` in `the_file`) in the output.

## Additional information

### filter versus list

`filter` and `list` are fundamentally the same operation. The only difference between them
is their default values for the `--abstract` option. In particular, the following two
commands are identical:
```
$ diag-tool list table.yaml
```
```
$ diag-tool -a table -a file -a var filter table.yaml
```

### file and variable YAMLs

`filter` outputs a filtered diag table, whereas `pick` outputs a YAML representation of a
variable (when a variable filter is provided) or a file (when no variable filter is
provided). The resulting YAMLs are treated differently by the `update` and `merge`
subcommands.

Specifically, a file or variable YAML can only be merged into a table (via an `update` or
`merge` command) in combination with a filter which specifies which variables (files) the
variable (file) YAML is to be merged into. As an example, the command below may be used to
rename `old_module` to `new_module` across all variables in `diag_table.yaml`:

```
echo "module: new_module" | diag-tool -i --var=*:old_module:* update diag_table.yaml
```

Providing a variable filter to an `update` or `merge` command will cause all YAMLs except
the right-most to be interpreted as variable YAMLs. Providing a file filter without a
variable filter will cause all YAMLs except the right-most to be interpreted as file
YAMLs.

### Filter string examples

| File filter               | Explanation                                              |
| ------------------------- | -------------------------------------------------------- |
| --file=*                  | Include all files                                        |
| --file=~*                 | Exclude all files                                        |
| --file=my_file            | Only include the file named "my_file"                    |
| --file=~my_file           | Exclude the file named "my_file"                         |
| --file=file1,file2,file3  | Include files named "file1", "file2", or "file3"         |
| --file=~file1,file2,file3 | Exclude files named "file1", "file2", or "file3"         |

| Variable filter      | Explanation                                                   |
| -------------------- | ------------------------------------------------------------- |
| --var=*              | Include all variables                                         |
| --var=~*             | Exclude all variables                                         |
| --var=my_var         | Only include variables named "my_var" (in any file or module) |
| --var=my_file:my_var | Only include the variable "my_var" in the file "my_file"      |
| --var=*:my_mod:*     | Only include variables in the module "my_mod"                 |
| --var=~*:my_mod:*    | Exclude all variables in the module "my_mod"                  |
| --var=~my_var        | Exclude any variable named "my_var"                           |
