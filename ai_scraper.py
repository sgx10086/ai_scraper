import requests
import os
from datetime import datetime, timedelta

def fetch_latest_ai_repos():
    # 获取环境变量中的 Token
    github_token = os.getenv("MY_GITHUB_TOKEN")
    
    # 【修改点1】将时间改为 30 天前
    last_month_date = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    url = "https://api.github.com/search/repositories"
    
    # 搜索条件：标签包含AI相关，且创建时间在近1个月内
    query = f'(topic:ai OR topic:llm OR topic:machine-learning OR topic:deep-learning OR topic:gpt) created:>={last_month_date}'
    
    params = {
        'q': query,
        'sort': 'stars',   # 依然按星标（Star）数量降序排列，找出这一个月内最火的项目
        'order': 'desc',
        'per_page': 20     # 【修改点2】将获取数量提升到前 20 名（最大可以改成100）
    }
    
    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }
    
    if github_token:
        headers['Authorization'] = f'token {github_token}'
        
    print(f"🔍 正在搜索 {last_month_date} 之后（近1个月内）创建的最高星 AI 项目...\n")
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        repos = data.get('items',[])
        
        if not repos:
            print("这段时间内暂时没有符合条件的新 AI 项目。")
            return

        print(f"📊 成功收集到 {len(repos)} 个近1个月内最火的 AI 项目：\n")
        print("-" * 40)
        
        for i, repo in enumerate(repos, 1):
            name = repo.get('full_name')
            desc = repo.get('description') or "无描述"
            url = repo.get('html_url')
            stars = repo.get('stargazers_count')
            language = repo.get('language') or "未知"
            topics = repo.get('topics',[])
            
            print(f"【{i}】{name} (⭐ {stars} stars)")
            print(f"  📝 描述: {desc}")
            print(f"  💻 语言: {language}")
            print(f"  🏷️ 标签: {', '.join(topics[:5])}")
            print(f"  🔗 链接: {url}")
            print("-" * 40)
            
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print(response.json())

if __name__ == "__main__":
    fetch_latest_ai_repos()
