# -*- coding: utf-8 -*-
import copy

import pydicom
import numpy as np
import cv2
import math
import os
import threading
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor

thread_num = 3
slice_thread = []


def rotate(ps, m):
    pts = np.float32(ps).reshape([-1, 2])  # 要映射的点
    pts = np.hstack([pts, np.ones([len(pts), 1])]).T
    target_point = np.dot(m, pts)
    target_point = [[target_point[0][x], target_point[1][x]] for x in range(len(target_point[0]))]
    return target_point


def multiProcessSlice(input_path, txt_path, save_path):
    global thread_num
    global slice_thread
    txt_list = []
    for line in open(txt_path):
        try:
            line = line.rstrip("\n")
            coordinate_arr = line.split(",")
            coordinate_arr = list(map(int, coordinate_arr))
            txt_list.append(coordinate_arr)
        except Exception as e:
            print("Error file:" + txt_path)
            print("Error line:" + line)
            print(e)
            return
    txt_num = len(txt_list)
    thread_d_num = int(txt_num / thread_num)
    for i in range(thread_d_num):
        txt_t = txt_list[i * thread_num:(i + 1) * thread_num]
        t = threading.Thread(target=multiProcessCut, args=(input_path, txt_t, save_path))
        slice_thread.append(t)
        t.start()
    if txt_num % thread_num != 0:
        t_p = txt_list[thread_num * thread_d_num:txt_num]
        t_r = threading.Thread(target=multiProcessCut, args=(input_path, t_p, save_path))
        slice_thread.append(t_r)
        t_r.start()
    return slice_thread


def multiProcessSlicePool(input_path, txt_path, save_path):
    global thread_num
    thread_args = []
    txt_list = []
    for line in open(txt_path):
        try:
            if line in ['\n', '\r\n']:
                continue
            line = line.rstrip("\n")
            if line.strip() == "":
                continue
            coordinate_arr = line.split(",")
            coordinate_arr = list(map(int, coordinate_arr))
            txt_list.append(coordinate_arr)
        except Exception as e:
            print("Error file:" + txt_path)
            print("Error line:" + line)
            print(e)
            return
    txt_num = len(txt_list)
    thread_d_num = int(txt_num / thread_num)
    for i in range(thread_d_num):
        txt_t = txt_list[i * thread_num:(i + 1) * thread_num]
        tup_tmp = (input_path, txt_t, save_path)
        thread_args.append(tup_tmp)
    if txt_num % thread_num != 0:
        t_p = txt_list[thread_num * thread_d_num:txt_num]
        tup_tmp = (input_path, t_p, save_path)
        thread_args.append(tup_tmp)
    with ThreadPoolExecutor(max_workers=thread_num) as pool:
        results = pool.map(multiProcessCutZip, thread_args)
        for r in results:
            print(r)


def multiProcessCutZip(args):
    multiProcessCut(args[0], args[1], args[2])


def multiProcessCut(input_path, txt_list, save_path):
    # slice height
    fixedH = 192
    fixedT = 192
    order_str = ""
    save_dcm_t_list = []
    save_short_dcm_t_list = []
    save_path_list = []
    save_path_short_list = []
    order_str_list = []
    lenth_txt = len(txt_list)
    dcm_d_list = []
    del_arr = []
    for i_t in range(lenth_txt):
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        try:
            coordinate_arr = txt_list[i_t]
            # Cut two parts, one 4cm and one 6cm,
            save_six_slice = os.path.join(save_path, "sixCm")
            save_four_slice = os.path.join(save_path, "fourCm")
            this_save_file = save_six_slice + os.sep + str(coordinate_arr[10]) + "_" + str(coordinate_arr[12]) + os.sep
            this_save_file_short = save_four_slice + os.sep + str(coordinate_arr[10]) + "_" + str(
                coordinate_arr[12]) + os.sep
            # calculate the slope and rotate the slice to the top
            if (coordinate_arr[2] - coordinate_arr[0]) == 0:
                jiao = math.degrees(math.atan(0))
            else:
                jiao = math.degrees(
                    math.atan((coordinate_arr[3] - coordinate_arr[1]) / (coordinate_arr[2] - coordinate_arr[0])))
            print("jjj:" + str(jiao))
            h, w = 640, 640
            # Rotate ,Get the rotated rotation matrix
            M = cv2.getRotationMatrix2D((w * 0.5, h * 0.5), jiao, 1)
            # two middle point
            out_points = rotate([[coordinate_arr[4], coordinate_arr[5]], [coordinate_arr[6], coordinate_arr[7]]], M)
            x1 = int(out_points[0][0])
            y1 = int(out_points[0][1])
            y2 = math.ceil(out_points[1][1])
            alti = coordinate_arr[9] - coordinate_arr[8]
            a_low_h = coordinate_arr[8]
            a_high_h = coordinate_arr[9]
            f_low_h = a_low_h
            f_high_h = a_high_h
            f_y2 = y2
            thickness = y2 - y1 + 1
            if thickness < fixedT:
                f_y2 = y2 + fixedT - thickness
            else:
                y1 = y1 - fixedT + thickness
            if alti < fixedH:
                # distinguish between the upper and lower jaws
                if coordinate_arr[10] == 1:  # upper jaws
                    f_high_h = a_high_h + fixedH - alti
                    if f_high_h > 419:
                        f_high_h = 419
                        f_low_h = 419 - fixedH
                else:
                    f_low_h = a_low_h - fixedH + alti
                    if f_low_h < 0:
                        f_low_h = 0
                        f_high_h = fixedH
            else:
                a_low_h = a_low_h - fixedH + alti
                f_low_h = a_low_h
            files_dcm_arr = []
            files_dcm_arr_short = []
            tmp_save_path_list = []
            dcm_list = []
            for k in range(f_low_h, f_high_h):
                path = input_path + '{:0>4}'.format(str(k)) + '.dcm'
                # the serial number of the newly generated file
                index = k - f_low_h
                order_str += 'Slice_' + '{:0>4}'.format(str(index)) + '.dcm\n'
                tmp_save_path = this_save_file + 'Slice_' + '{:0>4}'.format(str(index)) + '.dcm'
                dcm = pydicom.read_file(path)
                dcm_list.append(dcm)
                img_num = np.array(dcm.pixel_array, dtype=np.int16)
                res_img = cv2.warpAffine(img_num, M, (w, h))
                new_part = np.empty([fixedT, 240], dtype=np.int16)
                new_part_short = np.empty([fixedT, 160], dtype=np.int16)
                if a_low_h <= k <= a_high_h:
                    for i in range(w):
                        if y1 <= i <= y2:
                            new_part[i - y1][:] = res_img[i][x1 - 120:x1 + 120]
                            new_part_short[i - y1][:] = res_img[i][x1 - 80:x1 + 80]
                        elif y1 <= i <= f_y2 and i > y2:
                            new_part[i - y1][:] = -1000
                            new_part_short[i - y1][:] = -1000
                else:
                    new_part[:, :] = -1000
                    new_part_short[:, :] = -1000
                tmp_save_path_list.append(tmp_save_path)
                files_dcm_arr.append(deepcopy(new_part))
                files_dcm_arr_short.append(deepcopy(new_part_short))
            if coordinate_arr[10] == 1:
                intD = len(files_dcm_arr)
                tmp = copy.copy(files_dcm_arr)
                tmp_short = copy.copy(files_dcm_arr_short)
                for k in range(intD):
                    files_dcm_arr[k] = tmp[intD - k - 1]
                    files_dcm_arr_short[k] = tmp_short[intD - k - 1]
            dcm_d_list.append(dcm_list)
            save_dcm_t_list.append(files_dcm_arr)
            save_short_dcm_t_list.append(files_dcm_arr_short)
            save_path_list.append(this_save_file)
            save_path_short_list.append(this_save_file_short)
            order_str_list.append(order_str)
        except Exception as e:
            print("----------------------" + save_path)
            print("----------------------" + str(coordinate_arr))
            print(e)
            del_arr.append(i_t)
            continue
    for i in range(len(del_arr)):
        del txt_list[del_arr[i]]
    if len(dcm_d_list) != len(txt_list):
        return
    for i in range(len(txt_list)):
        dcm_list = dcm_d_list[i]
        files_dcm_arr = save_dcm_t_list[i]
        files_dcm_arr_short = save_short_dcm_t_list[i]
        files_dcm_path = save_path_list[i]
        file_dcm_path_short = save_path_short_list[i]
        creat_dir(files_dcm_path)
        creat_dir(file_dcm_path_short)
        order_str = order_str_list[i]
        for k in range(len(files_dcm_arr)):
            dcm = dcm_list[k]
            dcm.PixelData = files_dcm_arr[k].tobytes()
            dcm.Rows, dcm.Columns = files_dcm_arr[k].shape
            dcm_path = files_dcm_path + 'Slice_' + '{:0>4}'.format(str(k)) + '.dcm'
            dcm.save_as(dcm_path)
            dcm.PixelData = files_dcm_arr_short[k].tobytes()
            dcm.Rows, dcm.Columns = files_dcm_arr_short[k].shape
            dcm_short_path = file_dcm_path_short + 'Slice_' + '{:0>4}'.format(str(k)) + '.dcm'
            dcm.save_as(dcm_short_path)
        f = open(files_dcm_path + 'slice.index', 'w')
        f.write(order_str)
        f.close()
        f = open(file_dcm_path_short + 'slice.index', 'w')
        f.write(order_str)
        f.close()


def creat_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
