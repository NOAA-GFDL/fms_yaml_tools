#!/usr/bin/python3.6

import copy as cp


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


class DataType :

    def __init__(self, data_table_file='data_table') :

        self.data_table_file = data_table_file

        self.data_type  = []
        self.data_type_keys = ['gridname',
                               'fieldname_code',
                               'fieldname_file',
                               'file_name',
                               'interpol_method',
                               'factor',
                               'lon_start',
                               'lon_end',
                               'lat_start',
                               'lat_end',
                               'region_type']

        self.data_type_values = [ {'gridname' : str},
                                  {'fieldname_code' : str},
                                  {'fieldname_file' : str},
                                  {'file_name' : str},
                                  {'interpol_method' : str},
                                  {'factor': float},
                                  {'lon_start': float},
                                  {'lon_end': float},
                                  {'lat_start': float},
                                  {'lat_end': float},
                                  {'region_type': int} ]

        self.data_table_content = []

    def read_data_table(self) :
        if self.data_table_content != [] : self.data_table_content = []
        iline_count = 0
        with open(self.data_table_file, 'r') as myfile :
            for iline in myfile.readlines() :
                iline_count += 1
                if iline.strip() != '' and '#' not in iline.strip()[0] :
                    iline_list = iline.split(',')
                    for i in range( len(iline_list) ) :
                        try :
                            myfunct= self.data_type_values[i][self.data_type_keys[i]]
                            iline_list[i] = myfunct( iline_list[i].strip() )
                        except :
                            exit( '\nERROR in line ' + str(iline_count) + ": " + iline +
                                  '\nCHECK element ' + str(iline_list[i]) )
                self.data_table_content.append( cp.deepcopy(iline_list) )


    def parse_data_table(self) :
        if self.data_table_content == [] : exit('somethings wrong')
        for iline_list in self.data_table_content :
            tmp_list = [ {self.data_type_keys[i]:iline_list[i]} for i in range(len(iline_list)) ]
            self.data_type.append( cp.deepcopy(tmp_list) )


    def read_and_parse_data_table(self) :
        if self.data_table_content != [] : self.data_table_content = []
        self.read_data_table()
        self.parse_data_table()


    def write_yaml( self ) :
        outfile = self.data_table_file + '.yaml'
        init_yaml_file(outfile)
        write_yaml_sections( outfile, self.data_type, header='data_table' )



test_class = DataType(data_table_file='data_table')
test_class.read_and_parse_data_table()
test_class.write_yaml()
print( test_class.data_type )
