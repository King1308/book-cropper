import argparse
import logging
import os
import sys
from PIL import Image
import shutil
import asyncio


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="Book Cropper",
            description="Simple program to crop, rename, " \
                    "convert and structurize images",
            epilog="Want to contribute or learn more about app? " \
                    "Visit GitHub page: https://github.com/King1308/book-cropper",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-i', "--input", default="input", type=str,
            help="Folder containing input images ")

    parser.add_argument('-o', "--output", default="output", type=str,
            help="Folder to save proceed images")
    parser.add_argument('-tf', "--temp-folder", default="tmp", type=str,
            help="Temporary storage folder")

    parser.add_argument('-c', "--crop", action="store_true", default=False,
            help="Crop input images")
    parser.add_argument('-cs', "--crop-size", default="1080x1920", type=str,
            help="Crop size in WidthxHeight")
    parser.add_argument('-cp', "--crop-position", default="lt", type=str,
            help="Crop position from which counted cropping size \
            (lefttop, leftbottom, righttop, rightbottom, lt, lb, rt, rb)")

    parser.add_argument('-rt', "--rotate", default=0, type=int,
            help="Rotate proceed images. 0 - No, 1 - All, 2 - Pair, 3 - Odd")
    parser.add_argument('-j', "--convert-jpeg", action="store_true",
            default=False, help="Convert images to JPEG format")

    parser.add_argument('-r', "--rename", action="store_true", default=False,
            help="Rename output files according to the \"--rename-pattern\" value")
    parser.add_argument('-ri', "--rename-index", type=int, default=0,
            help="Rename index offset")
    parser.add_argument('-rp', "--rename-pattern", type=str, default=r"page_%s",
            help=r"Rename pattern (Use %%s to set index position, " \
                    "DO NOT add file extention)")

    parser.add_argument('-d', "--debug", action="store_true", default=False,
            help="Increase logging verbosity")
    parser.add_argument('-t', "--time-marks", default=False, action="store_true",
            help="Show time marks in logs")

    parser.add_argument('-cl', "--clean", action="store_true", default=False,
            help="Remove temporary files")

    return(parser.parse_args()) 

def configure_logging(use_time_marks: bool, is_debug: bool) -> None:
    logging_format = "%(asctime)s %(message)s" if use_time_marks else "%(message)s"
    logging_level = logging.DEBUG if is_debug else logging.INFO

    logging.basicConfig(level=logging_level, format=logging_format)
    logging.getLogger("PIL").setLevel(logging.ERROR)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

def clear_folder(folder: str) -> None:
    logging.warning(f"\nFolder \"{folder}\" contains files\n" \
            "Do you want to delete those files and continue?")
    clear_out = input("[Y/N]: ")
    if clear_out.lower() == "y":
        for f in os.listdir(folder):
            logging.debug(f"Deleting file: {f}")
            os.remove(f"{folder}/{f}")
    else:
        sys.exit(0)

def check_folders(args) -> None:
    global input_folder, output_folder, tmp_folder

    input_folder = args.input
    if not os.path.exists(input_folder):
        logging.error(f"Input folder \"{input_folder}\" does not exist!")
        sys.exit(1)
    if not os.listdir(input_folder):
        logging.error(f"Input folder \"{input_folder}\" is EMPTY!")
        sys.exit(1)


    output_folder = args.output
    if not os.path.exists(output_folder):
        logging.debug(f"Output folder \"{output_folder}\" does not exist. " \
                "Creating it")
        os.mkdir(output_folder)
    elif os.listdir(output_folder):
        clear_folder(output_folder)

    tmp_folder = args.temp_folder
    if not os.path.exists(tmp_folder):
        logging.debug(f"Temp folder \"{tmp_folder}\" does not exist. Creating it")
        os.mkdir(tmp_folder)
    elif os.listdir(tmp_folder):
        clear_folder(tmp_folder)

def crop_image(input_path: str, f: str, tmp_path: str,
        crop_size: tuple) -> None:
    with Image.open(f"{input_path}/{f}") as im:
        logging.debug(f"Cropping {f}")
        im = im.crop(crop_size)
        im.save(f"{tmp_path}/{f}")

def rotate_image(input_path: str, f: str, tmp_path: str) -> None:
    with Image.open(f"{input_path}/{f}") as im:
        logging.debug(f"Rotating {f}")
        im = im.rotate(180)
        im.save(f"{tmp_path}/{f}")

def rename_image(input_path: str, f: str, tmp_path: str, rename_index: int,
        rename_pattern: str, from_temp_folder: bool) -> None:
    f_name, f_ext = os.path.splitext(f)
    f_index = int("".join([char for char in f_name if char.isdigit()]) or 0) \
            + rename_index 
    new_f_name = str(rename_pattern % str(f_index)) + f"{f_ext}"
    logging.debug(f"Renaming \"{f}\" to \"{new_f_name}\"")
    full_input_path = f"{input_path}/{f}"
    full_output_path = f"{tmp_path}/{new_f_name}"
    if from_temp_folder:
        os.rename(full_input_path, full_output_path)
    else:
        shutil.copyfile(full_input_path, full_output_path)
 
def convert_image(input_path: str, f: str, tmp_path: str,
        from_temp_folder: bool) -> None:
    f_name, f_ext = os.path.splitext(f)
    if f_ext in ("jpg", "jpeg"):
        logging.debug(f"Can't convert {f} to jpg, because it is already JPEG")
    else:
        jpg_name = f"{f_name}.jpg"
        logging.debug(f"Converting file {f} to {jpg_name}")
        with Image.open(f"{input_path}/{f}") as im:
            jpg_im = im.convert("RGB")
            jpg_im.save(f"{tmp_path}/{jpg_name}")
        if from_temp_folder:
            os.remove(f"{input_path}/{f}")


async def crop_function(input_path: str, crop_size: str,
        crop_position: str) -> None:
    logging.info("Start cropping")
    crop_x, crop_y = map(int, crop_size.lower().split("x"))
    logging.debug(f"{crop_x = }, {crop_y = }")
    test_image_path = f"{input_path}/{os.listdir(input_path)[0]}" 
    match crop_position.lower():
        case "lt" | "lefttop":
            crop_size = (0, 0, crop_x, crop_y)
        case "lb" | "leftbottom":
            with Image.open(test_image_path) as im:
                x, y = im.size
            crop_size = (0, y-crop_y, crop_x, y)
        case "rt" | "righttop":
            with Image.open(test_image_path) as im:
                x, y = im.size
            crop_size = (x-crop_x, 0, x, crop_y)
        case "rb" | "rightbottom":
            with Image.open(test_image_path) as im:
                x, y = im.size
            crop_size = (x-crop_x, y-crop_y, x, y)
        case _:
            logging.error("Unsupportable crop position\nTry: lt, lb, rt, tb")
            sys.exit(1)
    tasks = [asyncio.to_thread(crop_image, input_path, f, tmp_folder,
            crop_size) for f in os.listdir(input_path)]
    await asyncio.gather(*tasks)
    logging.info("Cropped")

async def rotate_function(input_path: str, from_temp_folder: bool) -> None:
    logging.info("Rotating")
    match int(args.rotate):
        case 2:
            oddpair = 0
        case 3:
            oddpair = 1
        case _:
            oddpair = None
    f_list = os.listdir(input_path)
    f_list_left = []
    if oddpair is not None:
        for f in f_list: 
            if int("".join(filter(str.isdigit, f)) or 0) % 2 == oddpair:
                f_list_left.append(f)
                f_list.remove(f)
    tasks = [asyncio.to_thread(rotate_image, input_path, f, tmp_folder)
            for f in f_list]
    await asyncio.gather(*tasks)
    if not from_temp_folder:
        for f in f_list_left:
            shutil.copyfile(f"{input_path}/{f}", f"{tmp_folder}/{f}")
    logging.info("Rotated")

async def rename_function(input_path: str, from_temp_folder: bool,
        rename_index: int, rename_pattern: str) -> None:
    logging.info("Renaming")
    tasks = [asyncio.to_thread(rename_image, input_path, f, tmp_folder, rename_index,
            rename_pattern, from_temp_folder) for f in os.listdir(input_path)]
    await asyncio.gather(*tasks)
    logging.info("Renamed")

async def convert_function(input_path: str, from_temp_folder: bool) -> None:
    logging.info("Converting to jpeg")
    tasks = [asyncio.to_thread(convert_image, input_path, f, tmp_folder,
            from_temp_folder) for f in os.listdir(input_path)]
    await asyncio.gather(*tasks)
    logging.info("Converted")

def main(args) -> None:
    from_temp_folder = False
    if args.crop:
        input_path = tmp_folder if from_temp_folder else input_folder
        asyncio.run(crop_function(input_path, args.crop_size, args.crop_position))
        from_temp_folder = True

    if args.rotate:
        input_path = tmp_folder if from_temp_folder else input_folder
        asyncio.run(rotate_function(input_path, from_temp_folder))
        from_temp_folder = True

    if args.rename:
        input_path = tmp_folder if from_temp_folder else input_folder
        asyncio.run(rename_function(input_path, from_temp_folder,
                args.rename_index, args.rename_pattern))
        from_temp_folder = True

    if args.convert_jpeg:
        input_path = tmp_folder if from_temp_folder else input_folder
        asyncio.run(convert_function(input_path, from_temp_folder))
        from_temp_folder = True
    
    if args.clean and from_temp_folder:
        logging.info(f"Renaming temp folder:\"{tmp_folder}\" " \
                f"to output folder: \"{output_folder}\"")
        os.rmdir(output_folder)
        os.rename(tmp_folder, output_folder)
        logging.info("Done")
    elif from_temp_folder:
        logging.info(f"Copying images to output folder: \"{output_folder}\"")
        for f in os.listdir(tmp_folder):
            logging.debug(f"Copying file {f}")
            shutil.copyfile(f"{tmp_folder}/{f}", f"{output_folder}/{f}")
        logging.info("Moving done")
    else:
        logging.info(f"Copying images to output folder: \"{output_folder}\"")
        logging.warning("NO changes were applied to source images\n"+
                "Are you sure written arguments are right?")
        os.rmdir(tmp_folder)
        for f in os.listdir(input_folder):
            logging.debug(f"Copying file {f}")
            shutil.copyfile(f"{input_folder}/{f}", f"{output_folder}/{f}")
        logging.info("Moving done")
  
if __name__ == "__main__":
    args = parse_arguments()
    configure_logging(args.time_marks, args.debug)
    check_folders(args)
    main(args)
