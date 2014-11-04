#!/usr/bin/python
#coding=utf-8
#Filename:compiler_two.py

'''
Created on 2013-11-1
debugged on 2014-11-03

@author: Jarel Zhou
@author: winlandiano
'''
import string
import lexical_parser_kernel

tokenList = []
terminalSignMap = {}
nonTerminalSignMap = {}
productList = []
productListFor3 = []
emptySignList = []
analyseTable = {}
resultList = []
errorList = []
fuhaoMap = {}
currentTable = 'root'
hasValueList = ['IDN','CHAR','INT','FLOAT','DOUBLE','VOID','int','float','double']
dizhima = []

def init(code_sequence):
#    print '-----  init() start  -----'
    global tokenList
    global terminalSignMap
    global nonTerminalSignMap
    global productList
    initTokenList(code_sequence)
    initTerminalSignMap()
    initNonTerminalSignMap()
    initProductList()
    
def initTokenList(code_sequence):
    global tokenList
    result = lexical_parser_kernel.main(code_sequence)
    for eachline in result:
        if len(eachline)!=0:
            splitLine = eachline.split(' ')
            tokenList.append(Token(splitLine[0], splitLine[1]))
            
            
def initTerminalSignMap():
    global terminalSignMap
    f = open('terminalSignList.txt')
    for line in f:
        line=line.strip('\r\n')
        if len(line) != 0:
            terminalSignMap[line]=TerminalSign(line)

def initNonTerminalSignMap():
    global nonTerminalSignMap
    f = open('nonTerminalSignList.txt')
    for line in f:
        line=line.strip('\r\n')
        if len(line) != 0:
            nonTerminalSignMap[line] = NonTerminalSign(line)
    print nonTerminalSignMap

def initProductList():
    global productList
    global productListFor3
    f = open('grammar.txt')
    for line in f:
        line=line.strip('\r\n')
        if len(line) != 0:
            splitLine = line.split(' ')
            product = Product()
            product.left = splitLine[0]
            for item in splitLine[1:]:
                product.right.append(item)
            productList.append(product)
    f.close()
    
    f = open('grammar_with_action.txt')
    for line in f:
        line=line.strip('\r\n')
        if len(line) != 0:
            splitLine = line.split(' ')
            product = Product()
            product.left = splitLine[0]
            for item in splitLine[1:]:
                product.right.append(item)
            productListFor3.append(product)
    f.close()

def calculateEmpty():
    print '-----  calculateEmpty() start  -----'
    
    global emptySignList
    global productList
    for product in productList:
        if product.right[0] == '$':
            emptySignList.append(product.left)
    while True:
        isChanged = False
        for product in productList:
            isEmpty = True
            for i in range(0, len(product.right)):
                if product.right[i] not in emptySignList:
                    isEmpty = False
                    break
            if isEmpty:
                emptySignList.append(product.left)
                isChanged = True
        if not isChanged:
            break

    print '-----  calculateEmpty() end  -----'

def calculateFirst():
    print '-----  calculateFirst() start  -----'
    global terminalSignMap
    global nonTerminalSignMap
    global productList
    global emptySignList
    # step 1
    for key, value in terminalSignMap.items():
        value.first.append(key)
    # step 2
    for product in productList:
        if product.right[0] in terminalSignMap and product.right[0] not in nonTerminalSignMap[product.left].first:
            nonTerminalSignMap[product.left].first.append(product.right[0])
            print 'Step 2: add ' + product.right[0] + ' to ' + product.left
    
    while True:
        isChanged = False
        # step 3
        for product in productList:
            if product.right[0] in nonTerminalSignMap:
                for item in nonTerminalSignMap[product.right[0]].first:
                    if item not in nonTerminalSignMap[product.left].first:
                        nonTerminalSignMap[product.left].first.append(item)
                        print 'Step 3: add ' + item + ' to ' + product.left
                        isChanged = True
        # step 4
        for product in productList:
            for i in range(0, len(product.right)):
                if product.right[i] in emptySignList:
                    #合并first集到product[0]
                    for item in nonTerminalSignMap[product.right[i]].first:
                        if item not in nonTerminalSignMap[product.left].first:
                            nonTerminalSignMap[product.left].first.append(item)
                            print 'Step 4: add ' + item + ' to ' + product.left
                            isChanged = True
                else:
                    break
        if not isChanged:
            break
        print '\n'
        for key, value in nonTerminalSignMap.items():
            print key, value.first
        print '\n'
    
    print '-----  calculateFirst() end  -----\n'

def calculateFollow():
    print '-----  calculateFollow() start  -----'
    global productList
    global terminalSignMap
    global nonTerminalSignMap
    
    # step 1
    nonTerminalSignMap['S'].follow.append('#')
    
    # step 2
    for product in productList:
        for i in range(0, len(product.right) - 1):
            # 合并开始
            if product.right[i] in terminalSignMap:
                continue
            beta = []
            beta = product.right[i + 1: len(product.right)]
            combineList(getFirstOfList(beta), nonTerminalSignMap[product.right[i]].follow)
    
    print '----- step 2: nonTerminal sign follow'
    for key, value in nonTerminalSignMap.items():
        print key, value.follow
    
    # step 3
    while True:
        isChanged = False
        
        for product in productList:
            if product.right[-1] in nonTerminalSignMap:
                print 'step 3: product.left: ', product.left, 'product.right[-1]', product.right[-1]
                if combineList(nonTerminalSignMap[product.left].follow, nonTerminalSignMap[product.right[-1]].follow):
                    isChanged = True
        print '----- step 3\': nonTerminal sign follow'
        for key, value in nonTerminalSignMap.items():
            print key, value.follow
        
        for product in productList:
            seq = range(1, len(product.right))
            seq.reverse()
            print 'step 3 seq:', seq
            for i in seq:
                if product.right[i] in emptySignList and product.right[i - 1] in nonTerminalSignMap:
                    print '##### debug:', product.left, product.right[i - 1]
                    if combineList(nonTerminalSignMap[product.left].follow, nonTerminalSignMap[product.right[i - 1]].follow):
                        isChanged = True
                else:
                    break
        print '----- step 3": nonTerminal sign follow'
        for key, value in nonTerminalSignMap.items():
            print key, value.follow
        
        print 'isChanged:', isChanged, '\n'
        if not isChanged:
            break
    
    print '-----  calculateFollow() end  -----\n'

def calculateSelect():
    print '-----  calculateSelect() start  -----'
    
    global productList
    
    for product in productList:
        if product.right == ['$']:
            product.select = nonTerminalSignMap[product.left].follow[:]
            print 'product',product.left,product.right,'is $, select = ',product.left,'\'s follow'
        else:
            print 'product',product.left,product.right,', select = right\'s first'
            product.select = getFirstOfList(product.right)
            
            isEmpty = True
            for item in product.right:
                if item not in emptySignList:
                    isEmpty = False
                    break
                
            if isEmpty:
                print 'and it can be $, so add',product.left,'\'s follow to its select'
                combineList(nonTerminalSignMap[product.left].follow, product.select)
        print 'so now select is', product.select, '\n'
    
    print '-----  calculateSelect() end  -----\n'

def makeAnalyseTable():
    print '-----  makeAnalyseTable() start  -----'
    
    global analyseTable
    global productList
    global productListFor3
    
    isError = False
    
    # 复制productList中的select集到productListFor3
    if len(productList) != len(productListFor3):
        print '你妹妹的，两个不一样长啊，亲~'
        quit()
    for i in range(0, len(productList)):
        productListFor3[i].select = productList[i].select[:]
    
    for p in productListFor3:
        if p.left not in analyseTable:
            analyseTable[p.left] = {}
        for s in p.select:
            if s not in analyseTable[p.left]:
                analyseTable[p.left][s] = p.right[:]
            else:
                print '生成分析表时发生冲突:'
                print '已存在：左部', p.left, '，符号', s, '，产生式', analyseTable[p.left][s]
                print '又企图存入', p.right[:]
                isError = True
    
    if isError:
        quit()
    print '-----  makeAnalyseTable() end  -----\n'

def analyseSyntax():
    print '\n-----  analyseSyntax() start  -----'
    global tokenList
    global terminalSignMap
    global nonTerminalSignMap
    global analyseTable
    global resultList
    global errorList
    global fuhaoMap
    global currentTable
    global hasValueList
    global dizhima
    
    stack = [['#'],['S']]
    i = 0
    currentType = ''
    currentSize = -1
    currentIdn = ''
    isArray = False
    e_stack = []
    currentTNumber = 1
    currentAssignTo = ''
    findLocationList = []
#    isError = False
    
    fuhaoMap['root'] = [] # 初始化fuhaoMap 
    
    while stack[-1] != ['#']:
        print '\n----- i =', i, ', stack: ',
        for item in stack:
            print ''
            for item1 in item:
                print item1, '\t',
        print '\n-- stack end--\n'
        print '-----符号表-----'
        for item,value in fuhaoMap.items():
            print item, value
        print 'currentType是',currentType
        print 'currentSize是',currentSize
        print 'currentIdn是',currentIdn
        print 'currentAssign是',currentAssignTo
        print 'e_stack是',e_stack
        print '-----三地址码'
        for q in range(0,len(dizhima)):
            print q, dizhima[q]
        print '-----三地址码end'
        x = stack[-1]
        a = tokenList[i]
        print 'x =', x[0], 'a =', a.token, a.value
        # 是否为语义子程序
        if x[0] == '_act_':
            print x[1], '是个语义子程序，对吧~'
            
            if x[1] == '_act_type_1':
                stack[-2][2] = x[2]['syn']
                
            elif x[1] == '_act_function_1':
                stack[-4][2]['type'] = x[2]['syn'] 
            elif x[1] == '_act_function_2':
                fuhaoMap['root'].append([x[2]['syn'],'function',x[2]['syn']])
                fuhaoMap[x[2]['syn']] = [['root',0]]
                currentTable = x[2]['syn']
                print '加了一个符号表！！',currentTable
                
            elif x[1] == '_act_declaration_1':
                currentType = x[2]['syn']
                if currentType == 'int':
                    currentSize = 4
                elif currentType == 'float':
                    currentSize = 8
                elif currentType == 'double':
                    currentSize = 16
                elif currentType == 'char':
                    currentSize = 1
                else:
                    print '这是啥类型，不认识'
                    quit()
            elif x[1] == '_act_declaration_2':
                currentIdn = x[2]['syn']
            elif x[1] == '_act_declaration_3':
                # 插入符号表
                for item in fuhaoMap[currentTable]:
                    if item[0] == currentIdn:
                        print '标识符冲突：',currentIdn
                        quit()
                if isArray:
                    fuhaoMap[currentTable].append([currentIdn,'array(' + currentType + ')',fuhaoMap[currentTable][0][1]])
                else:
                    fuhaoMap[currentTable].append([currentIdn,currentType,fuhaoMap[currentTable][0][1]])
                fuhaoMap[currentTable][0][1] += currentSize 
                print '插了一个符号！',fuhaoMap[currentTable]
                isArray = False
            
            elif x[1] == '_act_declaration_list_1':
                #print '我在这里！！！'
                currentIdn = x[2]['syn']
            elif x[1] == '_act_declaration_list_2':
                for item in fuhaoMap[currentTable]:
                    if item[0] == currentIdn:
                        print '标识符冲突：',currentIdn
                        quit()
                fuhaoMap[currentTable].append([currentIdn,currentType,fuhaoMap[currentTable][0][1]])
                fuhaoMap[currentTable][0][1] += currentSize 
                print '又插了一个符号！',fuhaoMap[currentTable]
                isArray = False
            
            elif x[1] == '_act_declaration_number_1':
                #print '我在这里'
                isArray = True
                currentSize *= int(x[2]['syn'])
                print 'currentSize变成了',currentSize
                
            elif x[1] == '_act_variable_1':
                #print '我在这里1'
                currentIdn = x[2]['syn']
                notDefignedflag = True
                for item in fuhaoMap[currentTable]:
                    if item[0] == currentIdn:
                        notDefignedflag = False
                if notDefignedflag:
                    print '标识符未定义',currentIdn
                    quit()
            elif x[1] == '_act_variable_sub_sub_1':
                # 处理数组的情况
                currentIdn += '[' + x[2]['syn'] + ']'
                print '处理数组1'
            elif x[1] == '_act_variable_sub_sub_2':
                currentIdn += '[' + x[2]['syn'] + ']'
                print '处理数组2'
                notDefignedflag = True
                for item in fuhaoMap[currentTable]:
                    if item[0] == x[2]['syn']:
                        notDefignedflag = False
                if notDefignedflag:
                    print '标识符未定义',x[2]['syn']
                    quit()
            elif x[1] == '_act_assign_sub_1':
                currentAssignTo = currentIdn
            elif x[1] == '_act_assignment_statement_1':
                if len(e_stack) == 1:
                    print '-->', 't'+str(currentTNumber), '=', e_stack[-1]
                    dizhima.append('-->t'+str(currentTNumber)+'='+ e_stack[-1])
                    print '-->', currentAssignTo, '= t'+str(currentTNumber)
                    dizhima.append('-->' + currentAssignTo + '= t' +str(currentTNumber))
                    e_stack = []
                    currentTNumber += 1
                elif len(e_stack) > 1:
                    while len(e_stack) != 1:
                        print '-->', 't'+str(currentTNumber), '=', e_stack[0],e_stack[1],e_stack[2]
                        dizhima.append('-->t'+str(currentTNumber)+ '='+e_stack[0]+' '+e_stack[1]+' '+e_stack[2])
                        e_stack = e_stack[3:]
                        e_stack.insert(0,'t'+str(currentTNumber))
                        currentTNumber += 1
                    print '-->', currentAssignTo, '= t'+str(currentTNumber-1)
                    dizhima.append('-->'+ currentAssignTo+'= t'+str(currentTNumber-1))
                    e_stack = []
                    print '马上输出啦'
                else:
                    print '你妹的，e_stack里没东西啊！'
                    quit()
            elif x[1] == '_act_expression_1':
                print '我是_act_expression_1，我什么也不做'
            elif x[1] == '_act_expression_2':
                print '我是_act_expression_2，我什么也不做'
            elif x[1] in ['_act_cd_1','_act_cd_2','_act_cd_3']:
                stack[-2][2] = x[2]['syn']
            elif x[1] == '_act_expression_3':
                e_stack.append(x[2]['syn'])
            elif x[1] == '_act_expression_4':
                e_stack.append(currentIdn)
            elif x[1] == '_act_expression_5':
                print '-->', 't'+str(currentTNumber), '=', e_stack[-3],e_stack[-2],e_stack[-1]
                dizhima.append('-->t'+str(currentTNumber)+'='+ e_stack[-3]+' ' +e_stack[-2] +' '+e_stack[-1])
                e_stack.pop()
                e_stack.pop()
                e_stack.pop()
                e_stack.append('t'+str(currentTNumber))
                currentTNumber += 1
                print '出现括号啦，输出括号内容'
                
            elif x[1] == '_act_expression_sub_1':
                print '_act_expression_sub_1，我什么也不做'
            elif x[1] == '_act_while_block_1':
                dizhima.append('if '+string.join(e_stack,'')+' goto ' + str(len(dizhima) + 2))
                dizhima.append('goto ')
                findLocationList.append(len(dizhima))
                e_stack = []
                
            elif x[1] == '_act_while_block_2':
                findLocationList_pop_tmp = findLocationList.pop()
                dizhima.append('goto '+str(findLocationList_pop_tmp - 2))
                dizhima[findLocationList_pop_tmp - 1] += str(len(dizhima))
                
                
            elif x[1] == '_act_if_block_1':
                dizhima.append('if '+string.join(e_stack,'')+' goto ' + str(len(dizhima) + 2))
                dizhima.append('goto ')
                findLocationList.append(len(dizhima))
                e_stack = []
                
            elif x[1] == '_act_if_block_2':
                dizhima[findLocationList.pop() - 1] += str(len(dizhima) + 1)
                dizhima.append('goto '+str(len(dizhima)+1))
                findLocationList.append(len(dizhima))
            elif x[1] == '_act_if_block_3':
                dizhima[findLocationList.pop() - 1] = 'goto '+str(len(dizhima))
            else:
                print '喂，没有这个子程序啊：',x[1]
            
            stack.pop()
        # 是否为符号的综合属性_syn_
        elif x[0] == '_syn_':
            print x[1], '是个综合属性，对吧~'
            print 'debug',stack[-2]
            if x[1] in ['INT','FLOAT','DOUBLE','VOID','CHAR','type','IDN','int','float','double','char','CD','OP']:
                stack[-2][2]['syn'] = x[2]
            else:
                print '我是个_syn_，可是我没有把自己的值给下一位哦'
#             if x[1] in ['INT','FLOAT','DOUBLE','VOID','CHAR']:
#                 stack[-2][2]['type'] = x[1]
#                 print '我是个综合属性，我把自己的值传给了下一位的type'
#             elif x[1] == 'type':
#                 #这个不影响
#                 stack[-2][2]['type'] = x[2]
#             elif x[1] == 'IDN':
#                 #这个会有影响
#                 stack[-2][2]['IDN'] = x[2]
#             elif x[1] == 'int':
#                 #这个也会有影响
#                 stack[-2][2]['value'] = x[2]
            stack.pop()
        # 是否为终结符或#
        elif x[0] in terminalSignMap or x[0] == '#':
            print x, '哦，这好像是一个终结符'
            if x[0] == a.token:
                if x[0] != '#':
                    if x[0] in ['+','-','*','/','%','>','<','==','!=','>=','<=','||','&&']:
                        print '把符号加入e_stack'
                        e_stack.append(x[0])
                    print stack.pop(), 'is pop out 1'
                    ################
                    if x[0] in hasValueList:
                        print '终结符的值传给下一位综合属性'
                        stack[-1][2] = a.value
                    ################
                    i += 1
                    print 'now i is', i
            else:
                print 'ERROR: analyseSyntax() 1'
                print 'expecting a', x[0], ', but get a', a.token
#                isError = True
#                 errorList.append('ERROR: analyseSyntax() 1')
#                 errorList.append('x = ' + x[0] + ', a = ' + a.token)
#                 errorList.append('expecting a ' + x[0] + ', but get ' + a.token)
#                 errorList.append('--')
                break
        # 是否为非终结符
        else:
            print x, '哦，这好像是一个非终结符~'
            if a.token in analyseTable[x[0]]:
                print stack.pop(), 'is pop out 2'
                print 'analyseTable[',x[0],'][',a.token,'] is', analyseTable[x[0]][a.token]
                if analyseTable[x[0]][a.token] != ['$']:
                    # 逆序把产生式压入栈
                    for s in analyseTable[x[0]][a.token][::-1]:
                        if s in hasValueList or s in nonTerminalSignMap:
                            # 插入s的综合属性节点
                            stack.append(['_syn_', s,''])
                        if s in terminalSignMap or s in nonTerminalSignMap:
                            stack.append([s,''])
                        else:
                            stack.append(['_act_',s,{}])
                    #print 'after append, stack is', stack
                else:
                    print 'because it is $, do not append it'
                resultList.append({x[0] : analyseTable[x[0]][a.token]})
                print 'RESULLT:', x[0],'->',
                for item in analyseTable[x[0]][a.token]:
                    print item, ' ',
            else:
                print 'ERROR: analyseSyntax() 2'
                print 'get', a.token
                print 'expecting', x[0]
                print 'x can be', analyseTable[x[0]]
                print 'but can\'t be', a.token
#                isError = True
#                 errorList.append('ERROR: analyseSyntax() 2')
#                 errorList.append('x = ' + x[0] + ', a = ' + a.token)
#                 errorList.append('get ' + a.token)
#                 errorList.append('expecting ' + x[0])
#                 errorList.append('x can\'t be ' + a.token)
#                 errorList.append('--')
                break
    dizhima.append('end')
    print '\ntokenList:'
    for t in tokenList[i:]:
        print t.token
    print 'stack:', stack
    print '-----  analyseSyntax() end  -----\n'

def combineList(fromList, toList):
    print '--combine()', fromList, toList
    isChanged = False
    for item in fromList:
        if item not in toList:
            toList.append(item)
            isChanged = True
    return isChanged

def getFirstOfList(l):
    global emptySignList
    global terminalSignMap
    global nonTerminalSignMap
    first = []
    
    for s in l:
        if s in terminalSignMap:
            combineList(terminalSignMap[s].first, first)
        elif s in nonTerminalSignMap:
            combineList(nonTerminalSignMap[s].first, first)
        if s not in emptySignList:
            break
    print 'getFirstOfList:',first
    return first

class TerminalSign:
    def __init__(self, sign):
        self.sign = sign
        self.first = []

class NonTerminalSign:
    def __init__(self, sign):
        self.sign = sign
        self.first = []
        self.follow = []
        #self.sync = []

class Product:
    def __init__(self):
        self.left = ''
        self.right = []
        self.select = []

class Token:
    def __init__(self, token, value):
        self.token = token
        self.value = value
        
def main(code_sequence):
    global tokenList
    global terminalSignMap
    global nonTerminalSignMap
    global productList
    global productListFor3
    global emptySignList
    global analyseTable
    global resultList
    global errorList
    global fuhaoMap
    global currentTable
    global hasValueList
    global dizhima
    tokenList = []
    terminalSignMap = {}
    nonTerminalSignMap = {}
    productList = []
    productListFor3 = []
    emptySignList = []
    analyseTable = {}
    resultList = []
    errorList = []
    fuhaoMap = {}
    currentTable = 'root'
    hasValueList = ['IDN','CHAR','INT','FLOAT','DOUBLE','VOID','int','float','double']
    dizhima = []
    init(code_sequence)
    calculateEmpty()
    print '----- emptySignList', emptySignList
    
    calculateFirst()
#     print '----- terminal sign first'
#     for key, value in terminalSignMap.items():
#         print key, value.first
    print '----- nonTerminal sign first'
    for key, value in nonTerminalSignMap.items():
        print key, value.first
    
    calculateFollow()
    print '----- nonTerminal sign follow'
    for key, value in nonTerminalSignMap.items():
        print key, value.follow

    calculateSelect()
    print '----- select'
    for p in productList:
        print p.left,p.right,p.select 
    
    makeAnalyseTable()
    print '----- analyseTable'
    for key, value in analyseTable.items():
        print key, value
    
    
    analyseSyntax()
    print '----- analyseSyntax'
    for result in resultList:
        for key, value in result.items():
            print key, '->',
            for item in value:
                print item,
            print ''
    if len(errorList) > 0:
        print '----- 错误信息'
        for item in errorList:
            print item
    else:
        print '程序文法正确'
        
    return dizhima
        


if __name__ == '__main__':
    main('')