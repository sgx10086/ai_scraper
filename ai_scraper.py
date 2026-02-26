#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 近7天“刚诞生就爆火”项目自动抓取器（完整修复版）
功能：
- 自动计算过去7天
- 支持所有语言（默认）或指定语言（如Python）
- 安全处理 description=None、language=None
- 处理API速率限制提示
- 输出美观中文结果

使用方法：
1. 保存为 ai_scraper.py
2. pip install requests
3. python ai_scraper.py
4. 想只看Python项目：把下面 lang=None 改成 lang="Python"
5. 想看更多：把 min_stars 调低到 100~200

推荐每天跑一次，可放入 GitHub Actions 定时任务
"""

import requests
from datetime import datetime, timedelta


def get_hot_new_repos(days=7, min_stars=300, lang=None, top_n=15):
    # 动态计算7天前日期（UTC）
    today = datetime.utcnow().date()
    since_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")

    # 构建搜索条件
    query = f"created:>={since_date} stars:>={min_stars}"
    if lang:
        query += f" language:{lang}"

    url = "https://api.github.com/search/repositories"
    headers = {
        "Accept": "application/vnd.github+json",
        # 如有GitHub Token（强烈推荐，限额更高）：
        # "Authorization": "Bearer ghp_xxxxxxxxxxxxxxxxxxxxxxxx"
    }

    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": 100,
        "page": 1
    }

    print(f"🔍 搜索条件: {query}")
    print(f"🎯 正在获取前 {top_n} 个「近7天新建 + 较高star」的项目...\n")

    repos = []
    page = 1
    max_pages = 10  # 防止无限循环

    while len(repos) < top_n and page <= max_pages:
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 403:
            print("❌ GitHub API 速率限制！请等待 1 小时后再试，或添加 GitHub Token")
            break
        if response.status_code != 200:
            print(f"❌ 请求失败 (状态码 {response.status_code})")
            print(response.text)
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
                "language": repo.get("language") or "未知",
                "description": repo.get("description") or "暂无描述",
                "url": repo["html_url"]
            })

        if len(items) < 100:  # 最后一页
            break
        page += 1

    # 按 star 降序（API 已排序，保险起见再排一次）
    repos.sort(key=lambda x: x["stars"], reverse=True)

    return repos[:top_n]


if __name__ == "__main__":
    # ================== 在这里修改配置 ==================
    hot_repos = get_hot_new_repos(
        days=7,          # 近7天
        min_stars=300,   # “爆火”门槛（建议 300~500，可改成100看更多候选）
        lang=None,       # None=全GitHub；"Python"=只看Python；"Rust"=只看Rust等
        top_n=15         # 显示前多少个
    )
    # ====================================================

    if not hot_repos:
        print("❌ 未找到符合条件的项目")
        print("💡 建议：把 min_stars 改小一点（例如100），或者把 days 改成 10")
    else:
        print(f"✅ 成功找到 {len(hot_repos)} 个近7天新建且较火的项目（截至 {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC）\n")
        
        for i, r in enumerate(hot_repos, 1):
            print(f"{i:2d}. {r['full_name']}")
            print(f"   ★ {r['stars']:,}   forks: {r['forks']:,}")
            print(f"   {r['language']} | 创建于: {r['created_at'][:10]}")
            
            # 安全截取描述
            desc = r['description']
            truncated = desc[:120] + ("..." if len(desc) > 120 else "")
            print(f"   {truncated}")
            
            print(f"   🔗 {r['url']}\n")
        
        print("🚀 祝你早日发现下一个现象级项目！")
