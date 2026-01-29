"""
PDF 日期替换脚本
用正则匹配所有日期格式（如 2024-05-17），替换为最近3-4天的随机日期
"""

import fitz  # PyMuPDF
import os
import re
import random
from datetime import datetime, timedelta

def get_recent_date():
    """获取最近3-4天内的随机日期"""
    days_ago = random.randint(3, 4)
    recent_date = datetime.now() - timedelta(days=days_ago)
    return recent_date

def get_inspector_by_weekday(date):
    """根据日期的星期几返回对应的检测人员
    周一、周二、周三：李燕丽
    周四、周五：徐富
    周六、周日：张树芳
    """
    weekday = date.weekday()  # 0=周一, 6=周日
    if weekday in [0, 1, 2]:  # 周一、周二、周三
        return "李燕丽"
    elif weekday in [3, 4]:  # 周四、周五
        return "徐富"
    else:  # 周六、周日
        return "张树芳"

def get_random_work_time():
    """获取随机工作时间：上午9:00-11:30 或 下午13:00-17:00"""
    # 随机选择上午或下午
    if random.choice([True, False]):
        # 上午 9:00 - 11:30
        hour = random.randint(9, 11)
        if hour == 11:
            minute = random.randint(0, 30)
        else:
            minute = random.randint(0, 59)
    else:
        # 下午 13:00 - 17:00
        hour = random.randint(13, 16)
        minute = random.randint(0, 59)
    
    second = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}:{second:02d}"

def replace_dates_in_pdf(input_path, output_path):
    """
    替换 PDF 中所有日期
    """
    doc = fitz.open(input_path)
    
    # 系统字体路径
    font_path = "C:/Windows/Fonts/simsun.ttc"
    if not os.path.exists(font_path):
        font_path = "C:/Windows/Fonts/simsun.ttf"
    
    # 生成一个统一的新日期（同一文档用同一天）
    new_date = get_recent_date()
    new_date_str = new_date.strftime("%Y-%m-%d")
    
    # 生成随机工作时间
    new_time_str = get_random_work_time()
    
    # 根据日期获取检测人员
    inspector = get_inspector_by_weekday(new_date)
    
    # 日期正则：匹配 YYYY-MM-DD 格式
    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
    # 时间正则：匹配 HH:MM:SS 格式
    time_pattern = re.compile(r'\d{2}:\d{2}:\d{2}')
    # 检测人员正则：匹配已知的检测人员名字
    inspector_pattern = re.compile(r'(李燕丽|张树芳|徐富)')
    
    for page_num, page in enumerate(doc):
        blocks = page.get_text('dict')['blocks']
        
        # 收集所有需要替换的日期
        replacements = []
        
        for block in blocks:
            if 'lines' in block:
                for line in block['lines']:
                    for span in line['spans']:
                        text = span['text']
                        # 检查是否包含日期、时间或检测人员
                        if date_pattern.search(text) or time_pattern.search(text) or inspector_pattern.search(text):
                            bbox = span['bbox']
                            font_size = span['size']
                            
                            # 替换文本中的日期、时间和检测人员
                            new_text = date_pattern.sub(new_date_str, text)
                            new_text = time_pattern.sub(new_time_str, new_text)
                            new_text = inspector_pattern.sub(inspector, new_text)
                            
                            replacements.append({
                                'old_text': text,
                                'new_text': new_text,
                                'bbox': bbox,
                                'font_size': font_size
                            })
        
        # 执行替换
        for r in replacements:
            rect = fitz.Rect(r['bbox'])
            
            # 删除原文字
            page.add_redact_annot(rect, fill=False)
            page.apply_redactions(images=0, graphics=0)
            
            # 插入新文字
            text_point = fitz.Point(r['bbox'][0], r['bbox'][3] - 1)
            
            try:
                page.insert_text(
                    text_point,
                    r['new_text'],
                    fontsize=r['font_size'],
                    fontfile=font_path,
                    fontname="SimSun",
                    color=(0, 0, 0)
                )
            except:
                page.insert_text(
                    text_point,
                    r['new_text'],
                    fontsize=r['font_size'],
                    fontname="china-s",
                    color=(0, 0, 0)
                )
            
            print(f"第 {page_num + 1} 页: '{r['old_text']}' -> '{r['new_text']}'")
    
    doc.save(output_path)
    doc.close()
    print(f"\n新日期: {new_date_str} (星期{['一','二','三','四','五','六','日'][new_date.weekday()]})")
    print(f"新时间: {new_time_str}")
    print(f"检测人员: {inspector}")
    print(f"完成！已保存到: {output_path}")

if __name__ == "__main__":
    import sys
    
    input_file = "origin.pdf"
    output_file = "origin_modified.pdf"
    
    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    print("-" * 30)
    
    replace_dates_in_pdf(input_file, output_file)
