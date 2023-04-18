# -*- coding: utf-8 -*-
# @Time    : 2022/3/13 16:48
# @Author  : liuwenjing
#
import os.path

from PIL import Image

# source path
image_root_path = r"/home/lwj/file_data/testBox/imageDRR/test"
# save path
save_root_path = r"/home/lwj/file_data/testBox/imageDRR-s/test"


def cutImage(filePath):
    if os.path.exists(filePath):
        for path in os.listdir(filePath):
            # DE_
            image_path = os.path.join(image_root_path, path + os.sep + "sixCm")
            save_path = os.path.join(save_root_path, path + os.sep + "sixCm")
            for pp_path in os.listdir(image_path):
                file_path = os.path.join(image_path, pp_path)
                save_image_path = os.path.join(save_path, pp_path)
                for image in os.listdir(file_path):
                    if image.endswith(".tif"):
                        img = Image.open(os.path.join(file_path, image))
                        fileCreat(save_image_path)
                        save_file = os.path.join(save_image_path, image)
                        w, h = img.size
                        start = int((w - 160) / 2)
                        box = (start, 0, start + 160, h)
                        imgCenter = img.crop(box)
                        imgCenter.save(save_file)


def fileCreat(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)


if __name__ == '__main__':
    cutImage(image_root_path)
