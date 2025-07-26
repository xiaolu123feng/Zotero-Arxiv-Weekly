import numpy as np
from sentence_transformers import SentenceTransformer
from paper import ArxivPaper
from datetime import datetime

def rerank_paper(candidate: list[ArxivPaper], corpus: list[dict], model: str = 'avsolatorio/GIST-small-Embedding-v0') -> list[ArxivPaper]:
    encoder = SentenceTransformer(model)

    # 按时间排序 corpus，时间格式为 '2025-04-14 06:05:28'
    corpus = sorted(corpus, key=lambda x: datetime.strptime(x['dateAdded'], '%Y-%m-%d %H:%M:%S'), reverse=True)

    time_decay_weight = 1 / (1 + np.log10(np.arange(len(corpus)) + 1))
    time_decay_weight = time_decay_weight / time_decay_weight.sum()

    # 计算语义特征向量
    corpus_feature = encoder.encode([paper['abstractNote'] for paper in corpus])
    candidate_feature = encoder.encode([paper.summary for paper in candidate])

    # 计算相似度矩阵 [n_candidate, n_corpus]
    sim = encoder.similarity(candidate_feature, corpus_feature)

    # 按时间衰减加权求和得分
    scores = (sim * time_decay_weight).sum(axis=1) * 10  # [n_candidate]

    # 给 candidate 添加 score 属性
    for s, c in zip(scores, candidate):
        c.score = s.item() if hasattr(s, 'item') else s

    # 按分数排序 candidate，从高到低
    candidate = sorted(candidate, key=lambda x: x.score, reverse=True)

    return candidate
