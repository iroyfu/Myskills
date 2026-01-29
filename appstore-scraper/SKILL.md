---
name: appstore-scraper
description: 基于Selenium的App Store应用市场图抓取工具，可批量抓取应用截图并生成详细报告
---

# App Store Scraper Skill

## 技能描述
基于Selenium的App Store应用市场图抓取工具，可批量抓取应用截图并生成详细报告。

## 功能
- 批量抓取App Store应用的市场截图
- 支持单个应用或多个应用的抓取
- 生成HTML格式的详细报告，包含应用信息和截图
- 生成JSON格式的数据文件，包含结构化的应用信息和截图URL
- 智能识别和过滤应用截图，只保留真正的市场图

## 依赖
- Python 3.7+
- selenium
- webdriver-manager

## 使用方法

### 基本使用
提供App Store应用URL，获取应用市场截图：

```python
from appstore_scraper_selenium import AppStoreScraperSelenium

# 创建抓取器实例
scraper = AppStoreScraperSelenium(output_dir="appstore_report")

# 抓取单个应用
result = scraper.scrape_app("https://apps.apple.com/app/id6449351247")

# 生成报告
html_report = scraper.generate_html_report([result])
json_report = scraper.generate_json_report([result])
```

### 批量抓取
```python
# 批量抓取多个应用
app_urls = [
    "https://apps.apple.com/us/app/id6449351247",
    "https://apps.apple.com/us/app/id1545593132"
]

results = scraper.scrape_multiple_apps(app_urls)
html_report = scraper.generate_html_report(results)
```

### 快速使用
1. 打开 `example_usage.py` 文件
2. 在 `app_urls` 列表中添加需要抓取的 App Store URL
3. 运行脚本: `python example_usage.py`
4. 查看生成的报告文件

## 输出
- **HTML报告**：包含应用信息和截图的详细报告
- **JSON数据**：结构化的应用信息和截图URL

## 技术特点
- 使用Selenium自动化浏览器进行无头浏览
- 动态内容加载，确保所有截图都能被捕获
- 智能解析srcset属性，提取干净的图片URL
- 智能过滤，只保留真正的应用市场截图
- 详细的错误处理和日志记录

## 注意事项
- 需要安装Chrome浏览器
- 首次运行会自动下载Chrome WebDriver
- 抓取过程可能需要一些时间，取决于网络速度和应用数量
