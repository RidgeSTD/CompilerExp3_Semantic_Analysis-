#!/usr/bin/python
# Filename:One.py
import string
import wx
import os
import codecs

def isKeyWord(token):
    keyWordList = ('auto','default','do','enum','goto','long','register','short','signed','unsigned',
                   'sizeof','static','if', 'else', 'while', 'for', 'int', 'float', 'double', 'char', 
                   'return', 'const', 'void','switch', 'break', 'continue', 'case', 'struct',
                   'typedef', 'extern','union','volitile','NULL')
    if token in keyWordList:
        return True
    return False

def changePos(ch):
    global lineNum
    global columnNum
    if ch == '\n':
        lineNum += 1
        columnNum = 0
    else:
        columnNum += 1

def isBorder(ch):
    global faState
    if faState['float'] != 'h' and ch in (' ','\t','\n','!','#','%','&','|','*','(',')','-','=','+','{','}',',','/','?',':',
              ';',"'",'"','<','>','[',']'):
        return True
    elif faState['float'] == 'h' and ch in (' ','\t','\n','!','#','%','&','|','*','(',')','=','{','}',',','/','?',':',
              ';',"'",'"','<','>','[',']'):
        return True
    return False

def isSpace(ch):
    if ch in (' ', '\t', '\n'):
        return True
    return False

def reset():
    global tokenBuffer
    global faState
    global current
    global isError
    global isPrinted
    tokenBuffer = []
    faState = {'int':'s',
           'float':'s',
           'identifier':'s',
           'string':'s',
           'char':'s',
           'note':'s'}
    current = 'normal'
    isError = False
    isPrinted = False

def intFA(ch):
    global faState
    if faState['int'] == 's':
        if ch >= '0' and ch <= '9':
            faState['int'] = 't'
        else:
            faState['int'] = 'error'
    elif faState['int'] == 't':
        if ch >= '0' and ch <= '9':
            faState['int'] = 't'
        else:
            faState['int'] = 'error'

def floatFA(ch):
    global faState
    if faState['float'] == 's':
        if ch == '0':
            faState['float'] = 'a'
        elif ch >= '1' and ch <= '9':
            faState['float'] = 'm'
        else:
            faState['float'] = 'error'
    elif faState['float'] == 'a':
        if ch == '.':
            faState['float'] = 'b'
        else:
            faState['float'] = 'error'
    elif faState['float'] == 'b':
        if ch >= '0' and ch <= '9':
            faState['float'] = 'c'
        else:
            faState['float'] = 'error'
    elif faState['float'] == 'c':
        if ch >= '0' and ch <= '9':
            faState['float'] = 'c'
        else:
            faState['float'] = 'error'
    elif faState['float'] == 'd':
        if ch >= '0' and ch <= '9':
            faState['float'] = 'd'
        elif ch == '.':
            faState['float'] = 'b'
        else:
            faState['float'] = 'error'
    elif faState['float'] == 'm':
        if ch >= '0' and ch <= '9':
            faState['float'] = 'd'
        elif ch == '.':
            faState['float'] = 'k'
        else:
            faState['float'] = 'error'
    elif faState['float'] == 'k':
        if ch >= '0' and ch <= '9':
            faState['float'] = 'l'
        else:
            faState['float'] = 'error'
    elif faState['float'] == 'l':
        if ch >= '0' and ch <= '9':
            faState['float'] = 'l'
        elif ch == 'e':
            faState['float'] = 'h'
        else:
            faState['float'] = 'error'
    elif faState['float'] == 'h':
        if ch >= '1' and ch <= '9':
            faState['float'] = 'j'
        elif ch == '+' or ch == '-':
            faState['float'] = 'i'
        else:
            faState['float'] = 'error'
    elif faState['float'] == 'i':
        if ch >= '1' and ch <= '9':
            faState['float'] = 'j'
        else:
            faState['float'] = 'error'
    elif faState['float'] == 'j':
        if ch >= '0' and ch <= '9':
            faState['float'] = 'j'
        else:
            faState['float'] = 'error'

def identifierFA(ch):
    global faState
    if faState['identifier'] == 's':
        if (ch >= 'a' and ch <= 'z') or (ch >= 'A' and ch <= 'Z') or ch =='_':
            faState['identifier'] = 't'
        else:
            faState['identifier'] = 'error' 
    elif faState['identifier'] == 't':
        if (ch >= 'a' and ch <= 'z') or (ch >= 'A' and ch <= 'Z') or ch =='_' or (ch >= '0' and ch <='9'):
            faState['identifier'] = 't'
        else:
            faState['identifier'] = 'error'

def stringFA(ch):
    global faState
    global current
    if faState['string'] == 's':
        if ch == '"':
            current = 'string'
            faState['string'] = 'a'
        else:
            faState['string'] = 'error'
    elif faState['string'] =='a':
        if ch == '"':
            faState['string'] = 't'
    elif faState['string'] == 't':
        faState['string'] = 'error'

def charFA(ch):
    global faState
    global current
    if faState['char'] == 's':
        if ch == "'":
            current = 'char'
            faState['char'] = 'a'
        else:
            faState['char'] = 'error'
    elif faState['char'] == 'a':
        if ch != "'" and ch != '\\':
            faState['char'] = 'b'
        elif ch == '\\':
            faState['char'] = 'c'
        else:
            faState['char'] = 'error'
    elif faState['char'] == 'c':
        if ch in ['0','a','b','t','n','v','r','f','\\','"',"'"]:
            faState['char'] = 'b'
        else:
            faState['char'] = 'error'
    elif faState['char'] == 'b':
        if ch == "'":
            faState['char'] = 't'
        else:
            faState['char'] = 'error'
    elif faState['char'] == 't':
        faState['char'] = 'error'

def noteFA(ch):
    global faState
    global current
    if faState['note'] == 's':
        if ch == '/':
            faState['note'] = 'a'
        else:
            faState['note'] = 'error'
    elif faState['note'] =='a':
        if ch == '*':
            current = 'note'
            faState['note'] = 'b'
        else:
            faState['note'] = 'error'
    elif faState['note'] =='b':
        if ch == '*':
            faState['note'] = 'c'
    elif faState['note'] =='c':
        if ch == '/':
            faState['note'] = 't'
        elif ch == '*':
            pass
        else:
            faState['note'] = 'b'
    elif faState['note'] == 't':
        faState['note'] = 'error'

def singleToken(ch):
    global tokenBuffer
    global resultList
    resultList.append([string.join(tokenBuffer, ''), 'border', '-'])

def doNormal(ch):
    global tokenBuffer
    global faState
    global current
    global isError
    if isBorder(ch):
        if len(tokenBuffer) > 0:
            flag = 0
            if faState['int'] == 't':
                flag += 1
                resultList.append([string.join(tokenBuffer,''),'int', string.join(tokenBuffer,'')])
            elif faState['float'] in ('a','c','d','m','l','j'):
                flag += 1
                resultList.append([string.join(tokenBuffer,''), 'float', string.join(tokenBuffer,'')])
            elif faState['identifier'] == 't':
                flag += 1
                resultList.append([string.join(tokenBuffer,''), 'identifier', string.join(tokenBuffer,'')])
            elif faState['string'] == 't':
                flag += 1
                resultList.append([string.join(tokenBuffer,''), 'string', string.join(tokenBuffer,'')])
            elif faState['char'] == 't':
                flag += 1
                resultList.append([string.join(tokenBuffer,''), 'char', string.join(tokenBuffer,'')])
            elif faState['note'] == 't':
                flag += 1
                resultList.append([string.join(tokenBuffer,''), 'note', string.join(tokenBuffer,'')])
            
            reset()
            
            if flag == 0:
                isError = True
        if isSpace(ch) == False:
            tokenBuffer.append(ch)
            if ch == '"':
                current = 'string'
                stringFA(ch)
            elif ch == "'":
                current = 'char'
                charFA(ch)
            else:
                current = 'border'
    else:
        tokenBuffer.append(ch)
        faNum = 0
        if faState['int'] != 'error':
            faNum += 1
            intFA(ch)
        if faState['float'] != 'error':
            faNum += 1
            floatFA(ch)
        if faState['identifier'] != 'error':
            faNum += 1
            identifierFA(ch)
        if faState['string'] != 'error':
            faNum += 1
            stringFA(ch)
        if faState['char'] != 'error':
            faNum += 1
            charFA(ch)
        if faState['note'] != 'error':
            faNum += 1
            noteFA(ch)
        
        if faNum == 0:
            isError = True

class MainFrame(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'CompilerOne', size=(900, 600))
        self.panel = wx.Panel(self)
        self.analyzeButton = wx.Button(self.panel, label="Analyze", pos=(460, 365),size=(50, 25))
        self.Bind(wx.EVT_BUTTON, self.OnAnalyze, self.analyzeButton)
        self.openButton = wx.Button(self.panel, label="Open", pos=(400, 365),size=(50, 25))
        self.Bind(wx.EVT_BUTTON, self.OnOpenFile, self.openButton)
        self.codeTextCtrl = wx.TextCtrl(self.panel, -1, "", pos=(10, 10),size=(530,350),style=wx.TE_MULTILINE)
        self.resultTextCtrl = wx.TextCtrl(self.panel, -1, "", pos=(550, 10),size=(325,530),style=wx.TE_MULTILINE)
        self.errorTextCtrl = wx.TextCtrl(self.panel, -1, "", pos=(10, 400),size=(530,140),style=wx.TE_MULTILINE)
    def OnOpenFile(self, event):
        dialog = wx.FileDialog(None, "Choose a file", os.getcwd(),"", "", wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            f = file(dialog.GetPath())
            s = f.read()
            if s[:3] == codecs.BOM_UTF8:
                s = s[3:]
            self.codeTextCtrl.SetValue(s)
            self.resultTextCtrl.SetValue('')
            self.errorTextCtrl.SetValue('')
        dialog.Destroy()
    def OnAnalyze(self, event):
        global fileData
        global faState
        global tokenBuffer
        global resultList
        global lineNum
        global columnNum
        global current
        global isError
        global isPrinted
        global tokenListToFile
        
        fileData = ''
        faState = {'int':'s',
                   'float':'s',
                   'identifier':'s',
                   'string':'s',
                   'char':'s',
                   'note':'s'}
        tokenBuffer = []
        resultList = []
        lineNum = 1
        columnNum = 0
        current = 'normal'
        isError = False
        isPrinted = False
        
        self.resultTextCtrl.SetValue('')
        self.errorTextCtrl.SetValue('')
        
        fileData =  self.codeTextCtrl.GetValue()
        for ch in fileData:
            changePos(ch)
            print 'current state',current
            print 'CURRENT CH:',ch    
            if isError:
#                 if not isPrinted:
#                     pass
#                     
#                     isPrinted = True
                if isBorder(ch):
                    self.errorTextCtrl.AppendText('Syntax Error: Not a leagal '
                                                  +str(current)+' at line '+str(lineNum)
                                                  +' column '+str(columnNum) + ': ' + string.join(tokenBuffer,'') +'\n')
                    print 'Syntax Error: Not a leagal', current, 'at line', lineNum,' column', columnNum
                    reset()
                    continue
                else:
                    tokenBuffer.append(ch)
                    continue
            
            if current == 'border':
                if str(tokenBuffer[0] + ch) == '!=':
                    resultList.append(['!=', 'border', '-'])
                    reset()
                elif str(tokenBuffer[0] + ch) == '<=':
                    resultList.append(['<=', 'border', '-'])
                    reset()
                elif str(tokenBuffer[0] + ch) == '>=':
                    resultList.append(['>=', 'border', '-'])
                    reset()
                elif str(tokenBuffer[0] + ch) == '+=':
                    resultList.append(['+=', 'border', '-'])
                    reset()
                elif str(tokenBuffer[0] + ch) == '-=':
                    resultList.append(['-=', 'border', '-'])
                    reset()
                elif str(tokenBuffer[0] + ch) == '*=':
                    resultList.append(['*=', 'border', '-'])
                    reset()
                elif str(tokenBuffer[0] + ch) == '/=':
                    resultList.append(['/=', 'border', '-'])
                    reset()
                elif str(tokenBuffer[0] + ch) == '%=':
                    resultList.append(['%=', 'border', '-'])
                    reset()
                elif str(tokenBuffer[0] + ch) == '++':
                    resultList.append(['++', 'border', '-'])
                    reset()
                elif str(tokenBuffer[0] + ch) == '--':
                    resultList.append(['--', 'border', '-'])
                    reset()
                elif str(tokenBuffer[0] + ch) == '||':
                    resultList.append(['||', 'border', '-'])
                    reset()
                elif str(tokenBuffer[0] + ch) == '&&':
                    resultList.append(['&&', 'border', '-'])
                    reset()
                elif str(tokenBuffer[0] + ch) == '==':
                    resultList.append(['==', 'border', '-'])
                    reset()
                    
                elif str(tokenBuffer[0] + ch) == '/*':
                    tokenBuffer.append(ch)
                    current = 'note'
                    faState['note'] = 'b'
                else:
                    print 'singleToken()'
                    singleToken(ch)
                    reset()
                    doNormal(ch)
                    
            else:
                if current == 'normal':
                    doNormal(ch)
                elif current == 'char':
                    tokenBuffer.append(ch)
                    charFA(ch)
                    if faState['char'] == 't':
                        resultList.append([string.join(tokenBuffer, ''), 'char', string.join(tokenBuffer[1:2], '')])
                        reset()
                    elif faState['char'] == 'error':
                        isError = True
                elif current == 'string':
                    tokenBuffer.append(ch)
                    stringFA(ch)
                    if faState['string'] == 't':
                        resultList.append([string.join(tokenBuffer, ''), 'string', string.join(tokenBuffer[1:-1], '')])
                        reset()
                elif current == 'note':
                    tokenBuffer.append(ch)
                    noteFA(ch)
                    if faState['note'] == 't':
                        print 'NOTE, DROP', string.join(tokenBuffer, '')
                        #resultList.append([string.join(tokenBuffer, ''), 'note', string.join(tokenBuffer, '')])
                        reset()
            #print faState
            #print tokenBuffer
            #print '\n'
        
        if len(tokenBuffer) > 0:
            if current == 'normal':
                if faState['int'] == 't':
                    resultList.append([string.join(tokenBuffer, ''), 'int', string.join(tokenBuffer, '')])
                elif faState['float'] in ('a','c','d','m','l','j'):
                    resultList.append([string.join(tokenBuffer, ''), 'result', string.join(tokenBuffer, '')])
                elif faState['identifier'] == 't':
                    resultList.append([string.join(tokenBuffer, ''), 'identifier', string.join(tokenBuffer, '')])
                else:
                    print 'ERROR AT END'
                    self.errorTextCtrl.AppendText('ERROR AT END\n')
            elif current == 'note':
                if faState['note'] == 't':
                    resultList.append([string.join(tokenBuffer, ''), 'note', string.join(tokenBuffer, '')])
                else:
                    print 'NOTE ERROR AT END'
                    self.errorTextCtrl.AppendText('NOTE ERROR AT END\n')
            elif current == 'border':
                resultList.append([string.join(tokenBuffer, ''), 'border', '-'])
            elif current == 'char':
                if faState['char'] == 't':
                    resultList.append([string.join(tokenBuffer, ''), 'char', string.join(tokenBuffer, '')])
                else:
                    print 'CHAR ERROR AT END'
                    self.errorTextCtrl.AppendText('CHAR ERROR AT END\n')
            elif current == 'string':
                if faState['string'] == 't':
                    resultList.append([string.join(tokenBuffer, ''), 'string', string.join(tokenBuffer, '')])
                else:
                    print 'STRING ERROR AT END'
                    self.errorTextCtrl.AppendText('STRING ERROR AT END\n')
        
        for item in resultList:
            if item[1] == 'identifier':
                if isKeyWord(item[0]) != False:
                    if item[0] in ['int', 'float', 'double', 'char', 'void']:
                        item[2] = item[0]
                        item[1] = item[0].upper()
                    else:
                        item[1] = item[0]
                        item[2] = '-'
                else:
                    item[1] = 'IDN'
            elif item[1] == 'border':
                item[2] = '-'
                item[1] = item[0]
#                 if item[0] == '!':
#                     item[1] = 'NOT'
#                 elif item[0] == '#':
#                     item[1] = 'SHARP' 
#                 elif item[0] == '%':
#                     item[1] = 'PERCENT' 
#                 elif item[0] == '&':
#                     item[1] = 'AND' 
#                 elif item[0] == '|':
#                     item[1] = 'OR' 
#                 elif item[0] == '*':
#                     item[1] = 'MULTIPLY' 
#                 elif item[0] == '(':
#                     item[1] = 'LEFT_ROUND_BRACKET' 
#                 elif item[0] == ')':
#                     item[1] = 'RIGHT_ROUND_BRACKET' 
#                 elif item[0] == '-':
#                     item[1] = 'MINUS' 
#                 elif item[0] == '=':
#                     item[1] = 'EQUAL' 
#                 elif item[0] == '+':
#                     item[1] = 'PLUS' 
#                 elif item[0] == '{':
#                     item[1] = 'LEFT_CURLY_BRACKET' 
#                 elif item[0] == '}':
#                     item[1] = 'RIGHT_CURLY_BRACKET' 
#                 elif item[0] == ',':
#                     item[1] = 'COMMA' 
#                 elif item[0] == '/':
#                     item[1] = 'DIVIDE' 
#                 elif item[0] == '?':
#                     item[1] = 'QUESTION' 
#                 elif item[0] == ':':
#                     item[1] = 'COLON' 
#                 elif item[0] == ';':
#                     item[1] = 'SEMICOLON' 
#                 elif item[0] == '>':
#                     item[1] = 'GREATER_THAN' 
#                 elif item[0] == '<':
#                     item[1] = 'LESS_THAN' 
#                 elif item[0] == '[':
#                     item[1] = 'LEFT_SQUARE_BRACKET' 
#                 elif item[0] == ']':
#                     item[1] = 'RIGHT_SQUARE_BRACKET' 
#                 
#                 elif item[0] == '!=':
#                     item[1] = 'NOT_EQUAL' 
#                 elif item[0] == '>=':
#                     item[1] = 'GREATER_EQUAL' 
#                 elif item[0] == '<=':
#                     item[1] = 'LESS_EQUAL' 
#                 elif item[0] == '+=':
#                     item[1] = 'PLUS_EQUAL' 
#                 elif item[0] == '-=':
#                     item[1] = 'MINUS_EQUAL' 
#                 elif item[0] == '*=':
#                     item[1] = 'MULTIPLY_EQUAL' 
#                 elif item[0] == '/=':
#                     item[1] = 'DIVIDE_EQUAL' 
#                 elif item[0] == '%=':
#                     item[1] = 'PERCENT_EQUAL' 
#                 elif item[0] == '++':
#                     item[1] = 'PLUS_PLUS' 
#                 elif item[0] == '--':
#                     item[1] = 'MINUS_MINUS' 
#                 elif item[0] == '||':
#                     item[1] = 'OR_OR' 
#                 elif item[0] == '&&':
#                     item[1] = 'AND_AND' 
#                 elif item[0] == '==':
#                     item[1] = 'EQUAL_EQUAL' 
                    
        print '------------RESULT-------------'
        for item in resultList:   
            print item
            #self.resultTextCtrl.AppendText(item[0] + '\t' + item[1] + '\t' + item[2] + '\n')
            self.resultTextCtrl.AppendText(item[1] + ' ' + item[2] + '\n')
            tokenListToFile.append([item[1], item[2]])
        tokenListToFile.append(['#', '-'])
        f = open('tokenList.txt', 'w')
        for item in tokenListToFile:
            f.write(item[0] + ' ' + item[1] + '\n')
        f.close()
        tokenListToFile = []

fileData = ''
faState = {'int':'s',
           'float':'s',
           'identifier':'s',
           'string':'s',
           'char':'s',
           'note':'s'}
tokenBuffer = []
resultList = []
lineNum = 1
columnNum = 0
current = 'normal'
isError = False
isPrinted = False
tokenListToFile = []
if __name__ == '__main__':
    app = wx.PySimpleApp()
    mainFrame = MainFrame(parent=None, id=-1)
    mainFrame.Show()
    app.MainLoop()