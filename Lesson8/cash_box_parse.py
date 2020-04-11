
import shutil
import os
from pathlib import Path
import PyPDF2
from PyPDF2.utils import PdfReadError

from PIL import Image
import pytesseract
import time
from pymongo import MongoClient
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR/tesseract.exe'


image_folder_path = r'C:\data_for_parse\Image\Images'
unrecognized_image_folder_path = r'C:\data_for_parse\unrecognized'
path = r'C:\data_for_parse\data'


def get_files_location (path):
    folders = []
    file_names = []
    for i in os.walk(path):
        folders.append(i)
    for address, dirs, files in folders:
        for file in files:
            file_name = os.path.join(address, file)
            file_names.append((file_name, file))
    return file_names


def extract_pdf_image(pdf_path):


    try:
        pdf_file = PyPDF2.PdfFileReader(open(pdf_path, 'rb'), strict=False)
    except PdfReadError as e:
        print(e)
        return None
    except FileNotFoundError as e:
        print(e)
        return None
    result=[]
    for page_num in range(0, pdf_file.getNumPages()):
        page = pdf_file.getPage(page_num)
        page_obj = page['/Resources']['/XObject'].getObject()
        key = list(page_obj)[0]
        if page_obj[key].get('/Subtype') == '/Image':
            size =(page_obj[key]['/Width'],page_obj[key]['/Height'])
            data = page_obj[key]._data
            mode = 'RGB' if page_obj[key]['/ColorSpace'] == '/DeviceRGB' else 'p'
            decoder = page_obj[key]['/Filter']
            if decoder =='/DCTDecode':
                file_type = 'jpg'
            elif decoder == '/FlateDecode':
                file_type = 'png'
            elif decoder == '/JPXDecode':
                file_type = 'jp2'
            else:
                file_type = 'bmp'

            result_strict = {
                'page': page_num,
                'size': size,
                'data': data,
                'mode': mode,
                'file_type': file_type
            }
            result.append(result_strict)

    return result


def save_pdf_image(file_name, f_path, *pdf_strict):
    file_paths = []
    for itm in pdf_strict:
        name = f'{file_name}_#_{itm["page"]}.{itm["file_type"]}'
        file_path = os.path.join(f_path, name)

        with open(file_path, 'wb') as image:
            image.write(itm['data'])
        file_paths.append((file_path, name))
    return file_paths


def extract_number(file_path):
    numbers =[]
    img_obj = Image.open(file_path[0])
    text = pytesseract.image_to_string(img_obj, "rus")

    pattern = 'заводской'
    for idx, line in enumerate(text.split('\n')):

        if line.lower().find(pattern)+1:
            text_en = pytesseract.image_to_string(img_obj, "eng")
            number = text_en.split('\n')[idx].split(' ')[-1]
            numbers.append((number, file_path[0], file_path[1]))
    if len(numbers) == 0:
        numbers.append(('', file_path[0], file_path[1]))
    return numbers


def get_scan_data(number, file_name, pdf_file_path):
    item = {"equipment_serial_number": number[0][0],
            "file_name": file_name,
            "file_path": pdf_file_path,
            "image_path": number[0][1],
            "image_name":number[0][2]
            }
    return item


def save_db(item):
    if item['equipment_serial_number'] in [None, '-', ' ', '—', ';', ''] or len(item['equipment_serial_number']) < 2:
        shutil.copyfile(item['image_path'], os.path.join(unrecognized_image_folder_path, item['image_name']))
        collection2.insert_one(item)
    else:
        collection1.insert_one(item)


if __name__ =='__main__':
    client = MongoClient('mongodb://localhost:27017/')
    db = client['scan_parse']
    collection1 = db['recognized']
    collection2 = db['unrecognized']


    file_names = get_files_location(path)
    for file in file_names:
        file_suffix = Path(file[0]).suffix
        if file_suffix == '.pdf':
            pdf_file_path = file[0]
            file_name = file[1]
            a=extract_pdf_image(pdf_file_path)
            if a:
                b=save_pdf_image(file_name, image_folder_path, *a)
                c=[extract_number(itm) for itm in b]
                for number in c:
                    item= get_scan_data(number, file_name, pdf_file_path)
                    save_db(item)
            else:
                item = {"equipment_serial_number": None,
                        "file_name": file[1],
                        "file_path": file[0],
                        "image_path": file[0],
                        "image_name": file[1]
                        }
                save_db(item)

        elif file_suffix == '.jpg':
            c=extract_number(file)
            item = get_scan_data(c, file[1], file[0])
            save_db(item)

        else:
            item = {"equipment_serial_number": None,
                    "file_name": file[1],
                    "file_path": file[0],
                    "image_path": file[0],
                    "image_name": file[1]
                    }
            save_db(item)

    print(1)