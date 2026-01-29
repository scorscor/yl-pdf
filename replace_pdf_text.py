"""
PDF 文字替换脚本
将 origin.pdf 中的 "芒果" 替换为 "西瓜"
"""

import fitz  # PyMuPDF

def replace_text_in_pdf(input_path, output_path, old_text, new_text):
    """
    在 PDF 中替换文字
    """
    doc = fitz.open(input_path)
    
    for page_num, page in enumerate(doc):
        # 搜索所有匹配的文字
        text_instances = page.search_for(old_text)
        
        for inst in text_instances:
            # 用白色矩形覆盖原文字
            page.draw_rect(inst, color=(1, 1, 1), fill=(1, 1, 1))
            
            # 在相同位置插入新文字
            page.insert_text(
                (inst.x0, inst.y1 - 2),
                new_text,
                fontsize=10,
                fontname="china-s",
                color=(0, 0, 0)
            )
            print(f"第 {page_num + 1} 页: 已替换 '{old_text}' -> '{new_text}'")
    
    doc.save(output_path)
    doc.close()
    print(f"\n完成！已保存到: {output_path}")

if __name__ == "__main__":
    input_file = "origin.pdf"
    output_file = "origin_modified.pdf"
    
    replace_text_in_pdf(input_file, output_file, "芒果", "西瓜")
