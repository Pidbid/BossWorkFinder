# -*- encoding: utf-8 -*-
"""
@File    :   main.py
@Time    :   2024/09/08 14:23:31
@Author  :   Wicos 
@Version :   1.0
@Contact :   wicos@wicos.cn
@Blog    :   https://www.wicos.me
"""

# here put the import lib
import os
import csv
import time
import json
from DrissionPage import ChromiumPage, ChromiumOptions


YOUR_CITY = "金华"

config = (
    ChromiumOptions()
    .set_browser_path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
    .set_local_port(9224)
    .set_user_data_path("data1")
    .incognito()
)
page = ChromiumPage(addr_or_opts=config)


def boss_cities(save: bool = False, savename: str = "cities.json"):
    """跳过省直接获取所有的城市"""
    if os.path.exists(savename):
        return json.load(open(savename, "r", encoding="utf-8"))
    boss_index_url = "https://www.zhipin.com/?city=100010000&ka=city-sites-100010000"
    page.get(boss_index_url)
    # 模拟点击城市切换
    city_change_ele = page.ele("@class=switchover-city")
    city_change_ele.click()
    # 根据显示的数据筛选城市
    cities_data = {}
    city_elements = page.eles("@class=city-group-item__list")
    # print(len(city_elements))
    for i in city_elements:
        li_data = i.eles("tag:li")
        for j in li_data:
            a_data = j.ele("tag:a")
            # print(a_data.attr("href"), a_data.text)
            cities_data[a_data.text] = a_data.attr("href")
    if save:
        with open(savename, "w", encoding="utf-8") as fp:
            fp.write(json.dumps(cities_data, indent=4, ensure_ascii=False))
    return cities_data


cities = boss_cities()
your_city_url = cities[YOUR_CITY] if YOUR_CITY in cities.keys() else None
csv_header = [
    "name",
    "area",
    "salary",
    "experience",
    "education",
    "skills",
    "contact",
    "welfare",
    "company_name",
    "company_tags",
    "url",
]
csv_header_cn = [
    "名称",
    "地址",
    "薪资",
    "经验",
    "学历",
    "技能",
    "联系人",
    "福利",
    "公司名",
    "公司标签",
    "地址",
]
# 开始获取您所在城市的主页
page.get(your_city_url)
# 模拟点击您的目标职位
# 先点击“互联网AI”以展开右侧筛选框
work_ele = page.ele('xpath://*[@id="main"]/div/div[1]/div/div[1]/dl[1]/dd/b')
work_ele.click()
# 通过右侧的筛选框点击职位信息
job_ele = page.ele(
    'xpath://*[@id="main"]/div/div[1]/div/div[1]/dl[1]/div/ul/li[1]/div/a[4]'
)
job_class = job_ele.text
job_ele.click()
time.sleep(3)
# 获取主要内容部分并滑动页面至最底部
page.run_js("window.scrollTo(0, document.body.scrollHeight);")
# 获取有多少页
pages_ele = (
    page.ele('xpath://*[@id="wrap"]/div[2]/div[2]/div/div[1]/div[2]/div/div/div')
    .eles("tag:a")[-2]
    .text
)
pages = int(pages_ele)
print("共有{}页".format(pages))
# time.sleep(30)
job_data = []
# 首先写入csv头
with open(
    "./data/{}_{}.csv".format(YOUR_CITY, job_class), "w+", encoding="utf-8", newline=""
) as fp:
    wr = csv.writer(fp)
    wr.writerow(csv_header_cn)
    fp.close()
for i in range(pages):
    # 非第一页时进行新的页面跳转
    if i != 0:
        if "&page" in page.url:
            page.get(page.url.split("&page=")[0] + "&page=" + str(i + 1))
        else:
            page.get(page.url + "&page=" + str(i + 1))
        time.sleep(2)
        page.run_js("window.scrollTo(0, document.body.scrollHeight);")
    # 获取当前页面的工作列表
    print("当前正在获取页面{}的数据".format(i + 1))
    job_list = page.eles("tag:li@class=job-card-wrapper")
    print("共找到{}条招聘信息".format(len(job_list)))
    for j in job_list:
        in_job_data = []
        try:
            job_name = j.ele("tag:span@class=job-name").text
        except:
            continue
        job_area = (
            j.ele("tag:span@class=job-area").text.split("·")
            if "·" in j.ele("tag:span@class=job-area").text
            else j.ele("tag:span@class=job-area").text
        )
        job_salary = j.ele("tag:span@class=salary").text
        try:
            job_experience = j.ele("xpath:./div[1]/a/div[2]/ul/li[1]").text
            job_education = j.ele("xpath:./div[1]/a/div[2]/ul/li[2]").text
        except:
            continue
        job_contact = j.ele("tag:div@class=info-public").text
        job_company_name = j.ele("tag:h3@class=company-name").text
        try:
            job_c_list = j.ele("tag:ul@class=company-tag-list").eles("tag:li")
            job_company_tags = (
                [i.text for i in job_c_list] if len(job_c_list) > 0 else []
            )
        except:
            continue
        try:
            job_s_list = j.ele("xpath:./div[2]/ul").eles("tag:li")
            job_skills = [i.text for i in job_s_list] if len(job_s_list) > 0 else []
        except:
            continue
        job_welfare = j.ele("tag:div@class=info-desc").text
        job_url = j.ele("tag:a@class=job-card-left").attr("href")
        in_job_data = [
            job_name,
            job_area,
            job_salary,
            job_experience,
            job_education,
            job_skills,
            job_contact,
            job_welfare,
            job_company_name,
            job_company_tags,
            job_url,
        ]
        # print(
        #     job_name,
        #     job_area,
        #     job_salary,
        #     job_experience,
        #     job_education,
        #     job_contact,
        #     job_company_name,
        #     job_company_tags,
        #     job_skills,
        #     job_welfare,
        # )
        # job_data.append(in_job_data)
        with open(
            "./data/{}_{}.csv".format(YOUR_CITY, job_class),
            "a",
            encoding="utf-8",
            newline="",
        ) as fp:
            wr = csv.writer(fp)
            wr.writerow(in_job_data)
            fp.close()
    print("{}页{}条数据已采集写入完毕".format(i + 1, len(job_list)))
    time.sleep(2)

# 最后关闭
page.close()
