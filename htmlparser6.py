from bs4 import BeautifulSoup
import pysnooper


class HtmlParser():
    def __init__(self, file_name):
        self.prompt = '------'
        print('{}begain to initize the instance{}'.format(self.prompt, self.prompt))
        fi = open(file_name,'r')
        self.html = BeautifulSoup(fi.read(),'html.parser')
        self.soup = self.html.find(name='div', class_='main-content')
        fi.close()


    def organize_text(self):
        print('{}organizing text{}'.format(self.prompt, self.prompt))
        '''
        作为主函数，协作下列 简介抽取、基本信息抽取、目录抽取、主体内容抽取函数
        '''
        try:
            dic = {} # 作为返回值的初始化定义
            for name in ['entry', 'intro', 'basic_info', 'contents']:
                method = eval('self.{}'.format(name)) # 利用 eval 函数为各个文本抽取方法做循环赋值
                # self.process　函数的目的有两个：
                # 一是把下列文本抽取方法的返回结果的　BeautifulSoup 对象转换成字符串
                # 二是修改字符串的格式，去除多余的残存的 html 标识符
                dic[name] = tuple([self.para_process(value) for value in method()])

            return dic
            # 此处返回的结果是，按百科页面的四大部分，每一部分的各段落形成的字典结构化文本
        except Exception as e:
            print('Error: {}'.format(e))
            if '您所访问的页面不存在' in str(self.html):
                print('This Page Do Not Exist!')


    def extract_text(self, dic, file_name):
        print('{}saving to file{}'.format(self.prompt, self.prompt))
        # 把结果形成文本文件
        # dic 参数是　self.extract_text()　的返回值
        # file_name 参数是保存文件的文件名
        with open(file_name,'w') as fi:
            try:
                for partition, content in dic.items():
                    for number, paragrah in enumerate(content):
                        print('{}) {}'.format(number, paragrah))
                        fi.write(paragrah)
                        fi.write('\n')
            except Exception as e:
                print('Html Parsing Error: {}'.format(e))
                fi.write('Html Parsing Error')


    def entry(self):
        print('{}extracting the entry name{}'.format(self.prompt, self.prompt))
        entry_name = self.soup.find(name='dl',class_='lemmaWgt-lemmaTitle lemmaWgt-lemmaTitle-')
        return [ entry_name.dd.h1 ]


    def intro(self):
        print('{}extracting brief introduce{}'.format(self.prompt, self.prompt))
        """
        抽取百科介绍文字，输出成字典格式
        """
        brief_intro = self.soup.find(
            name='div',
            attrs={"class":"lemma-summary", "label-module":"lemmaSummary"}
        ) # 定位到简介的上一级
        try:
            paragrahs = list(brief_intro.find_all(
                name='div',
                attrs={'class':"para", 'label-module':"para"}
                )) # 找出简介一级下所有的段落

            return paragrahs #　此处的返回的对象类型是　字典，键是字符串，值是 BeautifulSoup 对象
        except Exception as e:
            print(e)
            return []


    def basic_info(self):
        print('{}extracting basic information{}'.format(self.prompt, self.prompt))
        # 抽取条目基本信息
        info_left, info_right = (self.soup.find(name='dl', attrs={"class":"basicInfo-block basicInfo-left"}),
                                 self.soup.find(name='dl', attrs={"class":"basicInfo-block basicInfo-right"}))
        paragrahs = []
        try:
            ls = str(info_left).split('</dd>')[:-1] # 把 BeautifulSoup 对象转换成字符串，以实现基本信息的配对
            # 此处的做法是用html 其中的 </dd> 标签作为分割的标记，或可日后优化
            ls.extend(str(info_right).split('</dd>')[:-1]) # 将左列基本信息和右列基本信息整合进入一个列表

            '''
            # 以下为检查信息是否互相匹配的代码，仅供测试使用
            print('.........................')
            for item in ls:
                print(item.replace('\n','\\n'),end='\n\n') # 在 print 的过程中不换行，直接输出 \n
            '''
            for item in ls:
                item = ''.join(item.split(' ')) # 去除\xa0，一种特殊的空格
                soup = BeautifulSoup('<dl class="basicInfo-block basicInfo-left">\n{}</dd>\n</dl>'.format(item),
                                     'html.parser')
                # 重新添加 父级 及 </dd> 截止标签，以被 BeautifulSoup 当做 html 解析，同时实现定位
                name, value = soup.dt.text, soup.dd.text
                paragrahs.append('{}:{}'.format(name,value)) # 将匹配后的结果添加进入字典

            return paragrahs
        #　此处的返回的对象类型是　字典，键是字符串，值是 BeautifulSoup 对象
        except Exception as e:
            print(e)
            return []


    def catalog_list(self):
        print('{}checking catalog list{}'.format(self.prompt, self.prompt))
        # 抽取目录
        catalog_list = self.soup.find(name='div', attrs={"class":"lemmaWgt-lemmaCatalog"})
        paragrahs = []
        cnt = 0
        try:
            for para in catalog_list.div.div.find_all(name='li'):
                paragrahs.append(para.find(name='span', class_='text').a)
            # 此处需要 try except
            return paragrahs
        except Exception as e:
            print(e)
            return []
            #　此处的返回的对象类型是　字典，键是字符串，值是 BeautifulSoup 对象


    def contents(self):
        print('{}extracting main content{}'.format(self.prompt, self.prompt))
#       try:
        if len(self.catalog_list()) == 0:
            begain = self.soup.find(
            name='div',
            attrs={'class':"lemma-summary", 'label-module':'lemmaSummary'}
            )

            contents = begain.find_all_next(
            name='div',
            attrs={'class':'para','label-module':"para"}
            )

            paragrahs = []

            for paragrah in contents:
                paragrahs.append(paragrah)

            return paragrahs
        else:
            dic_title_level_2 = dict(enumerate(self.soup.find_all(
            name='div',
            class_='para-title level-2'
            )))

            paragrahs = []
            condition = {
            'para':  {'class':'para','label-module':'para'},
            'title': {'label-module':'para-title'}
            }

            tag = {'para': 'div', 'title': 'div'}
            cnt = 0
            for key in dic_title_level_2.keys():
                cnt += 1
                if key == len(dic_title_level_2) - 1:
                    paragrahs.extend(self.find_rest(
                        dic_title_level_2[key],
                        tag,
                        condition
                    ))
                else:
                    ls = self.find_section(
                        dic_title_level_2[key],
                        dic_title_level_2[key+1],
                        tag,
                        condition
                    )

                    paragrahs.extend(ls)

            return paragrahs
#        except Exception as e:
#            print(e)
#            return []
    #@pysnooper.snoop('/home/dundant/Dun_Projects/ai+/htmlparser/snoop.log')
    def find_section(self, title_above, title_below, tag, condition):
        print('{}begain find_section{}'.format(self.prompt, self.prompt))
        '''
        condition = {
        'para':  {'class':'para','label-module':'para'},
        'title': {'lebel-module':'para-title'}
        }

        tag = {
        'para': 'div',
        'title': 'div'
        }
            '''
        # 此函数的用途是在找到两节标题之间所有的标题和正文部分
        # 用到了回归的方法
        paragrahs, cnt = [], 0
        ls = list(self.find_all_between(title_above, title_below, tag['title'], condition['title']))
        length = len(ls)
        if length == 0:
            paragrahs.append(self.title_prefix_remove(title_above))
            for para in self.find_all_between(title_above, title_below, tag['para'], condition['para']):
                paragrahs.append(para)

            '''
            # 此处代码仅用于测试
            print('paragrahs:')
            for number, paragrah in enumerate(paragrahs):
                print('{}{}  {}\n'.format(self.prompt, number, paragrah.text.strip()))
            '''

            return paragrahs

        elif length == 1:
            paragrahs.extend(self.find_section(title_above, ls[0], tag, condition))
            paragrahs.extend(self.find_section(ls[0], title_below, tag, condition))

            return paragrahs
        else:
            for n in range(length):
                if n == 0:
                    paragrahs.extend(self.find_section(title_above, ls[0], tag, condition))
                    paragrahs.extend(self.find_section(ls[0], ls[1], tag, condition))
                elif n == length - 1:
                    paragrahs.extend(self.find_section(ls[length-1], title_below, tag, condition))
                else:
                    paragrahs.extend(self.find_section(ls[n], ls[n+1], tag, condition))

            return paragrahs


    def find_rest(self,title,tag,condition):
        print('{}looking for the rest{}'.format(self.prompt, self.prompt))
        # 此函数的用途是找到一节标题之后的全部正文及下一级标题
        # 不可知之后是否存在父级的时候，使用
#        try:
        rest = dict(enumerate(title.find_all_next(
            name=tag['title'],
            attrs=condition['title']
        )))
        paragrahs, length = [], len(rest)
        if length == 0:
            paragrahs.append(self.title_prefix_remove(title))
            paragrahs.extend(list(title.find_all_next(
            name=tag['para'],attrs=condition['para']
            )))

            return paragrahs
        elif length == 1:
            paragrahs.extend(self.find_section(title_above, ls[0], tag, condition))
            paragrahs.extend(self.find_rest(rest[0], tag, condition))

            return paragrahs
        else:
            for key in rest.keys():
                if key == 0:
                    paragrahs.extend(self.find_section(title, rest[0], tag, condition))
                    paragrahs.extend(self.find_section(rest[0], rest[1], tag, condition))
                elif key == length - 1:
                    paragrahs.extend(self.find_rest(rest[length - 1], tag, condition))
                else:
                    paragrahs.extend(self.find_section(rest[key], rest[key+1], tag, condition))

            return paragrahs
#        except Exception as e:
#            print(e)
#            return []

    def title_prefix_remove(self, title):
        print('{}removing prefix of title'.format(self.prompt))
        # 去除多余的标题前缀
        # 如不去除标题前缀
        # 则　level ２　标题的 BeautifulSoup 对象的　text 属性上带有百科条目的名称
        # 因此这个函数修改了原 html 代码
        # 至于level 3 的标题或更低级的标题，暂未查证是否有此种现象
        try:
            title, prefix, edit = (
                str(title),
                str(title.find('span', class_='title-prefix')),
                str(title.find('a', class_='edit-icon j-edit-link'))
            )
            title = BeautifulSoup(title.replace(prefix,'').replace(edit, ''),'html.parser')

            return title
        except Exception as e:
            print(e)
            return title
        #    return title


    def find_all_between(self, element_before, element_after, name, attrs):
        print('{}searching the interval{}'.format(self.prompt, self.prompt))
        """
        功能描述：找到两个BeautifulSoup对象之间的元素
        利用已有的 find_all_previous 和 find_all_next 函数定位
        其功能分别是：找出之前所有符合条件的元素和之后的
        """

        '''
        # 此处代码仅用于测试
        print('Before  {}'.format(element_before.text.strip()))
        print('After  {}'.format(element_after.text.strip()))
        print('\n')
        '''

        starting_point, terminal_point = element_before, element_after

        list1, list2 = [], []
        try:
            while True:
                element_before = element_before.find_next(name=name, attrs=attrs)
                element_after = element_after.find_previous(name=name, attrs=attrs)

                '''
                # 此处代码仅用于测试
                print('Before  {}'.format(element_before.text.strip()))
                print('After  {}'.format(element_after.text.strip()))
                print('\n')
                '''

                # 遍历结束的终止条件
                if element_before.text == terminal_point.text:
                    print('Matched Intermediate Value Do Not Exist')
                    return []
                elif element_after.text == starting_point.text:
                    print('Matched Intermediate Value Do Not Exist')
                    return []
                else:
                    pass

                list1.append(element_before)
                list2.append(element_after)

                # 找到符合的终止条件
                if element_after.text == element_before.text:
                    list2.pop()
                    list2.reverse()
                    list1.extend(list2)
                    return list1
                    # 此处列表中返回的结果同样是　BeautifulSoup 对象，而不是字符串
                elif len(list1) >= 2:
                    if list1[-1].text == list2[-2].text:
                        #(list2[-2].text == list2[-2].text)
                        list2.pop()
                        list2.pop()
                        list2.reverse()
                        list1.extend(list2)
                        return list1
                        # 此处列表中返回的结果同样是　BeautifulSoup 对象，而不是字符串
                else:
                    pass

            return []
        except Exception as e:
            print('Could Not Find the Matched Intermediate Value, Error: {}'.format(e))
            return []


    def para_process(self, paragrah):
        print('{}deleting the redundant html marks in text{}'.format(self.prompt, self.prompt))
        '''
        鉴于百科内文章多处用到蓝色链接字体和右上角标号
        故需要对于文本内容做出处理
        目前就实践观察到的样本来看，仅需要做替换处理即可，后续需要做出优化
        '''
        try:# 针对 paragrah 参数是 BeautifulSoup 对象
            sups = paragrah.find_all(name='sup', class_='sup--normal')
            anchors = paragrah.find_all(name='a', class_='sup-anchor')
            sups, anchors = [ str(sup) for sup in sups ], [ str(anchor) for anchor in anchors ]
            sups.extend(anchors)
            paragrah_text = str(paragrah)
            for sup in sups:
                paragrah_text = paragrah_text.replace(sup,'')

            paragrah = BeautifulSoup(paragrah_text, 'html.parser')
            paragrah_text = ' '.join(paragrah.text.split('\xa0'))# 字符串中所有的'\xa0' 替换成标准空格
            paragrah_text = ''.join(paragrah_text.split('\n')) # 去掉换行符
            return paragrah_text
        except:# 针对 paragrah 参数是普通字符串
            # 去除所有空格的原理是，用　split　函数指定空格作为分割成列表的标记
            # 再用　join 函数将列表的所有元素连接
            # 具体见　join 和　split　函数的用法
            paragrah_text = ' '.join(paragrah.split('\xa0'))# 字符串中所有的'\xa0' 替换成标准空格
            paragrah_text = ''.join(paragrah_text.split('\n'))# 去掉换行符
            return paragrah_text


    def paras_process(self,paragrahs):
        '''
        作为段落处理函数的复数形式
        此处为习惯性定义方法，此代码并未使用该函数
        '''
        ls = []
        for paragrah in paragrahs:
            ls.append(para_process(paragrah))

        return tuple(ls)

name1 = input('To be parsed: ').strip().strip('\'')
name2 = input('To be saved: ').strip().strip('\'')
html = HtmlParser(name1)
html_dic = html.organize_text()
html.extract_text(html_dic, name2)
