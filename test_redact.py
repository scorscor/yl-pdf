import fitz

doc = fitz.open('origin.pdf')
page = doc[0]

# 查看 apply_redactions 的默认参数
help(page.apply_redactions)
