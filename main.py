import os
import shutil
import zipfile
from ebooklib import epub
import tkinter as tk
from tkinter import filedialog
from xml.dom.minidom import parse
import xml.dom.minidom

def get_epub_title(epub_path):
    book = epub.read_epub(epub_path)
    title = book.get_metadata('DC', 'title')[0][0]
    return title

def get_image_path_from_html(html):
    DOMTree = xml.dom.minidom.parseString(html)
    data = DOMTree.documentElement
    for img in data.getElementsByTagName('img'):
        return img.getAttribute('src')[3:]

def extract_img_from_epub(epub_path, extract_dir):
    book = zipfile.ZipFile(epub_path)
    book_structure = book.read('vol.opf') 
    DOMTree = xml.dom.minidom.parseString(book_structure)
    data = DOMTree.documentElement

    try:
        img_dir = ""
        for item in data.getElementsByTagName('item'):
            if not item.hasAttribute('id'):
                continue
            id = item.getAttribute('id')
            if not id.startswith('Page'):
                continue
            page = id[5:]
            if page == 'createby':
                continue
            if page == 'cover':
                page = '0'
            if not item.hasAttribute('href'):
                continue
            html = book.read(item.getAttribute('href'))
            img_path = get_image_path_from_html(html)
            ext = img_path.split('.')[-1]
            if ext not in ('jpg', 'png'):
                print('不支持的图片格式: ' + ext)
                continue
            img_path = book.extract(img_path, extract_dir)
            img_dir = os.path.split(img_path)[0]
            img_name = page + '.' + ext
            os.rename(img_path, os.path.join(img_dir, img_name))
        book.close()
        return True, img_dir
    except:
        return False, ""

def handle_epub(book_path, output_dir):
    book_title = get_epub_title(book_path)
    tmp_dir = os.path.join(output_dir, 'tmp')
    is_done, img_dir = extract_img_from_epub(book_path, os.path.join(tmp_dir, book_title))
    if not is_done:
        return
    output_path = os.path.join(output_dir, book_title + '.zip')
    if os.path.exists(output_path):
        print('warning: {} exists'.format(output_path))
    else:
        zip_images(img_dir, output_path)


def zip_images(img_dir, output_path):
    zip = zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED)
    imgs = os.listdir(img_dir)
    for img in imgs:
        img_path = os.path.join(img_dir, img)
        zip.write(img_path, img)
    zip.close()
    print('{} 创建成功'.format(output_path))


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()

    input_dir = filedialog.askdirectory()
    output_dir = input_dir
    if input_dir == "":
        exit()
    
    book_names = os.listdir(input_dir)
    for book_name in book_names:
        book_path = os.path.join(input_dir, book_name)
        if book_name.endswith('.epub'):
            handle_epub(book_path, output_dir)

    shutil.rmtree(os.path.join(output_dir, 'tmp'))
