

import os
import sys
import shutil
from ocr import OCRTools
from tools import Tools
from office import OfficeTools
from log import Log
import cv2
import re
import _thread

threadCount = 3


docxDir = Tools.getDocxDir()

cacheDir = Tools.getCacheDir()
Tools.createDir(cacheDir)
excelDir = Tools.getExcelDir()
Tools.createDir(excelDir)
logDir = Tools.getLogDir()
Tools.createDir(logDir)

""" for f in os.listdir(docxDir):
    if f.endswith('.docx'):
        print("    '" + Tools.joinPath(docxDir, f) + "',") """

docxFiles = (
    '../多湖街道/七里畈股东清册.docx',
    '../多湖街道/上古井村股东清册.docx',
    '../多湖街道/下渎口村股东清册.docx',
    '../多湖街道/东湄社区股权清册.docx',
    '../多湖街道/东盛村股东清册.docx',
    '../多湖街道/东龙口社区股东清册.docx',
    '../多湖街道/十二里村经济合作章程及股东清册.docx',
    '../多湖街道/四大门村股东清册.docx',
    '../多湖街道/垄窑村股东清册.docx',
    '../多湖街道/庄头社区股东清册.docx',
    '../多湖街道/新安村股东清册.docx',
    '../多湖街道/林头社区股东清册.docx',
    '../多湖街道/樟新村股东清册.docx',
    '../多湖街道/毛草山股东名册.docx',
    '../多湖街道/永红村股东清册.docx',
    '../多湖街道/潭头村股东清册.docx',
    '../多湖街道/王坦村股权清册.docx',
    '../多湖街道/王宅埠村股权清册.docx',
    '../多湖街道/西盛村股东名册.docx',
    '../多湖街道/近宅股东名单.docx',
    '../多湖街道/雅地村股东清册.docx',
    '../多湖街道/驿头村股东清册.docx',
    '../多湖街道/驿头村股东清册修改前.docx',
)

def doJob(i):
    docxFilePath = docxFiles[i]
    name = Tools.getFileName(docxFilePath)
    cDir = Tools.joinPath(cacheDir, str(i))
    Tools.createDir(cDir)
    officeTools = OfficeTools(cDir)
    picPaths, picDir = officeTools.extractPics(docxFilePath)
    fragDir = Tools.joinPath(cDir, 'fragment')
    Tools.createDir(fragDir)
    r = []
    leng = len(picPaths)
    # leng = 1 # TODO
    for j in range(leng):
        picPath = picPaths[j]
        childFragDir = Tools.joinPath(fragDir, str(j))
        Tools.createDir(childFragDir)
        ocr = OCRTools(childFragDir)
        tr = ocr.ocr(picPath)
        r += tr

    excelPath = Tools.joinPath(cDir, '{}.xlsx'.format(name))
    OfficeTools.writeIntoExcel(r, excelPath)
    shutil.copyfile(excelPath, Tools.joinPath(excelDir, '{}.xlsx'.format(name)))


def doJobs(name, tindex):
    docxCount = len(docxFiles)

    jobi = tindex
    while jobi < docxCount:
        try:
            doJob(jobi)
        except Exception as e:
            Log.e(str(e))
        jobi += threadCount


def startThread(tindex):
    try:
        _thread.start_new_thread(doJobs, ('Thread{}'.format(tindex + 1), tindex))
    except Exception as e:
        Log.e(str(e))

for i in range(threadCount):
    startThread(i)



input('任意键结束')

# for i in range(len(docxFiles)):
#     # doJob(i)
#     try:
#         # doJob(i)
#         pass
#     except Exception as e:
#         Log.e(str(e))





