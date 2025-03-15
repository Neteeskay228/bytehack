from ultralytics import YOLO
import zipfile

# Загружаем предобученную модель YOLOv8
model = YOLO("yolov8x.pt")  # Можно заменить на "yolov8m.pt", "yolov8l.pt" для точности

# async def process_file(file_path):
#     """ Обрабатывает один файл или ZIP-архив """
#     if file_path.lower().endswith('.zip'):
#         try:
#             with zipfile.ZipFile(file_path, "r") as archive:
#                 files_list = archive.namelist()
#                 archive.extractall('all_files/')
#                 return files_list
#         except zipfile.BadZipFile:
#             print("Ошибка: Невозможно открыть ZIP-файл!")
#             return []
#     return [file_path]  # Всегда возвращаем список для удобства

async def analyze_image(img_path):
    """ Анализирует изображение и возвращает список объектов """
    results = model(img_path)
    detected_objects = [model.names[int(box.cls[0])] for result in results for box in result.boxes]
    return ", ".join(detected_objects)



# async def objUU(pathimg: str):
#     files = await process_file(pathimg)

#     if type(files) == list:
#         for file in files:
#             # print(analyze_image('all_files/'+file, model))
#             return await analyze_image(file, model)
#     else:
#         # print(analyze_image(files, model))
#         return await analyze_image(files, model)
