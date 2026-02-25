# -*- coding: utf-8 -*-
"""
获取 GitHub 最近7天创建且 star 数最高的仓库（近似“刚诞生就爆火”）
每天运行一次，调整 created: 日期和 stars 阈值
需要 pip install requests python-dateutil
"""

import requests
from datetime import datetime, timedelta
import json

def get_hot_new_repos(days=7, min_stars=300, lang=None, top_n=20):
    today = datetime.utcnow().date()
    since_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")

    query = f"created:>={since_date} stars:>={min_stars}"
    if lang:
        query += f" language:{lang}"

    url = "https://api.github.com/search/repositories"
    headers = {
        "Accept": "application/vnd.github+json",
        # "Authorization": "Bearer YOUR_TOKEN"   # 有token可大幅提高限额
    }

    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": 100,   # 最大100
        "page": 1
    }

    print(f"搜索条件: {query}")
    print(f"正在获取前 {top_n} 个...\n")

    repos = []
    while len(repos) < top_n:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print("API 请求失败:", response.json().get("message", "未知错误"))
            break

        data = response.json()
        items = data.get("items", [])
        if not items:
            break

        for repo in items:
            repos.append({
                "full_name": repo["full_name"],
                "stars": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "created_at": repo["created_at"],
                "language": repo["language"],
                "description": repo.get("description", "无描述"),
                "url": repo["html_url"]
            })

        if len(items) < 100:
            break
        params["page"] += 1

    # 按star降序排序（API已排序，但以防万一）
    repos.sort(key=lambda x: x["stars"], reverse=True)

    return repos[:top_n]


if __name__ == "__main__":
    # 示例：获取最近7天，star >= 300 的 Python 项目前10个
    hot_repos = get_hot_new_repos(days=7, min_stars=300, lang="Python", top_n=10)

    if hot_repos:
        print("\n近7天创建且star较高的Python项目（可能刚诞生就火）：")
        for i, r in enumerate(hot_repos, 1):
            print(f"{i:2d}. {r['full_name']}")
            print(f"   ★ {r['stars']:,}   forks: {r['forks']:,}")
            print(f"   {r['language']} | 创建: {r['created_at'][:10]}")
            print(f"   {r['description'][:120]}{'...' if len(r['description'])>120 else ''}")
            print(f"   {r['url']}\n")
    else:
        print("暂未找到符合条件的项目，尝试降低 min_stars 或去掉 language 限制")
