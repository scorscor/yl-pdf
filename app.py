"""
PDF 样品名称替换 Web 应用
"""

from flask import Flask, render_template, request, send_file
import fitz
import os
import re
import random
from datetime import datetime, timedelta
import io

app = Flask(__name__)

# IP 错误次数记录：{ip: {'count': 次数, 'date': 日期}}
ip_fail_records = {}

def get_recent_date():
    days_ago = random.randint(3, 4)
    return datetime.now() - timedelta(days=days_ago)

def get_inspector_by_weekday(date):
    weekday = date.weekday()
    if weekday in [0, 1, 2]:
        return "李燕丽"
    elif weekday in [3, 4]:
        return "徐富"
    else:
        return "张树芳"

def get_random_work_time():
    if random.choice([True, False]):
        hour = random.randint(9, 11)
        minute = random.randint(0, 30) if hour == 11 else random.randint(0, 59)
    else:
        hour = random.randint(13, 16)
        minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}:{second:02d}"

def find_sample_name_text(page):
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
                            'size': span['size']
                        })
                        if text == '样品名称':
                            sample_name_header = span['bbox']
    
    if not sample_name_header:
        return None
    
    header_x0, header_y0, header_x1, header_y1 = sample_name_header
    for span in all_spans:
        bbox = span['bbox']
        if bbox[1] > header_y1 and bbox[0] < header_x1 + 20 and bbox[2] > header_x0 - 20:
            return span
    return None


def replace_pdf_content(input_path, new_name):
    doc = fitz.open(input_path)
    
    font_path = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"  # Linux 中文字体
    if not os.path.exists(font_path):
        font_path = "C:/Windows/Fonts/simsun.ttc"  # Windows 备用
    if not os.path.exists(font_path):
        font_path = None
    
    new_date = get_recent_date()
    new_date_str = new_date.strftime("%Y-%m-%d")
    new_date_compact = new_date.strftime("%Y%m%d")
    new_time_str = get_random_work_time()
    inspector = get_inspector_by_weekday(new_date)
    
    date_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
    sample_id_pattern = re.compile(r'([A-Z]+)(\d{4})(\d{2})(\d{2})(\d+)')
    time_pattern = re.compile(r'\d{2}:\d{2}:\d{2}')
    inspector_pattern = re.compile(r'(李燕丽|张树芳|徐富)')
    
    for page in doc:
        blocks = page.get_text('dict')['blocks']
        replacements = []
        
        sample_info = find_sample_name_text(page)
        if sample_info:
            replacements.append({
                'new_text': new_name,
                'bbox': sample_info['bbox'],
                'font_size': sample_info['size']
            })
        
        for block in blocks:
            if 'lines' in block:
                for line in block['lines']:
                    for span in line['spans']:
                        text = span['text']
                        bbox = span['bbox']
                        
                        if sample_info and bbox == sample_info['bbox']:
                            continue
                        
                        if date_pattern.search(text) or sample_id_pattern.search(text) or time_pattern.search(text) or inspector_pattern.search(text):
                            new_text = date_pattern.sub(new_date_str, text)
                            new_text = sample_id_pattern.sub(r'\g<1>' + new_date_compact + r'\5', new_text)
                            new_text = time_pattern.sub(new_time_str, new_text)
                            new_text = inspector_pattern.sub(inspector, new_text)
                            
                            replacements.append({
                                'new_text': new_text,
                                'bbox': bbox,
                                'font_size': span['size']
                            })
        
        for r in replacements:
            rect = fitz.Rect(r['bbox'])
            page.add_redact_annot(rect, fill=False)
            page.apply_redactions(images=0, graphics=0)
            
            text_point = fitz.Point(r['bbox'][0], r['bbox'][3] - 1)
            try:
                if font_path:
                    page.insert_text(text_point, r['new_text'], fontsize=r['font_size'],
                                   fontfile=font_path, fontname="CustomFont", color=(0, 0, 0))
                else:
                    page.insert_text(text_point, r['new_text'], fontsize=r['font_size'],
                                   fontname="china-s", color=(0, 0, 0))
            except:
                page.insert_text(text_point, r['new_text'], fontsize=r['font_size'],
                               fontname="china-s", color=(0, 0, 0))
    
    # 保存到内存
    pdf_bytes = io.BytesIO()
    doc.save(pdf_bytes)
    doc.close()
    pdf_bytes.seek(0)
    
    return pdf_bytes, new_date_str, new_time_str, inspector

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    sample_name = request.form.get('sample_name', '西瓜')
    code = request.form.get('code', '')
    
    # 获取客户端 IP
    ip = request.remote_addr
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 检查 IP 是否被封禁
    if ip in ip_fail_records:
        record = ip_fail_records[ip]
        if record['date'] == today and record['count'] >= 5:
            return '验证码错误次数过多，今日已禁止访问', 403
        # 如果是新的一天，重置计数
        if record['date'] != today:
            ip_fail_records[ip] = {'count': 0, 'date': today}
    
    # 验证码：年后两位 + 日（两位）
    now = datetime.now()
    correct_code = f"{now.year % 100:02d}{now.day:02d}"
    
    if code != correct_code:
        # 记录错误次数
        if ip not in ip_fail_records:
            ip_fail_records[ip] = {'count': 0, 'date': today}
        ip_fail_records[ip]['count'] += 1
        remaining = 5 - ip_fail_records[ip]['count']
        if remaining > 0:
            return f'验证码错误，还剩 {remaining} 次机会', 403
        else:
            return '验证码错误次数过多，今日已禁止访问', 403
    
    pdf_bytes, date_str, time_str, inspector = replace_pdf_content('origin.pdf', sample_name)
    
    filename = f"{sample_name}_{date_str}.pdf"
    
    return send_file(
        pdf_bytes,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
