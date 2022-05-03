from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from threading import Thread
from datetime import datetime


class TwitchPointCollector:
    def __init__(self, username, password, streamer, db, botMsgSender, faEnabled=False):
        self.username = username
        self.password = password
        self.url = f"https://www.twitch.tv/{streamer}"
        self.db = db
        self.faEnabled = faEnabled
        self.isRunning = False
        self.collectThread = Thread(target=self._collect)
        self.timeHandlerThread = Thread(target=self._handleTime)
        self.driver = webdriver.Firefox(
            service=Service(GeckoDriverManager().install()))
        self.todayName = datetime.today().strftime('%A')
        self.todaySchedule = self.db.getDaySchedule(self.todayName)
        self.timeHandlerThread.start()
        self.botMsgSender = botMsgSender
        self._2faCode = ''

    def _currentTimeParsed(self):
        now = datetime.now()
        return now.hour * 60 + now.minute

    def _isItTimeToRun(self):
        return not self.isRunning and self._currentTimeParsed() >= self.todaySchedule.get('startAt') and self._currentTimeParsed() < self.todaySchedule.get('endAt')

    def _isItTimeToStop(self):
        return self.isRunning and self._currentTimeParsed() > self.todaySchedule.get('endAt')

    def _handleTime(self):
        while True:
            today = datetime.today().strftime('%A')
            if self.todayName != today:
                self.todayName = today
                self.todaySchedule = self.db.getDaySchedule(today)
            if self._isItTimeToRun():
                self.collectThread.start()

    def _handle2faCode(self):
        self.botMsgSender.notify()
        while self._2faCode == '':
            continue
        faInput = self.driver.find_element(
            By.CSS_SELECTOR, ".focus-visible")
        faInput.send_keys(self._2faCode)
        self._2faCode = ''

    def _performLogin(self):
        self.driver.get(self.url)
        loginBtn = self.driver.find_element(
            By.CSS_SELECTOR, ".ScCoreButtonSecondary-sc-1qn4ixc-2 .Layout-sc-nxg1ff-0")
        loginBtn.click()
        usernameInput = WebDriverWait(self.driver, timeout=10).until(
            lambda d: d.find_element(By.ID, "login-username"))
        usernameInput.send_keys(self.username)
        passwordInput = WebDriverWait(self.driver, timeout=10).until(
            lambda d: d.find_element(By.ID, "password-input"))
        passwordInput.send_keys(self.password + Keys.ENTER)
        if self.faEnabled:
            self._handle2faCode()

    def _collectPoints(self):
        while not self._isItTimeToStop():
            rewardBtn = WebDriverWait(self.driver, timeout=900).until(
                lambda d: d.find_element(By.CSS_SELECTOR, ".claimable-bonus__icon"))
            if rewardBtn:
                rewardBtn.click()

    def _performLogout(self):
        self.driver.quit()

    def _collect(self):
        self.isRunning = True
        self._performLogin()
        self._collectPoints()
        self._performLogout()
        self.isRunning = False

    def start(self):
        self.timeHandlerThread.start()

    def set2faCode(self, faCode):
        self._2faCode = faCode
