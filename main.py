from fileinput import filename

from flask import Flask, render_template, request, send_from_directory, redirect, url_for, jsonify, send_file
import os
import zipfile, rarfile
import shutil

from text import EasyOCRtext, correct_text_with_speller, Tesseracttext
from obj import analyze_image
import uuid
from func import generate_xml
from pathlib import Path
from database import ImageDatabase
app = Flask(__name__)
db = ImageDatabase()
from deep_translator import GoogleTranslator



translator = GoogleTranslator(source='auto', target='ru')



IMAGE_FOLDER = 'static/images'
UPLOAD_FOLDER = 'static/images'


@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")


@app.route('/search', methods = [ 'GET'])
async def search():
    #data = request.get_json()
    #query = data.get("query")
    {
        "query":"cat"
    }
    query = 'cat'
    results = await db.search(query)
    json_result = []
    for result in results:
        json_result.append({"filename": result[1], "objects" : result[2], "text": result[3]})
    
    print(jsonify(json_result))
    return jsonify(json_result)



@app.route('/upload', methods = ['POST'])
async def upload_image():
    files = request.files.getlist('files')
    uu = request.form.get('selected_model')
    print(uu)
    json_result =[]
    for file in files:
        if file.filename:


            filepath = Path(file.filename)
            suffix = filepath.suffix.lower()
            if suffix == ".rar":
                try:
                    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                    file.save(filepath)
                    with rarfile.RarFile(UPLOAD_FOLDER + "/" + file.filename, "r") as archive:
                        files_list = archive.namelist()
                        archive.extractall('all_files/')  # По умолчанию, извлекает в текущую директорию

                    for filees in files_list:
                        filepath = Path(filees)
                        suffix = filepath.suffix.lower()
                        UUID = str(uuid.uuid4())
                        uuid_filename = UUID + suffix
                        new_destination_path = os.path.join(UPLOAD_FOLDER + '/', uuid_filename)
                        shutil.copy2("./all_files/" + filees, new_destination_path)
                        if uu == "Tesseracts":
                            text = await Tesseracttext(UPLOAD_FOLDER + '/' + uuid_filename)
                        else:
                            text = await EasyOCRtext(UPLOAD_FOLDER + '/' + uuid_filename)
                        obj = await analyze_image(UPLOAD_FOLDER + '/' + uuid_filename)
                        translated_text = translator.translate(obj)
                        await db.save_image_data(uuid_filename, translated_text, text)
                        await generate_xml(uuid_filename, translated_text, text)
                        json_result.append({"filename": uuid_filename, "objects" :translated_text, "text": text})
                        
                        
                        
                        os.remove("./all_files/" + filees)
                    # os.remove("./uploads/" + file.filename)


                except rarfile.NeedFirstVolume:
                    print("Ошибка: Необходим первый том RAR-архива!")
                except rarfile.Error as e:  # Перехватываем общую ошибку rarfile
                    print(f"Ошибка: Невозможно открыть RAR-файл: {e}")


            elif suffix == ".zip":
                try:
                    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                    file.save(filepath)
                    with zipfile.ZipFile(UPLOAD_FOLDER + "/" + file.filename, "r") as archive:
                        files_list = archive.namelist()
                        archive.extractall('all_files/')
                    
                    for filees in files_list:
                        filepath = Path(filees)
                        suffix = filepath.suffix.lower()
                        UUID = str(uuid.uuid4())
                        uuid_filename = UUID + suffix
                        new_destination_path = os.path.join(UPLOAD_FOLDER + '/', uuid_filename)
                        shutil.copy2("./all_files/" + filees, new_destination_path)
                        if uu == "Tesseracts":
                            text = await Tesseracttext(UPLOAD_FOLDER + '/' + uuid_filename)
                        else:
                            text = await EasyOCRtext(UPLOAD_FOLDER + '/' + uuid_filename)
                        obj = await analyze_image(UPLOAD_FOLDER + '/' + uuid_filename)
                        translated_text = translator.translate(obj)
                        await db.save_image_data(uuid_filename, translated_text, text)
                        await generate_xml(uuid_filename, translated_text, text)
                        json_result.append({"filename": uuid_filename, "objects" :translated_text, "text": text})
                        os.remove("./all_files/" + filees)
                        

                    # os.remove("./uploads/" + file.filename)

                    # return files_list
                except zipfile.BadZipFile:
                    print("Ошибка: Невозможно открыть ZIP-файл!")




            elif suffix == ".jpg" or suffix == ".jpeg" or suffix == ".png" or suffix == ".webp":
                UUID = str(uuid.uuid4())
                uuid_filename = UUID + suffix
                filepath = os.path.join(UPLOAD_FOLDER, uuid_filename)
                file.save(filepath)

                if uu == "Tesseracts":
                    text = await Tesseracttext(UPLOAD_FOLDER + '/' + uuid_filename)
                else:
                    text = await EasyOCRtext(UPLOAD_FOLDER + '/' + uuid_filename)
                obj = await analyze_image(filepath)
                translated_text = translator.translate(obj)
                await db.save_image_data(uuid_filename, translated_text, text)
                await generate_xml(uuid_filename, translated_text, text)
                json_result.append({"filename": uuid_filename, "objects" :translated_text, "text": text})


            # print(extension)
            #print(extension)
            # UUID = str(uuid.uuid4())
            # uuid_filename = UUID + suffix

            # filepath = os.path.join(UPLOAD_FOLDER, uuid_filename)
            # file.save(filepath)

            # text = await Tesseracttext(filepath)
            # text += "///////////"
            # text += await EasyOCRtext(filepath)
            # # text = "text"
            # print(text)
            # obj = await objUU(filepath)


            # await db.save_image_data(uuid_filename, obj, text)
            # await generate_xml(uuid_filename, obj, text)
            # print('-----------------------------------')
            # print(text)
            # print('-----------------------------------')
            # tt = await correct_text_with_speller(text)
            # print(tt)
            # print('-----------------------------------')
            # print(obj)
            # print('-----------------------------------')

        
            # json_result.append({"filename": uuid_filename, "objects" :translated_text, "text": text})



    print(json_result)
    # return jsonify(json_result)
    return render_template("index.html", json_result=json_result)


@app.route('/images/<path:filename>')
async def images(filename):
    # return redirect(url_for('download_file', name=UPLOAD_FOLDER + '/' + filename))
    filename =  filename.rsplit(".", 1)[0] + ".xml"
    return send_from_directory(app.root_path + '/static/images', filename, as_attachment=True)


# @app.route('/xml/<path:filename>', methods=['GET'])
# async def xml(filename):
#     filename =  filename.rsplit(".", 1)[0] + ".xml"
#     return send_from_directory(UPLOAD_FOLDER, UPLOAD_FOLDER + '/' + filename)


if __name__ == '__main__':
    app.run(debug=True)