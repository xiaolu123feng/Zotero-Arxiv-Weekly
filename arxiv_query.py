import os
import urllib.request
from tqdm import tqdm

def download_arxiv_pdfs(arxiv_ids, save_dir): 
    """
    根据arXiv ID列表批量下载PDF。
    
    参数:
        arxiv_ids: list[str] - arXiv论文ID列表，如 ['2507.11806', '2507.10530']
        save_dir: str - 保存PDF的本地目录
        
    返回:
        None
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    base_pdf_url = "https://arxiv.org/pdf/"
    
    for arxiv_id in tqdm(arxiv_ids, desc="Downloading PDFs"):
        # 生成PDF的完整URL
        pdf_url = f"{base_pdf_url}{arxiv_id}.pdf"
        local_path = os.path.join(save_dir, f"{arxiv_id}.pdf")
        
        # 如果已存在就跳过
        if os.path.exists(local_path):
            tqdm.write(f"已存在，跳过: {arxiv_id}.pdf")
            continue
        
        try:
            urllib.request.urlretrieve(pdf_url, local_path)
            tqdm.write(f"下载成功: {arxiv_id}.pdf")
        except Exception as e:
            tqdm.write(f"下载失败: {arxiv_id}.pdf，错误: {e}")

def main():
    # download_arxiv_pdfs测试函数，main.py中不使用这部分代码
    arxiv_ids = ['2507.11806',
                '2507.11806',]

    print(f"准备下载 {len(arxiv_ids)} 篇论文PDF到D盘arxiv_week目录。")
    download_arxiv_pdfs(arxiv_ids)
    print("下载完成。")

if __name__ == "__main__":
    main()