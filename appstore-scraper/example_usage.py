#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App Store Scraper Skill 使用示例

使用方法:
1. 运行此脚本: python example_usage.py
2. 在运行时输入App Store URL，每行一个，输入"done"结束
3. 查看生成的报告文件
"""

import logging
from appstore_scraper_selenium import AppStoreScraperSelenium

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("=== App Store Scraper Skill 市场图抓取 ===")
    
    # 动态获取用户输入的URL
    app_urls = []
    logger.info("请输入App Store URL，每行一个（输入'done'结束）：")
    
    while True:
        url = input("URL: ").strip()
        if url.lower() == 'done':
            break
        if url:
            app_urls.append(url)
    
    if not app_urls:
        logger.error("没有输入任何URL，程序退出")
        exit(1)
    
    logger.info(f"准备抓取 {len(app_urls)} 个应用的市场图...")
    
    # 创建抓取器实例
    scraper = AppStoreScraperSelenium(output_dir="appstore_report")
    
    # 批量抓取应用
    results = scraper.scrape_multiple_apps(app_urls)
    
    # 生成报告
    html_report = scraper.generate_html_report(results)
    json_report = scraper.generate_json_report(results)
    
    logger.info(f"\n批量抓取完成！")
    logger.info(f"HTML 报告: {html_report}")
    logger.info(f"JSON 报告: {json_report}")
    
    # 打印批量结果摘要
    success_count = sum(1 for app in results if app.get('status') == 'success')
    failure_count = sum(1 for app in results if app.get('status') != 'success')
    
    logger.info(f"\n批量结果摘要:")
    logger.info(f"总测试数: {len(results)}")
    logger.info(f"成功: {success_count}")
    logger.info(f"失败: {failure_count}")
    
    for i, app in enumerate(results, 1):
        logger.info(f"\n[{i}] {app.get('name', 'Unknown')} (ID: {app.get('id', 'Unknown')})")
        logger.info(f"  状态: {app.get('status', 'Unknown')}")
        if app.get('status') == 'success':
            logger.info(f"  截图数量: {len(app.get('screenshots', []))}")
        else:
            logger.info(f"  错误: {app.get('error', 'Unknown error')}")
    
    logger.info("\n=== 抓取完成 ===")
    logger.info("URL列表已清空，可重新运行程序输入新的URL")
