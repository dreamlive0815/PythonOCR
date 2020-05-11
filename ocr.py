
import cv2
from cnocr import CnOcr
from PIL import Image
from tools import Tools
from log import Log
import numpy as np
import pytesseract
import re

# 1653 * 2338 分辨率
# 30 * 9 格子
LTX = 112  # 左上X
LTY = 466  # 左上Y
RBX = 1482  # 右下X
RBY = 2136  # 右下Y
RH = (RBY - LTY) / 30  # 行高
PADDING = 4
#    0     1    2    3    4    5    6     7     8     9
XS = [112, 270, 418, 538, 640, 980, 1084, 1188, 1296, 1482]

digitReg = re.compile(r'\d')
digitsReg = re.compile(r'\d{1}')

class OCRTools():

    def __init__(self, cacheDir):
        super().__init__()
        self.cacheDir = cacheDir

    def getEmptyRow(self):
        r = []
        for j in range(9):
            r.append('')
        return r

    def getEmptyData(self):
        r = []
        for i in range(30):
            rr = self.getEmptyRow()
            r.append(rr)
        return r

    def ocr(self, imgPath):

        cacheDir = self.cacheDir
        srcImg = cv2.imread(imgPath)

        grayImg = cv2.cvtColor(srcImg, cv2.COLOR_BGR2GRAY)
        binImg = cv2.adaptiveThreshold(~grayImg, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, -5)
        ret, binImg2 = cv2.threshold(grayImg, 150, 255, cv2.THRESH_BINARY)

        cv2.imwrite(Tools.joinPath(cacheDir, 'bin.jpg'), binImg)
        cv2.imwrite(Tools.joinPath(cacheDir, 'bin2.jpg'), binImg2)

        Log.i('ocring: {}'.format(imgPath))

        x_point_arr, y_point_arr = self.getFramePosData(binImg)

        r = self.ocrCells(srcImg, x_point_arr, y_point_arr)
        return r

    def filterCellText(self, cellText):

        # 去除特殊字符
        arr = re.findall(r'[^\-\_\(\)\*"/:?\\|<>″′‖ 〈\n]', cellText, re.S)
        cellText = ''.join(arr)

        cellText = re.sub(r'[oO]', '0', cellText)
        cellText = re.sub(r'[lL]', '1', cellText)

        if cellText.__contains__('独生'):
            cellText = '独生子女'

        return cellText

    def ocrCells(self, img, x_point_arr, y_point_arr):

        def showImg(key, img):
            imgStorePath = Tools.joinPath(self.cacheDir, '{}.jpg'.format(key))
            cv2.imwrite(imgStorePath, img)
            return imgStorePath

        ocr = CnOcr()

        src = img
        # 循环y坐标，x坐标分割表格
        lenY = len(y_point_arr)
        lenX = len(x_point_arr)
        r = []
        for i in range(lenY - 1):
            rr = []
            for j in range(lenX - 1):
                # 在分割时，第一个参数为y坐标，第二个参数为x坐标
                cell = src[y_point_arr[i]:y_point_arr[i + 1], x_point_arr[j]:x_point_arr[j + 1]]

                imgStorePath = showImg('cells_{}_{}'.format(i, j), cell)

                # 读取文字，此为默认英文
                pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'
                cellText = pytesseract.image_to_string(cell, lang="chi_sim+eng")

                sr = digitsReg.search(cellText)
                if not sr:
                    resArr = ocr.ocr_for_single_line(imgStorePath)
                    cellText = ''.join(resArr)

                cellText = self.filterCellText(cellText)

                Log.i('单元格{}_{} = {}'.format(i, j, cellText))
                rr.append(cellText)
                j = j + 1

            r.append(rr)
            i = i + 1

        return r

        # oy = LTY
        # r = []
        # for i in range(30):
        #     rr = []
        #     ty = oy + PADDING
        #     ih = RH - 2 * PADDING
        #     for j in range(len(XS) - 1):
        #         tx = XS[j] + PADDING
        #         iw = XS[j + 1] - XS[j] - 2 * PADDING
        #         tx = int(tx)
        #         ty = int(ty)
        #         bx = int(tx + iw)
        #         by = int(ty + ih)
        #         region = img[ty:by, tx:bx]
        #         fragStorePath = Tools.joinPath(
        #             cacheDir, '{}_{}.jpg'.format(i, j))
        #         cv2.imwrite(fragStorePath, region)
        #         resArr = ocr.ocr_for_single_line(fragStorePath)
        #         rr.append(''.join(resArr))
        #     Log.i('ocr at row {}, result = {}'.format(i + 1, rr))
        #     r.append(rr)
        #     oy = oy + RH

    def getFramePosData(self, binImg):

        def showImg(key, img):
            imgStorePath = Tools.joinPath(self.cacheDir, '{}.jpg'.format(key))
            cv2.imwrite(imgStorePath, img)

        cacheDir = self.cacheDir
        binary = binImg
        rows, cols = binary.shape

        # 识别横线:
        scale = 40
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (cols // scale, 1))
        eroded = cv2.erode(binary, kernel, iterations=1)
        dilated_col = cv2.dilate(eroded, kernel, iterations=1)
        showImg('excel_horizontal_line.jpg', dilated_col)

        # 识别竖线：
        scale = 20
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, rows // scale))
        eroded = cv2.erode(binary, kernel, iterations=1)
        dilated_row = cv2.dilate(eroded, kernel, iterations=1)
        showImg('excel_vertical_line.jpg', dilated_row)

        # 将识别出来的横竖线合起来
        bitwise_and = cv2.bitwise_and(dilated_col, dilated_row)
        showImg("excel_bitwise_and", bitwise_and)

        # 标识表格轮廓
        merge = cv2.add(dilated_col, dilated_row)
        showImg("entire_excel_contour", merge)

        # 两张图片进行减法运算，去掉表格框线
        merge2 = cv2.subtract(binary, merge)
        showImg("binary_sub_excel_rect", merge2)

        new_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        erode_image = cv2.morphologyEx(merge2, cv2.MORPH_OPEN, new_kernel)
        showImg('erode_image2', erode_image)
        merge3 = cv2.add(erode_image, bitwise_and)
        showImg('merge3', merge3)

        # 将焦点标识取出来
        ys, xs = np.where(bitwise_and > 0)

        # 横纵坐标数组
        y_point_arr = []
        x_point_arr = []
        # 通过排序，排除掉相近的像素点，只取相近值的最后一点
        # 这个10就是两个像素点的距离，不是固定的，根据不同的图片会有调整，基本上为单元格表格的高度（y坐标跳变）和长度（x坐标跳变）
        i = 0
        sort_x_point = np.sort(xs)
        for i in range(len(sort_x_point) - 1):
            if sort_x_point[i + 1] - sort_x_point[i] > 10:
                x_point_arr.append(sort_x_point[i])
            i = i + 1
        # 要将最后一个点加入
        x_point_arr.append(sort_x_point[i])

        i = 0
        sort_y_point = np.sort(ys)
        # print(np.sort(ys))
        for i in range(len(sort_y_point) - 1):
            if (sort_y_point[i + 1] - sort_y_point[i] > 10):
                y_point_arr.append(sort_y_point[i])
            i = i + 1
        y_point_arr.append(sort_y_point[i])

        return x_point_arr, y_point_arr
