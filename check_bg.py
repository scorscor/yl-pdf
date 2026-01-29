import fitz
doc = fitz.open('origin.pdf')
page = doc[0]

# 获取页面上的所有绘图对象
drawings = page.get_drawings()
for i, d in enumerate(drawings):
    if d.get('fill'):
        print(f"绘图 {i}: fill={d.get('fill')}, rect={d.get('rect')}")

# 检查芒果区域的像素颜色
pix = page.get_pixmap()
# 芒果位置大约在 (231, 420)
x, y = 231, 420
pixel = pix.pixel(x, y)
print(f"\n芒果位置 ({x}, {y}) 的像素颜色 RGB: {pixel}")
