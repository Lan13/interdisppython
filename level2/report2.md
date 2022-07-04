# Level 2 实验报告

姓名：蓝俊玮 学号：PB20111689

实验环境：Windows 10 Python 3.9.0 Pycharm Community Edition 2021

## 1. 实验选题

Level 2.13 基于 Python，使用浏览器引擎 Selenium 爬取科大首页中的科大要闻第一条新闻，要求爬取结果至少有新闻标题、时间、以及新闻内容

## 2. 实验思路

通过 XPATH 的方式定位到我们所需要的元素位置，然后获取文本信息即可。通过仅两个月数10次的观察，发现科大主页的新闻元素布局的 XPATH 是不变的。所以通过审查页面元素，我们可以定位获取到相关内容或链接的 XPATH。最后通过点击链接或者获取元素的文本信息即可完成要求。

![](C:\Users\蓝\Desktop\作业文件\Python交叉学科\Level2\xptah.png)

## 3. 实验代码

**本次实验代码使用的是 Selenium 4.0.0 以及 Edge 浏览器**，实验开始前需要去  https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/ 下载最新的 Edge 浏览器引擎。

```python
from selenium import webdriver
from selenium.webdriver.common.by import By


if __name__ == '__main__':
    url = "https://www.ustc.edu.cn/"	# 科大主页的 url
    browser = webdriver.Edge()
    browser.get(url)	# 打开科大主页
    # 点击科大要闻的第一条新闻
    browser.find_element(By.XPATH, "/html/body/main/div[1]/section[1]/ul/li[1]/div[2]/h4[1]/a").click()
    # 获取新闻时间
    news_time = browser.find_element(By.XPATH, "/html/body/main/div/div/div[1]/form/div[1]").text
    # 获取新闻标题
    news_title = browser.find_element(By.XPATH, "/html/body/main/div/div/div[1]/form/div[2]").text
    # 获取新闻内容
    news_text = browser.find_element(By.XPATH, "/html/body/main/div/div/div[1]/form/div[3]/div").text
    print("新闻时间：", news_time)
    print("新闻标题：", news_title)
    print("新闻内容：", news_text)

```

## 4. 实验测试

在终端输入即可运行：

```bash
pip install -r requirements.txt
python level2.py
```

6 月 25 日运行测试：

![](C:\Users\蓝\Desktop\作业文件\Python交叉学科\Level2\June25.png)

6 月 29 日运行测试：

![](C:\Users\蓝\Desktop\作业文件\Python交叉学科\Level2\June29.png)

7 月 1 日运行测试：

![](C:\Users\蓝\Desktop\作业文件\Python交叉学科\Level2\July1.png)
