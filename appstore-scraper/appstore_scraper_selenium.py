#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App Store Scraper Skill - 简化版
"""

import time
import re
import os
import json
import logging
from typing import List, Dict, Optional
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AppStoreScraperSelenium:
    def __init__(self, output_dir: str = "appstore_report"):
        """
        初始化 App Store 抓取器
        
        Args:
            output_dir: 输出目录，将生成 HTML 报告文件
        """
        self.output_dir = output_dir
        
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"创建输出目录: {output_dir}")
        else:
            # 清理旧文件
            self._clean_old_files()
    
    def _clean_old_files(self):
        """清理旧的报告文件"""
        import glob
        
        # 删除所有旧的进度文件
        progress_files = glob.glob(os.path.join(self.output_dir, "progress_*.html"))
        progress_files.extend(glob.glob(os.path.join(self.output_dir, "progress_*.json")))
        progress_files.extend(glob.glob(os.path.join(self.output_dir, "appstore_report_*.html")))
        progress_files.extend(glob.glob(os.path.join(self.output_dir, "appstore_data_*.json")))
        
        if progress_files:
            logger.info(f"清理 {len(progress_files)} 个旧文件")
            for file_path in progress_files:
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.warning(f"删除文件失败 {file_path}: {str(e)}")
    
    def extract_app_id(self, url: str) -> Optional[str]:
        """
        从 App Store URL 中提取应用 ID

        Args:
            url: App Store 链接

        Returns:
            应用 ID 字符串，未找到则返回 None
        """
        # 支持多种 App Store URL 格式
        patterns = [
            r'[/]id(\d+)',  # /id431946152
            r'App[/]iPhone/.*?/(\d+)$',  # /App/iPhone/Name/id
            r'https://apps\.apple\.id/[\w-]+/app/.*?/id(\d+)'  # 正则表达式匹配
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        # 如果没有匹配到 ID，尝试从路径中提取
        parsed = urlparse(url)
        if 'id' in parsed.path:
            parts = parsed.path.split('/')
            for i, part in enumerate(parts):
                if part == 'id' and i + 1 < len(parts):
                    return parts[i + 1]
                    break

        logger.warning(f"无法从 URL 提取应用 ID: {url}")
        return None
    
    def _create_driver(self) -> webdriver.Chrome:
        """
        创建 Chrome 浏览器驱动

        Returns:
            Chrome 浏览器驱动实例
        """
        # 配置 Chrome 选项
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # 无头模式
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36')
        options.add_argument('--disable-application-cache')
        options.add_argument('--disable-local-storage')
        options.add_argument('--disable-session-storage')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        
        # 初始化浏览器
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        return driver
    
    def extract_app_name(self, driver: webdriver.Chrome) -> Optional[str]:
        """
        从页面中提取应用名称

        Args:
            driver: Chrome 浏览器驱动实例

        Returns:
            应用名称，未找到则返回 None
        """
        try:
            # 尝试多种方式查找应用名称
            app_name = None
            
            # 方式 1: 查找 h1 标签
            try:
                app_name_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'h1'))
                )
                app_name = app_name_element.text.strip()
            except:
                pass
            
            # 方式 2: 查找 og:title meta 标签
            if not app_name:
                try:
                    app_name = driver.find_element(By.XPATH, "//meta[@property='og:title']").get_attribute('content')
                except:
                    pass
            
            # 方式 3: 查找 title 标签
            if not app_name:
                try:
                    app_name = driver.title
                    # 清理标题，移除 " - App Store" 后缀
                    if ' - App Store' in app_name:
                        app_name = app_name.split(' - App Store')[0]
                except:
                    pass
            
            return app_name
            
        except Exception as e:
            logger.error(f"提取应用名称失败: {str(e)}")
            return None
    
    def extract_screenshots(self, driver: webdriver.Chrome) -> List[Dict]:
        """
        从页面中提取应用截图 URL

        Args:
            driver: Chrome 浏览器驱动实例

        Returns:
            截图 URL 列表
        """
        screenshots = []
        seen_urls = set()
        
        try:
            # 等待页面加载完成
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            
            # 执行 JavaScript 来查找截图
            logger.info("执行 JavaScript 来查找截图")
            try:
                # 查找所有可能的媒体元素
                media_elements = driver.execute_script("""
                    return Array.from(document.querySelectorAll('img, video, picture, source')).map(el => {
                        if (el.tagName === 'IMG') {
                            return el.src;
                        } else if (el.tagName === 'VIDEO') {
                            return el.poster || el.src;
                        } else if (el.tagName === 'SOURCE') {
                            return el.srcset || el.src;
                        } else if (el.tagName === 'PICTURE') {
                            const img = el.querySelector('img');
                            return img ? img.src : null;
                        }
                        return null;
                    }).filter(Boolean);
                """)
                
                logger.info(f"通过 JavaScript 找到 {len(media_elements)} 个媒体元素")
                logger.info(f"前10个媒体元素: {media_elements[:10]}")
                
                # 过滤截图
                for url in media_elements:
                    if url and 'mzstatic.com' in url:
                        # 从srcset中提取第一个URL
                        if ' ' in url and ('w,' in url or 'x,' in url):
                            # 这是一个srcset，提取第一个URL
                            first_url = url.split(',')[0].split(' ')[0].strip()
                            if any(ext in first_url.lower() for ext in ['.png', '.jpg', '.jpeg', '.webp']):
                                url = first_url
                        
                        if any(ext in url.lower() for ext in ['.png', '.jpg', '.jpeg', '.webp']):
                            # 过滤掉不需要的图片
                            if ('AppIcon' not in url and 'Placeholder' not in url and '1x1.gif' not in url and
                                '64x64' not in url and '128x128' not in url and '32x32' not in url and
                                'video-control' not in url and 'supports-' not in url):
                                # 只保留看起来像截图的URL
                                if any(keyword in url.lower() for keyword in ['source', 'screenshot', 'purple', 'app']):
                                    if url not in seen_urls:
                                        seen_urls.add(url)
                                        screenshots.append({
                                            'jpeg': url,
                                            'webp': url.replace('.png', '.webp') if '.png' in url else url,
                                            'base_url': url
                                        })
                                        logger.info(f"从 JavaScript 中添加截图: {url}")
            except Exception as e:
                logger.warning(f"JavaScript 执行失败: {str(e)}")
            
            # 查找 iframe 中的图片
            logger.info("查找 iframe 中的图片")
            try:
                iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                logger.info(f"找到 {len(iframes)} 个 iframe")
                
                for iframe in iframes:
                    try:
                        driver.switch_to.frame(iframe)
                        iframe_imgs = driver.find_elements(By.TAG_NAME, 'img')
                        logger.info(f"在 iframe 中找到 {len(iframe_imgs)} 个图片元素")
                        
                        for img in iframe_imgs:
                            try:
                                img_url = img.get_attribute('src')
                                if img_url and 'mzstatic.com' in img_url:
                                    if img_url not in seen_urls:
                                        seen_urls.add(img_url)
                                        screenshots.append({
                                            'jpeg': img_url,
                                            'webp': img_url.replace('.png', '.webp') if '.png' in img_url else img_url,
                                            'base_url': img_url
                                        })
                                        logger.info(f"从 iframe 中添加截图: {img_url}")
                            except:
                                pass
                        
                        driver.switch_to.default_content()
                    except Exception as e:
                        logger.warning(f"处理 iframe 失败: {str(e)}")
                        driver.switch_to.default_content()
                        continue
            except:
                pass
            
            # 查找所有图片元素
            img_elements = driver.find_elements(By.TAG_NAME, 'img')
            logger.info(f"找到 {len(img_elements)} 个图片元素")
            
            # 收集所有图片URL
            all_img_urls = []
            for img in img_elements:
                try:
                    img_url = img.get_attribute('src')
                    if img_url:
                        all_img_urls.append(img_url)
                except:
                    pass
            
            # 打印前15个图片URL用于调试
            logger.info(f"前15个图片URL: {all_img_urls[:15]}")
            
            # 查找脚本标签中的图片URL
            logger.info("尝试从脚本标签中提取截图")
            script_elements = driver.find_elements(By.TAG_NAME, 'script')
            
            for script in script_elements:
                try:
                    script_content = script.get_attribute('innerHTML')
                    if script_content:
                        # 查找 mzstatic.com 的图片URL
                        import re
                        screenshot_urls = re.findall(r'https://[\w.-]+mzstatic\.com/[\w/-]+\.(?:png|jpg|jpeg|webp)', script_content)
                        for url in screenshot_urls:
                            # 过滤掉不需要的图片
                            if ('AppIcon' not in url and 'Placeholder' not in url and '1x1.gif' not in url and
                                '64x64' not in url and '128x128' not in url and '32x32' not in url and
                                'video-control' not in url and 'supports-' not in url):
                                # 只保留看起来像截图的URL
                                if any(keyword in url.lower() for keyword in ['source', 'screenshot', 'purple', 'app']):
                                    if url not in seen_urls:
                                        seen_urls.add(url)
                                        screenshots.append({
                                            'jpeg': url,
                                            'webp': url.replace('.png', '.webp') if '.png' in url else url,
                                            'base_url': url
                                        })
                                        logger.info(f"从脚本中添加截图: {url}")
                except:
                    pass
            
            # 限制最多 8 张截图
            logger.info(f"最终提取到 {len(screenshots)} 张截图")
            return screenshots[:8]
            
        except Exception as e:
            logger.error(f"提取截图失败: {str(e)}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")
            return []
    
    def extract_app_icon(self, driver: webdriver.Chrome) -> Optional[Dict]:
        """
        提取应用图标

        Args:
            driver: Chrome 浏览器驱动实例

        Returns:
            包含图标 URL 的字典，返回 None 则未找到
        """
        try:
            # 查找 og:image meta 标签
            try:
                icon_url = driver.find_element(By.XPATH, "//meta[@property='og:image']").get_attribute('content')
                if icon_url:
                    return {
                        'url': icon_url,
                        'high_res': icon_url
                    }
            except:
                pass
            
            # 查找所有图片，寻找可能的图标
            img_elements = driver.find_elements(By.TAG_NAME, 'img')
            for img in img_elements:
                try:
                    img_url = img.get_attribute('src')
                    if img_url and 'mzstatic.com' in img_url and 'AppIcon' in img_url:
                        return {
                            'url': img_url,
                            'high_res': img_url
                        }
                except:
                    pass
            
            return None
            
        except Exception as e:
            logger.error(f"提取应用图标失败: {str(e)}")
            return None
    
    def scrape_app(self, url: str) -> Optional[Dict]:
        """
        抓取单个 App 应用信息

        Args:
            url: App Store 链接

        Returns:
            包含应用信息的字典，未成功抓取则返回 None
        """
        driver = None
        
        try:
            app_id = self.extract_app_id(url)
            if not app_id:
                logger.error(f"无法提取应用 ID: {url}")
                return None

            logger.info(f"开始抓取应用 (ID: {app_id}): {url}")

            # 创建浏览器驱动
            driver = self._create_driver()
            
            # 清除缓存和 cookies
            driver.delete_all_cookies()
            
            # 发送请求获取页面
            driver.get(url)
            
            # 等待页面加载
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )

            # 提取信息
            app_name = self.extract_app_name(driver)
            screenshots = self.extract_screenshots(driver)
            icon = self.extract_app_icon(driver)

            # 构建结果
            app_info = {
                'id': app_id,
                'name': app_name or f"App {app_id}",
                'url': url,
                'icon': icon,
                'screenshots': screenshots,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'success'
            }

            logger.info(f"成功抓取应用信息: {app_name}")
            return app_info

        except Exception as e:
            logger.error(f"抓取错误: {url} - {str(e)}")
            return {'id': 'unknown', 'name': 'Unknown', 'url': url, 'status': 'error', 'error': str(e)}
        finally:
            if driver:
                driver.quit()
    
    def scrape_multiple_apps(self, urls: List[str], max_workers: int = 6) -> List[Dict]:
        """
        批量抓取多个应用

        Args:
            urls: App Store 链接列表
            max_workers: 最大并发线程数

        Returns:
            应用信息列表
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = []
        
        logger.info(f"开始并发抓取 {len(urls)} 个应用，最大并发数: {max_workers}")
        
        def scrape_single_app(url):
            """单线程抓取函数"""
            return self.scrape_app(url)
        
        # 使用线程池并发处理
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_url = {executor.submit(scrape_single_app, url): url for url in urls}
            
            # 处理结果 - 不保存中间文件，只保留最终结果
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.error(f"抓取失败 {url}: {str(e)}")
        
        # 等待所有任务完成（线程池会自动等待）
        return results
    
    def _build_html_content(self, apps_data: List[Dict]) -> str:
        """
        构建 HTML 报告内容

        Args:
            apps_data: 应用信息列表

        Returns:
            HTML 内容字符串
        """
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>App Store 应用报告</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #147EFB;
            text-align: center;
            margin-bottom: 30px;
        }}
        .summary {{
            background-color: #fff;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-width: none;
        }}
        .app-card {{
            background-color: #fff;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-width: none;
        }}
        .app-card h2 {{
            color: #147EFB;
            margin-top: 0;
        }}
        .app-info {{
            margin-bottom: 15px;
        }}
        .app-info span {{
            font-weight: bold;
        }}
        .screenshots {{
            margin-top: 15px;
        }}
        .screenshot-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 10px;
        }}
        .screenshot-item {{
            border: 1px solid #ddd;
            border-radius: 4px;
            overflow: hidden;
            background-color: #f9f9f9;
        }}
        .screenshot-item img {{
            width: 100%;
            height: auto;
            display: block;
            transition: transform 0.3s ease;
        }}
        .screenshot-item img:hover {{
            transform: scale(1.05);
        }}
        .error {{
            background-color: #ffebee;
            border-left: 4px solid #f44336;
            padding: 10px;
            margin: 10px 0;
        }}
        .success {{
            background-color: #e8f5e8;
            border-left: 4px solid #4caf50;
            padding: 10px;
            margin: 10px 0;
        }}
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            .screenshot-grid {{
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 10px;
            }}
            .app-card, .summary {{
                padding: 15px;
            }}
        }}
        @media (max-width: 480px) {{
            .screenshot-grid {{
                grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
                gap: 8px;
            }}
            .app-card, .summary {{
                padding: 10px;
            }}
            h1 {{
                font-size: 1.5em;
            }}
        }}
    </style>
</head>
<body>
    <h1>App Store 应用报告</h1>
    <div class="summary">
        <h2>报告摘要</h2>
        <p>生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>总应用数: {len(apps_data)}</p>
        <p>成功: {sum(1 for app in apps_data if app.get('status') == 'success')}</p>
        <p>失败: {sum(1 for app in apps_data if app.get('status') != 'success')}</p>
    </div>
"""

        for app in apps_data:
            if app.get('status') == 'success':
                screenshots_html = ""
                if app.get('screenshots'):
                    screenshots_html = """
        <div class="screenshots">
            <h3>应用截图</h3>
            <div class="screenshot-grid">
                    """
                    for screenshot in app.get('screenshots', []):
                        screenshots_html += f"""
                <div class="screenshot-item">
                    <img src="{screenshot.get('jpeg')}" alt="应用截图">
                </div>
                        """
                    screenshots_html += """
            </div>
        </div>
                    """
            
                html_content += f"""
    <div class="app-card">
        <h2>{app.get('name', 'Unknown')}</h2>
        <div class="app-info">
            <p><span>应用 ID:</span> {app.get('id', 'Unknown')}</p>
            <p><span>应用链接:</span> <a href="{app.get('url', '#')}" target="_blank">{app.get('url', '#')}</a></p>
            <p><span>状态:</span> <span class="success">成功</span></p>
            <p><span>截图数量:</span> {len(app.get('screenshots', []))}</p>
        </div>
        {screenshots_html}
    </div>
                """
            else:
                html_content += f"""
    <div class="app-card">
        <h2>{app.get('name', 'Unknown')}</h2>
        <div class="app-info">
            <p><span>应用 ID:</span> {app.get('id', 'Unknown')}</p>
            <p><span>应用链接:</span> <a href="{app.get('url', '#')}" target="_blank">{app.get('url', '#')}</a></p>
            <p><span>状态:</span> <span class="error">失败</span></p>
            <p><span>错误信息:</span> {app.get('error', 'Unknown error')}</p>
        </div>
    </div>
                """
        
        html_content += """
</body>
</html>
        """
        
        return html_content
    
    def generate_html_report(self, apps_data: List[Dict], output_file: Optional[str] = None) -> str:
        """
        生成 HTML 报告

        Args:
            apps_data: 应用信息列表
            output_file: 输出文件路径，如果为 None 则使用默认路径

        Returns:
            生成的文件路径
        """
        if not output_file:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(self.output_dir, f'appstore_report_{timestamp}.html')

        # 生成 HTML 内容
        html_content = self._build_html_content(apps_data)
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML 报告已生成: {output_file}")
        return output_file
    
    def generate_json_report(self, apps_data: List[Dict], output_file: Optional[str] = None) -> str:
        """
        生成 JSON 报告

        Args:
            apps_data: 应用信息列表
            output_file: 输出文件路径，如果为 None 则使用默认路径

        Returns:
            生成的文件路径
        """
        if not output_file:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(self.output_dir, f'appstore_data_{timestamp}.json')

        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(apps_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON 报告已保存: {output_file}")
        return output_file

if __name__ == "__main__":
    # 测试脚本
    test_urls = [
        "https://apps.apple.com/us/app/id6449351247"
    ]
    
    logger.info("开始测试 App Store 抓取器...")
    logger.info(f"测试 URL 数量: {len(test_urls)}")
    
    # 创建抓取器实例
    scraper = AppStoreScraperSelenium(output_dir="test_appstore_report")
    
    # 批量抓取应用
    results = scraper.scrape_multiple_apps(test_urls)
    
    # 生成报告
    html_report = scraper.generate_html_report(results)
    json_report = scraper.generate_json_report(results)
    
    logger.info(f"\n测试完成！")
    logger.info(f"HTML 报告: {html_report}")
    logger.info(f"JSON 报告: {json_report}")
    
    # 打印结果摘要
    success_count = sum(1 for app in results if app.get('status') == 'success')
    failure_count = sum(1 for app in results if app.get('status') != 'success')
    
    logger.info(f"\n结果摘要:")
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