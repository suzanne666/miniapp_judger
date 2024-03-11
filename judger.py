import re
import os
from config import DirConfig

class Judger:
    def __init__(self, project_path, image_path):
        self.project_path = project_path
        self.image_path = image_path
        self.css_fuffix = '.wxss'
        self.xml_fuffix = '.wxml'
        self.js_fuffix = '.js'
        self.all_wxml_class = []
        self.all_wxml_tag = []
        self.all_page_content = []
        self.all_image = []

    def page_content(self, path):
        with open(path, 'r') as result:
            return result.read()

    def id_from_js(self, content):
        records = []
        records += re.findall(r"'#(.*?)'", content)
        records += re.findall(r'"#(.*?)"', content)
        for i in records:
            if i == '' or i is None:
                records.remove(i)
                continue
        return records

    def id_from_wxml(self, content):
        records = []
        records += re.findall(r" id='(.*?)'", content)
        records += re.findall(r' id="(.*?)"', content)
        for i in records:
            if i == '' or i is None:
                records.remove(i)
                continue
        return records

    def id_from_wxss(self, content):
        records = []
        records += re.findall(r"#(.*?){", content)
        result = []
        for i in records:
            result += i.split(' ')
        res = []
        for i in result:
            if i == '' or i == '>' or i is None:
                continue
            else:
                res.append(i)
        return res

    def data_from_js(self, content):
        records = []
        records += re.findall(r'data:(.*?),\n\n', content, re.DOTALL)
        records = records[0]
        records = re.sub(' ', '', records)
        records = re.sub('"', "'", records)
        _records = ''
        a = 0
        for i in records:
            if i == '{' or i == '[':
                a += 1
            if a <= 1:
                _records += i
            elif i == '}' or i == ']':
                a -= 1
        records = re.findall(r'\n(.*?):', _records)
        return records

    def variables_from_js(self, content):
        records = []
        records += re.findall(r'variables:(.*?),\n\n', content, re.DOTALL)
        if len(records) == 0:
            return records
        records = records[0]
        records = re.sub(' ', '', records)
        records = re.sub('"', "'", records)
        _records = ''
        a = 0
        for i in records:
            if i == '{' or i == '[':
                a += 1
            if a <= 1:
                _records += i
            elif i == '}' or i == ']':
                a -= 1
        records = re.findall(r'\n(.*?):', _records)
        return records

    def class_from_wxml(self, content):
        records = re.findall(r" class='(.*?)'", content)
        records += re.findall(r' class="(.*?)"', content)
        records += re.findall(r" hover-class='(.*?)'", content)
        records += re.findall(r' hover-class="(.*?)"', content)
        _result = []
        for i in records:
            _result += i.split(' ')
        result = []
        for i in _result:
            if '{{' in i or '"' in i or "'" in i:
                result += re.findall(r"'(.*?)'", i)
                result += re.findall(r'"(.*?)"', i)
                result += re.findall(r'{{(.*?)"', i)
                result += re.findall(r"{{(.*?)'", i)
            else:
                result.append(i)
        for i in result:
            if i == '' or i is None:
                result.remove(i)
                continue
        return result

    def class_from_wxss(self, content):
        records = []
        records += re.findall(r"\.(.*?){", content)
        result = []
        for i in records:
            result += i.split(' ')
        res = []
        for i in result:
            if i == '' or i == '>' or i is None:
                continue
            if i.startswith('.'):
                res.append(i[1:])
            elif i.endswith(','):
                res.append(i[:-1])
            elif '[' in i:
                res.append(i.split('[')[0])
            elif ':' in i:
                res.append(i.split(':')[0])
            else:
                res.append(i)
        return res

    def tag_from_wxml(self, content):
        records = re.findall(r"<(.*?) ", content)
        for i in records:
            if i == '' or i is None or i == '!--':
                records.remove(i)
        result = []
        for i in records:
            if '>' in i:
                result.append(i.split('>')[0])
            else:
                result.append(i)
        return result

    def check_single_page(self, path):
        _list = os.listdir(path)
        for i in _list:
            file_name = path + '/' + i
            if os.path.isfile(file_name):
                file_split = os.path.splitext(file_name)
                wxss = file_name
                wxml = file_split[0] + self.xml_fuffix
                js = file_split[0] + self.js_fuffix
                if file_split[1] == self.css_fuffix and os.path.exists(wxml):
                    js_content = self.page_content(js)
                    wxml_content = self.page_content(wxml)
                    wxss_content = self.page_content(wxss)
                    self.all_page_content.append(js_content)
                    self.all_page_content.append(wxml_content)
                    self.all_page_content.append(wxss_content)

                    js_data = self.data_from_js(js_content)
                    wxml_tag = self.tag_from_wxml(wxml_content)
                    wxml_class = self.class_from_wxml(wxml_content)
                    wxss_class = self.class_from_wxss(wxss_content)
                    js_variables = self.variables_from_js(js_content)
                    #  wxml_id = self.id_from_wxml(wxml)
                    #  wxss_id = self.id_from_wxss(wxss)
                    #  js_id = self.id_from_js(js)

                    #  print('wxml_id', wxml_id)
                    #  print('wxss_id', wxss_id)
                    #  print('js_id', js_id)
                    #  print('wxml class:', wxml_class)
                    #  print('wxss class:', wxss_class)
                    #  print('wxss tag:', wxml_tag)
                    self.all_wxml_class += wxml_class
                    self.all_wxml_tag += wxml_tag
                    for i in js_variables:
                        if 'variables.%s' % i not in js_content:
                            print('冗余变量:', i, '位于 js variables', wxml)
                    for i in js_data:
                        #  print(i)
                        if i not in wxml_content:
                            print('未渲染的变量:', i, '位于 js data', wxml)
                    for i in wxss_class:
                        is_match = False
                        for j in wxml_class:
                            if i == j:
                                is_match = True
                                break
                        if is_match is False and i not in wxml_tag:
                            print('冗余页面样式:', i, '位于', wxml)
                            for tag in wxml_class:
                                if i in tag:
                                    print('参考', wxml, tag)

            elif os.path.isdir(file_name):
                self.check_single_page(file_name)
            else:
                print('未知文件', file_name, type(file_name))

    def global_class(self, path):
        _list = os.listdir(path)
        if 'project.config.json' in _list and 'app.wxss' in _list:
            _path = path + '/' + 'app.wxss'
            return self.class_from_wxss(_path)
        for i in _list:
            file_name = path + '/' + i
            #  print(file_name)
            if os.path.isdir(file_name):
                global_wxss = self.global_class(file_name)
                if global_wxss is not None:
                    return global_wxss

    def check_global_class(self, path):
        global_wxss = self.global_class(path)
        for i in global_wxss:
            is_match = False
            for j in self.all_wxml_class:
                if i == j:
                    is_match = True
                    break
            if is_match is False and i not in self.all_wxml_tag:
                print('冗余全局样式:', i)

    def get_images(self, path):
        _list = os.listdir(path)
        for i in _list:
            file_name = path + '/' + i
            if os.path.isfile(file_name):
                self.all_image.append(file_name[len(self.image_path) - 6:])
            #  print(file_name)
            if os.path.isdir(file_name):
                self.get_images(file_name)

    def check_image(self, path):
        self.get_images(path)
        #  print(self.all_image)
        for i in self.all_image:
            is_match = False
            for j in self.all_page_content:
                if i in j:
                    is_match = True
                    break
            if is_match is False:
                print('冗余图片:', i)

    def checker(self):
        self.check_single_page(self.project_path)
        self.check_global_class(self.project_path)
        self.check_image(self.image_path)
        print('检查完毕')


print()
judger = Judger(DirConfig.project_path, DirConfig.images_path)
judger.checker()
