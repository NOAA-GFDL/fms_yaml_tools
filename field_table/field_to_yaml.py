#!/usr/bin/python3

import copy as cp
import argparse
from os import path
import yaml


def read_first_line(in_string) :
    try :
        split_string=in_string.split('"')
        return split_string[1], split_string[3], split_string[5]
    except :
        exit("ERROR IN READING FIRST LINE")
        
class Field_Table :
    
    def __init__(self, field_table_file='field_table') :

        self.field_table_file = field_table_file
        self.field_table_content = []
        self.keys = [ 'tracer', 'mod', 'name']
        self.fields = []
        
test_class = Field_Table(field_table_file='field_table2')

#: read field_table
with open(test_class.field_table_file, 'r') as myfile :
    for iline in myfile.readlines() : 
        #: delete empty line ; get rid of leading spaces ; get rid of new line ; get rid of comments
        stripped = iline.lstrip(' ').strip()
        if len(stripped) != 0 and stripped[0] != "#" :
            test_class.field_table_content.append( stripped )


end_line, tmp_dict = False, {}
for iline in test_class.field_table_content :

    if end_line : tmp_dict, end_line = {}, False

    #: line 1
    if "tracer" in iline.lower() and "mod" in iline.lower() :
        tmp_dict[test_class.keys[0]],tmp_dict[test_class.keys[1]],tmp_dict[test_class.keys[2]]=read_first_line(iline.lower())
        if iline[-1:] == '/' : end_line = True
    elif "species" in iline.lower() and "mod" in iline.lower() :
        tmp_dict[test_class.keys[0]],tmp_dict[test_class.keys[1]],tmp_dict[test_class.keys[2]]=read_first_line(iline.lower())
        if iline[-1:] == '/' : end_line = True
        
    #: not line 1
    else :
        if iline[-1:].strip() == '/' : iline, end_line = iline.strip()[:-1], True

        if '"' in iline :
            if iline.count('"') == 2 :
                #"Profile_type/Fixed/surface_value = 0.0E+00"
                if '/' in iline :
                    [ikey, ival, ikeyval2] = iline.replace('"','').split('/')
                    [ikey2, ival2] = ikeyval2.split('=')
                    tmp_dict[ikey] = [ival, {ikey2:ival2}]
                #"horizontal-advection-scheme = mdfl_sweby"
                else :
                    ikey, ival = iline.replace('"','').split('=')
                    tmp_dict[ikey] = ival
            #"horizontal-advection-scheme", "mdfl_sweby"
            elif iline.count('"') == 4 :
                ikey,ival = [iword.strip() for iword in iline.replace(',','').split('"')
                             if iword.strip()!='' ]
                tmp_dict[ikey] = ival                
            #"Profile_type","Fixed","surface_value = 0.0E+00"
            elif iline.count('"') == 6 :
                [ikey, ival, ikeyval2] = [iword.strip() for iword in iline.split('"')
                                          if iword.strip()!='' and iword.strip()!=',']
                #: this is assuming there is no horribleness such as
                #: "key1","val1","key2=val2,val3,val4, key3=val5"
                tmp_dict[ikey]=[ival]
                ikeyval2_pairs = [ipair.lstrip().strip() for ipair in ikeyval2.split(',')]
                for ipair in ikeyval2_pairs :
                    tmp_dict[ikey].append( {ipair.split('=')[0]:ipair.split('=')[1]} )
        else :          
            #Profile_type/Fixed/surface_value = 0.0E+00
            if '/' in iline :
                [ikey, ival, ikeyval2] = iline.split('/')
                [ikey2, ival2] = ikeyval2.split('=')
                tmp_dict[ikey] = {ival, {ikey2:ival2}}
            #vertical-advection-scheme = mdfl_sweby
            else :
                ikeyval2_pairs = [ipair.lstrip().strip() for ipair in ikeyval2.split(',')]
                for ipair in ikeyval2_pairs :
                    tmp_dict[ipair.split('=')[0].strip()] = ipair.split('=')[1].strip()                    

    if end_line : print( tmp_dict )
