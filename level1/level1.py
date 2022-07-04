import re


if __name__ == '__main__':
    element_lists = ['C', 'H', 'O', 'N']
    element_weight = {'C': 12, 'H': 1, 'O': 16, 'N': 14}
    error = False
    while True:
        compound = input('please input a chemical formula(quit or q to exit): \n')
        if compound == 'quit' or compound == 'q':
            break
        compound = compound.upper()     # 将输入的小写字母转化为大写字母
        elements = re.findall('[A-Z][^A-Z]*', compound)     # 将四个元素分割开
        formula_weight = 0
        for element in elements:
            if len(element) == 1:   # 如果只有一个元素，没有数字时，即只有1个元素
                if element not in element_lists:    # 如果输入了其他元素，则显示错误信息
                    print("please input a correct chemical formula!")
                    error = True
                    break
                formula_weight = formula_weight + element_weight[element]
            else:
                if element[0] not in element_lists: # 如果输入了其他元素，则显示错误信息
                    print("please input a correct chemical formula!")
                    error = True
                    break
                formula_weight = formula_weight + element_weight[element[0]] * int(element[1])
        if not error:
            print(formula_weight)
        error = False
    print("finishing calculated formula weight!")
