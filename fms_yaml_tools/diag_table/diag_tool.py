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
import sys
from fms_yaml_tools.diag_table import DiagTable, DiagTableFile, DiagTableVar, DiagTableError, abstract_dict


def echo(msg):
    click.echo(msg, err=True)


def get_filtered_table_obj(ctx, diag_table):
    options = ctx.obj
    diag_table_obj = DiagTable.from_file(diag_table).filter_files(options["file"]).filter_vars(options["var"])

    if options["prune"]:
        diag_table_obj = diag_table_obj.prune()

    return diag_table_obj


def write_out(ctx, filename, diag_table_obj):
    options = ctx.obj

    if options["in_place"]:
        if filename == "-":
            echo("Warning: Ignoring --in-place option, because the original table was read from standard input")
        else:
            if not (options["force"] or click.confirm("Overwrite {:s}?".format(click.format_filename(filename)))):
                echo("Changes have been discarded")
                return
    else:
        filename = "-"

    diag_table_obj.write(filename, options["abstract"])


@click.group(help="Utility for updating, combining, subsetting, and summarizing diag tables")
@click.pass_context
@click.option("-i", "--in-place", is_flag=True, default=False,
              help="Overwrite the existing table, rather than writing to standard output")
@click.option("-F", "--force", is_flag=True, default=False,
              help="Skip confirmation prompt when overwriting an existing table")
@click.option("-f", "--file", type=click.STRING, multiple=True,
              help="Comma-separated list of file filters; see README for more details")
@click.option("-v", "--var", type=click.STRING, multiple=True,
              help="Comma-separated list of variable filters; see README for more details")
@click.option("-p", "--prune", is_flag=True, default=False,
              help="Prune files which have no variables after filters are applied")
@click.option("-a", "--abstract", type=click.Choice(("table", "file", "var"), case_sensitive=True), multiple=True,
              help="Exclude table, file, or variable attributes from the output")
def diag_tool(ctx, in_place, force, file, var, prune, abstract):
    ctx.ensure_object(dict)
    options = ctx.obj

    options["in_place"] = in_place
    options["force"] = force
    options["file"] = file
    options["var"] = var
    options["prune"] = prune
    options["abstract"] = abstract_dict(abstract)


@diag_tool.command(help="Edit a table interactively")
@click.pass_context
@click.argument("diag_table", type=click.Path(), default="-")
def edit(ctx, diag_table):
    options = ctx.obj

    try:
        yaml0 = get_filtered_table_obj(ctx, diag_table).dump_yaml(options["abstract"])
        yaml1 = click.edit(yaml0)

        if yaml1 is None:
            echo("Changes have been discarded... passing original table through")
            yaml1 = yaml0

        options["abstract"] = {}
        diag_table_obj = DiagTable.from_yaml_str(yaml1)
        write_out(ctx, diag_table, diag_table_obj)
    except DiagTableError as err:
        echo(err)


def merge_generic(ctx, files, merge_func):
    if len(files) == 0:
        echo("At least one diag_table argument is required")
        return

    if len(files) == 1:
        files = ("-", files[0])

    try:
        diag_tables = [get_filtered_table_obj(ctx, f) for f in files]

        while len(diag_tables) > 1:
            merge_func(diag_tables[1], diag_tables.pop(0))

        write_out(ctx, files[-1], diag_tables[0])
    except DiagTableError as err:
        echo(err)


@diag_tool.command(help="Asymmetrically merge one table into another")
@click.argument("tables", type=click.Path(), nargs=-1)
@click.pass_context
def update(ctx, tables):
    def update_func(lhs, rhs):
        lhs |= rhs

    merge_generic(ctx, tables, update_func)


@diag_tool.command(help="Symmetrically merge two or more tables")
@click.argument("tables", type=click.Path(), nargs=-1)
@click.pass_context
def merge(ctx, tables):
    def merge_func(lhs, rhs):
        lhs += rhs

    merge_generic(ctx, tables, merge_func)


@diag_tool.command(help="Update all variables that match a given variable filter")
@click.argument("var-yaml", type=click.Path(), default="-", nargs=1)
@click.argument("table-yaml", type=click.Path(), nargs=1)
@click.pass_context
def update_var(ctx, var_yaml, table_yaml):
    options = ctx.obj

    try:
        var_obj = DiagTableVar.from_file(var_yaml)
        table_obj = DiagTable.from_file(table_yaml)

        for v in table_obj.get_filtered_vars(options["var"]):
            v |= var_obj

        write_out(ctx, table_yaml, table_obj)
    except DiagTableError as err:
        echo(err)


@diag_tool.command(help="Update all files that match a given file filter")
@click.argument("file-yaml", type=click.Path(), default="-", nargs=1)
@click.argument("table-yaml", type=click.Path(), nargs=1)
@click.pass_context
def update_file(ctx, file_yaml, table_yaml):
    options = ctx.obj

    try:
        file_obj = DiagTableFile.from_file(file_yaml)
        table_obj = DiagTable.from_file(table_yaml)

        for f in table_obj.get_filtered_files(options["file"]):
            f |= file_obj

        write_out(ctx, table_yaml, table_obj)
    except DiagTableError as err:
        echo(err)


@diag_tool.command(help="Filter files or variables from a table")
@click.pass_context
@click.argument("diag_table", type=click.Path(), default="-")
def filter(ctx, diag_table):
    try:
        diag_table_obj = get_filtered_table_obj(ctx, diag_table)
        write_out(ctx, diag_table, diag_table_obj)
    except DiagTableError as err:
        echo(err)


@diag_tool.command(help="List the files and variables in a table")
@click.pass_context
@click.argument("diag_table", type=click.Path(), default="-")
def list(ctx, diag_table):
    options = ctx.obj
    options["abstract"] = abstract_dict(("table", "file", "var")) | options["abstract"]

    try:
        diag_table_obj = get_filtered_table_obj(ctx, diag_table)
        write_out(ctx, diag_table, diag_table_obj)
    except DiagTableError as err:
        echo(err)


@diag_tool.command(help="Pick out a particular file")
@click.argument("diag_table", type=click.Path(), default="-")
@click.pass_context
def grep_file(ctx, diag_table):
    options = ctx.obj

    if options["in_place"]:
        echo("Warning: --in-place option is unsupported by the grep-file subcommand")

    try:
        diag_table_obj = get_filtered_table_obj(ctx, diag_table)
        n = len(diag_table_obj.diag_files)

        if n == 0:
            echo("No file was found matching the filter criteria")
            return
        elif n > 1:
            echo("Selecting the first out of {:d} files that match the filter criteria".format(n))

        file = diag_table_obj.diag_files[0]
        yaml = file.dump_yaml(options["abstract"])
        sys.stdout.write(yaml)
    except DiagTableError as err:
        echo(err)


@diag_tool.command(help="Pick out a particular variable")
@click.argument("diag_table", type=click.Path(), default="-")
@click.pass_context
def grep_var(ctx, diag_table):
    options = ctx.obj

    if options["in_place"]:
        echo("Warning: --in-place option is unsupported by the grep-var subcommand")

    try:
        diag_table_obj = get_filtered_table_obj(ctx, diag_table)
        vars = diag_table_obj.get_filtered_vars(None)
        n = len(vars)

        if n == 0:
            echo("No variable was found matching the filter criteria")
            return
        elif n > 1:
            echo("Selecting the first out of {:d} variables that match the filter criteria".format(n))

        yaml = vars[0].dump_yaml(options["abstract"])
        sys.stdout.write(yaml)
    except DiagTableError as err:
        echo(err)


def wizard_generic(ctx, diag_table, abstract_default):
    options = ctx.obj
    abstract = abstract_dict(abstract_default) | options["abstract"]

    try:
        yaml0 = get_filtered_table_obj(ctx, diag_table).dump_yaml(abstract)
        yaml1 = click.edit(yaml0)

        if yaml1 is None:
            echo("Changes have been discarded")
            return

        diag_table_obj = DiagTable.from_file(diag_table)
        diag_table_obj |= DiagTable.from_yaml_str(yaml1)

        options["abstract"] = {}
        write_out(ctx, diag_table, diag_table_obj)
    except DiagTableError as err:
        echo(err)


@diag_tool.command(help="Add a new file or modify an existing one")
@click.pass_context
@click.argument("diag_table", type=click.Path(), default="-")
def file_wizard(ctx, diag_table):
    abstract_default = ("table",)
    wizard_generic(ctx, diag_table, abstract_default)


@diag_tool.command(help="Add a new variable or modify an existing one")
@click.pass_context
@click.argument("diag_table", type=click.Path(), default="-")
def var_wizard(ctx, diag_table):
    options = ctx.obj
    options["prune"] = True
    abstract_default = ("table", "file")
    wizard_generic(ctx, diag_table, abstract_default)


if __name__ == "__main__":
    diag_tool(obj={})
