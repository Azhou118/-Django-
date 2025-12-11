import jieba
from matplotlib import pyplot as plt
from wordcloud import WordCloud
import numpy as np
from PIL import Image
from pymysql import connect

def get_img(field, targetImageSrc, resImageSrc):
    # 连接数据库
    conn = connect(host='localhost', user='root', password='330069676', database='dbbook', port=3306, charset='utf8mb4')
    cursor = conn.cursor()

    # 执行查询
    sql = f"select {field} from booklist"
    cursor.execute(sql)
    data = cursor.fetchall()

    # 提取文本数据
    text = ''
    for i in data:
        if i[0] != '':
            tarArr = i
            for j in tarArr:
                text += j

    # 打印查看文本内容
    # print(text)

    cursor.close()
    conn.close()

    # 分词处理
    data_cut = jieba.cut(text, cut_all=False)
    string = ' '.join(data_cut)  # 使用空格分隔每个词

    # 加载蒙版图片并转换为灰度图
    img = Image.open(targetImageSrc)
    ima_arr = np.array(img)

    # 生成词云
    wc = WordCloud(
        background_color='#fff',  # 背景色为白色
        font_path='STHUPO.TTF',  # 可以替换为系统字体，如 SimHei
        width=1000,  # 设置图片宽度
        height=800,  # 设置图片高度
        max_font_size=200,  # 最大字体大小
        min_font_size=10,  # 最小字体大小
        max_words=400,  # 显示最大词数
        mask=ima_arr,  # 使用蒙版
        random_state=42,  # 设置随机种子，保证结果一致性
        collocations=False,  # 避免重复计算词语组合
        scale=2  # 提高生成精度
    )

    wc.generate_from_text(string)

    # 绘制并保存词云图
    plt.figure(figsize=(10, 8))  # 设置图像的大小
    plt.imshow(wc, interpolation="bilinear")  # 插值方式为双线性
    plt.axis('off')  # 不显示坐标轴

    # 保存图像
    plt.savefig(resImageSrc, dpi=300, format='PNG', bbox_inches='tight', pad_inches=0)

    # 显示生成的词云图
    plt.show()

# 调用函数生成词云图
get_img('title', './static/tree.jpg', './static/cloudImg/titleCloud.png')
get_img('summary', './static/love.jpg', './static/cloudImg/summaryCloud.png')