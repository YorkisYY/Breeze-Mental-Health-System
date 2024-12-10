import numpy as np
import pickle
from trainModal import compute_tfidf
# 加载模型
with open('emotion_model.pkl', 'rb') as f:
    model = pickle.load(f)

word_index = model['word_index']
idf = model['idf']
centers = model['centers']


# 新数据情绪识别
def predict_emotion(new_document, word_index, idf, centers):
    # 计算新文档的TF-IDF特征
    new_tfidf = compute_tfidf([new_document], word_index, idf)[0]  # 计算新文档的TF-IDF特征

    # 计算新文档与每个聚类中心的距离
    distances = np.linalg.norm(centers - new_tfidf, axis=1)  # 计算与每个簇中心的距离

    # 找到距离最小的中心
    cluster_id = np.argmin(distances)
    return cluster_id


# 使用已加载的模型进行预测
new_comment = "die"
predicted_cluster = predict_emotion(new_comment, word_index, idf, centers)
print(f"Predicted cluster for the new comment: {predicted_cluster}")
