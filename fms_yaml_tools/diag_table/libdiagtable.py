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

import yaml
import re
import copy
from click import open_file


def diag_assert(condition, msg):
    """Raise a DiagTableError if condition is not true"""
    if not condition:
        raise DiagTableError(msg)


def dict_assert_mergeable(a, b):
    """Assert that two dictionaries can be symmetrically merged. This assertion fails
       if both dictionaries contain a common key with two different values."""
    common_keys = a.keys() & b.keys()
    for k in common_keys:
        diag_assert(a[k] == b[k],
                    "Failed to merge tables: Field '{:}' has two different values: '{:}' and '{:}'".
                    format(k, a[k], b[k]))


def parse_negate_flag(s):
    """Check if the first character of a filter string is '~', which indicates that the filter shall be negated."""
    if s[0] == "~":
        return (s[1:], True)
    else:
        return (s, False)


def file_filter_factory(filter_spec):
    """Return a function to be used as a file filter, from a specification string or a list thereof"""
    if callable(filter_spec):
        return filter_spec

    # Pass-through if no filter spec is provided
    if not filter_spec:
        return lambda file_obj: True

    if type(filter_spec) is str:
        filter_spec = (filter_spec,)

    def iterate_cases():
        for filter_str in filter_spec:
            filter_str, negate = parse_negate_flag(filter_str)
            for part in filter_str.split(","):
                yield (part or "*", negate)

    def file_filter(file_obj):
        match = False
        for name, negate in iterate_cases():
            if (file_obj.file_name == name or name == "*"):
                match = True
                break
        return match ^ negate

    return file_filter


def var_filter_factory(filter_spec):
    """Return a function to be used as a variable filter, from a specification string or a list thereof"""
    if callable(filter_spec):
        return filter_spec

    # Pass-through if no filter spec is provided
    if not filter_spec:
        return lambda file_obj, var_obj: True

    if type(filter_spec) is str:
        filter_spec = (filter_spec,)

    def iterate_cases():
        for filter_str in filter_spec:
            filter_str, negate = parse_negate_flag(filter_str)
            fmv = [component for component in filter_str.split(":")]

            def get_filter_component(index):
                try:
                    return fmv.pop(index)
                except IndexError:
                    return "*"

            var_name = get_filter_component(-1)
            file_name = get_filter_component(0)
            mod_name = get_filter_component(0)

            diag_assert(len(fmv) == 0, "Invalid variable filter was provided. Correct format is: " +
                                       "[file1[,file2[,...]]:[module1[,module2[,...]]:]]var1[,var2[,...]]")

            for f in file_name.split(","):
                for m in mod_name.split(","):
                    for v in var_name.split(","):
                        yield (f, m, v, negate)

    def var_filter(file_obj, var_obj):
        match = False
        for file, module, var, negate in iterate_cases():
            if (
                    (file_obj.file_name == file or file == "*") and
                    ((var_obj.module or file_obj.module) == module or module == "*") and
                    (var_obj.var_name == var or var == "*")):
                match = True
                break
        return match ^ negate

    return var_filter


class DiagTableError(Exception):
    pass


def abstract_dict(options):
    valid_flags = ("table", "file", "var")

    def parse_options(flags):
        for flag in flags:
            flag, disable = parse_negate_flag(flag)
            if flag in valid_flags:
                enable = not disable
                yield (flag, enable)
            else:
                raise DiagTableError("Attempted to set invalid 'abstract' option: {}".format(flag))

    return dict(parse_options(options))


class DiagTableBase:
    """This class should not be used directly. Child classes must implement a static `fields` dictionary, the values of
    which are functions which determine whether or not a given value of that field is valid."""

    def __add__(a, b):
        a = copy.deepcopy(a)
        a += b
        return a

    def __or__(a, b):
        a = copy.deepcopy(a)
        a |= b
        return a

    def validate(self, msg):
        """Validate every field of the object"""
        for k, v in self.__dict__.items():
            if v is not None:
                self.validate_field(k, v, msg)

    @classmethod
    def get_empty_dict(cls, list_key=None):
        """Return an empty dictionary for the child class"""
        empty_dict = dict((k, None) for k in cls.fields.keys())
        if list_key is not None:
            empty_dict[list_key] = []
        return empty_dict

    @classmethod
    def validate_field(cls, key, value, msg=""):
        if msg:
            msg = msg + ": "

        diag_assert(key in cls.fields,
                    msg + "Field name '{:}' is invalid".format(key))
        diag_assert(cls.fields[key](value),
                    msg + "Field '{:}' was assigned an invalid value: '{:}'". format(key, value))

    def set(self, key, value):
        """Generic setter with validation"""
        self.validate_field(key, value, "{:}: Failed to set {:}={:}".format(self.__class__.__name__, key, value))
        self.key = value

    def dump_yaml(self, abstract=None, fh=None):
        """Return the object as a YAML string"""
        try:
            return yaml.safe_dump(self.render(abstract), fh, default_flow_style=False, sort_keys=False)
        except yaml.YAMLError as err:
            print("Failed to represent data as YAML: {:s}".format(str(err)))
        except OSError as err:
            print("Failed to write to '{:s}': {:s}".format(err.filename, err.strerror))

    def write(self, filename, abstract=None):
        """Write the object to a YAML file"""
        try:
            with open_file(filename, "w") as fh:
                self.dump_yaml(abstract, fh)
        except OSError as err:
            print("Failed to open '{:s}': {:s}".format(err.filename, err.strerror))

    @classmethod
    def from_yaml_str(cls, yaml_str):
        """Initialize a DiagTable, DiagTableFile, DiagTableVar, or DiagTableSubRegion object from a YAML string"""
        try:
            struct = yaml.safe_load(yaml_str)
            return cls(struct)
        except yaml.YAMLError as err:
            print("Failed to parse YAML: {:s}".format(str(err)))

    @classmethod
    def from_file(cls, filename):
        """Initialize a DiagTable, DiagTableFile, DiagTableVar, or DiagTableSubRegion object from a YAML file"""
        try:
            with open_file(filename, "r") as fh:
                yaml_str = fh.read()
            return cls.from_yaml_str(yaml_str)
        except OSError as err:
            print("Failed to open '{:s}': {:s}".format(err.filename, err.strerror))

    def strip_none(self):
        """Strip all None values out of a dictionary and return the result"""
        return dict(kv for kv in self.__dict__.items() if kv[1] is not None)


class DiagTable(DiagTableBase):
    fields = {
            "title": lambda v: type(v) is str,
            "base_date": lambda v: type(v) is str,
            "diag_files": lambda v: type(v) is list and all(type(vi) is DiagTableFile for vi in v)
            }

    def __init__(self, diag_table={}):
        """Initialize a DiagTable object from a Python dictionary"""

        if type(diag_table) is self.__class__:
            diag_table = diag_table.render()
        elif type(diag_table) is not dict:
            raise TypeError("DiagTable must be constructed from a dictionary")

        self.__dict__ = DiagTable.get_empty_dict("diag_files") | diag_table
        self.diag_files = [DiagTableFile(f) for f in self.diag_files]
        self.validate("table failed to validate")

    def render(self, abstract=None):
        """Return a dictionary representation of the object"""
        table = self.strip_none()
        table["diag_files"] = list(f.render(abstract) for f in table["diag_files"])

        if abstract and abstract.get("table"):
            table = {"diag_files": table["diag_files"]}

        return table

    def filter_files(self, filter):
        """Apply a file filter and return the resulting DiagTable object"""
        filter = file_filter_factory(filter)

        table = copy.copy(self)
        table.diag_files = self.get_filtered_files(filter)
        return table

    def filter_vars(self, filter):
        """Apply a variable filter and return the resulting DiagTable object"""
        filter = var_filter_factory(filter)

        table = copy.copy(self)
        table.diag_files = [f.filter_vars(filter) for f in table.diag_files]
        return table

    def get_filtered_files(self, filter):
        """Apply a file filter and return the resulting list of DiagTableFile objects"""
        filter = file_filter_factory(filter)
        return [f for f in self.diag_files if filter(f)]

    def get_filtered_vars(self, filter):
        """Apply a variable filter and return the resulting list of DiagTableVar objects"""
        filter = var_filter_factory(filter)
        filtered_vars = []

        for f in self.diag_files:
            filtered_vars += f.get_filtered_vars(filter)

        return filtered_vars

    def prune(self):
        """Remove files without any variables"""
        return self.filter_files(lambda file_obj: len(file_obj.varlist) > 0)

    def __iadd__(self, other):
        """Symmetric merge of two DiagTable objects. Any conflict between the
           two operands shall result in a failure."""
        other = DiagTable(other)

        for i, fi in enumerate(self.diag_files):
            for j, fj in enumerate(other.diag_files):
                if fi.file_name == fj.file_name:
                    fi += fj
                    del other.diag_files[j]
                    break

        self.diag_files += other.diag_files
        del other.diag_files

        other = other.strip_none()

        dict_assert_mergeable(self.__dict__, other)
        self.__dict__ |= other
        return self

    def __ior__(self, other):
        """Asymmetric merge of two DiagTable objects. Any conflict between the
           two operands will resolve to the `other` value."""
        other = DiagTable(other)

        for i, fi in enumerate(self.diag_files):
            for j, fj in enumerate(other.diag_files):
                if fi.file_name == fj.file_name:
                    fi |= fj
                    del other.diag_files[j]
                    break

        self.diag_files += other.diag_files
        del other.diag_files

        other = other.strip_none()

        self.__dict__ |= other
        return self

    def set_title(self, title):
        self.set("title", title)

    def set_base_date(self, base_date):
        self.set("base_date", base_date)


class DiagTableFile(DiagTableBase):
    fields = {
            "file_name": lambda v: type(v) is str,
            "freq": lambda v: (type(v) is float) or (type(v) is str),
            "time_units": lambda v: v in ("seconds", "minutes", "hours", "days", "months", "years"),
            "unlimdim": lambda v: type(v) is str,
            "write_file": lambda v: type(v) is bool,
            "global_meta": lambda v: type(v) is dict,
            "sub_region": lambda v: type(v) is DiagTableSubRegion,
            "new_file_freq": lambda v: type(v) is str,
            "start_time": lambda v: type(v) is list and len(v) == 6,
            "file_duration": lambda v: type(v) is str,
            "is_ocean": lambda v: type(v) is bool,
            "kind": lambda v: v in ["r4", "r8", "i4", "i8"],
            "module": lambda v: type(v) is str,
            "reduction": lambda v: (v in ("average", "min", "max", "none", "rms", "sum") or
                                    re.search(r"^pow\d+$", v) or
                                    re.search(r"^diurnal\d+$", v)),
            "varlist": lambda v: type(v) is list and all(type(vi) is DiagTableVar for vi in v)
            }

    def __init__(self, file={}):
        """Initialize a DiagTableFile object from a Python dictionary"""

        if type(file) is self.__class__:
            file = file.render()
        elif type(file) is not dict:
            raise TypeError("DiagTableFile must be constructed from a dictionary")

        self.__dict__ = DiagTableFile.get_empty_dict("varlist") | file
        self.varlist = [DiagTableVar(v) for v in self.varlist]

        if self.sub_region:
            self.sub_region = DiagTableSubRegion(self.sub_region[0])

        if self.global_meta:
            diag_assert(type(self.global_meta) is list and len(self.global_meta) == 1,
                        "Failed to initialize DiagTableFile: Invalid 'global_meta' value")
            self.global_meta = self.global_meta[0]

        self.validate("table failed to validate due to an invalid file")

    def __iadd__(self, other):
        """Symmetric merge of two DiagTableFile objects. Any conflict between the
           two operands shall result in a failure."""
        other = DiagTableFile(other)

        if self.global_meta and other.global_meta:
            dict_assert_mergeable(self.global_meta, other.global_meta)
            self.global_meta |= other.global_meta
            del other.global_meta

        if self.sub_region and other.sub_region:
            self.sub_region += other.sub_region
            del other.sub_region

        for i, fi in enumerate(self.varlist):
            for j, fj in enumerate(other.varlist):
                if fi.var_name == fj.var_name:
                    fi += fj
                    del other.varlist[j]
                    break

        self.varlist += other.varlist
        del other.varlist

        other = other.strip_none()

        dict_assert_mergeable(self.__dict__, other)
        self.__dict__ |= other
        return self

    def __ior__(self, other):
        """Asymmetric merge of two DiagTableFile objects. Any conflict between the
           two operands will resolve to the `other` value."""
        other = DiagTableFile(other)

        if self.global_meta and other.global_meta:
            self.global_meta |= other.global_meta
            del other.global_meta

        if self.sub_region and other.sub_region:
            self.sub_region |= other.sub_region
            del other.sub_region

        for i, fi in enumerate(self.varlist):
            for j, fj in enumerate(other.varlist):
                if fi.var_name == fj.var_name:
                    fi |= fj
                    del other.varlist[j]
                    break

        self.varlist += other.varlist
        del other.varlist

        other = other.strip_none()

        self.__dict__ |= other
        return self

    def render(self, abstract=None):
        """Return a dictionary representation of the object"""
        file = self.strip_none()
        file["varlist"] = list(v.render(abstract) for v in file["varlist"])

        if abstract and abstract.get("file"):
            file = {
                    "file_name": file["file_name"],
                    "varlist": file["varlist"]}

        if len(file["varlist"]) == 0:
            del file["varlist"]

        if "sub_region" in file:
            file["sub_region"] = [file["sub_region"].render()]

        if "global_meta" in file:
            file["global_meta"] = [file["global_meta"]]

        return file

    def filter_vars(self, filter):
        file = copy.copy(self)
        file.varlist = self.get_filtered_vars(filter)
        return file

    def get_filtered_vars(self, filter):
        filter = var_filter_factory(filter)
        return [v for v in self.varlist if filter(self, v)]

    def set_file_name(self, file_name):
        self.set("file_name", file_name)

    def set_freq(self, freq):
        self.set("freq", freq)

    def set_time_units(self, time_units):
        self.set("time_units", time_units)

    def set_unlimdim(self, unlimdim):
        self.set("unlimdim", unlimdim)

    def set_write_file(self, write_file):
        self.set("write_file", write_file)

    def set_global_meta(self, global_meta):
        self.set("global_meta", [global_meta])

    def set_sub_region(self, sub_region):
        self.set("sub_region", sub_region)

    def set_new_file_freq(self, new_file_freq):
        self.set("new_file_freq", new_file_freq)

    def set_start_time(self, start_time):
        self.set("start_time", start_time)

    def set_file_duration(self, file_duration):
        self.set("file_duration", file_duration)

    def set_is_ocean(self, is_ocean):
        self.set("is_ocean", is_ocean)

    def set_kind(self, kind):
        self.set("kind", kind)

    def set_module(self, module):
        self.set("module", module)

    def set_reduction(self, reduction):
        self.set("reduction", reduction)


class DiagTableVar(DiagTableBase):
    fields = {
            "var_name": lambda v: type(v) is str,
            "kind": lambda v: v in ["r4", "r8", "i4", "i8"],
            "module": lambda v: type(v) is str,
            "reduction": lambda v: (v in ["average", "min", "max", "none", "rms", "sum"] or
                                    re.search(r"^pow\d+$", v) or
                                    re.search(r"^diurnal\d+$", v)),
            "write_var": lambda v: type(v) is bool,
            "output_name": lambda v: type(v) is str,
            "long_name": lambda v: type(v) is str,
            "attributes": lambda v: type(v) is dict,
            "zbounds": lambda v: type(v) is str
            }

    def __init__(self, var={}):
        """Initialize a DiagTableVar object from a Python dictionary"""

        if type(var) is self.__class__:
            var = var.render()
        elif type(var) is not dict:
            raise TypeError("DiagTableVar must be constructed from a dictionary")

        if "attributes" in var:
            diag_assert(type(var["attributes"]) is list and len(var["attributes"]) == 1,
                        "Failed to initialize DiagTableVar: Invalid 'attributes' value")
            var["attributes"] = var["attributes"][0]

        self.__dict__ = DiagTableVar.get_empty_dict() | var
        self.validate("table failed to validate due to an invalid variable")

    def __iadd__(self, other):
        """Symmetric merge of two DiagTableVar objects. Any conflict between the
           two operands shall result in a failure."""
        other = DiagTableVar(other)

        if self.attributes and other.attributes:
            dict_assert_mergeable(self.attributes, other.attributes)
            self.attributes |= other.attributes
            del other.attributes

        other = other.strip_none()

        dict_assert_mergeable(self.__dict__, other)
        self.__dict__ |= other
        return self

    def __ior__(self, other):
        """Asymmetric merge of two DiagTableVar objects. Any conflict between the
           two operands will resolve to the `other` value."""
        other = DiagTableVar(other)

        if self.attributes and other.attributes:
            self.attributes |= other.attributes
            del other.attributes

        other = other.strip_none()

        self.__dict__ |= other
        return self

    def render(self, abstract=None):
        """Return a dictionary representation of the object"""
        if abstract and abstract.get("var"):
            return self.var_name
        else:
            var = self.strip_none()
            if "attributes" in var:
                var["attributes"] = [var["attributes"]]
            return var

    def set_var_name(self, var_name):
        self.set("var_name", var_name)

    def set_kind(self, kind):
        self.set("kind", kind)

    def set_module(self, module):
        self.set("module", module)

    def set_reduction(self, reduction):
        self.set("reduction", reduction)

    def set_write_var(self, write_var):
        self.set("write_var", write_var)

    def set_output_name(self, output_name):
        self.set("output_name", output_name)

    def set_long_name(self, long_name):
        self.set("long_name", long_name)

    def set_attributes(self, attributes):
        self.set("attributes", attributes)

    def set_zbounds(self, zbounds):
        self.set("zbounds", zbounds)


class DiagTableSubRegion(DiagTableBase):
    @staticmethod
    def validate_corner(v):
        return type(v) is list and len(v) == 2 and all(type(vi) is float for vi in v)

    fields = {
            "grid_type": lambda v: v in ("indices", "latlon"),
            "corner1": validate_corner,
            "corner2": validate_corner,
            "corner3": validate_corner,
            "corner4": validate_corner,
            "tile": lambda v: type(v) is int
            }

    def __init__(self, sub_region={}):
        """Initialize a DiagTableSubRegion object from a Python dictionary"""

        if type(sub_region) is self.__class__:
            sub_region = sub_region.render()
        elif type(sub_region) is not dict:
            raise TypeError("DiagTableSubRegion must be constructed from a dictionary")

        self.__dict__ = DiagTableSubRegion.get_empty_dict() | sub_region
        self.validate("table failed to validate due to an invalid subregion")

    def __iadd__(self, other):
        """Symmetric merge of two DiagTableSubRegion objects. Any conflict between the
           two operands shall result in a failure."""
        other = DiagTableSubRegion(other)
        other = other.strip_none()

        dict_assert_mergeable(self.__dict__, other)
        self.__dict__ |= other
        return self

    def __ior__(self, other):
        """Asymmetric merge of two DiagTableSubRegion objects. Any conflict between the
           two operands will resolve to the `other` value."""
        other = DiagTableSubRegion(other)
        other = other.strip_none()

        self.__dict__ |= other
        return self

    def render(self, abstract=None):
        """Return a dictionary representation of the object"""
        return self.strip_none()

    def set_grid_type(self, grid_type):
        self.set("grid_type", grid_type)

    def set_corner1(self, corner1):
        self.set("corner1", corner1)

    def set_corner2(self, corner2):
        self.set("corner2", corner2)

    def set_corner3(self, corner3):
        self.set("corner3", corner3)

    def set_corner4(self, corner4):
        self.set("corner4", corner4)

    def set_tile(self, tile):
        self.set("tile", tile)
