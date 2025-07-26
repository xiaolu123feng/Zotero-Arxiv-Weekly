import os
import sqlite3
from tqdm import tqdm
import arxiv
from recommender import rerank_paper
from paper import ArxivPaper
from pprint import pprint
from datetime import datetime, timedelta, timezone
from arxiv_query import download_arxiv_pdfs

# 路径配置
local_storage_path = r"C:\Users\username\Zotero" # 替换为你的Zotero本地存储路径
arxiv_query = "cs.AI,cs.LG" # 替换为你感兴趣的arXiv分类，逗号分隔
categories = arxiv_query.split(",")
max_paper_num = 50 # 最多返回的论文数量
save_dir=r"D:\test" # 替换为你想保存论文PDF的本地目录


# 1 读取 Zotero 本地文献,并忽略Zotero里面的ignore标签，不想添加到查询范围的文献可以在Zotero里面加上ignore标签
def get_zotero_corpus(zotero_dir: str) -> list[dict]:
    db_path = os.path.join(zotero_dir, 'zotero.sqlite')
    storage_path = os.path.join(zotero_dir, 'storage')
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"未找到数据库文件：{db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
    SELECT items.itemID, itemDataValues.value AS abstractNote,
           items.key AS itemKey, itemTypes.typeName,
           itemAttachments.path AS filePath, items.dateAdded
    FROM items
    LEFT JOIN itemData ON items.itemID = itemData.itemID
    LEFT JOIN itemDataValues ON itemData.valueID = itemDataValues.valueID
    LEFT JOIN fields ON itemData.fieldID = fields.fieldID
    LEFT JOIN itemTypes ON items.itemTypeID = itemTypes.itemTypeID
    LEFT JOIN itemAttachments ON items.itemID = itemAttachments.parentItemID
    -- 排除包含标签 "ignore" 的项
    WHERE fields.fieldName = 'abstractNote'
      AND itemDataValues.value IS NOT NULL
      AND items.itemID NOT IN (
          SELECT itemTags.itemID
          FROM itemTags
          JOIN tags ON itemTags.tagID = tags.tagID
          WHERE LOWER(tags.name) = 'ignore'
      )
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    corpus = []
    for row in rows:
        item = {
            "itemID": row["itemID"],
            "itemKey": row["itemKey"],
            "type": row["typeName"],
            "abstractNote": row["abstractNote"],
            "filePath": row["filePath"] if row["filePath"] else "",
            "storagePath": os.path.join(storage_path, row["itemKey"]),
            "dateAdded": row["dateAdded"],
        }
        corpus.append(item)
    return corpus


# 2. 获取arXiv论文
def get_recent_papers_by_categories(categories: list[str]) -> dict[str, list[ArxivPaper]]:
    client = arxiv.Client(num_retries=10, delay_seconds=10)

    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=3)

    all_results = {}

    for cat in categories:
        print(f"正在获取分类 {cat} 的论文")
        search = arxiv.Search(
            query=f"cat:{cat}",
            max_results=100,  # 每个分类最多查询100篇文献
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        papers = []
        bar = tqdm(desc=f"{cat}", unit="篇")
        for result in client.results(search):
            if start_date <= result.published <= end_date:
                papers.append(ArxivPaper(result))
                bar.update(1)
            else:
                break  
        bar.close()
        all_results[cat] = papers

    return all_results


def main():
    print("正在读取 Zotero 本地文献摘要...")
    corpus = get_zotero_corpus(local_storage_path)
    print(f"共读取到 {len(corpus)} 篇文献。")
    
    print("正在从 arXiv 获取新论文...")
    papers_dict = get_recent_papers_by_categories(categories)
    all_papers = []
    for category, papers in papers_dict.items():
        all_papers.extend(papers)
    print(f"共获取到 {len(all_papers)} 篇新论文。")

    if not all_papers:
        print("没有获取到任何论文。")
        return []

    print("正在根据相似度进行筛选和排序...")
    papers_reranked = rerank_paper(all_papers, corpus)
    papers = papers_reranked[:max_paper_num]


    # 返回论文ID列表并下载到本地
    arxiv_ids = [p.arxiv_id for p in papers]
    download_arxiv_pdfs(arxiv_ids, save_dir)
    print(f"筛选后论文ID列表（共{len(arxiv_ids)}篇）：")
    pprint(arxiv_ids)

    return arxiv_ids

if __name__ == '__main__':
    main()

