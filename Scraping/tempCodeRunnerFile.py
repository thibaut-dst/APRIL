import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import shutil
import fitz  # PyMuPDF for PDF to text conversion
import re
import urllib3
# 加载CSV文件，指定分隔符为 ;
file_path = "APRIL/Imput_voc/Sources.csv"  # 根据实际路径修改
df = pd.read_csv(file_path, sep=';')

# 去除列名中的多余空格
df.columns = df.columns.str.strip()

# 打印列名查看是否正确
print(df.columns)

# 访问 "Source gouvernementale" 列
sources = df['Source gouvernementale'].dropna()  # 使用正确的列名

# 对每个网址进行处理
for source in sources:
    url = source.strip()
    
    # 添加协议（http/https）到 URL
    if not url.startswith('http'):
        url = 'https://' + url
        
    try:
        # 尝试访问网站
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 如果响应失败则抛出异常
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 进一步处理网页（如爬取PDF等）
        # 以下为示例代码，具体爬取内容根据需求修改
        pdf_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].lower().endswith('.pdf')]
        print(f"Found PDF links: {pdf_links}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
