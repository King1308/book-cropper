# Book Cropper

Book Cropper is a command-line tool designed to crop, rename, convert, and organize images efficiently. It is highly configurable and user-friendly, making it ideal for processing batches of images for digital books or other structured documents.

## Features

- **Image Cropping**: Crop images to a specified size and position.
- **Rotation**: Rotate images based on user-defined criteria.
- **Renaming**: Rename images using customizable patterns.
- **Conversion**: Convert images to JPEG format.

## Requirements

- Python 3.10 or later
- Dependencies:
- `Pillow` (for image processing)
- `asyncio` (for asynchronous operations)

Install the required libraries using pip:

```bash
pip install Pillow
```

## Installation

Clone the repository:

```bash
git clone https://github.com/King1308/book-cropper.git
cd book-cropper
```

## Building the Project

If you wish to create a standalone executable for the Book Cropper tool, you can use the `book_cropper.spec` file with **PyInstaller**. Follow the steps below:

### Prerequisites

- Install **PyInstaller**:

```bash
pip install pyinstaller
```

### Building the Executable

1. Clone the repository and navigate to the project directory:
```bash
git clone https://github.com/King1308/book-cropper.git
cd book-cropper
```

2. Use PyInstaller with the provided `.spec` file to build the executable:
```bash
pyinstaller book_cropper.spec
```

3. The executable will be located in the `dist/` directory after the build process completes.

### Running the Executable

After building, you can use the executable to process images without needing a Python runtime. For example:

```bash
book_cropper.exe -i input -o output -c -r
```


### Downloading the Executable

You can also skip building the executable yourself and directly download the precompiled version from the [Releases Page](https://github.com/King1308/book-cropper/releases).

1. Navigate to the [Releases Page](https://github.com/King1308/book-cropper/releases).
2. Download the latest version of `book_cropper.exe`.
3. Run the executable from your terminal or file explorer.



## Usage

Run the script with various options to process your images:

```bash
python book_cropper.py [OPTIONS]
```

### Options

| Option                | Description                                                                                          | Default Value         |
|-----------------------|------------------------------------------------------------------------------------------------------|-----------------------|
| `-i`, `--input`       | Folder containing input images.                                                                      | `input`              |
| `-o`, `--output`      | Folder to save processed images.                                                                     | `output`             |
| `-tf`, `--temp-folder`| Temporary storage folder.                                                                            | `tmp`                |
| `-c`, `--crop`        | Crop input images.                                                                                   | `False`              |
| `-cs`, `--crop-size`  | Crop size in `WidthxHeight` format.                                                                  | `1080x1920`          |
| `-cp`, `--crop-position`| Crop position (e.g., `lt`, `lb`, `rt`, `rb`).                                                      | `lt`                 |
| `-rt`, `--rotate`     | Rotate images (`0`: No, `1`: All, `2`: Even, `3`: Odd).                                              | `0`                  |
| `-j`, `--convert-jpeg`| Convert images to JPEG format.                                                                       | `False`              |
| `-r`, `--rename`      | Rename output files according to the specified pattern.                                              | `False`              |
| `-ri`, `--rename-index`| Rename index offset.                                                                                | `0`                  |
| `-rp`, `--rename-pattern`| Rename pattern (e.g., `page_%s`).                                                                  | `page_%s`            |
| `-d`, `--debug`       | Enable debug logging.                                                                                | `False`              |
| `-t`, `--time-marks`  | Show time marks in logs.                                                                             | `False`              |
| `-cl`, `--clean`      | Remove temporary files after processing.                                                             | `False`              |

### Example

Crop images from the `input` folder, rotate, rename them, convert to jpg, and save them in the `output` folder:

```bash
python book_cropper.py -i input -o output -c -cs 1200x1600 -cp rt -r -ri -1 -rp "image_%s" -j -t -cl
```

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please fork the repository and submit a pull request.
