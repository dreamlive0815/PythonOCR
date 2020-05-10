
import cv2
from cnocr import CnOcr
from PIL import Image
from tools import Tools
from log import Log

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

class OCRTools():

    def __init__(self, cacheDir):
        super().__init__()
        self.cacheDir = cacheDir

    def preprocImage(self, img):
        grayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(grayImage, 150, 255, cv2.THRESH_TRUNC)
        return thresh

    def ocr(self, imgPath):
        ocr = CnOcr()
        img = cv2.imread(imgPath)
        img = self.preprocImage(img)
        cacheDir = self.cacheDir

        Log.i('ocring: {}'.format(imgPath))

        oy = LTY
        r = []
        for i in range(30):
            rr = []
            ty = oy + PADDING
            ih = RH - 2 * PADDING
            for j in range(len(XS) - 1):
                tx = XS[j] + PADDING
                iw = XS[j + 1] - XS[j] - 2 * PADDING
                tx = int(tx)
                ty = int(ty)
                bx = int(tx + iw)
                by = int(ty + ih)
                region = img[ty:by, tx:bx]
                fragStorePath = Tools.joinPath(cacheDir, '{}_{}.jpg'.format(i, j))
                cv2.imwrite(fragStorePath, region)
                resArr = ocr.ocr_for_single_line(fragStorePath)
                rr.append(''.join(resArr))
            Log.i('ocr at row {}, result = {}'.format(i + 1, rr))
            r.append(rr)
            oy = oy + RH

        return r
