#!/usr/bin/python3.6

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

import copy as cp
#import yaml

# global section
class DiagTable :

    def __init__(self, diag_table_filename='Diag_Table' ) :

        ''' add description of this class later'''

        self.diag_table_filename = diag_table_filename

        self.global_section = []
        self.global_section_keys = ['title',
                                    'base_year',
                                    'base_month',
                                    'base_day',
                                    'base_hour',
                                    'base_minute',
                                    'base_second']

        self.file_section = []
        self.file_section_keys = ['file_name',
                                  'output_freq',
                                  'output_freq_units',
                                  'file_format',
                                  'time_axis_units',
                                  'time_axis_name',
                                  'new_file_freq',
                                  'new_file_freq_units',
                                  'start_time',
                                  'file_duration',
                                  'file_duration_units',
                                  'filename_suffix']

        self.field_section = []
        self.field_section_keys = ['module_name',
                                   'field_name',
                                   'output_name',
                                   'file_name',
                                   'time_sampling',
                                   'reduction_method',
                                   'regional_section',
                                   'packing']

        self.diag_table_content = []

        #: check if diag_table file exists
        #if self.diag_table_filename

    def read_diag_table(self) :
        with open( self.diag_table_filename, 'r' ) as myfile :
            for iline in myfile.readlines() :
                if iline.strip() != '' and '#' not in iline : self.diag_table_content.append( iline.strip() )

    def parse_global_section(self) :
        if self.diag_table_content == [] : print( 'something is wrong' )
        self.global_section = []
        self.global_section.append( {self.global_section_keys[0]:self.diag_table_content[0]} )
        line_two_list = self.diag_table_content[1].strip().split(' ')
        for i in range(len(line_two_list)) :
            self.global_section.append( {self.global_section_keys[i+1] : line_two_list[i] } )

    def parse_file_section(self) :
        if self.diag_table_content == [] : print( 'something is wrong' )
        for iline in self.diag_table_content[2:] :
            if 'mod' not in iline :
                iline_list = iline.strip().split(',')
                tmp_list = [ {self.file_section_keys[i]:iline_list[i]} for i in range(len(iline_list)) ]
                self.file_section.append( cp.deepcopy(tmp_list) )

    def parse_field_section(self) :
        if self.diag_table_content == [] : print( 'something is wrong' )
        for iline in self.diag_table_content[2:] :
            if 'mod' in iline :
                iline_list = iline.strip().split(',')
                tmp_list = [ {self.field_section_keys[i]:iline_list[i]} for i in range(len(iline_list)) ]
                self.field_section.append( cp.deepcopy(tmp_list) )

    def parse_all_sections(self) :
        if self.diag_table_content == [] : print( 'something is wrong' )
        self.parse_global_section()
        self.parse_file_section()
        self.parse_field_section()

    def read_and_parse_all_sections(self) :
        self.read_diag_table()
        self.parse_all_sections()

    def write_yaml(self, outfile='DEFAULT') :
        if outfile == 'DEFAULT' : outfile=self.diag_table_filename+'.yaml'
        with open(outfile, 'w') as myfile :
            myfile.write('---')
            myfile.write('diag_files:')
            #for ifile in range(self.file_section) :


test_class = DiagTable( diag_table_filename='diag_table_21' )
test_class.read_diag_table()
test_class.parse_global_section()
test_class.parse_file_section()
print( test_class.file_section )
test_class.parse_field_section()
#print( test_class.field_section )
test_class.write_yaml()
