import os
import time

import cv2
import numpy as np
from metrics import metrics
from common.logging_sd import configure_logger
from PIL import Image
from numpy import ndarray
import logging


logger = configure_logger(__name__)


SCALED_SIZE_DEFAULT = (1200, 1200)
INPUT_DATA_PATH = "data/input"
OUTPUT_DATA_PATH = "data/output"


def create_dir(new_dir_name: str, index: str = ""):
    try:
        os.makedirs(f"{OUTPUT_DATA_PATH}/{new_dir_name}/")
    except FileNotFoundError:
        logger.error(f"failed to create directory {OUTPUT_DATA_PATH}/{new_dir_name}", exc_info=True)



def load_image(path: str = INPUT_DATA_PATH):
    try:    
        for filename in os.listdir(path):
            if filename.endswith('.png') or filename.endswith('.jpg'):
                f = os.path.join(path, filename)
                logger.debug(f"{f}, {filename}")
                if os.path.isfile(f):
                    yield f, filename
        logger.debug(f"Frame search success in {path} directory")
    except FileNotFoundError:
        logger.error(f"Error while reading image from directory {path}, catalog not found", exc_info=True)



def save_img(img, path: str, name_img: str = 'default'):
    if os.path.exists(f'{OUTPUT_DATA_PATH}/{path}'):
        try:
            cv2.imwrite(f'{OUTPUT_DATA_PATH}/{path}/0_{name_img}', img)
            logger.debug(f"The compressed image {name_img} was "
                         f"saved successfully in the directory {OUTPUT_DATA_PATH}/{path}")
        except Exception:
            logger.error(f"Failed to save images {name_img} to the directory {OUTPUT_DATA_PATH}/{path}, "
                          f"file is corrupted", exc_info=True)
    else:
        logger.error(f"Failed to save images {name_img} to the directory {OUTPUT_DATA_PATH}/{path}, catalog not found", exc_info=True)


def get_rescaled_cv2(image, scaled_size: tuple = (512, 512)):
    try:
        res = cv2.resize(image, scaled_size)
        logger.debug(f'file compression in the directory successfully')
        return res
    except Exception:
        logger.error(f'file compression in the directory failed', exc_info=True)


def write_metrics_in_file(path: str, data: tuple, image_name: str, time: time):
    if os.path.exists(path):
        data_str = f"image_name: {image_name}\n" \
                   f"ssim_data = {data[0]}\n" \
                   f"pirson_data = {data[1]}\n" \
                   f"cosine_similarity = {data[2]}\n" \
                   f"mse = {data[3]}\n" \
                   f"hamming_distance = {data[4]}\n"\
                   f"frame_compression_time = {time}\n"
        with open(f"{path}/metrics.txt", mode='w') as f:
            f.write(data_str)
    else:
        logger.error(f"Failed to save metrics to the directory {path}, catalog not found", exc_info=True)


def metrics_img(image, denoised_img) -> tuple:
    try:
        img1 = (np.array(image).ravel())
        img2 = (np.array(denoised_img).ravel())
        ssim_data = metrics.ssim(image, denoised_img)
        pirson_data = metrics.cor_pirson(img1, img2)
        cosine_similarity = metrics.cosine_similarity_metric(img1, img2)
        mse = metrics.mse_metric(image, denoised_img)
        hamming_distance = metrics.hamming_distance_metric(image, denoised_img)
        logger.debug(f'Collecting image metrics successfully')
        result_metrics: tuple = (ssim_data, pirson_data, cosine_similarity, mse, hamming_distance)
        return result_metrics
    except Exception:
        logger.error(f'Failed to collect image metrics', exc_info=True)

