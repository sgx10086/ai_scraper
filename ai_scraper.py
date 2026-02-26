#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub 近7天爆火新项目抓取器 → 生成静态 HTML 网页版
输出：index.html（可直接托管到 GitHub Pages）
每个项目包含：名称、主要内容（description）、stars/forks、语言、创建日期、链接
"""
import requests
from datetime import datetime, timedelta
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

def get_hot_new_repos(days=7, min_stars=300, lang=None, top_n=15):
    today = datetime.utcnow().date()
    since_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")

    query = f"created:>={since_date} stars:>={min_stars}"
    if lang:
        query += f" language:{lang}"

    url = "https://api.github.com/search/repositories"
    headers = {"Accept": "application/vnd.github+json"}
    # headers["Authorization"] = "Bearer ghp_你的token"  # 推荐加 token 防限速

    params = {"q": query, "sort": "stars", "order": "desc", "per_page": 100, "page": 1}

    print(f"🔍 搜索: {query}")
    repos = []
    page = 1
    while len(repos) < top_n and page <= 10:
        params["page"] = page
        try:
            r = requests.get(url, headers=headers, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()
            items = data.get("items", [])
            if not items:
                break
            for repo in items:
                repos.append({
                    "full_name": repo["full_name"],
                    "stars": repo["stargazers_count"],
                    "forks": repo["forks_count"],
                    "created_at": repo["created_at"][:10],
                    "language": repo.get("language") or "未知",
                    "description": repo.get("description") or "暂无描述",
                    "url": repo["html_url"]
                })
            if len(items) < 100:
                break
            page += 1
        except Exception as e:
            print(f"请求失败: {e}")
            break

    repos.sort(key=lambda x: x["stars"], reverse=True)
    return repos[:top_n]

# ================== Jinja2 模板字符串（简单美观） ==================
TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub 近 {{ days }} 天爆火新项目（{{ today }}）</title>
    <style>
        body { font-family: system-ui, sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 20px; background: #f8f9fa; color: #333; }
        h1 { color: #0366d6; text-align: center; }
        .intro { text-align: center; color: #586069; }
        ol { padding-left: 20px; }
        li { margin: 20px 0; padding: 15px; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        a { color: #0366d6; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .meta { color: #586069; font-size: 0.95em; margin: 8px 0; }
        .desc { margin: 12px 0; }
        footer { text-align: center; margin-top: 40px; color: #888; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>GitHub 近 {{ days }} 天新建且高 Star 项目</h1>
    <p class="intro">前 {{ repos|length }} 名（stars ≥ {{ min_stars }} {% if lang %} | 语言：{{ lang }}{% endif %}）<br>
    数据时间：{{ update_time }} UTC | 自动更新</p>

    <ol>
    {% for r in repos %}
        <li>
            <strong><a href="{{ r.url }}" target="_blank">{{ r.full_name }}</a></strong>
            <div class="meta">
                ★ {{ r.stars | int | default(0) | string | replace(',', ',') }} &nbsp; forks: {{ r.forks }}
                &nbsp; • &nbsp; {{ r.language }} &nbsp; • &nbsp; 创建于 {{ r.created_at }}
            </div>
            <div class="desc"><strong>主要内容：</strong> {{ r.description | safe }}</div>
            <a href="{{ r.url }}" target="_blank">→ 查看项目</a>
        </li>
    {% endfor %}
    </ol>

    <footer>
        由 Python 脚本自动生成 · <a href="https://github.com/你的用户名/你的仓库名">源代码</a> · 每天更新 · 发现下一个爆款！
    </footer>
</body>
</html>
"""

def generate_html(repos, days, min_stars, lang=None):
    today = datetime.now().strftime("%Y-%m-%d")
    update_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M")

    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(['html', 'xml'])
    )
    # 因为用字符串模板，直接用 from_string
    template = env.from_string(TEMPLATE)

    html_content = template.render(
        days=days,
        today=today,
        repos=repos,
        min_stars=min_stars,
        lang=lang,
        update_time=update_time
    )

    output_file = "index.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ 已生成网页: {os.path.abspath(output_file)}")
    print(f"   打开浏览器查看: file://{os.path.abspath(output_file)}")

if __name__ == "__main__":
    # ================== 配置 ==================
    DAYS = 7
    MIN_STARS = 300
    LANGUAGE = None       # "Python", "Rust" 等
    TOP_N = 15
    # ==========================================

    hot_repos = get_hot_new_repos(days=DAYS, min_stars=MIN_STARS, lang=LANGUAGE, top_n=TOP_N)

    if not hot_repos:
        print("❌ 未找到项目，建议降低 min_stars")
    else:
        generate_html(hot_repos, DAYS, MIN_STARS, LANGUAGE)
        print(f"找到 {len(hot_repos)} 个项目，已生成 index.html")
