import requests
import os
from datetime import datetime, timedelta

def fetch_latest_ai_repos():
    # 获取环境变量中的 Token（GitHub Actions 会自动传入）
    github_token = os.getenv("MY_GITHUB_TOKEN")
    
    # 获取过去24小时内的日期
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    url = "https://api.github.com/search/repositories"
    query = f'(topic:ai OR topic:llm OR topic:machine-learning OR topic:deep-learning OR topic:gpt) created:>={yesterday}'
    
    params = {
        'q': query,
        'sort': 'stars',
        'order': 'desc',
        'per_page': 10
    }
    
    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }
    
    if github_token:
        headers['Authorization'] = f'token {github_token}'
        
    print(f"🔍 正在搜索 {yesterday} 之后创建的最新 AI 项目...\n")
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        repos = data.get('items',[])
        
        if not repos:
            print("今天暂时没有热门的新 AI 项目产生。")
            return

        print(f"📊 成功收集到 {len(repos)} 个最新 AI 项目：\n")
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
