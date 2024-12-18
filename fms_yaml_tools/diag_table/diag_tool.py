#!/usr/bin/env python
# ***********************************************************************
# *                   GNU Lesser General Public License
# *
# * This file is part of the GFDL Flexible Modeling System (FMS) YAML
# * tools.
# *
# * FMS_yaml_tools is free software: you can redistribute it and/or
# * modify it under the terms of the GNU Lesser General Public License
# * as published by the Free Software Foundation, either version 3 of the
# * License, or (at your option) any later version.
# *
# * FMS_yaml_tools is distributed in the hope that it will be useful, but
# * WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# * General Public License for more details.
# *
# * You should have received a copy of the GNU Lesser General Public
# * License along with FMS.  If not, see <http://www.gnu.org/licenses/>.
# ***********************************************************************

import click
from fms_yaml_tools.diag_table import DiagTable, DiagTableFile, DiagTableVar, DiagTableError, abstract_dict


def echo(msg):
    """Print a message to STDERR"""
    click.echo(msg, err=True)


def get_editor():
    """Get the user's preferred editor as per the VISUAL or EDITOR env variable. Redirect the editor's STDOUT to STDERR,
    so that diag-tool's own STDOUT can be redirected or piped by the user"""
    from click._termui_impl import Editor
    return "1>&2 " + Editor().get_editor()


def apply_filters(obj):
    """Apply file and var filters, then prune empty files if desired"""
    if type(obj) is DiagTable:
        obj = obj.filter_files(options["file"])

    if type(obj) in (DiagTable, DiagTableFile):
        obj = obj.filter_vars(options["var"])

    if type(obj) is DiagTable and options["prune"]:
        obj = obj.prune()

    return obj


def get_filtered_table_obj(diag_table):
    """Load a diag_table object from a filename, then apply file and var filters to it"""
    return apply_filters(DiagTable.from_file(diag_table))


def write_out(filename, obj):
    """Write the object to standard output or to the filename provided, depending on the `in_place` option"""
    if options["in_place"]:
        if filename == "-":
            echo("Warning: Ignoring --in-place option, because the original table was read from standard input")
        else:
            if not (options["force"] or click.confirm("Overwrite {:s}?".format(click.format_filename(filename)))):
                echo("Changes have been discarded")
                return
    else:
        filename = "-"

    obj.write(filename, options["abstract"])


def get_filtered_files(table_obj):
    """Get an iterator over the table's files after file filters are applied"""
    return table_obj.get_filtered_files(options["file"])


def get_filtered_vars(table_obj):
    """Get an iterator over the table's variables after file and variable filters are applied"""
    return table_obj.filter_files(options["file"]).get_filtered_vars(options["var"])


def merge_generic(yamls, combine_func):
    """Perform either a symmetric or asymmetric merge according to `combine_func`"""
    if len(yamls) == 0:
        echo("At least one YAML argument is required")
        return
    elif len(yamls) == 1:
        yamls = ["-", yamls[0]]
    else:
        yamls = list(yamls)

    if len(options["var"]) > 0:
        cls = DiagTableVar
        lhs_iter = get_filtered_vars
    elif len(options["file"]) > 0:
        cls = DiagTableFile
        lhs_iter = get_filtered_files
    else:
        cls = DiagTable
        lhs_iter = lambda table_obj: (yield table_obj)

    try:
        diag_table = yamls.pop()
        diag_table_obj = DiagTable.from_file(diag_table)

        while len(yamls) > 0:
            rhs = cls.from_file(yamls.pop())
            for lhs in lhs_iter(diag_table_obj):
                combine_func(lhs, rhs)

        write_out(diag_table, diag_table_obj)
    except DiagTableError as err:
        echo(err)


def yaml_str_from_file(yaml):
    """Read a YAML string from a file"""
    with click.open_file(yaml, "r") as fh:
        return fh.read()


def get_obj_generic(yaml):
    """Get a DiagTable, DiagTableFile, or DiagTableVar object from a YAML file"""
    yaml_str = yaml_str_from_file(yaml)
    for cls in (DiagTable, DiagTableFile, DiagTableVar):
        try:
            return cls.from_yaml_str(yaml_str)
        except DiagTableError:
            pass


@click.group()
@click.version_option("alpha1", "-V", "--version")
@click.help_option("-h", "--help")
@click.option("-i", "--in-place", is_flag=True, default=False,
              help="Overwrite the existing table, rather than writing to standard output")
@click.option("-F", "--force", is_flag=True, default=False,
              help="Skip the confirmation prompt when overwriting an existing table")
@click.option("-f", "--file", type=click.STRING, multiple=True,
              help="Apply a file filter, of the form `[~]FILE`, where FILE may be an individual file name or a"
              + " comma-separated list thereof")
@click.option("-v", "--var", type=click.STRING, multiple=True,
              help="Apply a variable filter, of the form `[~][FILE:[MODULE:]]VAR`, where FILE, MODULE, and VAR may be"
              + " individual names or comma-separated lists thereof")
@click.option("-p", "--prune", is_flag=True, default=False,
              help="Prune files which have no variables after filters are applied")
@click.option("-a", "--abstract", type=click.Choice(("table", "file", "var"), case_sensitive=True), multiple=True,
              help="Exclude table, file, or variable attributes from the output")
def diag_tool(in_place, force, file, var, prune, abstract):
    """Utility to update, merge, subset, or summarize diag YAMLs"""
    global options
    options = {
            "in_place": in_place,
            "force": force,
            "file": file,
            "var": var,
            "prune": prune,
            "abstract": abstract_dict(abstract)
            }


@diag_tool.command(name="edit")
@click.argument("yaml", type=click.Path(), default="-")
def edit_cmd(yaml):
    """Edit a table interactively, then merge the changes back in"""
    try:
        obj = get_obj_generic(yaml)

        if obj is None:
            echo("{:s} was not a valid table, file, or variable... exiting".format(yaml))
            return

        yaml_str_0 = apply_filters(obj).dump_yaml(options["abstract"])
        yaml_str_1 = click.edit(yaml_str_0, editor=get_editor(), extension=".yaml")

        if yaml_str_1:
            cls = obj.__class__
            obj |= cls.from_yaml_str(yaml_str_1)
        else:
            if options["in_place"]:
                echo("No changes were made... exiting without modifying '{}'".format(yaml))
                return
            else:
                echo("No changes were made... passing original table through")

        options["abstract"] = {}
        write_out(yaml, obj)
    except DiagTableError as err:
        echo(err)


@diag_tool.command(name="update")
@click.argument("yamls", type=click.Path(), nargs=-1)
def update_cmd(yamls):
    """Update a table or its files/variables"""
    def combine_func(lhs, rhs):
        lhs |= rhs
    merge_generic(yamls, combine_func)


@diag_tool.command(name="merge")
@click.argument("yamls", type=click.Path(), nargs=-1)
def merge_cmd(yamls):
    """Symmetrically merge tables, failing if any conflicts occur"""
    def combine_func(lhs, rhs):
        lhs += rhs
    merge_generic(yamls, combine_func)


@diag_tool.command(name="filter")
@click.argument("diag_table", type=click.Path(), default="-")
def filter_cmd(diag_table):
    """Apply file or variable filters to a table"""
    try:
        diag_table_obj = get_filtered_table_obj(diag_table)
        write_out(diag_table, diag_table_obj)
    except DiagTableError as err:
        echo(err)


@diag_tool.command(name="list")
@click.argument("diag_table", type=click.Path(), default="-")
def list_cmd(diag_table):
    """List the files and variables in a table"""
    options["abstract"] = abstract_dict(("table", "file", "var")) | options["abstract"]

    try:
        diag_table_obj = get_filtered_table_obj(diag_table)
        write_out(diag_table, diag_table_obj)
    except DiagTableError as err:
        echo(err)


@diag_tool.command(name="pick")
@click.argument("diag_table", type=click.Path(), default="-")
def pick_cmd(diag_table):
    """Pick a single file or variable from a table"""
    if len(options["var"]) > 0:
        noun = "variable"
        pick_func = get_filtered_vars
    elif len(options["file"]) > 0:
        noun = "file"
        pick_func = get_filtered_files
    else:
        echo("`diag-tool pick` requires a file or variable filter to be provided")
        return

    try:
        diag_table_obj = DiagTable.from_file(diag_table)
        picked_objs = tuple(pick_func(diag_table_obj))
        n = len(picked_objs)

        if n == 0:
            echo("No {:s} was found matching the filter criteria".format(noun))
            return
        elif n > 1:
            echo("Selecting the first out of {:d} {:s}s which satisfy the filter criteria".format(n, noun))

        write_out(diag_table, picked_objs[0])
    except DiagTableError as err:
        echo(err)


if __name__ == "__main__":
    diag_tool()
