import numpy as np
import pandas as pd
import math
import pickle  # 用于保存和加载模型


# 计算TF
def compute_tf(documents):
    tf = []
    for doc in documents:
        word_count = {}
        for word in doc.split():
            word_count[word] = word_count.get(word, 0) + 1
        tf.append(word_count)
    return tf


# 计算IDF
def compute_idf(documents):
    total_docs = len(documents)
    word_document_count = {}
    for doc in documents:
        unique_words = set(doc.split())
        for word in unique_words:
            word_document_count[word] = word_document_count.get(word, 0) + 1

    idf = {}
    for word, count in word_document_count.items():
        idf[word] = np.log(total_docs / count)
    return idf


# 计算TF-IDF
def compute_tfidf(documents, word_index, idf):
    tf = compute_tf(documents)

    # 构建TF-IDF矩阵
    tfidf_matrix = np.zeros((len(documents), len(word_index)))

    for doc_idx, doc in enumerate(documents):
        tf_dict = tf[doc_idx]
        for word, count in tf_dict.items():
            if word in word_index:
                tfidf_matrix[doc_idx, word_index[word]] = count * idf.get(word, 0)

    return tfidf_matrix


# K-means聚类算法
def kmeans(tfidf_features, k=3, max_iters=100):
    # 随机选择k个中心点
    centers = tfidf_features[np.random.choice(tfidf_features.shape[0], k, replace=False)]

    for _ in range(max_iters):
        # 步骤 1：分配每个数据点到最近的中心
        clusters = [[] for _ in range(k)]
        for i, doc in enumerate(tfidf_features):
            distances = np.linalg.norm(tfidf_features[i] - centers, axis=1)
            closest_center = np.argmin(distances)
            clusters[closest_center].append(i)

        # 步骤 2：更新每个簇的中心
        new_centers = []
        for cluster in clusters:
            if cluster:
                new_center = np.mean(tfidf_features[cluster], axis=0)
                new_centers.append(new_center)
            else:
                new_centers.append(np.zeros_like(centers[0]))  # 处理空簇

        centers = np.array(new_centers)

    return clusters, centers


# 假设你已经训练好了模型，并且有以下数据：
comments = [
    "a tad bit anxious, and the winter in london has not been helpful",
    "feeling good",
    "feeling sad",
    "I am really happy",
    "stressed out from work",
    "feeling balanced and focused",
    "a bit anxious about the future",
    "feeling calm and relaxed",
    "feeling low, depressed"
]

# TF-IDF特征和K-means聚类
all_words = set(word for doc in comments for word in doc.split())  # 提取所有词汇
word_index = {word: idx for idx, word in enumerate(all_words)}  # 为每个词汇创建索引
idf = compute_idf(comments)  # 计算IDF

# 计算TF-IDF矩阵
tfidf_features = compute_tfidf(comments, word_index, idf)

# 使用K-means进行聚类
clusters, centers = kmeans(tfidf_features, k=5)

# 保存模型：保存词汇表、IDF和聚类中心
model = {
    'word_index': word_index,
    'idf': idf,
    'centers': centers
}

# 检查是否已经保存模型
try:
    with open('emotion_model.pkl', 'rb') as f:
        model = pickle.load(f)
#    print("load！")
except FileNotFoundError:
    with open('emotion_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    print("saved")
