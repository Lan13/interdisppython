from selenium import webdriver
from selenium.webdriver.common.by import By


if __name__ == '__main__':
    url = "https://www.ustc.edu.cn/"    # 科大主页的 url
    browser = webdriver.Edge()
    browser.get(url)    # 打开科大主页
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
