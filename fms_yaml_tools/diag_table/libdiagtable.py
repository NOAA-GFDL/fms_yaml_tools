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
import sys
import re
import itertools
import copy

strip_none = lambda d: dict(kv for kv in d.items() if kv[1] is not None)

class DiagTableFilter:
    @staticmethod
    def parse_negate_flag(s):
        if s[0] == "~":
            return (s[1:], True)
        else:
            return (s, False)

    @staticmethod
    def file_filter_factory(files):
        """Return a function to be used as a file filter"""
        if type(files) is str:
            files = (files,)

        # Pass-through if no filter string is provided
        if len(files) == 0:
            return lambda file_obj: True

        def iterate_cases():
            for file in files:
                file, negate = DiagTableFilter.parse_negate_flag(file)
                for part in file.split(","):
                    yield (part or "*", negate)

        def file_filter(file_obj):
            match = False
            for name,negate in iterate_cases():
                if (file_obj.file_name == name or name == "*"):
                    match = True
            return match ^ negate

        return file_filter

    @staticmethod
    def var_filter_factory(vars):
        """Return a function to be used as a variable filter"""
        if type(vars) is str:
            vars = (vars,)

        # Pass-through if no filter string is provided
        if len(vars) == 0:
            return lambda file_obj, var_obj: True

        def iterate_cases():
            for var in vars:
                var, negate = DiagTableFilter.parse_negate_flag(var)
                fmv = [p.split(",") or ("*",) for p in var.split(":")]

                match len(fmv):
                    case 1:
                        iter = itertools.product(("*",), ("*",), fmv[0], (negate,))
                    case 2:
                        iter = itertools.product(fmv[0], ("*",), fmv[1], (negate,))
                    case 3:
                        iter = itertools.product(fmv[0], fmv[1], fmv[2], (negate,))
                    case _:
                        raise Exception("Invalid variable filter specification")

                for case in iter:
                    yield case

        def var_filter(file_obj, var_obj):
            match = False
            for file,module,var,negate in iterate_cases():
                if (
                        (file_obj.file_name == file or file == "*") and
                        ((var_obj.module or file_obj.module) == module or module == "*") and
                        (var_obj.var_name == var or var == "*")):
                    match = True
            return match ^ negate

        return var_filter

def dict_assert_mergeable(a, b):
    """Assert that two dictionaries can be symmetrically merged. This assertion fails
       if both dictionaries contain a common key with two different values."""
    common_keys = a.keys() & b.keys()
    for k in common_keys:
        if a[k] != b[k]:
            raise Exception("Could not merge dictionaries: key '{:s}' has two different values".format(k))

class DiagTableBase:
    """This class should not be used directly. Child classes must
       implement a static `validate_field` method, which decides whether or
       not a key/value pair is valid."""

    def validate(self):
        for key, value in self.__dict__.items():
            if value is not None:
                self.__class__.validate_field(key, value)

    def set(key, value):
        self.__class__.validate_field(key, value)
        self.__dict__[key] = value

    def coerce_type(self, other):
        if type(other) is dict:
            other = self.__class__(other)

        if type(other) is not self.__class__:
            raise TypeError("Unable to create {:s} from type {:s}".format(type(self).__name__, type(other).__name__))

        other.__dict__ = strip_none(other.__dict__)
        return other

    def __add__(a, b):
        a = copy.deepcopy(a)
        a += b
        return a

    def __or__(a, b):
        a = copy.deepcopy(a)
        a |= b
        return a

class DiagTable(DiagTableBase):
    fields = {
        "title":      None,
        "base_date":  None,
        "diag_files": []
    }

    @staticmethod
    def validate_field(key, value):
        match key:
            case "title":
                assert type(value) is str
            case "base_date":
                assert type(value) is str
            case "diag_files":
                assert type(value) is list
                for f in value:
                    assert type(f) is DiagTableFile
            case _:
                raise AttributeError("DiagTable: Invalid key name: {:s}".format(key))

    @staticmethod
    def from_file(filename, open_func=open):
        """Initialize a DiagTable object from a YAML file"""

        try:
            with open_func(filename, "r") as fh:
                yaml_str = fh.read()
            return DiagTable.from_yaml_str(yaml_str)
        except FileNotFoundError as err:
            print(err)

    @staticmethod
    def from_yaml_str(yaml_str):
        """Initialize a DiagTable object from a YAML string"""
        try:
            diag_table = yaml.safe_load(yaml_str)
            return DiagTable(diag_table)
        except yaml.scanner.ScannerError as err:
            print("YAML parsing error: {}".format(err))

    def __init__(self, diag_table={}):
        """Initialize a DiagTable object from a Python dictionary"""

        if type(diag_table) is not dict:
            raise TypeError("DiagTable must be constructed from a dictionary")

        self.__dict__ = self.fields | diag_table
        self.diag_files = [DiagTableFile(f) for f in self.diag_files]
        self.validate()

    def render(self, abstract=None):
        table = strip_none(self.__dict__)
        table["diag_files"] = list(f.render(abstract) for f in table["diag_files"])

        if abstract and "table" in abstract:
            table = {"diag_files": table["diag_files"]}

        return table

    def filter_files(self, filter):
        if not callable(filter):
            filter = DiagTableFilter.file_filter_factory(filter)

        table = copy.copy(self)
        table.diag_files = [f for f in table.diag_files if filter(f)]
        return table

    def filter_vars(self, filter):
        if not callable(filter):
            filter = DiagTableFilter.var_filter_factory(filter)

        table = copy.copy(self)
        table.diag_files = [f.filter_vars(filter) for f in table.diag_files]
        return table

    def __iadd__(self, other):
        """Symmetric merge of two DiagTable objects. Any conflict between the
           two operands shall result in a failure."""
        other = copy.copy(self.coerce_type(other))

        if "diag_files" in self.__dict__ and "diag_files" in other.__dict__:
            b = copy.copy(other.diag_files)

            for i,fi in enumerate(self.diag_files):
                for j,fj in enumerate(b):
                    if fi.file_name == fj.file_name:
                        fi += fj
                        del b[j]
                        break

            self.diag_files += b
            del other.diag_files

        dict_assert_mergeable(self.__dict__, other.__dict__)
        self.__dict__ |= other.__dict__
        return self

    def __ior__(self, other):
        """Asymmetric merge of two DiagTable objects. Any conflict between the
           two operands will resolve to the `other` value."""
        other = copy.copy(self.coerce_type(other))

        if "diag_files" in self.__dict__ and "diag_files" in other.__dict__:
            b = copy.copy(other.diag_files)

            for i,fi in enumerate(self.diag_files):
                for j,fj in enumerate(b):
                    if fi.file_name == fj.file_name:
                        fi |= fj
                        del b[j]
                        break

            self.diag_files += b
            del other.diag_files

        self.__dict__ |= other.__dict__
        return self

    def set_title(self, title):
        self.set("title", title)

    def set_base_date(self, base_date):
        self.set("base_date", base_date)

    def dump_yaml(self, abstract=None, fh=None):
        return yaml.safe_dump(self.render(abstract), fh, default_flow_style=False, sort_keys=False)

    def write(self, filename, abstract=None):
        """Write the DiagTable to a file"""
        try:
            with open(filename, "w") as fh:
                self.dump_yaml(abstract, fh)
        except Exception as err:
            print("Failed to write YAML file: {:s}".format(err))
        #except Exception as err:
            #print("Failed to open file for writing: {:s}".format(err))

class DiagTableFile(DiagTableBase):
    fields = {
        "file_name":     None,
        "freq":          None,
        "time_units":    None,
        "unlimdim":      None,
        "write_file":    None,
        "global_meta":   None,
        "sub_region":    None,
        "new_file_freq": None,
        "start_time":    None,
        "file_duration": None,
        "is_ocean":      None,
        "kind":          None,
        "module":        None,
        "reduction":     None,
        "varlist":       []
    }

    @staticmethod
    def validate_field(key, value):
        match key:
            case "file_name":
                assert type(value) is str
            case "freq":
                assert (type(value) is float) or (type(value) is str)
            case "time_units":
                assert value in ["seconds", "minutes", "hours", "days", "months", "years"]
            case "unlimdim":
                assert type(value) is str
            case "write_file":
                assert type(value) is bool
            case "global_meta":
                type(value) is dict
            case "sub_region":
                assert type(value) is DiagTableSubRegion
            case "new_file_freq":
                assert type(value) is str
            case "start_time":
                assert type(value) is list and len(value) == 6
            case "file_duration":
                assert type(value) is str
            case "is_ocean":
                assert type(value) is bool
            case "kind":
                assert value in ["r4", "r8", "i4", "i8"]
            case "module":
                assert type(value) is str
            case "reduction":
                assert (value in ["average", "min", "max", "none", "rms", "sum"] or
                        re.search(r"^pow\d+$", value) or
                        re.search(r"^diurnal\d+$", value))
            case "varlist":
                assert type(value) is list
                for v in value:
                      assert type(v) is DiagTableVar
            case _:
                raise AttributeError("DiagTableFile: Invalid key name: {:s}".format(key))

    def __init__(self, file={}):
        """Initialize a DiagTableFile object from a Python dictionary"""

        if type(file) is not dict:
            raise TypeError("DiagTableFile must be constructed from a dictionary")

        self.__dict__ = self.fields | file
        self.varlist = [DiagTableVar(v) for v in self.varlist]

        if self.sub_region:
            self.sub_region = DiagTableSubRegion(self.sub_region[0])

        if self.global_meta:
            assert type(self.global_meta) is list and len(self.global_meta) == 1
            self.global_meta = self.global_meta[0]

        self.validate()

    def __iadd__(self, other):
        other = copy.copy(self.coerce_type(other))

        if self.global_meta and other.global_meta:
            dict_assert_mergeable(self.global_meta, other.global_meta)
            self.global_meta |= other.global_meta
            del other.global_meta

        if self.sub_region and other.sub_region:
            self.sub_region += other.sub_region
            del other.sub_region

        b = copy.copy(other.varlist)

        for i,fi in enumerate(self.varlist):
            for j,fj in enumerate(b):
                if fi.var_name == fj.var_name:
                    fi += fj
                    del b[j]
                    break
        self.varlist += b
        del other.varlist

        dict_assert_mergeable(self.__dict__, other.__dict__)
        self.__dict__ |= other.__dict__
        return self

    def __ior__(self, other):
        other = copy.copy(self.coerce_type(other))

        if self.global_meta and other.global_meta:
            self.global_meta |= other.global_meta
            del other.global_meta

        if self.sub_region and other.sub_region:
            self.sub_region |= other.sub_region
            del other.sub_region

        b = copy.copy(other.varlist)

        for i,fi in enumerate(self.varlist):
            for j,fj in enumerate(b):
                if fi.var_name == fj.var_name:
                    fi |= fj
                    del b[j]
                    break
        self.varlist += b
        del other.varlist

        self.__dict__ |= other.__dict__
        return self

    def render(self, abstract=None):
        file = strip_none(self.__dict__)
        file["varlist"] = list(v.render(abstract) for v in file["varlist"])

        if abstract and "file" in abstract:
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
        if not callable(filter):
            filter = DiagTableFilter.var_filter_factory(filter)

        file = copy.copy(self)
        file.varlist = [v for v in file.varlist if filter(self, v)]
        return file

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
        "var_name":    None,
        "kind":        None,
        "module":      None,
        "reduction":   None,
        "write_var":   None,
        "output_name": None,
        "long_name":   None,
        "attributes":  None,
        "zbounds":     None
    }

    @staticmethod
    def validate_field(key, value):
        match key:
            case "var_name":
                assert type(value) is str
            case "kind":
                assert value in ["r4", "r8", "i4", "i8"]
            case "module":
                assert type(value) is str
            case "reduction":
                assert (value in ["average", "min", "max", "none", "rms", "sum"] or
                        re.search(r"^pow\d+$", value) or
                        re.search(r"^diurnal\d+$", value))
            case "write_var":
                assert type(value) is bool
            case "output_name":
                assert type(value) is str
            case "long_name":
                assert type(value) is str
            case "attributes":
                assert type(value) is dict
            case "zbounds":
                assert type(value) is str
            case _:
                raise AttributeError("DiagTableVar: Invalid key name: {:s}".format(key))

    def __init__(self, var={}):
        """Initialize a DiagTableVar object from a Python dictionary"""

        if type(var) is not dict:
            raise TypeError("DiagTableVar must be constructed from a dictionary")

        if "attributes" in var:
            assert type(var["attributes"]) is list and len(var["attributes"]) == 1
            var["attributes"] = var["attributes"][0]

        self.__dict__ = self.fields | var
        self.validate()

    def __iadd__(self, other):
        other = self.coerce_type(other)

        if "attributes" in self.__dict__ and "attributes" in other.__dict__:
            dict_assert_mergeable(self.attributes, other.attributes)
            self.attributes |= other.attributes
            other = copy.copy(other)
            del other.attributes

        dict_assert_mergeable(self.__dict__, other.__dict__)
        self.__dict__ |= other.__dict__
        return self

    def __ior__(self, other):
        other = self.coerce_type(other)

        if "attributes" in self.__dict__ and "attributes" in other.__dict__:
            self.attributes |= other.attributes
            other = copy.copy(other)
            del other.attributes

        self.__dict__ |= other.__dict__
        return self

    def render(self, abstract=None):
        if abstract and "var" in abstract:
            return self.var_name
        else:
            var = strip_none(self.__dict__)
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
    fields = {
        "grid_type": None,
        "corner1":   None,
        "corner2":   None,
        "corner3":   None,
        "corner4":   None,
        "tile":      None
    }

    @staticmethod
    def validate_field(key, value):
        match key:
            case "grid_type":
                assert value in ["indices", "latlon"]
            case "corner1" | "corner2" | "corner3" | "corner4":
                assert type(value) is list
                assert len(value) == 2
                for i in (0, 1):
                    assert type(value[i]) is float
            case "tile":
                assert type(value) is int
            case _:
                raise AttributeError("DiagTableSubRegion: Invalid key name: {:s}".format(key))

    def __init__(self, sub_region={}):
        """Initialize a DiagTableSubRegion object from a Python dictionary"""

        if type(sub_region) is not dict:
            raise TypeError("DiagTableSubRegion must be constructed from a dictionary")

        self.__dict__ = self.fields | sub_region
        self.validate()

    def __iadd__(self, other):
        other = self.coerce_type(other)
        dict_assert_mergeable(self.__dict__, other.__dict__)
        self.__dict__ |= other.__dict__
        return self

    def __ior__(self, other):
        other = self.coerce_type(other)
        self.__dict__ |= other.__dict__
        return self

    def render(self):
        return strip_none(self.__dict__)

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
