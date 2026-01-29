import fitz
doc = fitz.open('origin.pdf')
page = doc[0]

# 获取详细的文字信息，包括位置和字体
blocks = page.get_text('dict')['blocks']
for block in blocks:
    if 'lines' in block:
        for line in block['lines']:
            for span in line['spans']:
                text = span['text'].strip()
                if text and ('芒果' in text or '样品名称' in text or '样品编号' in text):
                    print(f'文字: {text}')
                    print(f'  位置: x0={span["bbox"][0]:.1f}, y0={span["bbox"][1]:.1f}, x1={span["bbox"][2]:.1f}, y1={span["bbox"][3]:.1f}')
                    print(f'  字体: {span["font"]}')
                    print(f'  字号: {span["size"]}')
                    print()
