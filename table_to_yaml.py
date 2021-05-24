#!/usr/bin/python

# converts the following three sections of diag_table to yaml format:
# global, file, and field

# global section
# line 1:  title of the experiment; a string
# line 2:  base reference date > model start time
#          format:  year month day hour minute second

# file section
#      1           2               3                 4               5                 6
# "file_name", output_freq, "output_freq_units", file_format, "time_axis_units", "time_axis_name"
#        7                 8                   9               10                  11
# [, new_file_freq, "new_file_freq_units"[, "start_time"[, file_duration, "file_duration_units"]]]
# add uriel's new contribution


# field section
# "module_name", "field_name", "output_name", "file_name", "time_sampling", "reduction_method", "regional_section", packing


# global section
class DiagTable :

    def __init__(self, diag_table_filename='Diag_Table' ) :

        ''' add description of this class later'''

        self.diag_table_filename = diag_table_filename
        self.global_section = [{'title'      : ''},
                               {'base_year'  : ''},
                               {'base_month' : ''},
                               {'base_day'   : ''},
                               {'base_hour'  : ''},
                               {'base_minute':'' },
                               {'base_second': ''} ]

        self.file_section = [{'file_name'          : ''},
                             {'output_freq'        : ''},
                             {'output_freq_units'  : ''},
                             {'file_format'        : ''},
                             {'time_axis_units'    : ''},
                             {'time_axis_name'     : ''},
                             {'new_file_freq'      : ''},
                             {'new_file_freq_units': ''},
                             {'start_time'         : ''},
                             {'file_duration'      : ''},
                             {'file_duration_units': ''},
                             {'filename_suffix'    : ''} ]

        self.field_section = [{ 'module_name'     : ''},
                              { 'field_name'      : ''},
                              { 'output_name'     : ''},
                              { 'file_name'       : ''},
                              { 'time_sampling'   : ''},
                              { 'reduction_method': ''},
                              { 'regional_section': ''},
                              { 'packing'         : ''} ]
        self.diag_table_content = []

        #: check if diag_table file exists
        #if self.diag_table_filename

    def read_diag_table_filename(self) :
        with open( self.diag_table_filename, 'r' ) as myfile :
            for iline in myfile.readlines() :
                if iline.strip() != '' : self.diag_table_content.append( iline.strip() )

    def parse_global_section(self) :
        if self.diag_table_content == [] : print( 'something is wrong' )
        self.global_section[0]['title'] = self.diag_table_content[0]
        line_two_list = self.diag_table_content[1].split(' ')
        for i in range(len(line_two_list)) :
            ikey = self.global_section[i+1].keys()[0]
            self.global_section[i+1][ikey] = int(line_two_list[i])


test_class = DiagTable( diag_table_filename='diag_table_21' )
test_class.read_diag_table_filename()
test_class.parse_global_section()
print( test_class.global_section )
