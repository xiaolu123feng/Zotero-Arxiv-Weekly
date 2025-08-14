import numpy as np
from sentence_transformers import SentenceTransformer
from paper import ArxivPaper
from datetime import datetime

def rerank_paper(candidate: list[ArxivPaper], corpus: list[dict], 
                 model: str = 'avsolatorio/GIST-small-Embedding-v0',
                 tag_weights: dict[str, float] | None = None) -> list[ArxivPaper]:
    encoder = SentenceTransformer(model)

    # 按时间排序 corpus
    corpus = sorted(corpus, key=lambda x: datetime.strptime(x['dateAdded'], '%Y-%m-%d %H:%M:%S'), reverse=True)

    # 时间衰减权重
    time_decay_weight = 1 / (1 + np.log10(np.arange(len(corpus)) + 1))
    time_decay_weight = time_decay_weight / time_decay_weight.sum()

    # 语义特征向量
    corpus_feature = encoder.encode([paper['abstractNote'] for paper in corpus])
    candidate_feature = encoder.encode([paper.summary for paper in candidate])

    # 相似度矩阵 [n_candidate, n_corpus]
    sim = encoder.similarity(candidate_feature, corpus_feature)

    # 标签权重
    tag_weight_list = []
    for paper in corpus:
        weight = 1.0
        if tag_weights:
            for tag in paper.get("tags", []):
                if tag in tag_weights:
                    weight = max(weight, tag_weights[tag])  # 取最大标签权重
        tag_weight_list.append(weight)
    tag_weight_list = np.array(tag_weight_list)

    # 综合权重 = 时间衰减 * 标签权重
    final_weight = time_decay_weight * tag_weight_list
    final_weight = final_weight / final_weight.sum()

    # 计算最终得分
    scores = (sim * final_weight).sum(axis=1) * 10

    for s, c in zip(scores, candidate):
        c.score = s.item() if hasattr(s, 'item') else s

    candidate = sorted(candidate, key=lambda x: x.score, reverse=True)
    return candidate

