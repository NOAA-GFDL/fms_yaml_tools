#!/usr/bin/python3.6

#: converts the global, file and field sections in diag_table to yaml format:

import copy as cp
import argparse
from os import path
import yaml

#: parse user input
parser = argparse.ArgumentParser(prog='diag_table_to_yaml', description="converts diag_table to yaml format")
parser.add_argument('-f', type=str, help='diag_table file' )
in_diag_table = parser.parse_args().f

#: diag_table related attributes and functions
class DiagTable :

    def __init__(self, diag_table_file='Diag_Table' ) :

        '''add description of this class later'''

        self.diag_table_file = diag_table_file

        self.global_section = {}
        self.global_section_keys = ['title','baseDate' ]
        self.global_section_fvalues = {'title'    : str,
                                      'baseDate' : [int,int,int,int,int,int]}
        self.max_global_section = len(self.global_section_keys) - 1 #: minus title

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
        self.file_section_fvalues = {'file_name'           : str,
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
        self.max_file_section = len(self.file_section_keys)

        self.field_section = []
        self.field_section_keys = ['module_name',
                                   'field_name',
                                   'output_name',
                                   'file_name',
                                   'time_sampling',
                                   'time_method',
                                   'spatial_ops',
                                   'pack']
        self.field_section_fvalues = {'module_name'   : str,
                                     'field_name'    : str,
                                     'output_name'   : str,
                                     'file_name'     : str,
                                     'time_sampling' : str,
                                     'time_method'   : str,
                                     'spatial_ops'   : str,
                                     'pack'          : int }
        self.max_field_section = len(self.field_section_keys)

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
                        mykey    = self.global_section_keys[1]
                        #tmp_list = [ self.global_section_fvalues[mykey][i](iline_list[i].strip()) for i in range(6) ]
                        #self.global_section[mykey] = tmp_list
                        self.global_section[mykey] = iline.split('#')[0].strip()
                        global_count += 1
                    except :
                        exit(" ERROR with line # " + str(iline_count) + '\n'
                             " CHECK:            " + str(iline) + '\n' )
                #: line 1
                if global_count == 0 :
                    try :
                        mykey   = self.global_section_keys[0]
                        myfunct = self.global_section_fvalues[mykey]
                        myval   = myfunct( iline.strip().strip('"').strip("'") )
                        self.global_section[mykey] = myval
                        global_count += 1
                    except :
                        exit(" ERROR with line # " + str(iline_count) + '\n'
                             " CHECK:            " + str(iline) + '\n' )

        #: rest are either going to be file or field section
        for iline in self.diag_table_content[iline_count:] :
            iline_count += 1
            if iline.strip() != '' and '#' not in iline.strip()[0] : #: if not blank line or comment
                iline_list = iline.split('#')[0].split(',')          #:get rid of comment at the end
                try :
                    #: see if file section
                    tmp_dict = {}
                    for i in range(len(iline_list)) :
                        mykey   = self.file_section_keys[i]
                        myfunct = self.file_section_fvalues[mykey]
                        myval   = myfunct( iline_list[i].strip().strip('"').strip("'"))
                        tmp_dict[mykey] = myval
                    self.file_section.append( cp.deepcopy(tmp_dict) )
                except :
                    #: see if field section
                    try :
                        tmp_dict = {}
                        for i in range(len(self.field_section_keys)) :
                            mykey   = self.field_section_keys[i]
                            myfunct = self.field_section_fvalues[mykey]
                            myval   = myfunct( iline_list[i].strip().strip('"').strip("'") )
                            tmp_dict[mykey] = myval
                        self.field_section.append( cp.deepcopy(tmp_dict) )
                    except :
                        exit(" ERROR with line # " + str(iline_count) + '\n'
                             " CHECK:            " + str(iline) + '\n' )

    def construct_yaml(self) :
        yaml_doc= {}
        #: title
        mykey = self.global_section_keys[0]
        yaml_doc[mykey]=self.global_section[mykey]
        #: basedate
        mykey = self.global_section_keys[1]
        yaml_doc[mykey]=self.global_section[mykey]
        #: diag_files
        yaml_doc['diag_files']=[]
        #: go through each file
        for ifile_dict in self.file_section : #: file_section = [ {}, {}, {} ]
            ifile_dict['varlist']=[]
            for ifield_dict in self.field_section : #: field_section = [ {}, {}. {} ]
                if ifield_dict['file_name'] == ifile_dict['file_name'] :
                    tmp_dict=cp.deepcopy(ifield_dict)
                    del tmp_dict['file_name']
                    ifile_dict['varlist'].append(tmp_dict)
            yaml_doc['diag_files'].append(ifile_dict)
        myfile = open(self.diag_table_file+'.yaml', 'w')
        yaml.dump(yaml_doc, myfile, sort_keys=False)

    def read_and_parse_diag_table(self) :
        self.read_diag_table()
        self.parse_diag_table()

#: start
test_class = DiagTable( diag_table_file=in_diag_table )
test_class.read_and_parse_diag_table()
test_class.construct_yaml()
