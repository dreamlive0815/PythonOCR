
import os

class Tools():

    @classmethod
    def getCacheDir(cls):
        return './cache'

    @classmethod
    def getDocxDir(cls):
        return '../多湖街道'

    @classmethod
    def createDir(cls, dirPath):
        dirPath = dirPath.strip()
        dirPath = dirPath.rstrip("\\")
        isExists = os.path.exists(dirPath)
        if not isExists:
            os.makedirs(dirPath)

    @classmethod
    def joinPath(cls, *arr):
        return '/'.join(arr)

    @classmethod
    def getFileName(cls, filePath):
        name = os.path.basename(filePath)
        nameWithoutSuf = name.split('.')[0]
        return nameWithoutSuf

    @classmethod
    def removeAllFiles(cls, dir):
        for root, dirs, files in os.walk(dir, topdown = False):
            for name in files:
                os.remove(cls.joinPath(root, name))
            for name in dirs:
                os.rmdir(cls.joinPath(root, name))