import imageio
import jieba
import pandas as pd
import time
import matplotlib.pyplot as plt
from pyecharts.charts import Bar
from pyecharts import options as opts
from pyecharts.charts import Pie
import wordcloud

# 根据指定路径读取文件内容
def read_file(file_path):
    message = pd.read_csv(file_path, sep=',', encoding='utf-8', low_memory=False)
    print(message.shape)
    return message


# 对message表中内容进行处理，只留下所需的type, isSend, createTime, talker, content内容，并将之存储于新的文件中
def get_needed_data(file_path, save_file_path):
    """
    :param file_path: 原始message文件路径
    :param save_file_path: 经过数据筛选后的message文件存储路径
    :return:
    """
    message = read_file(file_path)
    message = message[['type', 'isSend', 'createTime', 'talker', 'content']]
    message.to_csv(save_file_path, encoding='utf_8_sig')


# 对message表中数据进行处理，删除content中的无用数据，将type中非1值对应的content数据统统置为零
def data_clean(file_path, save_path):
    """
    :param file_path: 经过数据筛选后的message文件存储路径
    :param save_path: 将非文本消息置零后message存储路径
    :return:
    """
    message = pd.read_csv(file_path, sep=',', encoding='utf-8', low_memory=False)
    print("源文件大小： ", message.shape)
    message.loc[message.type != 1, 'content'] = 0
    print("处理后文件大小： ", message.shape)
    message.to_csv(save_path, encoding='utf_8_sig', header=True, index=False)


# 对contact表中数据进行预处理，获取所需数据，清除其余数据
def contact_pre_treatment(file_path, save_path):
    """
    :param file_path: 原始contact表存储位置
    :param save_path: 经过数据筛选后的contact表存储位置
    :return:
    """
    # file_path = r"D:\wechet-anayze\recontact.txt"
    # save_path = r"D:\wechet-anayze\pre-recontact.csv"

    contact = pd.read_csv(file_path, sep=',', encoding="utf-8", low_memory=False)
    print("处理前文件大小： ", contact.shape)
    contact = contact[['username', 'alias', 'conRemark', 'nickname']]
    # 删除无用记录，只保留有备注的联系人
    contact1 = contact.drop(contact[pd.isna(contact.conRemark)].index)
    print("处理后文件大小： ", contact.shape)
    contact1.to_csv(save_path, encoding='utf_8_sig', header=True, index=False)

# 数据预处理整体部分，如不关系具体预处理过程，直接使用此部分代码即可
def data_pretreatment(message_file_path, contact_file_path):
    message = pd.read_csv(contact_file_path, sep=',', encoding="utf-8", low_memory=False)
    message = message[['type', 'isSend', 'createTime', 'talker', 'content']]
    message.loc[message.type != 1, 'content'] = 0

    contact = pd.read_csv(contact_file_path, sep=',', encoding="utf-8", low_memory=False)
    contact = contact[['username', 'alias', 'conRemark', 'nickname']]
    contact = contact.drop(contact[pd.isna(contact.conRemark)].index)
    contact = contact[['username', 'conRemark']]
    return message, contact

# 获取常用联系人聊天次数
def get_chat_nums(message_path, contact_path):
    """
    :param message_path: 预处理完成后的message表存储路径
    :param contact_path: 预处理完成后的contact表存储路径
    :return:
    """
    # message_path = r'D:\wechet-anayze\pre-message-2.txt'
    # contact_path = r'D:\wechet-anayze\pre-recontact.csv'

    message = pd.read_csv(message_path, sep=',', encoding='utf-8', low_memory=False)
    contact = pd.read_csv(contact_path, sep=',', encoding='utf-8', low_memory=False)
    # 提取出联系人列表中用户名和备注名称
    contact = contact[['username', 'conRemark']]
    # 将用户名提取出来
    username = contact['username'].tolist()
    print(type(username))
    # 将用户名及备注名提取为一个字典
    contact_dict = dict(zip(contact['username'], contact['conRemark']))
    # 联系人及其聊天次数集合
    contact_sum_message = {}
    # 全部联系人聊天次数集合
    sum_message = 0
    # 联系人列表
    uname_list = []
    # 联系人列表对应的聊天次数列表
    chat_num_list = []
    # 遍历联系人列表，并逐一统计聊天次数
    for uname in username:
        # 根据微信id获取真实姓名,key为真实姓名
        key = contact_dict.get(uname)
        # 根据微信id统计聊天次数，value:聊天次数
        value = (message['talker'] == uname).sum()
        # 过滤聊天次数为0的联系人，只保留聊天次数不为0的联系人
        if value != 0:
            contact_sum_message[key] = value
            sum_message += value
            uname_list.append(key)
            # 这里需特别注意：value值也即聊天的次数格式是int64,但是pyecharts中如果传入的是int64时，最终渲染出的html文件中会数据会丢失，
            # 所以需转为int值（血泪教训）
            chat_num_list.append(int(value))

    # print(contact_sum_message)
    print("总聊天次数： ", sum_message)

    # 使用pyecharts绘制柱状图
    c = (
        Bar(init_opts=opts.InitOpts(width="1600px", height="600px", page_title="聊天次数统计"))
        .add_xaxis(uname_list)
        .add_yaxis(series_name="聊天次数", y_axis=chat_num_list, color='#FF6666')
        .set_global_opts(
            # 标题配置
            title_opts=opts.TitleOpts(title="聊天次数统计"),
            # X轴区域缩放配置项,可使用list同时配置多个配置项
            datazoom_opts=[opts.DataZoomOpts(range_start=20, range_end=40), opts.DataZoomOpts(type_="inside")],
            # 区域选择组件
            brush_opts=opts.BrushOpts(),
            # X坐标轴旋转
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
            # 工具箱组件
            toolbox_opts=opts.ToolboxOpts(),
            # 图例配置
            legend_opts=opts.LegendOpts(is_show=False),
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False),
            # 配置最大值最小值刻度线
            markline_opts=opts.MarkLineOpts(
                data=[
                    opts.MarkLineItem(type_="min", name="最小值"),
                    opts.MarkLineItem(type_="max", name="最大值"),
                    opts.MarkLineItem(type_="average", name="平均值"),
                ]
            ),
        )
        .render("chat_num_count.html")
    )

# 获取各个消息聊天记录数量，并使用pycharts绘图
def get_message_type_frequency(file_path, wxid):
    """
    :param file_path: 经过预处理后的message表存储位置
    :param wxid: 待查询人的微信id
    :return:
    """
    # file_path = r'D:\wechet-anayze\pre-message-2.txt'
    message = pd.read_csv(file_path, sep=',', encoding='utf-8', low_memory=False)
    # wxid = ''

    # 进行数据筛选，选择message表中与所需微信id一致的数据
    message = message[message['talker'] == wxid]
    # 根据消息类型统计每种类型的频次（索引为数字编码）
    chat_type_count = message['type'].groupby(message['type']).size()
    # 消息类型对应关系
    message_type = {'1': '文本内容', "3": "图片及视频", "34": "语音消息", "42": "名片信息", "43": "图片及视频",
                    "47": "表情包", "48": "定位信息", "49": "小程序链接", "10000": "消息撤回提醒", "1048625": "网络照片",
                    "16777265": "链接信息", "419430449": "微信转账", "436207665": "红包", "469762097": "红包",
                    "-1879048186": "位置共享"}
    # 集合对象，功能与chat_type_count相同，存储（聊天类型：频次）信息（索引为对应中文类型）
    chat_type_count_dict = {}
    # 根据消息类型代码
    for key in chat_type_count.index:
        if str(key) in message_type.keys():
            print(message_type.get(str(key)))
            chat_type_count_dict[message_type.get(str(key))] = chat_type_count[key]
        else:
            chat_type_count_dict[key] = chat_type_count[key]
    print("结果集类型: ", type(chat_type_count_dict))
    print(chat_type_count_dict)

    x_data = []
    y_data = []
    for key in chat_type_count_dict:
        temp = [str(key), chat_type_count_dict.get(key)]
        x_data.append(str(key))
        y_data.append(int(chat_type_count_dict.get(key)))

    a1 = []
    for z in zip(x_data, y_data):
        a1.append(z)

    pie = Pie(init_opts=opts.InitOpts(width="1600px", height="600px", page_title="消息类型统计"))
    pie.add(
        "",
        data_pair=a1,
        center=["35%", "60%"],
    )
    pie.set_global_opts(
        title_opts=opts.TitleOpts(title="Pie-调整位置"),
        legend_opts=opts.LegendOpts(pos_left="15%"),
    )
    pie.set_series_opts(label_opts=opts.LabelOpts(formatter="{b}:{c}"))
    pie.render("message_type_count.html")


# 从message文件中，根据createTime信息获取年份，月份，日期，星期，yday，小时，分钟信息，并将之存储到新的文件中
def get_time_file(file_path, save_path):
    message = pd.read_csv(file_path, sep=',', encoding='utf-8', low_memory=False)
    message = message[['talker', 'createTime', 'isSend']]
    year = []
    month = []
    day = []
    hour = []
    minute = []
    yday = []
    wday = []
    content = []

    for sec_time in message['createTime']:
        sec_time = sec_time / 1000
        struct_time = time.localtime(sec_time)

        year.append(struct_time.tm_year)
        month.append(struct_time.tm_mon)
        day.append(struct_time.tm_mday)
        hour.append(struct_time.tm_hour)
        minute.append(struct_time.tm_min)
        yday.append(struct_time.tm_yday)
        wday.append(struct_time.tm_wday)

    message['year'] = year
    message['month'] = month
    message['day'] = day
    message['wday'] = wday
    message['yday'] = yday
    message['hour'] = hour
    message['minute'] = minute
    message['content'] = content
    # 写入到指定位置
    message.to_csv(save_path, encoding='utf_8_sig', header=True, index=False)

# 根据聊天记录生成词云
def get_wordcloud(file_path, stopword_path, wxid, image_path):
    """
    :param file_path: 预处理完成后的message表存储位置
    :param stopword_path: 停用词文件存储位置
    :param wxid: 待查询人微信id
    :return:
    """
    # 分词及词云处理
    # message_path = r'D:\wechet-anayze\pre-message-2.txt'
    # stopword_path = r'D:/wechet-anayze/stopword.txt'
    # 文件读取
    message = pd.read_csv(file_path, sep=',', encoding='utf-8', low_memory=False)
    # 数据筛选，选择对应微信id的信息
    message = message[message['talker'] == wxid]
    # 提取聊天内容信息
    content = message['content']

    # 中文字型存储路径
    font_path = r'C:\Windows\Fonts\MSYH.TTC'
    # 是否选用分词
    wordcut_flag = True
    # 词云图片输出路径
    image_out_name = 'word-heart.png'

    # struct_time = time.localtime()
    # image_out_name = str(struct_time.tm_year) + str(struct_time.tm_mon) + str(struct_time.tm_mday) + "-" + str(
    #     struct_time.tm_hour) + str(struct_time.tm_min) + "-" + image_out_name

    # 读取停用词表
    stopwords = [line.strip() for line in open(stopword_path, encoding='UTF-8').readlines()]

    if image_out_name is None:
        image_out_name = 'word-heart.png'
    if wordcut_flag:
        print("进行中文分词")
        outstr = ""
        text = ",".join(content)
        text_list = jieba.lcut(text, cut_all=False)

        for word in text_list:
            if word not in stopwords:
                if word != '\t' and '\n':
                    outstr += word
                    outstr += " "

        # 如果想存储分词后结果，可取消下方注释
        # savepath = r'D:/wechet-anayze/textlist.txt'
        # fp = open(savepath, 'w', encoding='utf8', errors='ignore')
        # fp.write(outstr)
        # fp.close()

        text = outstr
    else:
        print("不进行中文分词")
        text = " ".join(content)

    # 词云形状图片位置
    mk = imageio.imread(image_path)

    # 构建并配置词云对象w，注意要加scale参数，提高清晰度
    w = wordcloud.WordCloud(width=1000,
                            height=700,
                            background_color='white',
                            font_path=font_path,
                            mask=mk,
                            scale=2,
                            stopwords=None,
                            contour_width=1,
                            contour_color='red')
    # 将string变量传入w的generate()方法，给词云输入文字
    w.generate(text)
    # 展示图片
    # 根据原始背景图片的色调进行上色
    image_colors = wordcloud.ImageColorGenerator(mk)
    plt.imshow(w.recolor(color_func=image_colors))
    # 根据原始黑白色调进行上色
    # plt.imshow(wc.recolor(color_func=grey_color_func, random_state=3), interpolation='bilinear') #生成黑白词云图
    # 根据函数原始设置进行上色
    # plt.imshow(wc)

    # 隐藏图像坐标轴
    plt.axis("off")
    plt.show()

    # 将词云图片导出到当前文件夹
    w.to_file(image_out_name)
