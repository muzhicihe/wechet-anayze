# 简介：

此python代码主要用于从微信数据库中读取数据，并进行相应处理，主要功能如下：

1. 获取常用联系人的聊天次数，并使用pyecharts绘制柱状图，生成对应得html文件
2. 根据输入的微信id，分析彼此之间所发消息类型，并使用pyecharts绘制饼图
3. 获取联系人年份，月份，日期，星期，yday，小时，分钟信息，并存入文件中（可用Excel做数据透视表）
4. 根据聊天内容进行分词，进而生成专属词云（使用jieba+wordcloud库）

# 使用说明：

使用时请先**仔细阅读**“**微信聊天记录数据提取并分析.md**”文件，如果已经提取到微信数据库中message表和contact表，并将之以utf-8格式存储，则可以直接修改wechet-anayze-main.py中main函数中message_file_path, contact_file_path为本机存储位置，wxid设置为想要分析的人的微信id，点击运行即可观察到结果。

# 文件说明：

heart.png: 设置词云形状的照片，如果想设置其他形状词云，可更换此照片

stopword.txt: 停用词文件，用于在词云中去除常用的停用词

wechet-anayze.py: 微信聊天记录分析的各个部分，内有详细注释，如想自行修改代码，建议阅读此代码

wechet-anayze-main.py: 主要内容于wechet-anayze.py相同，包含main函数，将文件路径及微信id自行设置后可直接运行

