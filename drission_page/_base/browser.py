# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from pathlib import Path
from shutil import rmtree
from time import sleep, perf_counter

from websocket import WebSocketBadStatusException

from .driver import BrowserDriver, Driver
from .._functions.tools import stop_process_on_port, raise_error
from .._units.downloader import DownloadManager
from ..errors import PageDisconnectedError

__ERROR__ = 'error'


class Browser(object):
    BROWSERS = {}

    def __new__(cls, address, browser_id, page):
        """
        :param address: 浏览器地址
        :param browser_id: 浏览器id
        :param page: ChromiumPage对象
        """
        if browser_id in cls.BROWSERS:
            return cls.BROWSERS[browser_id]
        return object.__new__(cls)

    def __init__(self, address, browser_id, page):
        """
        :param address: 浏览器地址
        :param browser_id: 浏览器id
        :param page: ChromiumPage对象
        """
        if hasattr(self, '_created'):
            return
        self._created = True
        Browser.BROWSERS[browser_id] = self

        self.page = page
        self.address = address
        self._driver = BrowserDriver(browser_id, 'browser', address, self)
        self.id = browser_id
        self._frames = {}
        self._drivers = {}
        self._all_drivers = {}
        self._connected = False

        self._process_id = None
        try:
            r = self.run_cdp('SystemInfo.getProcessInfo')
            for i in r.get('processInfo', []):
                if i['type'] == 'browser':
                    self._process_id = i['id']
                    break
        except:
            pass

        self.run_cdp('Target.setDiscoverTargets', discover=True)
        self._driver.set_callback('Target.targetDestroyed', self._onTargetDestroyed)
        self._driver.set_callback('Target.targetCreated', self._onTargetCreated)

    def _get_driver(self, tab_id, owner=None):
        """新建并返回指定tab id的Driver
        :param tab_id: 标签页id
        :param owner: 使用该驱动的对象
        :return: Driver对象
        """
        d = self._drivers.pop(tab_id, Driver(tab_id, 'page', self.address))
        d.owner = owner
        self._all_drivers.setdefault(tab_id, set()).add(d)
        return d

    def _onTargetCreated(self, **kwargs):
        """标签页创建时执行"""
        if (kwargs['targetInfo']['type'] in ('page', 'webview')
                and kwargs['targetInfo']['targetId'] not in self._all_drivers
                and not kwargs['targetInfo']['url'].startswith('devtools://')):
            try:
                tab_id = kwargs['targetInfo']['targetId']
                d = Driver(tab_id, 'page', self.address)
                self._drivers[tab_id] = d
                self._all_drivers.setdefault(tab_id, set()).add(d)
            except WebSocketBadStatusException:
                pass

    def _onTargetDestroyed(self, **kwargs):
        """标签页关闭时执行"""
        tab_id = kwargs['targetId']
        if hasattr(self, '_dl_mgr'):
            self._dl_mgr.clear_tab_info(tab_id)
        for key in [k for k, i in self._frames.items() if i == tab_id]:
            self._frames.pop(key, None)
        for d in self._all_drivers.get(tab_id, tuple()):
            d.stop()
        self._drivers.pop(tab_id, None)
        self._all_drivers.pop(tab_id, None)

    def connect_to_page(self):
        """执行与page相关的逻辑"""
        if not self._connected:
            self._dl_mgr = DownloadManager(self)
            self._connected = True

    def run_cdp(self, cmd, **cmd_args):
        """执行Chrome DevTools Protocol语句
        :param cmd: 协议项目
        :param cmd_args: 参数
        :return: 执行的结果
        """
        ignore = cmd_args.pop('_ignore', None)
        r = self._driver.run(cmd, **cmd_args)
        return r if __ERROR__ not in r else raise_error(r, ignore)

    @property
    def driver(self):
        return self._driver

    @property
    def tabs_count(self):
        """返回标签页数量"""
        j = self.run_cdp('Target.getTargets')['targetInfos']  # 不要改用get，避免卡死
        return len([i for i in j if i['type'] in ('page', 'webview') and not i['url'].startswith('devtools://')])

    @property
    def tabs(self):
        """返回所有标签页id组成的列表"""
        j = self._driver.get(f'http://{self.address}/json').json()  # 不要改用cdp，因为顺序不对
        return [i['id'] for i in j if i['type'] in ('page', 'webview') and not i['url'].startswith('devtools://')]

    @property
    def process_id(self):
        """返回浏览器进程id"""
        return self._process_id

    def find_tabs(self, title=None, url=None, tab_type=None, single=True):
        """查找符合条件的tab，返回它们的id组成的列表
        :param title: 要匹配title的文本
        :param url: 要匹配url的文本
        :param tab_type: tab类型，可用列表输入多个
        :param single: 是否返回首个结果的id，为False返回所有信息
        :return: tab id或tab列表
        """
        tabs = self._driver.get(f'http://{self.address}/json').json()  # 不要改用cdp

        if isinstance(tab_type, str):
            tab_type = {tab_type}
        elif isinstance(tab_type, (list, tuple, set)):
            tab_type = set(tab_type)
        elif tab_type is not None:
            raise TypeError('tab_type只能是set、list、tuple、str、None。')

        r = [i for i in tabs if ((title is None or title in i['title']) and (url is None or url in i['url'])
                                 and (tab_type is None or i['type'] in tab_type))]
        return r[0]['id'] if r and single else r

    def close_tab(self, tab_id):
        """关闭标签页
        :param tab_id: 标签页id
        :return: None
        """
        self._onTargetDestroyed(targetId=tab_id)
        self.driver.run('Target.closeTarget', targetId=tab_id)

    def stop_driver(self, driver):
        """停止一个Driver
        :param driver: Driver对象
        :return: None
        """
        driver.stop()
        self._all_drivers.get(driver.id, set()).discard(driver)

    def activate_tab(self, tab_id):
        """使标签页变为活动状态
        :param tab_id: 标签页id
        :return: None
        """
        self.run_cdp('Target.activateTarget', targetId=tab_id)

    def get_window_bounds(self, tab_id=None):
        """返回浏览器窗口位置和大小信息
        :param tab_id: 标签页id
        :return: 窗口大小字典
        """
        return self.run_cdp('Browser.getWindowForTarget', targetId=tab_id or self.id)['bounds']

    def quit(self, timeout=5, force=False):
        """关闭浏览器
        :param timeout: 等待浏览器关闭超时时间（秒）
        :param force: 是否立刻强制终止进程
        :return: None
        """
        for tab in self._all_drivers.values():
            for driver in tab:
                driver.stop()
        try:
            self.run_cdp('Browser.close')
        except PageDisconnectedError:
            self.driver.stop()
            return
        self.driver.stop()

        if force:
            ip, port = self.address.split(':')
            if ip not in ('127.0.0.1', 'localhost'):
                return
            stop_process_on_port(port)
            return

        if self.process_id:
            from os import popen
            from platform import system
            txt = f'tasklist | findstr {self.process_id}' if system().lower() == 'windows' \
                else f'ps -ef | grep  {self.process_id}'
            end_time = perf_counter() + timeout
            while perf_counter() < end_time:
                p = popen(txt)
                sleep(.1)
                try:
                    if f'  {self.process_id} ' not in p.read():
                        return
                except TypeError:
                    pass

    def _on_disconnect(self):
        self.page._on_disconnect()
        Browser.BROWSERS.pop(self.id, None)
        if self.page._chromium_options.is_auto_port and self.page._chromium_options.user_data_path:
            path = Path(self.page._chromium_options.user_data_path)
            end_time = perf_counter() + 7
            while perf_counter() < end_time:
                if not path.exists():
                    break
                try:
                    rmtree(path)
                    break
                except (PermissionError, FileNotFoundError, OSError):
                    pass
