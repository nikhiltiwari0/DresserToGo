import sys
import numpy as np
from functools import reduce
from albumentations import resize
from collections import Counter
import cv2

def load_img(image):
    return cv2.imread(image, cv2.IMREAD_COLOR)

def stitch_images(images):
    img_list = list(map(load_img, images))
    max_width = reduce(lambda acc, arr: max(acc, arr.shape[1]), img_list, 0)
    img_list = map(lambda x: resize(x, target_shape=(x.shape[0], max_width), interpolation=cv2.INTER_CUBIC), img_list)
    return np.vstack(list(img_list))

def replace_black_with_majority_color(image):
    pixels = image.reshape(-1, 3)
    non_black_pixels = pixels[(pixels != [0, 0, 0]).any(axis=1)]
    color_counts = Counter(map(tuple, non_black_pixels))
    majority_color = max(color_counts, key=color_counts.get)
    black_pixels_mask = (image == [0, 0, 0]).all(axis=2)
    image[black_pixels_mask] = majority_color
    return image

def create_stitched_images(files, output_path):
    stitched_image = stitch_images(files)
    stitched_image = replace_black_with_majority_color(stitched_image)
    cv2.imwrite(output_path, stitched_image)

if __name__ == "__main__":
    input_files = sys.argv[1:-1]
    output_file = sys.argv[-1]
    create_stitched_images(input_files, output_file)
