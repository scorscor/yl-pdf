from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import json
import re
from datetime import datetime

def load_config():
    """加载配置文件"""
    config_file = 'rental_config.json'
    default_config = {
        'last_processed_date': None,
        'processed_rental_count': 0,
        'last_secondhand_processed_date': None,
        'processed_secondhand_count': 0
    }
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f'加载配置文件失败: {str(e)}，使用默认配置')
            return default_config
    else:
        return default_config

def save_config(config):
    """保存配置文件"""
    config_file = 'rental_config.json'
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f'配置已保存到 {config_file}')
    except Exception as e:
        print(f'保存配置文件失败: {str(e)}')

def is_already_processed_today(config):
    """检查今天是否已经处理过租房房源"""
    today = datetime.now().strftime('%Y-%m-%d')
    last_processed = config.get('last_processed_date')
    return last_processed == today

def is_secondhand_already_processed_today(config):
    """检查今天是否已经处理过二手房源"""
    today = datetime.now().strftime('%Y-%m-%d')
    last_processed = config.get('last_secondhand_processed_date')
    return last_processed == today

def open_anjuke_login():
    # 加载配置
    config = load_config()
    today = datetime.now().strftime('%Y-%m-%d')
    
    print(f'今天日期: {today}')
    print(f'上次租房处理日期: {config.get("last_processed_date", "从未处理过")}')
    print(f'上次租房处理数量: {config.get("processed_rental_count", 0)}')
    print(f'上次二手房处理日期: {config.get("last_secondhand_processed_date", "从未处理过")}')
    print(f'上次二手房处理数量: {config.get("processed_secondhand_count", 0)}')
    
    # 检查今天是否已经处理过租房房源
    if is_already_processed_today(config):
        print(f'⚠️ 今天({today})已经处理过租房房源，跳过租房房源处理步骤')
        skip_rental_processing = True
    else:
        print(f'✅ 今天({today})尚未处理租房房源，将执行完整处理流程')
        skip_rental_processing = False
    
    # 检查今天是否已经处理过二手房源
    if is_secondhand_already_processed_today(config):
        print(f'⚠️ 今天({today})已经处理过二手房源，跳过二手房源处理步骤')
        skip_secondhand_processing = True
    else:
        print(f'✅ 今天({today})尚未处理二手房源，将执行二手房源处理流程')
        skip_secondhand_processing = False
    
    # 配置 Chrome 选项
    chrome_options = Options()
    # 指定 Chrome 浏览器路径
    chrome_options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    # 添加一些基本选项
    chrome_options.add_argument('--start-maximized')  # 最大化窗口
    chrome_options.add_argument('--disable-gpu')  # 禁用 GPU 加速
    chrome_options.add_argument('--no-sandbox')  # 禁用沙盒模式
    chrome_options.add_argument('--disable-dev-shm-usage')  # 禁用开发者共享内存
    
    # 使用 webdriver-manager 自动管理 ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # 打开安居客登录页面
        driver.get('https://vip.anjuke.com/portal/login')
        print('成功打开安居客登录页面')
        
        # 等待页面加载完成
        wait = WebDriverWait(driver, 10)
        time.sleep(2)

        # 查找并点击"账号登录"元素
        try:
            # 等待登录类型元素出现
            login_type_ul = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.loginType__UbzYt"))
            )
            
            # 查找"账号登录"的li元素（第一个li，没有active类的那个）
            account_login_li = login_type_ul.find_element(
                By.XPATH, ".//li[contains(text(), '账号登录')]"
            )
            
            # 点击账号登录
            account_login_li.click()
            print('已切换到账号登录方式')
            
            # 等待一下确保切换完成
            time.sleep(2)
            
        except Exception as e:
            print(f'切换登录方式时发生错误: {str(e)}')
        
        # 自动输入账号和密码
        try:
            # 等待账号输入框出现并输入账号
            account_input = wait.until(
                EC.presence_of_element_located((By.ID, "loginAccount"))
            )
            account_input.clear()
            account_input.send_keys("15861317151")
            print('已输入账号')
            
            # 等待密码输入框出现并输入密码
            password_input = wait.until(
                EC.presence_of_element_located((By.ID, "loginPwd"))
            )
            password_input.clear()
            password_input.send_keys("Zjdc5200")
            print('已输入密码')
            
            # 等待一下确保输入完成
            time.sleep(1)
            
            # 查找并点击登录按钮
            login_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][value='登录']"))
            )
            login_button.click()
            print('已点击登录按钮')
            
            # 等待登录结果
            time.sleep(3)
            print('登录操作完成')
            
        except Exception as e:
            print(f'自动登录时发生错误: {str(e)}')
        
        # 处理实名信息回填
        try:
            # 等待实名信息回填按钮出现并点击
            realname_button = wait.until(
                EC.element_to_be_clickable((By.ID, "61"))
            )
            realname_button.click()
            print('已点击实名信息回填按钮')
            
            # 等待弹窗出现
            time.sleep(2)
            
            # 输入完整姓名
            name_input = wait.until(
                EC.presence_of_element_located((By.ID, "veeification_challenge_realName"))
            )
            name_input.clear()
            name_input.send_keys("继委")
            print('已输入姓名：继委')
            
            # 输入最后6位
            id_input = wait.until(
                EC.presence_of_element_located((By.ID, "veeification_challenge_idNo"))
            )
            id_input.clear()
            id_input.send_keys("011017")
            print('已输入最后6位：011017')
            
            # 等待一下确保输入完成
            time.sleep(1)
            
            # 点击提交按钮
            try:
                # 尝试多种方式查找提交按钮
                submit_button = None
                
                # 方式1：通过按钮文本查找
                try:
                    submit_button = driver.find_element(
                        By.XPATH, 
                        "//button[contains(text(), '提交') or contains(text(), '确认') or contains(text(), '确定')]"
                    )
                except:
                    pass
                
                # 方式2：通过input[type="submit"]查找
                if not submit_button:
                    try:
                        submit_button = driver.find_element(
                            By.CSS_SELECTOR, "input[type='submit']"
                        )
                    except:
                        pass
                
                # 方式3：通过包含submit类名的按钮查找
                if not submit_button:
                    try:
                        submit_button = driver.find_element(
                            By.CSS_SELECTOR, 
                            "button[class*='submit'], .submit-btn, .btn-submit"
                        )
                    except:
                        pass
                
                # 方式4：通过弹窗内的按钮查找（通常是最后一个按钮）
                if not submit_button:
                    try:
                        buttons = driver.find_elements(
                            By.CSS_SELECTOR, 
                            ".multi_challenge_pop button, .pop button"
                        )
                        if buttons:
                            submit_button = buttons[-1]  # 取最后一个按钮
                    except:
                        pass
                
                if submit_button:
                    submit_button.click()
                    print('已点击提交按钮')
                    time.sleep(2)
                    print('实名信息提交完成')
                else:
                    print('未找到提交按钮，请手动点击')
                    
            except Exception as e:
                print(f'点击提交按钮时发生错误: {str(e)}')
            
        except Exception as e:
            print(f'实名信息回填时发生错误: {str(e)}')
        
        # 如果两种房源都已处理过，直接结束
        if skip_rental_processing and skip_secondhand_processing:
            print('今天租房和二手房房源都已处理过，跳过所有页面访问和处理')
            print('如需重新处理，请删除 rental_config.json 文件或修改其中的日期')
        else:
            # 处理租房房源
            all_rental_keys = []
            if not skip_rental_processing:
                # 登录成功后访问租房页面
                try:
                    print('登录成功，正在访问租房页面...')
                    driver.get('https://vip.anjuke.com/zufang/main/zufang/subpages/allHouse')
                    time.sleep(3)
                    print('成功访问租房页面')
                    
                    # 关闭弹框
                    try:
                        # 查找并点击关闭弹框按钮
                        close_button = wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "i.anticon.anticon-close-circle"))
                        )
                        close_button.click()
                        print('已关闭弹框')
                        time.sleep(1)
                        
                    except Exception as e:
                        print(f'关闭弹框时发生错误: {str(e)}')
                    
                    # 筛选推广中的房源
                    try:
                        print('开始筛选推广中的房源...')
                        
                        # 点击端口下拉菜单
                        port_dropdown = wait.until(
                            EC.element_to_be_clickable((
                                By.XPATH, 
                                "//div[contains(@class, 'ant-select-selection__placeholder') and text()='端口']"
                            ))
                        )
                        port_dropdown.click()
                        print('已点击端口下拉菜单')
                        time.sleep(2)
                        
                        # 选择"58推广"选项
                        try:
                            promotion_option = wait.until(
                                EC.element_to_be_clickable((
                                    By.XPATH, 
                                    "//li[contains(@class, 'ant-select-dropdown-menu-item') and contains(text(), '58推广')]"
                                ))
                            )
                            promotion_option.click()
                            print('已选择58推广选项')
                            time.sleep(3)  # 等待筛选结果加载
                            
                        except Exception as e:
                            print(f'选择58推广选项时发生错误: {str(e)}')
                            # 如果找不到"58推广"，尝试查找其他推广相关选项
                            try:
                                promotion_options = driver.find_elements(
                                    By.XPATH, 
                                    "//li[contains(@class, 'ant-select-dropdown-menu-item') and contains(text(), '推广')]"
                                )
                                if promotion_options:
                                    promotion_options[0].click()
                                    print(f'已选择推广相关选项: {promotion_options[0].text}')
                                    time.sleep(3)
                                else:
                                    print('未找到推广相关选项')
                            except Exception as e2:
                                print(f'查找推广选项时发生错误: {str(e2)}')
                        
                        # 点击查询按钮应用筛选条件
                        try:
                            query_button = wait.until(
                                EC.element_to_be_clickable((
                                    By.XPATH, 
                                    "//button[@type='submit' and contains(@class, 'ant-btn-primary') and .//span[text()='查询']]"
                                ))
                            )
                            query_button.click()
                            print('已点击查询按钮，正在应用筛选条件...')
                            time.sleep(3)  # 等待查询结果加载
                            
                        except Exception as e:
                            print(f'点击查询按钮时发生错误: {str(e)}')
                        
                        print('推广房源筛选完成')
                        
                    except Exception as e:
                        print(f'筛选推广房源时发生错误: {str(e)}')
                        print('将继续处理所有房源...')
                    
                    # 点击编辑日期排序按钮
                    try:
                        # 查找编辑日期排序按钮
                        sort_button = wait.until(
                            EC.element_to_be_clickable((
                                By.XPATH, 
                                "//div[contains(@class, 'sort-control') and contains(text(), '编辑日期')]"
                            ))
                        )
                        sort_button.click()
                        print('已点击编辑日期排序按钮')
                        
                        # 等待排序完成
                        time.sleep(2)
                        
                        # 检查是否已经按照从老到新排序（检查是否出现asc-icon）
                        try:
                            asc_icon = driver.find_element(
                                By.CSS_SELECTOR, 
                                "div.sort-control.active i.sort-icon.asc-icon"
                            )
                            print('编辑日期排序成功：已按从老到新排序')
                        except:
                            print('排序状态检查：可能需要再次点击或排序未完成')
                            
                    except Exception as e:
                        print(f'编辑日期排序时发生错误: {str(e)}')
                    
                    # 获取所有租房房源编号(data-row-key)
                    rental_page_count = 0
                    
                    try:
                        print('开始获取所有推广中的租房房源编号(data-row-key)...')
                        
                        while True:
                            rental_page_count += 1
                            print(f'正在获取推广中租房第{rental_page_count}页的数据...')
                            
                            # 等待页面加载完成
                            time.sleep(3)
                            
                            # 获取当前页面所有data-row-key属性的元素
                            try:
                                row_elements = driver.find_elements(By.CSS_SELECTOR, "[data-row-key]")
                                current_page_keys = []
                                
                                for element in row_elements:
                                    row_key = element.get_attribute("data-row-key")
                                    if row_key:
                                        current_page_keys.append(row_key)
                                
                                print(f'租房第{rental_page_count}页获取到 {len(current_page_keys)} 个房源编号')
                                all_rental_keys.extend(current_page_keys)
                                
                                # 打印当前页的租房房源编号
                                for key in current_page_keys:
                                    print(f'  - 租房编号: {key}')
                                
                            except Exception as e:
                                print(f'获取租房第{rental_page_count}页房源编号时发生错误: {str(e)}')
                            
                            # 查找下一页按钮
                            try:
                                # 查找包含"下一页"的li元素
                                next_li = driver.find_element(
                                    By.XPATH, 
                                    "//li[contains(@class, 'ant-pagination-next') and .//span[text()='下一页']]"
                                )
                                
                                # 检查li元素的aria-disabled属性
                                aria_disabled = next_li.get_attribute("aria-disabled")
                                
                                if aria_disabled == "true":
                                    print('租房下一页按钮已禁用（aria-disabled="true"），已到达最后一页')
                                    break
                                else:
                                    # 查找li元素内的button按钮并点击
                                    next_button = next_li.find_element(By.TAG_NAME, "button")
                                    print('找到租房下一页按钮，正在点击...')
                                    driver.execute_script("arguments[0].click();", next_button)
                                    time.sleep(2)
                                    
                            except Exception as e:
                                print(f'查找或点击租房下一页按钮时发生错误: {str(e)}')
                                print('可能已到达最后一页或页面结构发生变化')
                                break
                        
                        # 打印租房房源编号汇总结果
                        print('\n' + '='*50)
                        print('租房房源编号获取完成！汇总结果：')
                        print(f'总共获取了 {rental_page_count} 页租房数据')
                        print(f'总共获取了 {len(all_rental_keys)} 个租房房源编号')
                        print('\n所有租房房源编号列表：')
                        for i, key in enumerate(all_rental_keys, 1):
                            print(f'{i:3d}. 租房编号: {key}')
                        print('='*50)
                        
                    except Exception as e:
                        print(f'获取租房房源编号时发生错误: {str(e)}')
                        
                except Exception as e:
                    print(f'访问租房页面时发生错误: {str(e)}')
            else:
                print(f'\n⚠️ 跳过租房页面访问 - 今天({today})已处理过 {config.get("processed_rental_count", 0)} 个租房房源')
            
            # 处理二手房房源
            all_secondhand_numbers = []
            if not skip_secondhand_processing:
                # 访问二手房页面获取二手房源编号
                print('\n开始访问二手房页面获取二手房源编号...')
                secondhand_page_count = 0
                
                try:
                    # 访问二手房页面
                    driver.get('https://vip.anjuke.com/threenets/mix/second-hand/list__sl')
                    time.sleep(3)
                    print('成功访问二手房页面')
                    
                    while True:
                        secondhand_page_count += 1
                        print(f'正在获取二手房第{secondhand_page_count}页的编号数据...')
                        
                        # 等待页面加载完成
                        time.sleep(3)
                        
                        # 获取当前页面所有二手房源编号
                        try:
                            # 查找所有编辑按钮链接
                            edit_links = driver.find_elements(
                                By.CSS_SELECTOR, 
                                "a.ant-typography.threenetslist-operate-title[href*='propertyId=']"
                            )
                            current_page_numbers = []
                            
                            for link in edit_links:
                                href = link.get_attribute("href")
                                if href and "propertyId=" in href:
                                    # 从链接中提取propertyId参数值
                                    match = re.search(r'propertyId=(\d+)', href)
                                    if match:
                                        property_id = match.group(1)
                                        current_page_numbers.append(property_id)
                            
                            print(f'二手房第{secondhand_page_count}页获取到 {len(current_page_numbers)} 个房源编号')
                            all_secondhand_numbers.extend(current_page_numbers)
                            
                            # 打印当前页的二手房源编号
                            for number in current_page_numbers:
                                print(f'  - 二手房编号: {number}')
                            
                        except Exception as e:
                            print(f'获取二手房第{secondhand_page_count}页房源编号时发生错误: {str(e)}')
                        
                        # 查找下一页按钮
                        try:
                            # 查找下一页的li元素
                            next_li = driver.find_element(By.XPATH, "//li[@title='下一页']")
                            
                            # 检查li元素的aria-disabled属性
                            aria_disabled = next_li.get_attribute("aria-disabled")
                            
                            if aria_disabled == "true":
                                print('下一页按钮已禁用（aria-disabled="true"），已到达最后一页')
                                break
                            else:
                                # 查找下一页按钮并点击
                                next_button = driver.find_element(
                                    By.CSS_SELECTOR, 
                                    "button.ant-pagination-item-link[tabindex='-1'] span.anticon.anticon-right"
                                )
                                print('找到下一页按钮，正在点击...')
                                # 点击按钮的父元素（button）
                                button_element = next_button.find_element(By.XPATH, "..")
                                driver.execute_script("arguments[0].click();", button_element)
                                time.sleep(2)
                                
                        except Exception as e:
                            print(f'查找或点击二手房下一页按钮时发生错误: {str(e)}')
                            print('可能已到达最后一页或页面结构发生变化')
                            break
                    
                    # 打印二手房源编号汇总结果
                    print('\n' + '='*50)
                    print('二手房源编号获取完成！汇总结果：')
                    print(f'总共获取了 {secondhand_page_count} 页二手房数据')
                    print(f'总共获取了 {len(all_secondhand_numbers)} 个二手房源编号')
                    print('\n所有二手房源编号列表：')
                    for i, number in enumerate(all_secondhand_numbers, 1):
                        print(f'{i:3d}. 二手房编号: {number}')
                    print('='*50)
                    
                except Exception as e:
                    print(f'访问二手房页面时发生错误: {str(e)}')
            else:
                print(f'\n⚠️ 跳过二手房页面访问 - 今天({today})已处理过 {config.get("processed_secondhand_count", 0)} 个二手房源')
            
            # 循环打开每个二手房源页面并保存
            if all_secondhand_numbers and not skip_secondhand_processing:
                print('\n开始循环处理二手房源页面...')
                secondhand_success_count = 0
                secondhand_failed_count = 0
                
                for i, secondhand_number in enumerate(all_secondhand_numbers, 1):
                    try:
                        print(f'\n正在处理第 {i}/{len(all_secondhand_numbers)} 个二手房源: {secondhand_number}')
                        
                        # 构造二手房源页面URL
                        secondhand_url = (
                            f'https://vip.anjuke.com/threenets/mix/second-hand/second-hand-house-v2'
                            f'?propertyType=2&propertyId={secondhand_number}'
                        )
                        
                        # 打开二手房源页面
                        driver.get(secondhand_url)
                        print(f'已打开二手房源页面: {secondhand_url}')
                        
                        # 等待页面加载
                        time.sleep(3)
                        
                        # 检查并确保房源发布规则复选框被选中
                        try:
                            # 查找包含"《房源发布规则》"的链接元素
                            rules_link = driver.find_element(
                                By.XPATH, "//a[contains(text(), '《房源发布规则》')]"
                            )
                            
                            # 向上查找到label元素
                            label_element = rules_link.find_element(
                                By.XPATH, "./ancestor::label[contains(@class, 'ant-checkbox-wrapper')]"
                            )
                            
                            # 查找label内的checkbox span元素
                            checkbox_span = label_element.find_element(
                                By.CSS_SELECTOR, "span.ant-checkbox"
                            )
                            
                            # 检查是否已被选中
                            checkbox_classes = checkbox_span.get_attribute("class")
                            
                            if "ant-checkbox-checked" not in checkbox_classes:
                                print(f'二手房源发布规则复选框未选中，正在选中...')
                                # 点击checkbox来选中
                                checkbox_span.click()
                                time.sleep(1)
                                print(f'✅ 已选中二手房源发布规则复选框')
                            else:
                                print(f'✅ 二手房源发布规则复选框已经是选中状态')
                                
                        except Exception as e:
                            print(f'⚠️ 检查二手房源发布规则复选框时发生错误: {str(e)}')
                        
                        # 查找并点击"保存房源"按钮
                        try:
                            save_button = wait.until(
                                EC.element_to_be_clickable((
                                    By.XPATH, 
                                    "//button[@type='button' and contains(@class, 'ant-btn') and contains(@class, 'ant-btn-primary') and .//span[text()='保存房源']]"
                                ))
                            )
                            save_button.click()
                            print(f'✅ 二手房源 {secondhand_number} 保存成功')
                            secondhand_success_count += 1
                            
                            # 等待保存操作完成
                            time.sleep(2)
                            
                        except Exception as e:
                            print(f'❌ 二手房源 {secondhand_number} 保存失败: {str(e)}')
                            secondhand_failed_count += 1
                        
                        # 添加短暂延迟避免请求过于频繁
                        time.sleep(1)
                        
                    except Exception as e:
                        print(f'❌ 处理二手房源 {secondhand_number} 时发生错误: {str(e)}')
                        secondhand_failed_count += 1
                
                # 打印二手房源处理结果汇总
                print('\n' + '='*50)
                print('二手房源处理完成！汇总结果：')
                print(f'总共处理二手房源数量: {len(all_secondhand_numbers)}')
                print(f'成功保存二手房源数量: {secondhand_success_count}')
                print(f'失败二手房源数量: {secondhand_failed_count}')
                print(f'二手房源保存成功率: {secondhand_success_count/len(all_secondhand_numbers)*100:.1f}%')
                print('='*50)
                
                # 更新配置文件 - 记录今天已处理二手房源
                config['last_secondhand_processed_date'] = today
                config['processed_secondhand_count'] = len(all_secondhand_numbers)
                save_config(config)
                print(f'✅ 已更新二手房源处理记录，今天({today})的二手房源处理已完成')
            
            elif all_secondhand_numbers and skip_secondhand_processing:
                print(f'\n⚠️ 跳过二手房源处理 - 今天({today})已处理过 {config.get("processed_secondhand_count", 0)} 个二手房源')
                print('如需重新处理，请删除 rental_config.json 文件或修改其中的日期')
            
            # 循环打开每个租房房源页面并保存
            if all_rental_keys and not skip_rental_processing:
                print('\n开始循环处理租房房源页面...')
                success_count = 0
                failed_count = 0
                
                for i, rental_key in enumerate(all_rental_keys, 1):
                    try:
                        print(f'\n正在处理第 {i}/{len(all_rental_keys)} 个租房房源: {rental_key}')
                        
                        # 构造租房房源页面URL
                        house_url = (
                            f'https://vip.anjuke.com/zufang/main/zufang/rentPages/publishPage'
                            f'?houseId={rental_key}&from=hugList'
                        )
                        
                        # 打开租房房源页面
                        driver.get(house_url)
                        print(f'已打开租房房源页面: {house_url}')
                        
                        # 等待页面加载
                        time.sleep(3)
                        
                        # 检查并确保房源发布规则复选框被选中
                        try:
                            # 查找包含"《房源发布规则》"的链接元素
                            rules_link = driver.find_element(
                                By.XPATH, "//a[contains(text(), '《房源发布规则》')]"
                            )
                            
                            # 向上查找到label元素
                            label_element = rules_link.find_element(
                                By.XPATH, "./ancestor::label[contains(@class, 'ant-checkbox-wrapper')]"
                            )
                            
                            # 查找label内的checkbox span元素
                            checkbox_span = label_element.find_element(
                                By.CSS_SELECTOR, "span.ant-checkbox"
                            )
                            
                            # 检查是否已被选中
                            checkbox_classes = checkbox_span.get_attribute("class")
                            
                            if "ant-checkbox-checked" not in checkbox_classes:
                                print(f'房源发布规则复选框未选中，正在选中...')
                                # 点击checkbox来选中
                                checkbox_span.click()
                                time.sleep(1)
                                print(f'✅ 已选中房源发布规则复选框')
                            else:
                                print(f'✅ 房源发布规则复选框已经是选中状态')
                                
                        except Exception as e:
                            print(f'⚠️ 检查房源发布规则复选框时发生错误: {str(e)}')
                        
                        # 检查并处理必填项未填的情况
                        try:
                            # 检查页面是否出现"1 项必填项未填"提示
                            error_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '项必填项未填')]")
                            if error_elements:
                                print(f'⚠️ 检测到必填项未填提示，正在点击该元素跳转到需要填写的位置...')
                                # 点击错误提示元素，自动跳转到需要填写的字段
                                try:
                                    error_elements[0].click()
                                    time.sleep(2)  # 等待跳转完成
                                    print(f'✅ 已点击错误提示，页面已跳转到需要填写的位置')
                                except Exception as e:
                                    print(f'⚠️ 点击错误提示元素时发生错误: {str(e)}')
                                
                                print(f'正在检查和选择必需的radio按钮...')
                                
                                # 检查并选择"商品房住宅"radio按钮
                                try:
                                    commercial_radio_label = driver.find_element(
                                        By.XPATH, "//label[contains(@class, 'ant-radio-wrapper') and .//span[text()='商品房住宅']]"
                                    )
                                    commercial_radio_span = commercial_radio_label.find_element(By.CSS_SELECTOR, "span.ant-radio")
                                    
                                    # 检查是否已被选中
                                    if "ant-radio-checked" not in commercial_radio_span.get_attribute("class"):
                                        print(f'商品房住宅未选中，正在选中...')
                                        commercial_radio_span.click()
                                        time.sleep(1)
                                        print(f'✅ 已选中商品房住宅')
                                    else:
                                        print(f'✅ 商品房住宅已经是选中状态')
                                        
                                except Exception as e:
                                    print(f'⚠️ 处理商品房住宅radio按钮时发生错误: {str(e)}')
                                
                                # 检查并选择"普通住宅"radio按钮
                                try:
                                    ordinary_radio_label = driver.find_element(
                                        By.XPATH, "//label[contains(@class, 'ant-radio-wrapper') and .//span[text()='普通住宅']]"
                                    )
                                    ordinary_radio_span = ordinary_radio_label.find_element(By.CSS_SELECTOR, "span.ant-radio")
                                    
                                    # 检查是否已被选中
                                    if "ant-radio-checked" not in ordinary_radio_span.get_attribute("class"):
                                        print(f'普通住宅未选中，正在选中...')
                                        ordinary_radio_span.click()
                                        time.sleep(1)
                                        print(f'✅ 已选中普通住宅')
                                    else:
                                        print(f'✅ 普通住宅已经是选中状态')
                                        
                                except Exception as e:
                                    print(f'⚠️ 处理普通住宅radio按钮时发生错误: {str(e)}')
                                
                                # 等待一下确保选择生效
                                time.sleep(2)
                            else:
                                print(f'✅ 未发现必填项未填提示，页面填写完整')
                                
                        except Exception as e:
                            print(f'⚠️ 检查必填项时发生错误: {str(e)}')
                        
                        # 查找并点击"保存房源"按钮
                        try:
                            save_button = wait.until(
                                EC.element_to_be_clickable((
                                    By.XPATH, 
                                    "//button[@type='button' and contains(@class, 'ant-btn') and contains(@class, 'ant-btn-primary') and .//span[text()='保存房源']]"
                                ))
                            )
                            save_button.click()
                            print(f'✅ 租房房源 {rental_key} 保存成功')
                            success_count += 1
                            
                            # 等待保存操作完成
                            time.sleep(2)
                            
                        except Exception as e:
                            print(f'❌ 租房房源 {rental_key} 保存失败: {str(e)}')
                            failed_count += 1
                        
                        # 添加短暂延迟避免请求过于频繁
                        time.sleep(1)
                        
                    except Exception as e:
                        print(f'❌ 处理租房房源 {rental_key} 时发生错误: {str(e)}')
                        failed_count += 1
                
                # 打印租房房源处理结果汇总
                print('\n' + '='*50)
                print('租房房源处理完成！汇总结果：')
                print(f'总共处理租房房源数量: {len(all_rental_keys)}')
                print(f'成功保存租房房源数量: {success_count}')
                print(f'失败租房房源数量: {failed_count}')
                print(f'租房房源保存成功率: {success_count/len(all_rental_keys)*100:.1f}%')
                print('='*50)
                
                # 更新配置文件 - 记录今天已处理
                config['last_processed_date'] = today
                config['processed_rental_count'] = len(all_rental_keys)
                save_config(config)
                print(f'✅ 已更新处理记录，今天({today})的租房房源处理已完成')
            
            elif all_rental_keys and skip_rental_processing:
                print(f'\n⚠️ 跳过租房房源处理 - 今天({today})已处理过 {config.get("processed_rental_count", 0)} 个租房房源')
                print('如需重新处理，请删除 rental_config.json 文件或修改其中的日期')
        
        # 保持浏览器窗口打开
        input('按回车键关闭浏览器...')
    except Exception as e:
        print(f'发生错误: {str(e)}')
    finally:
        driver.quit()

if __name__ == '__main__':
    open_anjuke_login() 