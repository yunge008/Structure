from __future__ import print_function
# -*- coding: utf-8 -*-
__author__ = 'yunge008'

import sys
from os import listdir, getcwd, system
from os.path import isfile, join

def open_files():
    # open e2k files and return lines list
    FileList = []
    dataStr = []
    FileName = []
    for f in listdir(getcwd()):
        if isfile(join(getcwd(),f)) and f[-4:] == ".e2k":
            FileList.append(f)
    if len(FileList) == 0:
        print("Cant find any e2k file in " + getcwd() + "\nProgram will exit")
        system('pause')
        sys.exit(0)
    for i in xrange(len(FileList)):
        print(str(i + 1) + " :  " + FileList[i])
    print("Please input your e2k file index, input 0 when finish.")
    file_count = 1
    while 1:
        try:
            if file_count == 1:
                file_index = int(raw_input("input Base model e2k file to compare:"))
            else:
                file_index = int(raw_input("input model " + str(file_count - 1) + " to compare with Base model:"))
            if file_index == 0:
                break
            filename = FileList[file_index - 1]
            with open(filename, "rt") as f:
                dataStr.append(f.readlines())
                FileName.append(filename)
            f.close()
            file_count += 1
        except ValueError:
            print("please enter correct file index")
    return dataStr, FileName


def define_tol():
    tol_input = raw_input("Please input point tolorance (Default 0 if not input)")
    if tol_input != "" and float(tol_input > 0):
        try:
            tol = float(tol_input)
        except ValueError:
            print("tolerance must be number")
            sys.exit(0)
    else:
        tol = 0
    return tol


def get_points_data(dataStr):
    # input file
    # output points_coor, line_ends, line_section, coincident_lines
    end_of_file = len(dataStr)
    point_coor_start = dataStr.index("$ POINT COORDINATES\n")

    # get point coordinates
    point_xy = {}
    for i in xrange(point_coor_start + 1, end_of_file):
        if dataStr[i] == "\n":
            break
        templist = dataStr[i].split()
        point_xy[templist[1][1:-1]] = [templist[2], templist[3]]
    return point_xy


def get_line_data(dataStr, point_coor):
    end_of_file = len(dataStr)
    line_coor_start = dataStr.index("$ LINE CONNECTIVITIES\n")
    line_assign_start = dataStr.index("$ LINE ASSIGNS\n")
    # get line two ends points
    # line_data key: floor&label
    # line_data value: section x1 y1 x2 y2
    line_ends = {}
    line_data = {}
    # percentage = 1
    for i in xrange(line_coor_start + 1, end_of_file):
        # print("$:%.2f complete!" %float(percentage/(end_of_file-line_coor_start)),end = "\r")
        if dataStr[i] == "\n":
            break
        templist = dataStr[i].split()
        line_ends[templist[1][1:-1]] = [templist[3][1:-1], templist[4][1:-1]]
        # percentage += 1
    for j in xrange(line_assign_start + 1, end_of_file):
        # print("$:%.2f complete!" %float(percentage/(end_of_file-line_assign_start)),end = "\r")
        if dataStr[j] == "\n":
            break
        templist = dataStr[j].split()
        # percentage += 1
        if templist[3] == 'SECTION':
            line_data[templist[2][1:-1] + "&" + templist[1][1:-1]] = [templist[4][1:-1],
                                    point_coor[line_ends[templist[1][1:-1]][0]][0], point_coor[line_ends[templist[1][1:-1]][0]][1],
                                    point_coor[line_ends[templist[1][1:-1]][1]][0], point_coor[line_ends[templist[1][1:-1]][1]][1]]
    return line_data


def line_compare(line_data1, line_data2):
    # input points corresponding, lines_ends
    # output line cooresponding
    # note: no matter which floor
    line_compare_list = {}
    for line1_no in line_data1.keys():
        try:
            for line2_no, line2_ends in line_data2.iteritems():
                if line_data2[line2_no][1:] == line_data1[line1_no][1:] and line1_no.split('&')[0] == line2_no.split('&')[0]:
                    line_compare_list[line1_no] = [line2_no]
                    for x in line_data1[line1_no]: line_compare_list[line1_no].append(x)
                    line_compare_list[line1_no].append(line_data2[line2_no][0])
        except KeyError:
            pass
    return line_compare_list


def output_linecompare4Excel(line_compare_data):
    printStr = ["FLOOR  LABEL_base  LABEL_compare  SECTION_base  SECTION_compare  POINT_1X  POINT_1Y  POINT_2X  POINT_2Y" + "\n"]
    for key in line_compare_data.keys():
        tempstr =  str(key.split('&')[0]) + '  '
        tempstr += str(key.split('&')[1]) + '  '
        tempstr += str(line_compare_data[key][0].split('&')[1]) + '  '
        tempstr += str(line_compare_data[key][1]) + '  '
        tempstr += str(line_compare_data[key][6]) + '  '
        tempstr += str(line_compare_data[key][2]) + '  '
        tempstr += str(line_compare_data[key][3]) + '  '
        tempstr += str(line_compare_data[key][4]) + '  '
        tempstr += str(line_compare_data[key][5]) + ' \n'
        printStr.append(tempstr)
    return printStr


if __name__ == '__main__':
    dataStrs, file_names = open_files()
    print("please wait.....\n")
    pointcoor_base = get_points_data(dataStrs[0])
    linedata_base = get_line_data(dataStrs[0], pointcoor_base)
    for file_no in xrange(1, len(file_names)):
        print("Runing with model: " + file_names[file_no])
        pointcoor_com = get_points_data(dataStrs[file_no])
        linedata_com = get_line_data(dataStrs[file_no], pointcoor_com)
        line_compare_com = output_linecompare4Excel(line_compare(linedata_base, linedata_com))
        with open(file_names[0][:-4]+ "_&_" + file_names[file_no][:-4] + "_compare.txt", "w") as wf:
            for line in line_compare_com: wf.write(line)
        wf.close()
        print("Comparesion complete with " + file_names[0] + " and " + file_names[file_no])
        print("Please check result as:  " + file_names[0][:-4] + "_&_" + file_names[file_no][:-4] + "_compare.txt\n")
    print("All files deal with line element done.")
    exitprogram = raw_input("Press any key to exit")
