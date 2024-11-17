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
    # Reshape image to a list of pixels
    pixels = image.reshape(-1, 3)

    # Exclude black pixels (all channels are zero)
    non_black_pixels = pixels[(pixels != [0, 0, 0]).any(axis=1)]

    # Count the occurrence of each color
    color_counts = Counter(map(tuple, non_black_pixels))

    # Find the most common color
    majority_color = max(color_counts, key=color_counts.get)

    # Replace black pixels in the original image
    black_pixels_mask = (image == [0, 0, 0]).all(axis=2)
    image[black_pixels_mask] = majority_color

    # Convert back to BGR for saving/viewing with OpenCV
    return image