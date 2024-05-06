import json
import os
from datetime import datetime
from time import sleep

from selenium.webdriver import Edge
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from local_storage import LocalStorage

PEOPLE = {"your name", 'another name'}
SHOW_ID = "227485"
TICKET_IDS = ["cdbd09d5c8b6d922978c1e5abb42ef13", "df0ed51798236d99806f224828a70f86"]
START_TIME = datetime(2024, 5, 2, 13, 00)

FLAG = True

people_indexs = []


def login(driver: Edge) -> None:
    driver.get(
        "https://wap.showstart.com/pages/passport/login/login?redirect=%2Fpages%2FmyHome%2FmyHome"
    )
    storage = LocalStorage(driver)
    if os.path.exists("session.json"):
        with open("session.json", "r") as f:
            session = json.load(f)
        for k, v in session.items():
            storage.set(k, v)
    else:
        print("请前往浏览器登陆")
        WebDriverWait(driver, 300).until(EC.title_contains("我的"))
        print("登陆成功，保存...")
        session = {}
        for key in [
            "sign",
            "userInfo",
            "st_flpv",
            "idToken",
            "accessToken",
            "__DC_STAT_UUID",
            "token",
        ]:
            session[key] = storage[key]
        with open("session.json", "w") as f:
            json.dump(session, f)


def sleep_until_zero_min(extra: float = 0.01) -> None:
    """
    睡眠直到整分钟
    """
    now = datetime.now()
    secs = 60 - now.second - now.microsecond / 1000000
    sleep(secs + extra)


def select_people(driver: Edge) -> None:
    # 打开身份证列表
    pleaseSelect = WebDriverWait(driver, 3).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".link-item>.rr>.tips"))
    )
    pleaseSelect.click()

    # 等待加载完毕
    WebDriverWait(driver, 3).until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                ".uni-scroll-view-content > uni-checkbox-group > uni-label",
            )
        )
    )

    # 选择观演人
    if people_indexs:
        # 使用缓存的 index
        for i in people_indexs:
            driver.find_element(
                By.CSS_SELECTOR,
                f".uni-scroll-view-content > uni-checkbox-group > uni-label:nth-child({i + 1})",
            ).click()
    else:
        items = driver.find_elements(
            By.CSS_SELECTOR, ".uni-scroll-view-content > uni-checkbox-group > uni-label"
        )
        for i, item in enumerate(items):
            name = item.find_element(By.CLASS_NAME, "name")
            if name.text.strip() in PEOPLE:
                item.click()
                people_indexs.append(i)

    # 确认
    confirm = WebDriverWait(driver, 3).until(
        EC.visibility_of_element_located(
            (
                By.CSS_SELECTOR,
                ".uni-popup-bottom > .pop-box > .pop-head > uni-view:nth-child(2)",
            )
        )
    )
    confirm.click()


def main(driver: Edge, ticket_id: str):
    login(driver)
    sleep = True
    while True:
        driver.get(
            f"https://wap.showstart.com/pages/order/activity/confirm/confirm?sequence={SHOW_ID}&ticketId={ticket_id}&ticketNum={len(PEOPLE)}"
        )
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".payBtn"))
        )

        select_people(driver)
        payBtn: WebElement = WebDriverWait(driver, 1).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".payBtn"))
        )

        if sleep:
            sleep_until_zero_min()

        if datetime.now() >= START_TIME and FLAG:
            payBtn.click()
            sleep = False
            print("已经进行抢票操作，请关注是否有验证码！")
            print("按下回车重试抢票！")
            input()


if __name__ == "__main__":
    driver = Edge()
    main(driver, TICKET_IDS[0])
