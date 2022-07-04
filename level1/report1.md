# Level 1 实验报告

姓名：蓝俊玮 学号：PB20111689

实验环境：Windows 10 Python 3.9.0 Pycharm Community Edition 2021

## 1. 实验选题

Level 1.10 分子量计算：给定一个只含 $C,H,O,N$ 的化学分子式，输出它的分子量

## 2. 实验思路

对于一个只含 $C,H,O,N$ 的化学分子式而言，其化学分子式正确的格式一定是按 $C_xH_yO_mN_n$ 来的，即每个数字之前一定会有一个字母，那么可以将每个元素单独提取出来，将输入的化学分子式进行分割，得到多个部分，然后计算出各部分总的质量，最后加起来便是化学分子式的质量。其中采用的方法是用正则表达式进行分割：

```python
elements = re.findall('[A-Z][^A-Z]*', compound)
```

通过分割正则表达式分割，可以迅速且准确的得到各个原子的数量，同时还可以依此来判断输入的化学分子式是否有误（即判断输入了其他元素信息），当遇见错误时，则提示错误信息并返回重新输入。

## 3. 实验代码

```python
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

```

## 4. 实验测试

在终端输入即可运行：

```bash
pip install -r requirements.txt
python level1.py
```

当输入 $C_6H_6$， $C_2H_4O_2$，$C_2H_6ON$ 时：

![](C:\Users\蓝\Desktop\作业文件\Python交叉学科\Level1\correct.png)

当输入错误分子式或退出信息时：

![](C:\Users\蓝\Desktop\作业文件\Python交叉学科\Level1\fail.png)