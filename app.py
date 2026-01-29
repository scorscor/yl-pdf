"""
PDF 样品名称替换 Web 应用
"""

from flask import Flask, render_template, request, send_file
import fitz
import os
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


def replace_pdf_content(input_path, new_name):
    doc = fitz.open(input_path)
    
    font_path = "/usr/share/fonts/simsun.ttc"  # Docker 容器内宋体
    if not os.path.exists(font_path):
        font_path = "C:/Windows/Fonts/simsun.ttc"  # Windows 本地开发
    if not os.path.exists(font_path):
        font_path = None
    
    new_date = get_recent_date()
    new_date_str = new_date.strftime("%Y-%m-%d")
    new_date_compact = new_date.strftime("%Y%m%d")
    new_time_str = get_random_work_time()
    inspector = get_inspector_by_weekday(new_date)
    
    # 精确匹配原 PDF 中的固定文本
    exact_replacements = {
        '2024-05-17': new_date_str,
        '09:02:47': new_time_str,
        'ZCGPSC202405170007': f'ZCGPSC{new_date_compact}0007',
        '芒果': new_name,
        '李燕丽': inspector,
        '报告签发日期：2024-05-17': f'报告签发日期：{new_date_str}',
    }
    
    for page in doc:
        blocks = page.get_text('dict')['blocks']
        replacements = []
        
        for block in blocks:
            if 'lines' in block:
                for line in block['lines']:
                    for span in line['spans']:
                        text = span['text'].strip()
                        bbox = span['bbox']
                        
                        # 精确匹配
                        if text in exact_replacements:
                            replacements.append({
                                'new_text': exact_replacements[text],
                                'bbox': bbox,
                                'font_size': span['size']
                            })
                        # 处理包含日期时间的组合文本，如 "2024-05-17 09:02:47"
                        elif '2024-05-17' in text and '09:02:47' in text:
                            new_text = text.replace('2024-05-17', new_date_str).replace('09:02:47', new_time_str)
                            replacements.append({
                                'new_text': new_text,
                                'bbox': bbox,
                                'font_size': span['size']
                            })
        
        for r in replacements:
            rect = fitz.Rect(r['bbox'])
            page.add_redact_annot(rect, fill=False)
        
        # 一次性应用所有 redaction
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
        
        # 重新插入文字
        for r in replacements:
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
