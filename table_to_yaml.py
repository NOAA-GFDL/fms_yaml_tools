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

import copy as cp

def init_yaml_file(outfile='') :
    with open(outfile,'w') as myfile : myfile.write('---\n')

def write_yaml_sections(outfile='', section=[], header='') :
    with open(outfile, 'a+') as myfile :
        myfile.write( header + '\n')
        for isection in range(len(section)) :
            ilist = section[isection]
            myfile.write( '-  ' + list(ilist[0].keys())[0] + ':' + list(ilist[0].values())[0]+'\n')
            for i in range(1,len(ilist)) :
                myfile.write( '   ' + list(ilist[i].keys())[0] + ':' + list(ilist[i].values())[0]+'\n')

# global section
class DiagTable :

    def __init__(self, diag_table_filename='Diag_Table' ) :

        ''' add description of this class later'''

        self.diag_table_filename = diag_table_filename

        self.global_section = []
        self.global_section_keys = ['title',
                                    'base_date_year',
                                    'base_date_month',
                                    'base_date_day',
                                    'base_date_hour',
                                    'base_date_minute',
                                    'base_date_second']

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
        self.global_section, tmp_list = [], []
        tmp_list.append( {self.global_section_keys[0]:self.diag_table_content[0]} )
        line_two_list = self.diag_table_content[1].strip().split(' ')
        for i in range(len(line_two_list)) :
            tmp_list.append( {self.global_section_keys[i+1] : line_two_list[i] } )
        self.global_section.append(cp.deepcopy(tmp_list))

    def parse_file_section(self) :
        if self.diag_table_content == [] : print( 'something is wrong' )
        for iline in self.diag_table_content[2:] :
            iline_list = iline.strip().split(',')
            if isinstance(iline_list[1], int) : 
                tmp_list = [ {self.file_section_keys[i]:iline_list[i]} for i in range(len(iline_list)) ]
                self.file_section.append( cp.deepcopy(tmp_list) )

    def parse_field_section(self) :
        if self.diag_table_content == [] : print( 'something is wrong' )
        for iline in self.diag_table_content[2:] :
            iline_list = iline.strip().split(',')
            if not isinstance(iline_list[1], int) :
                tmp_list = [ {self.field_section_keys[i]:iline_list[i]} for i in range(len(iline_list)) ]
                self.field_section.append( cp.deepcopy(tmp_list) )

    def parse_diag_table(self) :
        if self.diag_table_content == [] : print( 'something is wrong' )
        self.parse_global_section()
        self.parse_file_section()
        self.parse_field_section()

    def read_and_parse_diag_table(self) :
        self.read_diag_table()
        self.parse_diag_table()

    def write_yaml(self, outfile='DEFAULT') :
        if outfile == 'DEFAULT' : outfile=self.diag_table_filename+'.yaml'
        init_yaml_file(outfile)
        write_yaml_sections( outfile, self.global_section, header='diag_global' )
        write_yaml_sections( outfile, self.file_section, header='diag_files' )
        write_yaml_sections( outfile, self.field_section, header='diag_fields')

test_class = DiagTable( diag_table_filename='diag_table' )
test_class.read_and_parse_diag_table()
test_class.write_yaml()
