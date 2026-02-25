import requests
import os
from datetime import datetime, timedelta

def fetch_latest_trending_repos():
    # 获取环境变量中的 Token
    github_token = os.getenv("MY_GITHUB_TOKEN")
    
    # 【修改点1】将时间改为 7 天前（近1周）
    last_week_date = (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    url = "https://api.github.com/search/repositories"
    
    # 【修改点2】去掉了 topic 限制，只搜索近1周内创建的所有项目
    query = f'created:>={last_week_date}'
    
    params = {
        'q': query,
        'sort': 'stars',   # 按星标（Star）数量降序排列，寻找这周最受关注的项目
        'order': 'desc',
        'per_page': 20     # 获取排名前 20 的项目（你可以自己改成 30 或 50）
    }
    
    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }
    
    if github_token:
        headers['Authorization'] = f'token {github_token}'
        
    print(f"🔍 正在搜索 {last_week_date} 之后（近1周内）诞生的全球最高星开源项目...\n")
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        repos = data.get('items',
