import os
import time

import cv2
import numpy as np
from PIL import Image

from bonch_utils import load_image, save_img, get_rescaled_cv2, create_dir
from common.dir_utils import is_dir_empty
from common.logging_sd import configure_logger
from compress import run_coder, run_decoder
from constants.constant import DIR_NAME, DIR_PATH_INPUT, DIR_PATH_OUTPUT, SIZE

logger = configure_logger(__name__)


def default_main(is_quantize=True, is_save=False, save_metrics=True, save_rescaled_out=False, debug=False):
    if is_dir_empty(DIR_PATH_INPUT):
        logger.info(f'Input dir is empty! Exiting....')
        return
    # logger.info(is_dir_empty(DIR_PATH_INPUT))
    # logger.info(os.listdir(DIR_PATH_INPUT))
    start = time.time()  ## точка отсчета времени
    logger.debug(f"compressing files for is_quantize = {str(is_quantize)}")

    if not os.path.exists(DIR_PATH_INPUT):
        os.makedirs(DIR_PATH_INPUT)
    if not os.path.exists(DIR_PATH_OUTPUT):
        os.makedirs(DIR_PATH_OUTPUT)

    count = 0
    logger.debug(f"get files in dir = {DIR_NAME}")

    for dir_name in os.listdir(DIR_PATH_INPUT):  # цикл обработки кадров
        if dir_name == '.DS_Store':
            continue

        for img_path, img_name in load_image(f"{DIR_PATH_INPUT}/{dir_name}"):
            start = time.time()

            # считывание кадра из input
            image = cv2.imread(img_path)
            count += 1
            logger.debug(f"compressing file {img_name} in dir {DIR_NAME}; count = {count};"
                         f" img size = {SIZE} max 9")

            if not os.path.exists(f"{DIR_PATH_OUTPUT}/{dir_name}_run"):
                create_dir(DIR_PATH_OUTPUT, f"{dir_name}_run")
            save_parent_dir_name = f"{dir_name}_run"

            # создание директории для сохранения сжатого изображения и резултатов метрик
            if not os.path.exists(f"{DIR_PATH_OUTPUT}/{save_parent_dir_name}/{count}_run"):
                create_dir(f"{DIR_PATH_OUTPUT}/{save_parent_dir_name}", f"{count}_run")
            save_dir_name = f"{count}_run"

            # сжатие кадра для отправления на НС
            img = get_rescaled_cv2(image, SIZE)
            if save_rescaled_out:
                save_img(img, path=f"{save_parent_dir_name}/{save_dir_name}", name_img=f"resc_{img_name}")

            # функции НС
            compress_img = run_coder(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

            # if is_save: TODO: it is code not work for old sd pipeline, but good work for sd inp pipeline
            #     print(compress_img[0].shape)
            #     print(compress_img[1].shape)
            #     print(compress_img[2].shape)
            #     image_1 = Image.fromarray(compress_img[0][0])
            #     image_1.save(f"{DIR_PATH_OUTPUT}/{save_parent_dir_name}/{save_dir_name}/image_1.png")
            #
            #     for i in range(compress_img[1].shape[0]):
            #         image_2 = Image.fromarray(compress_img[1][i])
            #         image_2.save(f"{DIR_PATH_OUTPUT}/{save_parent_dir_name}/{save_dir_name}/image_2_{i}.png")
            #     for i in range(compress_img[2].shape[0]):
            #         image_2 = Image.fromarray(compress_img[1][i])
            #         image_2.save(f"{DIR_PATH_OUTPUT}/{save_parent_dir_name}/{save_dir_name}/image_3_{i}.png")

            uncompress_img = run_decoder(compress_img)
            logger.debug(uncompress_img)
            uncompress_img = cv2.cvtColor(np.array(uncompress_img), cv2.COLOR_RGB2BGR)

            end_time = time.time() - start

            if is_save:
                save_img(uncompress_img, path=f"{save_parent_dir_name}/{save_dir_name}", name_img=img_name)

            # сохранение метрик
            if save_metrics:
                width = int(image.shape[1])
                height = int(image.shape[0])
                dim = (width, height)
                rescaled_img = cv2.resize(uncompress_img, dim, interpolation=cv2.INTER_AREA)
                # data = metrics_img(image, rescaled_img, img_path,
                #                    f"{DIR_PATH_OUTPUT}/{save_parent_dir_name}/{save_dir_name}/0_{img_name}")
                # write_metrics_in_file(f"{DIR_PATH_OUTPUT}/{save_parent_dir_name}/{save_dir_name}", data, img_name,
                #                       end_time)

        end = time.time() - start  ## собственно время работы программы
        logger.debug(f'Complete: {end}')


if __name__ == '__main__':
    logger.debug(f"aaa")
    default_main(is_quantize=True, is_save=True, save_metrics=True, save_rescaled_out=True)
