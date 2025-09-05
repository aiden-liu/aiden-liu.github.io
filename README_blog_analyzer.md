# Blog Analyzer

This script analyzes the current blog posts in this GitHub Pages repository and provides statistics about them.

## Usage

```bash
python3 blog_analyzer.py
```

## What it does

- Lists all current blog posts from `blogBase.json`
- Counts the total number of blogs
- Identifies which blogs are empty (word count = 0 or no description)
- Provides detailed statistics and summaries

## Current Blog Status

As of the last analysis:
- **Total blogs**: 17
- **Empty blogs**: 7 (41.2%)
- **Blogs with content**: 10 (58.8%)

### Empty blogs that need content:
1. Log Analytics Workspace（部署篇）
2. Cloudflare域名代理，白嫖起来  
3. PostgreSQL 总结 (开发篇)
4. PostgreSQL 总结 (运维篇)
5. OSI层级是啥，咋弄，为啥
6. API Management stv2（迁移篇）
7. Log Analytics Workspace（使用篇）

The script helps track which blog posts have been created as placeholders but still need content to be written.