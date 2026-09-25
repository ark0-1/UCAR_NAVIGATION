from PIL import Image

# 创建一个空白的图像，尺寸为500x400像素, 'L'是指灰度图像
image = Image.new('L', (502, 402), color=255)

# 绘制黑线矩形框
for y in range(image.height):
    image.putpixel((0, y), 0)       # 左边界
for y in range(0, 150):
    image.putpixel((200, y), 0)
for y in range(201, 402):
    image.putpixel((200, y), 0)

for y in range(0, 150):
    image.putpixel((300, y), 0)
for y in range(201, 252):
    image.putpixel((300, y), 0)
for y in range(0, 150):
    image.putpixel((450, y), 0)
for y in range(201, 252):
    image.putpixel((450, y), 0)
for y in range(101, 200):
    image.putpixel((351, y), 0)
for y in range(101, 200):
    image.putpixel((400, y), 0)

for x in range(0, 200):
    image.putpixel((x, 0), 0)
for x in range(0, 200):
    image.putpixel((x, 401), 0)
for x in range(301, 450):
    image.putpixel((x, 0), 0)
for x in range(301, 450):
    image.putpixel((x, 251), 0)
for x in range(351, 401):
    image.putpixel((x, 100), 0)
for x in range(351, 401):
    image.putpixel((x, 200), 0)


print(image.width)
print(image.height)

# 保存为PGM格式文件
image.save('../map/map.pgm')