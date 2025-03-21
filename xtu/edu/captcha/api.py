import numpy as np
import cv2


from .CharMap import charMap


def cutting_img(im, im_position, xoffset=1, yoffset=1):
    """图片切割"""
    # 识别出的字符个数
    im_number = len(im_position[1])
    if im_number >= 4:
        im_number = 4

    imgArr = []
    # 切割字符
    for i in range(im_number):
        im_start_X = im_position[1][i][0] - xoffset
        im_end_X = im_position[1][i][1] + xoffset
        im_start_Y = im_position[2][i][0] - yoffset
        im_end_Y = im_position[2][i][1] + yoffset
        cropped = im[im_start_Y:im_end_Y, im_start_X:im_end_X]
        imgArr.append(cropped)
        # cv2.imwrite(str(i)+"v.jpg",cropped) # 写入切割后的图片
    return im_number, imgArr


def captcha(img: bytes) -> str:
    """识别验证码, 参数为图片, 返回识别结果"""
    img = Convert().run(img)
    # cv2.imwrite("img.jpg", img)  # 写入处理后的图片

    # 切割的位置
    im_position = (
        [7, 7, 7, 7],
        [[5, 12], [15, 22], [25, 32], [34, 41]],
        [[4, 15], [4, 15], [4, 15], [4, 15]],
    )

    cutting_img_num, imgArr = cutting_img(img, im_position, 1, 1)

    # 识别验证码
    result = ""
    for i in range(cutting_img_num):
        try:
            template = imgArr[i]
            tempResult = ""
            matchingDegree = 0.0
            for char in charMap:
                img = np.asarray(charMap[char], dtype=np.uint8)
                # img原图 template模板   用模板匹配原图
                res = cv2.matchTemplate(img, template, 3)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                if max_val > matchingDegree:
                    tempResult = char
                    matchingDegree = max_val
            result += tempResult
            matchingDegree = 0.0
        except Exception as err:
            print("ERROR " + str(err))

    return result


class Convert:
    def _get_dynamic_binary_image(self, img):
        """
        自适应阀值二值化
        """
        img = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 1)

        # 低于阈值的像素点灰度值置为0；高于阈值的值置为参数3
        # _,img = cv2.threshold(img, 125, 255, cv2.THRESH_BINARY)
        return img

    def clear_border(self, img):
        """去除边框"""
        h, w = img.shape[:2]
        for y in range(0, w):
            for x in range(0, h):
                # if y ==0 or y == w -1 or y == w - 2:
                if y < 4 or y > w - 4:
                    img[x, y] = 255
                # if x == 0 or x == h - 1 or x == h - 2:
                if x < 4 or x > h - 4:
                    img[x, y] = 255
        return img

    def interference_line(self, img):
        """干扰线降噪"""
        h, w = img.shape[:2]
        # ！！！opencv矩阵点是反的
        # img[1,2] 1:图片的高度，2：图片的宽度
        for y in range(1, w - 1):
            for x in range(1, h - 1):
                count = 0
                if img[x, y - 1] > 245:
                    count = count + 1
                if img[x, y + 1] > 245:
                    count = count + 1
                if img[x - 1, y] > 245:
                    count = count + 1
                if img[x + 1, y] > 245:
                    count = count + 1
                if count > 2:
                    img[x, y] = 255
        return img

    def interference_point(self, img, x=0, y=0):
        """
        点降噪 9邻域框,以当前点为中心的田字框,黑点个数
        # param x
        # param y
        """
        # todo 判断图片的长宽度下限
        cur_pixel = img[x, y]  # 当前像素点的值
        height, width = img.shape[:2]

        for y in range(0, width - 1):
            for x in range(0, height - 1):
                if y == 0:  # 第一行
                    if x == 0:  # 左上顶点,4邻域
                        # 中心点旁边3个点
                        sum = (
                            int(cur_pixel) + int(img[x, y + 1]) + int(img[x + 1, y]) + int(img[x + 1, y + 1])
                        )
                        if sum <= 2 * 245:
                            img[x, y] = 0
                    elif x == height - 1:  # 右上顶点
                        sum = (
                            int(cur_pixel) + int(img[x, y + 1]) + int(img[x - 1, y]) + int(img[x - 1, y + 1])
                        )
                        if sum <= 2 * 245:
                            img[x, y] = 0
                    else:  # 最上非顶点,6邻域
                        sum = (
                            int(img[x - 1, y])
                            + int(img[x - 1, y + 1])
                            + int(cur_pixel)
                            + int(img[x, y + 1])
                            + int(img[x + 1, y])
                            + int(img[x + 1, y + 1])
                        )
                        if sum <= 3 * 245:
                            img[x, y] = 0
                elif y == width - 1:  # 最下面一行
                    if x == 0:  # 左下顶点
                        # 中心点旁边3个点
                        sum = (
                            int(cur_pixel) + int(img[x + 1, y]) + int(img[x + 1, y - 1]) + int(img[x, y - 1])
                        )
                        if sum <= 2 * 245:
                            img[x, y] = 0
                    elif x == height - 1:  # 右下顶点
                        sum = (
                            int(cur_pixel) + int(img[x, y - 1]) + int(img[x - 1, y]) + int(img[x - 1, y - 1])
                        )

                        if sum <= 2 * 245:
                            img[x, y] = 0
                    else:  # 最下非顶点,6邻域
                        sum = (
                            int(cur_pixel)
                            + int(img[x - 1, y])
                            + int(img[x + 1, y])
                            + int(img[x, y - 1])
                            + int(img[x - 1, y - 1])
                            + int(img[x + 1, y - 1])
                        )
                        if sum <= 3 * 245:
                            img[x, y] = 0
                else:  # y不在边界
                    if x == 0:  # 左边非顶点
                        sum = (
                            int(img[x, y - 1])
                            + int(cur_pixel)
                            + int(img[x, y + 1])
                            + int(img[x + 1, y - 1])
                            + int(img[x + 1, y])
                            + int(img[x + 1, y + 1])
                        )

                        if sum <= 3 * 245:
                            img[x, y] = 0
                    elif x == height - 1:  # 右边非顶点
                        sum = (
                            int(img[x, y - 1])
                            + int(cur_pixel)
                            + int(img[x, y + 1])
                            + int(img[x - 1, y - 1])
                            + int(img[x - 1, y])
                            + int(img[x - 1, y + 1])
                        )

                        if sum <= 3 * 245:
                            img[x, y] = 0
                    else:  # 具备9领域条件的
                        sum = (
                            int(img[x - 1, y - 1])
                            + int(img[x - 1, y])
                            + int(img[x - 1, y + 1])
                            + int(img[x, y - 1])
                            + int(cur_pixel)
                            + int(img[x, y + 1])
                            + int(img[x + 1, y - 1])
                            + int(img[x + 1, y])
                            + int(img[x + 1, y + 1])
                        )
                        if sum <= 4 * 245:
                            img[x, y] = 0
        return img

    def run(self, img):
        # 自适应阈值二值化
        img = self._get_dynamic_binary_image(img)
        # 去除边框
        img = self.clear_border(img)
        # 对图片进行干扰线降噪
        img = self.interference_line(img)
        # 对图片进行点降噪
        img = self.interference_point(img)
        return img
