# Zotero-Arxiv-Weekly
非常简陋的，从本地Zotero读取存储文献摘要，与Arxiv选中领域的最新论文的摘要进行余弦相似度比对，并返回最相关的文献的工，适配以下文献管理模式：
1. 使用Zotero local版本
2. 本地Zotero文件夹里具备zotero.sqlite文件，可查找文献摘要等字段

# 环境配置
```
conda env create -f environment.yml
```

# 路径配置
`main.py`
```
# 路径配置
local_storage_path = r"C:\Users\username\Zotero" # 替换为你的Zotero本地存储路径(包含zotero.sqlite文件)
arxiv_query = "cs.AI,cs.LG" # 替换为你感兴趣的arXiv分类，逗号分隔
categories = arxiv_query.split(",")
max_paper_num = 50 # 最多返回的论文数量
save_dir=r"D:\test" # 替换为你想保存论文PDF的本地目录
```

# 下载与运行
```
git clone https://github.com/xiaolu123feng/Zotero-Arxiv-Weekly.git
cd Zotero-Arxiv-Weekly
python main.py
```
