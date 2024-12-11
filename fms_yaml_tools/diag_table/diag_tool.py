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
from fms_yaml_tools.diag_table import DiagTable


def echo(msg):
    click.echo(msg, err=True)


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
    options["abstract"] = abstract


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

    yaml = diag_table_obj.dump_yaml(options["abstract"])

    with click.open_file(filename, "w") as fh:
        fh.write(yaml)


def get_filtered_table_obj(ctx, diag_table):
    options = ctx.obj
    diag_table_obj = DiagTable.from_file(diag_table).filter_files(options["file"]).filter_vars(options["var"])

    if options["prune"]:
        diag_table_obj = diag_table_obj.filter_files(lambda file_obj: len(file_obj.varlist) > 0)

    return diag_table_obj


@diag_tool.command(help="Edit a table interactively")
@click.pass_context
@click.argument("diag_table", type=click.Path(), default="-")
def edit(ctx, diag_table):
    options = ctx.obj

    yaml0 = get_filtered_table_obj(ctx, diag_table).dump_yaml(options["abstract"])
    yaml1 = click.edit(yaml0)

    if yaml1 is None:
        echo("Changes have been discarded... passing original table through")
        yaml1 = yaml0

    diag_table_obj = DiagTable.from_yaml_str(yaml1)
    write_out(ctx, diag_table, diag_table_obj)


def merge_generic(ctx, files, merge_func):
    if len(files) == 0:
        echo("At least one diag_table argument is required")
        return

    if len(files) == 1:
        files = ("-", files[0])

    diag_tables = [get_filtered_table_obj(ctx, f) for f in files]

    while len(diag_tables) > 1:
        merge_func(diag_tables[1], diag_tables.pop(0))

    write_out(ctx, files[-1], diag_tables[0])


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


@diag_tool.command(help="Filter files or variables from a table")
@click.pass_context
@click.argument("diag_table", type=click.Path(), default="-")
def filter(ctx, diag_table):
    diag_table_obj = get_filtered_table_obj(ctx, diag_table)
    write_out(ctx, diag_table, diag_table_obj)


@diag_tool.command(help="List the files and variables in a table")
@click.pass_context
@click.argument("diag_table", type=click.Path(), default="-")
def list(ctx, diag_table):
    options = ctx.obj

    if len(options["abstract"]) == 0:
        options["abstract"] = ("table", "file", "var")

    diag_table_obj = get_filtered_table_obj(ctx, diag_table)
    write_out(ctx, diag_table, diag_table_obj)


@diag_tool.command(help="Pick out a particular file")
@click.argument("diag_table", type=click.Path(), default="-")
@click.pass_context
def grep_file(ctx, diag_table):
    options = ctx.obj

    if len(options["abstract"]) == 0:
        options["abstract"] = ("table",)

    diag_table_obj = get_filtered_table_obj(ctx, diag_table)
    write_out(ctx, diag_table, diag_table_obj)


@diag_tool.command(help="Pick out a particular variable")
@click.argument("diag_table", type=click.Path(), default="-")
@click.pass_context
def grep_var(ctx, diag_table):
    options = ctx.obj

    if len(options["abstract"]) == 0:
        options["abstract"] = ("table", "file")

    options["prune"] = True

    diag_table_obj = get_filtered_table_obj(ctx, diag_table)
    write_out(ctx, diag_table, diag_table_obj)


def wizard_generic(ctx, diag_table, abstract):
    options = ctx.obj

    if len(options["abstract"]) > 0:
        # User has overridden the default abstract setting
        abstract = options["abstract"]

    yaml0 = get_filtered_table_obj(ctx, diag_table).dump_yaml(abstract)
    yaml1 = click.edit(yaml0)

    if yaml1 is None:
        echo("Changes have been discarded")
        return

    with click.open_file(diag_table, "r") as fh:
        diag_table_original = DiagTable.from_yaml_str(fh.read())

    diag_table_changes = DiagTable.from_yaml_str(yaml1)

    diag_table_obj = diag_table_original | diag_table_changes
    write_out(ctx, diag_table, diag_table_obj)


@diag_tool.command(help="Add a new file or modify an existing one")
@click.pass_context
@click.argument("diag_table", type=click.Path(), default="-")
def file_wizard(ctx, diag_table):
    wizard_generic(ctx, diag_table, ("table",))


@diag_tool.command(help="Add a new variable or modify an existing one")
@click.pass_context
@click.argument("diag_table", type=click.Path(), default="-")
def var_wizard(ctx, diag_table):
    options = ctx.obj
    options["prune"] = True
    wizard_generic(ctx, diag_table, ("table","file"))


if __name__ == "__main__":
    diag_tool(obj={})
