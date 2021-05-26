#!/usr/bin/python

#: converts the global, file and field sections in diag_table to yaml format:

import copy as cp
import argparse
from os import path


#: parse user input
parser = argparse.ArgumentParser(prog='diag_table_to_yaml',
                                 description="converts the user-specified diag_table to -yaml format")
parser.add_argument('-f',
                    type=str,
                    help='diag_table file' )
in_diag_table = parser.parse_args().f


#: write '---' at top of the yaml file
def init_yaml_file(outfile='') :
    with open(outfile,'w') as myfile : myfile.write('---\n')


#: section = [ [list1], [list2], [list3], ... ]
def write_yaml_sections(outfile='', section=[], header='') :
    with open(outfile, 'a+') as myfile :
        myfile.write( header + ':\n')
        for ilist in section :
            mystr = ' {:2s}' + '{:17s} : ' + '{:' + str(len(ilist[0].values())) + 's} \n'
            myfile.write( mystr.format( '-', str(*ilist[0].keys()) , str(*ilist[0].values()) ))
            for i in range(1,len(ilist)) :
                mystr = ' {:2s}' + '{:17s} : ' + '{:' + str(len(ilist[i].values())) + 's} \n'
                myfile.write( mystr.format( '', str(*ilist[i].keys()) , str(*ilist[i].values()) ))
            myfile.write('\n')


#: diag_table related attributes and functions
class DiagTable :

    def __init__(self, diag_table_file='Diag_Table' ) :

        '''add description of this class later'''

        self.diag_table_file = diag_table_file

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
        if not path.exists( self.diag_table_file ) : exit( 'file '+self.diag_table_file+' does not exist' )


    def check_diag_table(self) :
        #: checks diag_table for correct number of elements for each section
        #: exists if the number of elements is wrong

        if self.diag_table_content == [] : exit( 'diag_table_content is empty.' )

        global_length = 6  #: base date section
        file_length   = 6  #: required fields
        field_length  = 8  #: required fields
        nerrors, nfiles_counted, nfields_counted = 0, 0, 0

        #: global_section
        if len(self.diag_table_content[0]) != 1 :
            print( 'ERROR:  ' + str(self.diag_table_content[0]) )
            nerrors += 1
        if len(self.diag_table_content[1]) != global_length :
            print( 'ERROR:  ' + str(self.diag_table_content[1]) )
            nerrors += 1
        for i in range( 2,len(self.diag_table_content) ) :
            if isinstance(self.diag_table_content[i][1], int) : #: file section
                if len(self.diag_table_content[i]) < file_length :
                    print( 'ERROR: ' + str( self.diag_table_content[i]) )
                    nerrors += 1
                else :
                    nfiles_counted += 1
            else : #: field section
                if len(self.diag_table_content[i]) != field_length :
                    print( 'ERROR:  ' + str(self.diag_table_content[i]) )
                    nerrors += 1
                else :
                    nfields_counted += 1

        if nerrors != 0 :
            exit( 'fix errors in ' + self.diag_table_file )
        else :
            print( 'diag_table_file          = ' + self.diag_table_file )
            print( 'number of files counted  = ' + str(nfiles_counted) )
            print( 'number of fields counted = ' + str(nfields_counted) )


    def read_diag_table(self) :
        with open( self.diag_table_file, 'r' ) as myfile :
            for iline in myfile.readlines() :
                if iline.strip() != '' and '#' not in iline.strip()[0] : #: if not blank line or comment
                    iline_list = iline.strip().split(',')                #: all columns must be comma-separated
                    for i in range(len(iline_list)) :
                        try :
                            iline_list[i] = int(iline_list[i])           #: readline converts everything to string
                        except :
                            iline_list[i] = iline_list[i].strip().split('#')[0] #: there can be comment at eof
                    self.diag_table_content.append( cp.deepcopy(iline_list) )
            self.diag_table_content[1] = [ int(iele) for iele in self.diag_table_content[1][0].split() ] #: basedate not , separated
            self.check_diag_table()

    def parse_global_section(self) :
        if self.diag_table_content == [] : exit( 'diag_table_content is empty.' )
        self.global_section, tmp_list = [], []
        tmp_list.append( {self.global_section_keys[0] : self.diag_table_content[0][0]} )
        line_two_list = self.diag_table_content[1]
        for i in range(len(line_two_list)) : tmp_list.append( {self.global_section_keys[i+1] : line_two_list[i]} )
        self.global_section.append(cp.deepcopy(tmp_list))

    def parse_file_section(self) :
        if self.diag_table_content == [] : exit( 'diag_table_content is empty.' )
        for iline_list in self.diag_table_content[2:] :
            if isinstance(iline_list[1], int) : #: second element in the file section is an integer; it is not in the field section
                tmp_list = [ {self.file_section_keys[i]:iline_list[i]} for i in range(len(iline_list)) ]
                self.file_section.append( cp.deepcopy(tmp_list) )

    def parse_field_section(self) :
        if self.diag_table_content == [] : exit( 'diag_table_content is empty.' )
        for iline_list in self.diag_table_content[2:] :
            if not isinstance(iline_list[1], int) :
                tmp_list = [ {self.field_section_keys[i]:iline_list[i]} for i in range(len(self.field_section_keys)) ]
                self.field_section.append( cp.deepcopy(tmp_list) )

    def parse_diag_table(self) :
        if self.diag_table_content == [] : exit( 'diag_table_content is empty.' )
        self.parse_global_section()
        self.parse_file_section()
        self.parse_field_section()

    def read_and_parse_diag_table(self) :
        self.read_diag_table()
        self.parse_diag_table()

    def write_yaml(self, outfile='DEFAULT') :
        if outfile == 'DEFAULT' : outfile=self.diag_table_file+'.yaml'
        init_yaml_file(outfile)
        write_yaml_sections( outfile, self.global_section, header='diag_global' )
        write_yaml_sections( outfile, self.file_section, header='diag_files' )
        write_yaml_sections( outfile, self.field_section, header='diag_fields')

test_class = DiagTable( diag_table_file=in_diag_table )
test_class.read_and_parse_diag_table()
test_class.write_yaml()
