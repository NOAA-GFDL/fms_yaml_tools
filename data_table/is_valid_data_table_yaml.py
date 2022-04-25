import yaml
import sys
import argparse

def check_gridname(grid_name):
    valid = ["OCN", "LND", "ATM", "ICE"]
    if (gridname not in valid): sys.exit('The only values allowed for grid_name are "OCN", "LND", "ATM", "ICE"')

def check_fieldname_code(fieldname):
    if (fieldname == ""): sys.exit("Fieldname is not empty")

def check_filename_and_field(field, interp_method):
    if (field =="" and interp_method != "none"): sys.exit('If "fieldname_file" is empty, interp_method must be "none"')

def check_interp_method(interp_method):
    valid = ["bilinear", "bicubic", "none"]
    if (interp_method not in valid): sys.exit('The only values allowed for interp method are "bilinear", "bicubic", and "none"')

def check_region_type(region_type):
    valid = ["inside_region", "outside_region"]
    if (region_type not in valid): sys.exit('The only values allowed for region_type are "inside_region" and "outside_region"')

def check_if_bounds_present(entry):
    if ("lat_start" not in entry): sys.exit('lat_start must be present if region_type is set')
    if ("lat_end" not in entry): sys.exit('lat_end must be present if region_type is set')
    if ("lon_start" not in entry): sys.exit('lon_start must be present if region_type is set')
    if ("lon_end" not in entry): sys.exit('lon_end must be present if region_type is set')

def check_region(my_type, start, end):
    if (start > end): sys.exit(my_type+"_start is greater than "+my_type+"_end")

#: parse user input
parser = argparse.ArgumentParser(prog='is_valid_data_table_yaml', description="checks in data_table.yaml is valid")
parser.add_argument('-f', type=str, help='data_table file' )
in_data_table = parser.parse_args().f

with open(in_data_table) as fl:
    my_table = yaml.safe_load(fl)
    for key, value in my_table.items():
        for i in range(0, len(value)):
            entry = value[i]
            gridname = entry["gridname"]
            check_gridname(gridname)

            fieldname_code = entry["fieldname_code"]
            check_fieldname_code(fieldname_code)

            fieldname_file = entry["fieldname_file"]
            file_name = entry["file_name"]
            interp_method = entry["interpol_method"]
            check_interp_method(interp_method)
            check_filename_and_field(fieldname_file, interp_method)

            factor = entry["factor"]

            if "region_type" in entry:
                region_type = entry["region_type"]
                check_region_type(region_type)
                check_if_bounds_present(entry)

                lat_start = entry["lat_start"]
                lat_end = entry["lat_end"]
                check_region("lat", lat_start, lat_end)

                lon_start = entry["lon_start"]
                lon_end = entry["lon_end"]
                check_region("lon", lon_start, lon_end)
