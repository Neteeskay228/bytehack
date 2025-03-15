XML_DIRECTORY = "./static/images/"
async def generate_xml(filename, obj, text):
    data = {'name': filename, 'object': obj, 'text': text}
    xml_content = '<?xml version="1.0" encoding="utf-8"?>\n<metadata>\n'
    # for item in data:
    xml_content += f'  <image name="{filename}">\n'
    xml_content += f'    <object>{obj}</object>\n'
    xml_content += f'    <text>{text}</text>\n'
    xml_content += '  </image>\n'

    xml_content += '</metadata>\n'

    with open(XML_DIRECTORY + filename.rsplit(".", 1)[0] + ".xml", 'w', encoding='utf-8') as f:
        f.write(xml_content)