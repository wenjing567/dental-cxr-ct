import os
import os.path
import image_files
import threading
from concurrent.futures import ThreadPoolExecutor

# number of threads
thread_num = 3

# label file path
txt_path = r"/home/lwj/file_txt"

# CT file path
ct_files_path = r"/home/huangyunyou/EranCTData"

# tif file save path
tif_save_path = r"imageDRR"

# slice save path
new_path = r"/home/lwj/file_slice"

# overwrite the previously generated slice,default is True
replaceSlice = True

# work_path
work_path = r"/home/lwj/file_data/testBox"

# nii file save root  path
repo_dir = r"/home/lwj/al-ct-x-multi/data"

# nii save path
nii_save_path = r"boxRes"


# Group tagged files according to the number of threads
def multi_process_label_files(loacl_txt_path, local_new_path):
    global thread_num
    files = os.listdir(loacl_txt_path)
    files_list = []
    thread_args = []
    for i in range(len(files)):
        files_list.append(files[i])
    files_num = len(files)
    # Calculate how many markup files each thread needs to process
    thread_files = int(files_num / thread_num)
    for i in range(thread_files):
        thread_param = files[i * thread_num:i * thread_num + thread_num]
        thread_args.append((loacl_txt_path, local_new_path, thread_param))
    # the rest are divided into a group
    if files_num % thread_num != 0:
        t_p = files[thread_num * thread_files:files_num]
        thread_args.append((loacl_txt_path, local_new_path, t_p))
    with ThreadPoolExecutor(max_workers=thread_num) as pool:
        results = pool.map(generate_tile_file_zip, thread_args)
        for r in results:
            continue


def generate_tile_file_zip(thread_args):
    generate_tile_file(thread_args[0], thread_args[1], thread_args[2])


# Generate a new slice file based on the markup file and the original file
def generate_tile_file(local_txt_path, local_new_path, files):
    for i in range(len(files)):
        str = files[i]
        prefix = str.split(".")
        txt_d_path = os.path.join(local_txt_path, str)
        data_path = os.path.join(ct_files_path, prefix[0])
        if not os.path.exists(data_path):
            continue
        dcm_files = get_file_path(data_path)
        dcm_files = dcm_files + os.sep + "Slice_"
        save_path = local_new_path + os.sep + prefix[0]
        if not replaceSlice:
            if os.path.exists(save_path):
                continue
        if not os.path.exists(local_new_path):
            os.mkdir(local_new_path)
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        image_files.multiProcessSlicePool(dcm_files, txt_d_path, save_path)


# Get the path of the upper level directory where the file is located
def get_file_path(root_path):
    dir_or_files = os.listdir(root_path)
    for dir_file in dir_or_files:
        dir_file_path = os.path.join(root_path, dir_file)
        pre_root_path = root_path
        if os.path.isdir(dir_file_path):
            return get_file_path(dir_file_path)
        else:
            return pre_root_path


# Convert slice files to nii files
def multiProcessNiiPool(local_nii_save_path, slice_path):
    global thread_num
    file_num = len(os.listdir(slice_path))
    thread_d_num = int(file_num / thread_num)
    thread_args = []
    for i in range(thread_d_num):
        thread_args.append((local_nii_save_path, slice_path, i * thread_num, (i + 1) * thread_num))
    if file_num % thread_num != 0:
        thread_args.append((local_nii_save_path, slice_path, thread_d_num * thread_num, file_num))
    with ThreadPoolExecutor(max_workers=thread_num) as pool:
        results = pool.map(multiProcessGenetionNiiZip, thread_args)
        for r in results:
            print(r)


def multiProcessGenetionNiiZip(args):
    multiProcessGenetionNii(args[0], args[1], args[2], args[3])


def multiProcessGenetionNii(local_nii_save_path, slice_path, start, end):
    print("./data/extractNiftiData.sh %s %d %d %s %s %s" % (
        slice_path, start, end - 1, work_path, local_nii_save_path, repo_dir))
    os.system("./data/extractNiftiData.sh %s %d %d %s %s %s" % (
        slice_path, start, end - 1, work_path, local_nii_save_path, repo_dir))


# Convert nii files to tif files
def multiProcessHandTifPool(src_path, dst_path):
    global thread_num
    file_num = len(os.listdir(os.path.join(work_path, src_path)))
    thread_d_num = int(file_num / thread_num)
    thread_args = []
    for i in range(thread_d_num):
        thread_args.append((src_path, dst_path, i * thread_num, (i + 1) * thread_num))
    if file_num % thread_num != 0:
        thread_args.append((src_path, dst_path, thread_d_num * thread_num, file_num))
    with ThreadPoolExecutor(max_workers=thread_num) as pool:
        results = pool.map(mutiProcessGenetionTifZip, thread_args)
        for r in results:
            print(r)


def mutiProcessGenetionTifZip(args):
    mutiProcessGenetionTif(args[0], args[1], args[2], args[3])


def mutiProcessGenetionTif(src_path, dst_path, start, end):
    print("./data/runDrive.sh %d %d %s %s %s" % (start, end - 1, work_path, src_path, dst_path))
    os.system("./data/runDrive.sh %d %d %s %s %s" % (start, end - 1, work_path, src_path, dst_path))


def main():
    multi_process_label_files(txt_path,new_path)
    multiProcessNiiPool(nii_save_path,new_path)
    multiProcessHandTifPool(nii_save_path,tif_save_path)


if __name__ == '__main__':
    main()
