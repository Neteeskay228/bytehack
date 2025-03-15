import pytesseract
from PIL import Image
import requests
import easyocr

YANDEX_SPELLER_API_URL = "https://speller.yandex.net/services/spellservice.json/checkText"
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


async def correct_text_with_speller(text):
    params = {'text': text}
    response = requests.get(YANDEX_SPELLER_API_URL, params=params)

    if response.status_code == 200:
        corrections = response.json() 
        corrected_text = text
        
        for correction in corrections:
            error = correction.get('word', '') 
            suggestions = correction.get('s', [])  

            if suggestions:  
                suggestion = suggestions[0]  
                corrected_text = corrected_text.replace(error, suggestion)  

        return corrected_text
    else:
        print(f"Error with Yandex Speller API: {response.status_code}")
        return text 



# Откройте изображение
# async def textUU(pathimg: str, lang: str):
#     image = Image.open(pathimg)
#     # , lang=lang
#     text = pytesseract.image_to_string(image, lang=lang)  # Укажите 'rus' для русского языка
#     return await correct_text_with_speller(text)
#     # return text


# print(textUU("./uploads/i-2.webp", "eng"))

async def EasyOCRtext(image_path):
    try:
        reader = easyocr.Reader(['ru', 'en'], gpu=False)
        easyocr_results = reader.readtext(image_path)
        recognized_text = "" 
        for (bbox, text, prob) in easyocr_results:
            recognized_text += text + " " 
        # return recognized_text
        return await correct_text_with_speller(recognized_text)
    except Exception:
        return ''

# 2. Tesseract OCR
async def Tesseracttext(image_path):
    try:
        tesseract_text = pytesseract.image_to_string(Image.open(image_path), lang='rus+eng')
        # return tesseract_text
        return await correct_text_with_speller(tesseract_text)
    except Exception:
        return ''

