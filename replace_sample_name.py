"""
PDF 样品名称替换脚本
自动替换样品名称、日期、时间、检测人员
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
    weekday = date.weekday()
    if weekday in [0, 1, 2]:
        return "李燕丽"
    elif weekday in [3, 4]:
        return "徐富"
    else:
        return "张树芳"

def get_random_work_time():
    """获取随机工作时间：上午9:00-11:30 或 下午13:00-17:00"""
    if random.choice([True, False]):
        hour = random.randint(9, 11)
        if hour == 11:
            minute = random.randint(0, 30)
        else:
            minute = random.randint(0, 59)
    else:
        hour = random.randint(13, 16)
        minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}:{second:02d}"

def find_sample_name_text(page):
    """找到"样品名称"下方格子里的文字及其位置信息"""
    blocks = page.get_text('dict')['blocks']
    sample_name_header = None
    all_spans = []
    
    for block in blocks:
        if 'lines' in block:
            for line in block['lines']:
                for span in line['spans']:
                    text = span['text'].strip()
                    if text:
                        all_spans.append({
                            'text': text,
                            'bbox': span['bbox'],
                            'font': span['font'],
                            'size': span['size']
                        })
                        if text == '样品名称':
                            sample_name_header = span['bbox']
    
    if not sample_name_header:
        return None
    
    header_x0, header_y0, header_x1, header_y1 = sample_name_header
    
    for span in all_spans:
        bbox = span['bbox']
        span_x0, span_y0, span_x1, span_y1 = bbox
        if span_y0 > header_y1:
            if span_x0 < header_x1 + 20 and span_x1 > header_x0 - 20:
                return span
    return None


def replace_pdf_content(input_path, output_path, new_name):
    """替换 PDF 中的样品名称、日期、时间、检测人员"""
    doc = fitz.open(input_path)
    
    font_path = "C:/Windows/Fonts/simsun.ttc"
    if not os.path.exists(font_path):
        font_path = "C:/Windows/Fonts/simsun.ttf"
    
    # 生成新日期、时间、检测人员
    new_date = get_recent_date()
    new_date_str = new_date.strftime("%Y-%m-%d")
    new_time_str = get_random_work_time()
    inspector = get_inspector_by_weekday(new_date)
    
    # 正则模式
    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
    # 只匹配样品编号格式：字母开头+日期+数字结尾
    sample_id_pattern = re.compile(r'([A-Z]+)(\d{4})(\d{2})(\d{2})(\d+)')
    time_pattern = re.compile(r'\d{2}:\d{2}:\d{2}')
    inspector_pattern = re.compile(r'(李燕丽|张树芳|徐富)')
    
    # 紧凑日期格式（无横线）
    new_date_compact = new_date.strftime("%Y%m%d")
    
    for page_num, page in enumerate(doc):
        blocks = page.get_text('dict')['blocks']
        replacements = []
        
        # 1. 找样品名称
        sample_info = find_sample_name_text(page)
        if sample_info:
            replacements.append({
                'old_text': sample_info['text'],
                'new_text': new_name,
                'bbox': sample_info['bbox'],
                'font_size': sample_info['size']
            })
        
        # 2. 找日期、时间、检测人员
        for block in blocks:
            if 'lines' in block:
                for line in block['lines']:
                    for span in line['spans']:
                        text = span['text']
                        bbox = span['bbox']
                        
                        # 跳过已处理的样品名称
                        if sample_info and bbox == sample_info['bbox']:
                            continue
                        
                        if date_pattern.search(text) or sample_id_pattern.search(text) or time_pattern.search(text) or inspector_pattern.search(text):
                            new_text = date_pattern.sub(new_date_str, text)
                            # 替换样品编号中的日期部分，保留前缀和后缀
                            new_text = sample_id_pattern.sub(r'\g<1>' + new_date_compact + r'\5', new_text)
                            new_text = time_pattern.sub(new_time_str, new_text)
                            new_text = inspector_pattern.sub(inspector, new_text)
                            
                            replacements.append({
                                'old_text': text,
                                'new_text': new_text,
                                'bbox': bbox,
                                'font_size': span['size']
                            })
        
        # 执行替换
        for r in replacements:
            rect = fitz.Rect(r['bbox'])
            page.add_redact_annot(rect, fill=False)
            page.apply_redactions(images=0, graphics=0)
            
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
            
            print(f"'{r['old_text']}' -> '{r['new_text']}'")
    
    doc.save(output_path)
    doc.close()
    
    weekday_names = ['一','二','三','四','五','六','日']
    print(f"\n--- 替换结果 ---")
    print(f"样品名称: {new_name}")
    print(f"日期: {new_date_str} (星期{weekday_names[new_date.weekday()]})")
    print(f"时间: {new_time_str}")
    print(f"检测人员: {inspector}")
    print(f"已保存到: {output_path}")

if __name__ == "__main__":
    import sys
    
    input_file = "origin.pdf"
    output_file = "origin_modified.pdf"
    new_name = "西瓜"
    
    if len(sys.argv) >= 2:
        new_name = sys.argv[1]
    if len(sys.argv) >= 3:
        input_file = sys.argv[2]
    if len(sys.argv) >= 4:
        output_file = sys.argv[3]
    
    print(f"输入: {input_file}")
    print(f"输出: {output_file}")
    print("-" * 30)
    
    replace_pdf_content(input_file, output_file, new_name)
