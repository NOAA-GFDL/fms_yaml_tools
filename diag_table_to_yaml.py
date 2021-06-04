#!/usr/bin/python3.6

#: converts the global, file and field sections in diag_table to yaml format:

import copy as cp
import argparse
from os import path


#: parse user input
parser = argparse.ArgumentParser(prog='diag_table_to_yaml', description="converts diag_table to yaml format")
parser.add_argument('-f', type=str, help='diag_table file' )
in_diag_table = parser.parse_args().f


#: write '---' at top of the yaml file
def init_yaml_file(outfile='') :
    with open(outfile,'w') as myfile : myfile.write('---\n')


#: section = [ list1, list2, list3, ... ]
#: list1   = [ {key1:val1}, {key2:val2}, ... ]
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
                                    'base_year',
                                    'base_month',
                                    'base_day',
                                    'base_hour',
                                    'base_minute',
                                    'base_second']
        self.global_section_values = {'title'      : str,
                                      'base_year'  : int,
                                      'base_month' : int,
                                      'base_day'   : int,
                                      'base_hour'  : int,
                                      'base_minute': int,
                                      'base_second': int}

        self.file_section = []
        self.file_section_keys = ['file_name',
                                  'output_freq',
                                  'output_freq_units',
                                  'file_format',
                                  'time_units',
                                  'long_name',
                                  'new_file_freq',
                                  'new_file_freq_units',
                                  'start_time_s',
                                  'file_duration',
                                  'file_duration_units',
                                  'filename_time_bounds' ]
        self.file_section_values = {'file_name'           : str,
                                    'output_freq'         : int,
                                    'output_freq_units'   : str,
                                    'file_format'         : int,
                                    'time_units'          : str,
                                    'long_name'           : str,
                                    'new_file_freq'       : int,
                                    'new_file_freq_units' : str,
                                    'start_time_s'        : str,
                                    'file_duration'       : int,
                                    'file_duration_units' : str,
                                    'filename_time_bounds': str }

        self.field_section = []
        self.field_section_keys = ['module_name',
                                   'field_name',
                                   'output_name',
                                   'file_name',
                                   'time_sampling',
                                   'time_method',
                                   'spatial_ops',
                                   'pack']
        self.field_section_values = {'module_name'   : str,
                                     'field_name'    : str,
                                     'output_name'   : str,
                                     'file_name'     : str,
                                     'time_sampling' : str,
                                     'time_method'   : str,
                                     'spatial_ops'   : str,
                                     'pack'          : int }

        self.diag_table_content = []

        #: check if diag_table file exists
        if not path.exists( self.diag_table_file ) : exit( 'file '+self.diag_table_file+' does not exist' )


    def read_diag_table(self) :
        #: read
        with open( self.diag_table_file, 'r' ) as myfile :
            self.diag_table_content = myfile.readlines()


    def parse_diag_table(self) :
        if self.diag_table_content == [] : exit('ERROR:  diag_table_content is empty')

        iline_count, global_count = 0, 0

        #: global section; should be the first two lines
        while global_count < 2 :
            iline = self.diag_table_content[iline_count]
            iline_count += 1
            if iline.strip() != '' and '#' not in iline.strip()[0] : #: if not blank or comment
                #: line 2
                if global_count == 1 :
                    try :
                        iline_list, tmp_list = iline.split('#')[0].split(), [] #: not comma separated integers
                        for i in range(1,len(self.global_section_keys) ) :
                            mykey   = self.global_section_keys[i]
                            myfunct = self.global_section_values[mykey]
                            myval   = myfunct( iline_list[i-1].strip() )
                            tmp_list.append( {mykey:myval} )
                        self.global_section[0][1:] = tmp_list
                        global_count += 1
                    except :
                        exit(" ERROR with line # " + str(iline_count) + '\n'
                             " CHECK:            " + str(iline) + '\n' )
                #: line 1
                if global_count == 0 :
                    try :
                        mykey   = self.global_section_keys[0]
                        myfunct = self.global_section_values[mykey]
                        myval   = '"' + myfunct( iline.strip() ) + '"'
                        self.global_section.append( [{mykey:myval}] )
                        global_count += 1
                    except :
                        exit(" ERROR with line # " + str(iline_count) + '\n'
                             " CHECK:            " + str(iline) + '\n' )

        #: rest are either going to be file or field section
        for iline in self.diag_table_content[iline_count+1:] :
            iline_count += 1
            if iline.strip() != '' and '#' not in iline.strip()[0] : #: if not blank line or comment
                iline_list = iline.split('#')[0].split(',')          #:get rid of comment at the end
                try :
                    #: see if file section
                    tmp_list = []
                    for i in range(len(iline_list)) :
                        mykey   = self.file_section_keys[i]
                        myfunct = self.file_section_values[mykey]
                        myval   = myfunct( iline_list[i].strip() )
                        tmp_list.append( {mykey:myval} )
                    self.file_section.append( cp.deepcopy(tmp_list) )
                except :
                    #: see if field section
                    try :
                        tmp_list = []
                        for i in range(len(self.field_section_keys)) :
                            mykey   = self.field_section_keys[i]
                            myfunct = self.field_section_values[mykey]
                            myval   = myfunct( iline_list[i].strip() )
                            tmp_list.append( {mykey:myval} )
                        self.field_section.append( cp.deepcopy(tmp_list) )
                    except :
                        exit(" ERROR with line # " + str(iline_count) + '\n'
                             " CHECK:            " + str(iline) + '\n' )


    def write_yaml(self, outfile='DEFAULT') :
        if outfile == 'DEFAULT' : outfile=self.diag_table_file+'.yaml'
        init_yaml_file(outfile)
        write_yaml_sections( outfile, self.global_section, header='diag_global' )
        write_yaml_sections( outfile, self.file_section,   header='diag_files' )
        write_yaml_sections( outfile, self.field_section,  header='diag_fields')

    def read_and_parse_diag_table(self) :
        self.read_diag_table()
        self.parse_diag_table()


    def convert_diag_table(self) :
        self.read_and_parse_diag_table()
        self.write_yaml()


#: start
test_class = DiagTable( diag_table_file=in_diag_table )
test_class.convert_diag_table()
