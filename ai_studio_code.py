import requests
from datetime import datetime, timedelta

def fetch_latest_ai_repos(github_token=None):
    # 计算昨天的日期，格式为 YYYY-MM-DD
    # 这样可以获取过去24小时内最新创建的项目
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # GitHub 搜索 API 地址
    url = "https://api.github.com/search/repositories"
    
    # 构建搜索查询语句 (Query)
    # 关键词：包含 ai, llm, machine-learning, deep-learning, gpt 标签的项目
    # 时间：在昨天之后创建的
    query = f'(topic:ai OR topic:llm OR topic:machine-learning OR topic:deep-learning OR topic:gpt) created:>={yesterday}'
    
    params = {
        'q': query,
        'sort': 'stars',   # 按星标数量排序，找出刚发布就受欢迎的项目
        'order': 'desc',   # 降序
        'per_page': 10     # 每次获取前 10 个（可修改，最大100）
    }
    
    # 设置请求头
    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # 如果有 Token，加入请求头以提升 API 调用额度
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
            print(f"  🏷️ 标签: {', '.join(topics[:5])}") # 只显示前5个标签
            print(f"  🔗 链接: {url}")
            print("-" * 40)
            
        # 这里你可以拓展代码，比如将数据保存到 TXT/CSV，或者发送到微信/钉钉/Telegram
            
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print(response.json())

if __name__ == "__main__":
    # 【强烈建议】填入你的 GitHub Token 以防触发 API 频率限制。
    # 申请地址：GitHub -> Settings -> Developer settings -> Personal access tokens (Tokens (classic)) -> Generate new token
    GITHUB_TOKEN = "" # 在引号内填入你的 token，留空也能运行但次数受限
    
    fetch_latest_ai_repos(GITHUB_TOKEN)