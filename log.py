
import sys
from tools import Tools

STYLE = {
    'fore':
    {   # 前景色
        'black'    : 30,   #  黑色
        'red'      : 31,   #  红色
        'green'    : 32,   #  绿色
        'yellow'   : 33,   #  黄色
        'blue'     : 34,   #  蓝色
        'purple'   : 35,   #  紫红色
        'cyan'     : 36,   #  青蓝色
        'white'    : 37,   #  白色
    },

    'back' :
    {   # 背景
        'black'     : 40,  #  黑色
        'red'       : 41,  #  红色
        'green'     : 42,  #  绿色
        'yellow'    : 43,  #  黄色
        'blue'      : 44,  #  蓝色
        'purple'    : 45,  #  紫红色
        'cyan'      : 46,  #  青蓝色
        'white'     : 47,  #  白色
    },

    'mode' :
    {   # 显示模式
        'mormal'    : 0,   #  终端默认设置
        'bold'      : 1,   #  高亮显示
        'underline' : 4,   #  使用下划线
        'blink'     : 5,   #  闪烁
        'invert'    : 7,   #  反白显示
        'hide'      : 8,   #  不可见
    },

    'default' :
    {
        'end' : 0,
    },
}

def UseStyle(string, mode = '', fore = '', back = ''):
    mode  = '%s' % STYLE['mode'][mode] if STYLE['mode'].__contains__(mode) else ''
    fore  = '%s' % STYLE['fore'][fore] if STYLE['fore'].__contains__(fore) else ''
    back  = '%s' % STYLE['back'][back] if STYLE['back'].__contains__(back) else ''
    style = ';'.join([s for s in [mode, fore, back] if s])
    style = '\033[%sm' % style if style else ''
    end   = '\033[%sm' % STYLE['default']['end'] if style else ''
    return '%s%s%s' % (style, string, end)

class Log():

    @classmethod
    def i(cls, msg):
        print(msg)

    @classmethod
    def e(cls, msg):
        s = '!!!ERROR!!! {}'.format(msg)
        print(UseStyle(s, fore = 'red'), file = sys.stderr)
        filePath = Tools.joinPath(Tools.getLogDir(), 'error.log')
        with open(filePath, 'a+') as f:
            f.write(msg + '\n')



