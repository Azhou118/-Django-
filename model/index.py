import os
import django
import json
import numpy as np
from tqdm import tqdm

# 设置 Django 环境变量并初始化 Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doubantushu.settings')
django.setup()

# 导入 Django 数据模型
from myApp.models import BookList, User


# 获取所有用户的评分数据
def getAllData():
    allData = BookList.objects.all()  # 获取所有书籍数据
    commentList = []

    # 遍历所有书籍数据
    for i in allData:
        comment_list = json.loads(i.commentList)  # 解析 JSON 格式的评论数据
        for j in comment_list:
            commentList.append(j)
            j['realId'] = i.id  # 记录书籍的真实 ID

    rateList = []
    # 整理评分数据，转换为 [userId, bookId, rating, createTime, realId] 格式
    for i in comment_list:
        rateList.append([int(i['userId']), int(i['bookId']), int(i['star']), i['createTime'], int(i['realId'])])

    return rateList


# 生成用户-物品评分矩阵
def getUIMat(data):
    user_list = [i[0] for i in data]  # 获取所有用户 ID
    item_list = [i[1] for i in data]  # 获取所有物品（书籍）ID

    # 创建一个用户-物品矩阵，大小为 (max(user_list)+1, max(item_list)+1)
    UI_matrix = np.zeros((max(user_list) + 1, max(item_list) + 1))

    # 遍历评分数据，将评分填充到矩阵中
    for each_interaction in tqdm(data, total=len(data)):
        UI_matrix[each_interaction[0]][each_interaction[1]] = each_interaction[2]

    return UI_matrix


# 矩阵分解类（基于梯度下降的矩阵分解）
class MF():
    def __init__(self, R, K, alpha, beta, iterations):
        """
        :param R: 用户-物品评分矩阵
        :param K: 潜在因子数量
        :param alpha: 学习率
        :param beta: 正则化参数
        :param iterations: 迭代次数
        """
        self.R = R
        self.num_users, self.num_items = R.shape  # 获取用户数和物品数
        self.K = K
        self.alpha = alpha
        self.beta = beta
        self.iterations = iterations

    # 训练模型
    def train(self):
        """
        通过随机梯度下降 (SGD) 训练矩阵分解模型
        """
        # 初始化用户特征矩阵 P 和物品特征矩阵 Q
        self.P = np.random.normal(scale=1. / self.K, size=(self.num_users, self.K))
        self.Q = np.random.normal(scale=1. / self.K, size=(self.num_items, self.K))

        # 初始化用户偏差、物品偏差和整体偏差
        self.b_u = np.zeros(self.num_users)
        self.b_i = np.zeros(self.num_items)
        self.b = np.mean(self.R[np.where(self.R != 0)])  # 计算所有非零评分的均值作为全局偏差

        # 创建训练样本（所有非零评分的 (用户, 物品, 评分)）
        self.samples = [
            (i, j, self.R[i, j])
            for i in range(self.num_users)
            for j in range(self.num_items)
            if self.R[i, j] > 0
        ]

        training_process = []
        for i in tqdm(range(self.iterations), total=self.iterations):
            np.random.shuffle(self.samples)  # 随机打乱训练数据
            self.sgd()  # 进行一次梯度下降更新

            mse = self.mse()  # 计算当前模型的误差
            training_process.append((i, mse))

        return training_process

    # 计算均方误差
    def mse(self):
        xs, ys = self.R.nonzero()  # 获取所有非零评分的索引
        predicted = self.full_matrix()  # 计算当前模型的预测评分矩阵
        error = 0
        for x, y in zip(xs, ys):
            error += pow(self.R[x, y] - predicted[x, y], 2)  # 计算误差的平方
        return np.sqrt(error)  # 计算均方根误差

    # 随机梯度下降更新 P、Q、b_u、b_i
    def sgd(self):
        for i, j, r in self.samples:
            prediction = self.get_rating(i, j)  # 计算预测评分
            e = (r - prediction)  # 计算误差

            # 更新偏差项
            self.b_u[i] += self.alpha * (e - self.beta * self.b_u[i])
            self.b_i[j] += self.alpha * (e - self.beta * self.b_i[j])

            # 更新 P 和 Q
            self.P[i, :] += self.alpha * (e * self.Q[j, :] - self.beta * self.P[i, :])
            self.Q[j, :] += self.alpha * (e * self.P[i, :] - self.beta * self.Q[j, :])

    # 计算用户 i 对物品 j 的预测评分
    def get_rating(self, i, j):
        return self.b + self.b_u[i] + self.b_i[j] + self.P[i, :].dot(self.Q[j, :].T)

    # 计算完整的用户-物品评分预测矩阵
    def full_matrix(self):
        return self.b + self.b_u[:, np.newaxis] + self.b_i[np.newaxis:, ] + self.P.dot(self.Q.T)


# 书籍推荐模型
def modelFn(each_user):
    """
    为指定用户推荐书籍
    :param each_user: 用户 ID
    :return: 推荐书籍的 ID 列表（按照推荐程度排序）
    """
    starList = getAllData()  # 获取所有评分数据

    # 构建 (用户 ID, 真实书籍 ID, 评分) 数据集
    obs_dataset = []
    for i in starList:
        obs_dataset.append([i[0], i[4], i[2]])

    # 生成用户-物品评分矩阵
    R = getUIMat(obs_dataset)

    # 训练矩阵分解模型
    mf = MF(R, K=2, alpha=0.1, beta=0.8, iterations=10)
    mf.train()

    # 获取指定用户的预测评分
    user_ratings = mf.full_matrix()[each_user].tolist()

    # 对书籍进行排序，获取推荐结果
    topN = [(i, user_ratings.index(i)) for i in user_ratings]
    topN = [i[1] for i in sorted(topN, key=lambda x: x[0], reverse=True)]

    return topN  # 返回推荐书籍的 ID 列表


if __name__ == '__main__':
    print(modelFn(1))  # 测试推荐系统，获取用户 1 的推荐书籍列表
