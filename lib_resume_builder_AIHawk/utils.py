import os
import re
import time
import traceback
import datetime

import pdfkit
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from langchain_core.messages import AIMessage, AIMessageChunk
from lib_resume_builder_AIHawk.config import GlobalConfig
from lib_resume_builder_AIHawk.asset_manager import ChunkManager

global_config = GlobalConfig()
def read_chunk(fn, path='', ext='chunk', enc='utf-8', **kwargs) -> str:
    # first check if chunk file exists
    #
    # chunk_fname = find_valid_path(file_name=fn, ext=ext,search_path=kwargs.get('search_path'), base_path=global_config.lib_path)
    #
    # if not chunk_fname:
    #     raise FileNotFoundError()

    chunk = ChunkManager().load_chunk(fn, ext)
    if not chunk:
        raise FileNotFoundError(f'Failed to load chunk {fn}')

    #remove comments
    chunk = re.sub(r'<!--.*?-->', '', chunk, flags=re.DOTALL)
    if chunk:
        if kwargs:
            return chunk.format(**kwargs)
        else:
            return chunk

    return None


def find_valid_path(file_name:str, ext, search_path:list=None, base_path = os.path.dirname(os.path.relpath(__file__))):
    fn_ext = f'{file_name}.{ext}'
    if os.path.isfile(file_name): return file_name
    if os.path.isfile(fn_ext): return fn_ext

    p_ = []
    path = [base_path] if isinstance(base_path, str) else base_path
    if search_path: path.extend(search_path)
    for p in path:
        p_.append(p)
        if os.path.isfile(os.path.join(*p_, file_name)): return os.path.join(*p_, file_name)
        if os.path.isfile(os.path.join(*p_, fn_ext)): return os.path.join(*p_, fn_ext)
    print(f'WARNING: {file_name} is not found', "yellow")
    return None
def is_valid_path(file_name:str, ext, search_path:list=None, base_path = os.path.dirname(os.path.relpath(__file__))):
    return True if find_valid_path(file_name, ext, search_path, base_path) else False



def list_of_strings_parser(ai_message: AIMessage):
    if ai_message and ai_message.content:
        return [x for x in ai_message.content.split('\n') if x]
    return []

def custom_json_serializer(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()  # Convert datetime to ISO string
    raise TypeError(f"Type {type(obj)} not serializable")



def get_dict_values_from_files(directory_path: str = '',
                               allowed_pattern=r'^(?![_\.]{1,2})[a-zA-Z0-9_-]+(?!\.py$)(\.[a-zA-Z0-9]+)?$'):
    d = {}
    if not os.path.exists(directory_path):
        print(f'Unable to return dict values. Dir {directory_path} does not exist')
        return d
    try:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                # Split the file name and extension
                file_name_without_ext, file_ext = os.path.splitext(file)
                if bool(re.match(allowed_pattern, file)):
                    with open(file, mode='r', encoding='utf-8') as f:
                        content = f.read()
                        d[file_name_without_ext] = content
    except Exception as e:
        print(f'Exception while reading dir {directory_path}. Error: {e}')
    return d

def get_content(file:str, dir:str=''):
    fpath = file
    content = ''
    try:
        if dir is not None and len(dir)>0:
            fpath = os.path.join(dir, file)
        if os.path.exists(fpath) and os.path.isfile(fpath):
            with open(fpath, mode='r', encoding='utf-8') as f:
                content = f.read()
        else:
            print(f'Unable to read content of a a file {fpath}. Error: "File does not exist"')
    except Exception as e:
        print(f'Exception while reading content of a a file {fpath}. Error: {e}')
    return content

def create_driver_selenium():
    options = get_chrome_browser_options()  # Usa il metodo corretto per ottenere le opzioni
    service = ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def HTML2PDF(html, pdf=None, css=None, options = None, config=None, return_value = False):
    def unique_file(fn, counter_width = 4):
        if not os.path.exists(fn): return fn

        base_name, ext = os.path.splitext(fn)
        counter = 0

        # Check if filename has an existing counter at the end (like `file_0003.txt`)
        match = re.search(r".(\d+)$", base_name)
        if match:
            counter = int(match.group(1))
            base_name = base_name[:match.start()]  # Remove existing counter to increment anew

        # Keep incrementing counter until a unique filename is found
        while os.path.exists(f"{base_name}.{str(counter).zfill(counter_width)}{ext}"):
            counter += 1

        return f"{base_name}.{str(counter).zfill(counter_width)}{ext}"


    try:

        if os.path.isfile(html):
            # use from_file(...) method
            pdfc = pdfkit.from_file
        else:
            pdfc = pdfkit.from_string

        if pdf:
            pdf = unique_file(pdf)
            pdfc(html, pdf, css=css, options=options, configuration=config)
        else:
            return pdfc(html, css=css, options=options, configuration=config)
    except Exception as e:
        print(f'Failed pdfkit.from_string(html)')
    return None

def HTML_to_PDF(FilePath, sleep_time:int=2, by:(By, str)=(None, None)):
    # Validazione e preparazione del percorso del file
    if not os.path.isfile(FilePath):
        raise FileNotFoundError(f"The specified file does not exist: {FilePath}")

    FilePath = f"file:///{os.path.abspath(FilePath).replace(os.sep, '/')}"
    driver:webdriver.Chrome = None
    try:
        driver = create_driver_selenium()
        driver.get(FilePath)
        time.sleep(sleep_time)
        if not all(by):
            pdf_base64 = driver.execute_cdp_cmd("Page.printToPDF", {
                "printBackground": True,         # Include lo sfondo nella stampa
                "landscape": False,              # Stampa in verticale (False per ritratto)
                "paperWidth": 8,              # Larghezza del foglio in pollici (A4)
                "paperHeight": 11,            # Altezza del foglio in pollici (A4)
                "marginTop": 0.5,                # Margine superiore in pollici (circa 2 cm)
                "marginBottom": 0.5,             # Margine inferiore in pollici (circa 2 cm)
                "marginLeft": 0.3,               # Margine sinistro in pollici (circa 2 cm)
                "marginRight": 0.3,              # Margine destro in pollici (circa 2 cm)
                "displayHeaderFooter": False,   # Non visualizzare intestazioni e piè di pagina
                "preferCSSPageSize": True,       # Preferire le dimensioni della pagina CSS
                "generateDocumentOutline": False, # Non generare un sommario del documento
                "generateTaggedPDF": False,      # Non generare PDF taggato
                "transferMode": "ReturnAsBase64" # Restituire il PDF come stringa base64
            })
            return pdf_base64['data']
        else:
            return ';'.join([x.text for x in driver.find_elements(by[0], by[1])])


    except WebDriverException as e:
        raise RuntimeError(f"WebDriver exception occurred: {e}")
    finally:
        if driver is not None:
            driver.quit()

def get_chrome_browser_options():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # Avvia il browser a schermo intero
    options.add_argument("--no-sandbox")  # Disabilita la sandboxing per migliorare le prestazioni
    options.add_argument("--disable-dev-shm-usage")  # Utilizza una directory temporanea per la memoria condivisa
    options.add_argument("--ignore-certificate-errors")  # Ignora gli errori dei certificati SSL
    options.add_argument("--disable-extensions")  # Disabilita le estensioni del browser
    options.add_argument("--disable-gpu")  # Disabilita l'accelerazione GPU
    options.add_argument("window-size=1200x800")  # Imposta la dimensione della finestra del browser
    options.add_argument("--disable-background-timer-throttling")  # Disabilita il throttling dei timer in background
    options.add_argument("--disable-backgrounding-occluded-windows")  # Disabilita la sospensione delle finestre occluse
    options.add_argument("--disable-translate")  # Disabilita il traduttore automatico
    options.add_argument("--disable-popup-blocking")  # Disabilita il blocco dei popup
    #options.add_argument("--disable-features=VizDisplayCompositor")  # Disabilita il compositore di visualizzazione
    options.add_argument("--no-first-run")  # Disabilita la configurazione iniziale del browser
    options.add_argument("--no-default-browser-check")  # Disabilita il controllo del browser predefinito
    options.add_argument("--single-process")  # Esegui Chrome in un solo processo
    options.add_argument("--disable-logging")  # Disabilita il logging
    options.add_argument("--disable-autofill")  # Disabilita l'autocompletamento dei moduli
    #options.add_argument("--disable-software-rasterizer")  # Disabilita la rasterizzazione software
    options.add_argument("--disable-plugins")  # Disabilita i plugin del browser
    options.add_argument("--disable-animations")  # Disabilita le animazioni
    options.add_argument("--disable-cache")  # Disabilita la cache
    #options.add_argument('--proxy-server=localhost:8081')
    #options.add_experimental_option("useAutomationExtension", False)  # Disabilita l'estensione di automazione di Chrome
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])  # Esclude switch della modalità automatica e logging

    options.add_argument("--single-process")  # Esegui Chrome in un solo processo
    return options

def read_format_string(file)->str:
    fmt = ''
    try:
        with open(file, 'r', encoding='utf-8') as f:
           fmt = f.read()
    except FileNotFoundError as e:
        printred(f'EXCEPTION in read_format_string - FileNotFound: {file} ')
        printred(traceback.format_exc())
    except Exception as e:
        printred(printred(f'EXCEPTION in read_format_string - FileNotFound: {file}. Error {e}'))
        raise e
    return fmt

def printred(text):
    RED = "\033[91m"
    RESET = "\033[0m"
    print(f"{RED}{text}{RESET}")

def printyellow(text):
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    print(f"{YELLOW}{text}{RESET}")

def printcolor(text, color="none", intensity="none"):
    RESET = "\033[0m"
    colors = {
        "none": 0,
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "magenta": 35,
        "cyan": 36,
        "white": 37
    }

    intensity_offsets = {
        "none": 0,
        "normal": 0,
        "bright": 60
    }
    _color = colors.get(color.lower(), 0)
    _offset = intensity_offsets.get(intensity.lower(), 0)
    COLOR = f"\033[{_color+_offset}m"
    print(f"{COLOR}{text}{RESET}")
