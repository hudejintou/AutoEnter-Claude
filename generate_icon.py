"""生成 AutoEnter 现代风格图标 (纯 Python，无需 Pillow)"""
import struct

def create_ico(filepath, size=64):
    """生成一个深色背景 + 发光回车箭头的 .ico 文件"""
    # 创建像素数组 BGRA
    pixels = []
    cx, cy = size // 2, size // 2
    for y in range(size):
        for x in range(size):
            dx, dy = x - cx, y - cy
            dist = (dx*dx + dy*dy) ** 0.5
            outer = size // 2
            inner = outer - 3

            if dist < outer - 1.5:
                bg_r = int(20 + (1 - dist/outer) * 25)
                bg_g = int(20 + (1 - dist/outer) * 30)
                bg_b = int(40 + (1 - dist/outer) * 40)
                a = 255

                # 绘制回车箭头 (简化: ⏎ 形状)
                arrow_color = False
                aw, ah = 16, 16
                ax0 = cx - aw//2
                ay0 = cy - ah//2

                # 竖线
                if ax0 + 4 <= x <= ax0 + 6 and ay0 <= y <= ay0 + ah:
                    arrow_color = True
                # 横线
                if ax0 + 4 <= x <= ax0 + aw and ay0 + ah - 3 <= y <= ay0 + ah - 1:
                    arrow_color = True
                # 箭头尖端
                if ay0 <= y <= ay0 + ah - 2:
                    rel_y = y - ay0
                    rel_x = abs(x - (ax0 + 4))
                    if rel_x <= 4 and rel_y <= (ah - 2 - rel_y * 0.6):
                        arrow_color = True

                if arrow_color:
                    # 发光青色
                    glow = max(0, 1 - dist/outer)
                    r = int(80 + glow * 175)
                    g = int(200 + glow * 55)
                    b = int(220 + glow * 35)
                    pixels.extend([b, g, r, a])
                else:
                    pixels.extend([bg_b, bg_g, bg_r, a])
            else:
                pixels.extend([0, 0, 0, 0])

    # BMP 位图数据 (倒序行)
    bmp_data = b''
    for y in range(size - 1, -1, -1):
        row = bytes(pixels[y * size * 4 : (y + 1) * size * 4])
        bmp_data += row

    # AND mask (全透明)
    and_mask = b'\x00' * (size * size // 8)
    bmp_data += and_mask

    # BMP info header (40 bytes)
    bmp_size = 40 + len(bmp_data)
    bmp_header = struct.pack('<IiiHHIIiiII',
        40,          # header size
        size,        # width
        size * 2,    # height (double for ICO: image + mask)
        1,           # planes
        32,          # bpp
        0,           # compression
        len(bmp_data) - len(and_mask),  # image size (just pixels)
        0, 0, 0, 0   # unused
    )

    # ICO header
    ico_header = struct.pack('<HHH', 0, 1, 1)  # reserved, type=icon, count=1

    # ICO directory entry
    entry = struct.pack('<BBBBHHII',
        size, size,  # width, height
        0,           # palette
        0,           # reserved
        1,           # color planes
        32,          # bpp
        len(bmp_data) + 40,  # size of BMP data + header
        22,          # offset (6 header + 16 entry)
    )

    with open(filepath, 'wb') as f:
        f.write(ico_header)
        f.write(entry)
        f.write(bmp_header)
        f.write(bmp_data)

    print(f"Icon created: {filepath} ({size}x{size})")

if __name__ == "__main__":
    create_ico(r"C:\Users\lenovo\autoenter_icon.ico", 64)
