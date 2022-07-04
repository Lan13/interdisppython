from PIL import Image


def bfs(x, y):
    queue.append((x, y))
    while len(queue) != 0:
        (xx, yy) = queue.pop()
        flag[xx][yy] = False
        for k in range(4):
            new_x = xx + dx[k]
            new_y = yy + dy[k]
            if 0 <= new_x < height and 0 <= new_y < width and flag[new_x][new_y]:
                queue.append((new_x, new_y))


if __name__ == '__main__':
    cell_cnt = 0  # 细胞数目
    queue = []     # bfs 队列
    dx = [-1, 0, 1, 0]  # 坐标转移数组
    dy = [0, 1, 0, -1]
    flag = []   # 亮斑的标记
    img = Image.open("cell_image.png")  # 打开图像
    newImg = img.convert("L")  # 转换图像模式，L 表示灰度图像（黑白）
    width, height = newImg.size   # 得到图片的宽度以及高度
    for i in range(height):
        flag.append([])
        for j in range(width):
            flag[i].append(False)   # 亮斑像素标记初始化

    pixel_min = 255
    pixel_max = 0
    for i in range(height):
        for j in range(width):
            newImg.putpixel((j, i), 255 - newImg.getpixel((j, i)))  # 黑白颠倒
            pixel_min = min(pixel_min, newImg.getpixel((j, i)))
            pixel_max = max(pixel_max, newImg.getpixel((j, i)))
    newImg.show()   # 显示初始灰度转换图像

    table = []
    for i in range(256):
        table.append(200*(i-pixel_min)/(pixel_max-pixel_min))   # 灰度增强归一化
    newImg = newImg.point(table, 'L')   # 灰度转换
    newImg.show()   # 显示灰度增强的图像

    brightness = 0  # 计算基本底色亮度
    for i in range(height):
        for j in range(width):
            brightness += newImg.getpixel((j, i))
    brightness /= (width * height)  # 此时 brightness 是平均的亮度

    for i in range(height):
        for j in range(width):
            if newImg.getpixel((j, i)) > brightness + 20:   # 根据基本底色亮度确认亮斑
                flag[i][j] = True
                newImg.putpixel((j, i), 255)

    for i in range(height):
        for j in range(width):
            if flag[i][j]:  # 如果是亮斑，就对其bfs，遍历其所在的连通图
                bfs(i, j)   # 聚合亮斑
                cell_cnt += 1   # 细胞数加 1

    newImg.save("gray.jpg")
    newImg.show()
    print("细胞数为：", cell_cnt)
