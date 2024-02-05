# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from pathlib import Path
from threading import Lock
from time import sleep, perf_counter

from requests import get

from .._base.browser import Browser
from .._configs.chromium_options import ChromiumOptions
from .._functions.browser import connect_browser
from .._functions.tools import PortFinder
from .._pages.chromium_base import ChromiumBase, get_mhtml, get_pdf, Timeout
from .._pages.chromium_tab import ChromiumTab
from .._units.setter import ChromiumPageSetter
from .._units.waiter import PageWaiter
from ..errors import BrowserConnectError


class ChromiumPage(ChromiumBase):
    """用于管理浏览器的类"""
    _PAGES = {}

    def __new__(cls, addr_or_opts=None, tab_id=None, timeout=None, addr_driver_opts=None):
        """
        :param addr_or_opts: 浏览器地址:端口、ChromiumOptions对象或端口数字（int）
        :param tab_id: 要控制的标签页id，不指定默认为激活的
        :param timeout: 超时时间（秒）
        """
        addr_or_opts = addr_or_opts or addr_driver_opts
        opt = handle_options(addr_or_opts)
        is_exist, browser_id = run_browser(opt)
        if browser_id in cls._PAGES:
            r = cls._PAGES[browser_id]
            while not hasattr(r, '_frame_id'):
                sleep(.1)
            return r
        r = object.__new__(cls)
        r._chromium_options = opt
        r._is_exist = is_exist
        r._browser_id = browser_id
        r.address = opt.address
        cls._PAGES[browser_id] = r
        return r

    def __init__(self, addr_or_opts=None, tab_id=None, timeout=None, addr_driver_opts=None):
        """
        :param addr_or_opts: 浏览器地址:端口、ChromiumOptions对象或端口数字（int）
        :param tab_id: 要控制的标签页id，不指定默认为激活的
        :param timeout: 超时时间（秒）
        """
        if hasattr(self, '_created'):
            return
        self._created = True

        self._page = self
        self._run_browser()
        super().__init__(self.address, tab_id)
        self._type = 'ChromiumPage'
        self._lock = Lock()
        self.set.timeouts(base=timeout)
        self._page_init()

    def _run_browser(self):
        """连接浏览器"""
        self._browser = Browser(self._chromium_options.address, self._browser_id, self)
        if (self._is_exist and self._chromium_options._headless is False and
                'headless' in self._browser.run_cdp('Browser.getVersion')['userAgent'].lower()):
            self._browser.quit(3)
            connect_browser(self._chromium_options)
            ws = get(f'http://{self._chromium_options.address}/json/version', headers={'Connection': 'close'})
            ws = ws.json()['webSocketDebuggerUrl'].split('/')[-1]
            self._browser = Browser(self._chromium_options.address, ws, self)

    def _d_set_runtime_settings(self):
        """设置运行时用到的属性"""
        self._timeouts = Timeout(self, page_load=self._chromium_options.timeouts['page_load'],
                                 script=self._chromium_options.timeouts['script'],
                                 base=self._chromium_options.timeouts['base'])
        if self._chromium_options.timeouts['base'] is not None:
            self._timeout = self._chromium_options.timeouts['base']
        self._load_mode = self._chromium_options.load_mode
        self._download_path = None if self._chromium_options.download_path is None \
            else str(Path(self._chromium_options.download_path).absolute())
        self.retry_times = self._chromium_options.retry_times
        self.retry_interval = self._chromium_options.retry_interval

    def _page_init(self):
        """浏览器相关设置"""
        self._browser.connect_to_page()

    # ----------挂件----------

    @property
    def set(self):
        """返回用于设置的对象"""
        if self._set is None:
            self._set = ChromiumPageSetter(self)
        return self._set

    @property
    def wait(self):
        """返回用于等待的对象"""
        if self._wait is None:
            self._wait = PageWaiter(self)
        return self._wait

    # ----------挂件----------

    @property
    def browser(self):
        """返回用于控制浏览器cdp的driver"""
        return self._browser

    @property
    def tabs_count(self):
        """返回标签页数量"""
        return self.browser.tabs_count

    @property
    def tabs(self):
        """返回所有标签页id组成的列表"""
        return self.browser.tabs

    @property
    def latest_tab(self):
        """返回最新的标签页id，最新标签页指最后创建或最后被激活的"""
        return self.tabs[0]

    @property
    def process_id(self):
        """返回浏览器进程id"""
        return self.browser.process_id

    def save(self, path=None, name=None, as_pdf=False, **kwargs):
        """把当前页面保存为文件，如果path和name参数都为None，只返回文本
        :param path: 保存路径，为None且name不为None时保存在当前路径
        :param name: 文件名，为None且path不为None时用title属性值
        :param as_pdf: 为Ture保存为pdf，否则为mhtml且忽略kwargs参数
        :param kwargs: pdf生成参数
        :return: as_pdf为True时返回bytes，否则返回文件文本
        """
        return get_pdf(self, path, name, kwargs) if as_pdf else get_mhtml(self, path, name)

    def get_tab(self, id_or_num=None):
        """获取一个标签页对象
        :param id_or_num: 要获取的标签页id或序号，为None时获取当前tab，序号从1开始，可传入负数获取倒数第几个，不是视觉排列顺序，而是激活顺序
        :return: 标签页对象
        """
        with self._lock:
            if isinstance(id_or_num, str):
                return ChromiumTab(self, id_or_num)
            elif isinstance(id_or_num, int):
                return ChromiumTab(self, self.tabs[id_or_num - 1 if id_or_num > 0 else id_or_num])
            elif id_or_num is None:
                return ChromiumTab(self, self.tab_id)
            elif isinstance(id_or_num, ChromiumTab):
                return id_or_num
            else:
                raise TypeError(f'id_or_num需传入tab id或序号，非{id_or_num}。')

    def find_tabs(self, title=None, url=None, tab_type=None, single=True):
        """查找符合条件的tab，返回它们的id组成的列表
        :param title: 要匹配title的文本
        :param url: 要匹配url的文本
        :param tab_type: tab类型，可用列表输入多个
        :param single: 是否返回首个结果的id，为False返回所有信息
        :return: tab id或tab列表
        """
        return self._browser.find_tabs(title, url, tab_type, single)

    def new_tab(self, url=None, new_window=False, background=False, new_context=False):
        """新建一个标签页
        :param url: 新标签页跳转到的网址
        :param new_window: 是否在新窗口打开标签页
        :param background: 是否不激活新标签页，如new_window为True则无效
        :param new_context: 是否创建新的上下文
        :return: 新标签页对象
        """
        tab = ChromiumTab(self, tab_id=self._new_tab(new_window, background, new_context))
        if url:
            tab.get(url)
        return tab

    def _new_tab(self, new_window=False, background=False, new_context=False):
        """新建一个标签页
        :param new_window: 是否在新窗口打开标签页
        :param background: 是否不激活新标签页，如new_window为True则无效
        :param new_context: 是否创建新的上下文
        :return: 新标签页对象
        """
        bid = None
        if new_context:
            bid = self.browser.run_cdp('Target.createBrowserContext')['browserContextId']

        kwargs = {'url': ''}
        if new_window:
            kwargs['newWindow'] = True
        if background:
            kwargs['background'] = True
        if bid:
            kwargs['browserContextId'] = bid

        return self.browser.run_cdp('Target.createTarget', **kwargs)['targetId']

    def close(self):
        """关闭Page管理的标签页"""
        self.close_tabs(self.tab_id)

    def close_tabs(self, tabs_or_ids=None, others=False):
        """关闭传入的标签页，默认关闭当前页。可传入多个
        :param tabs_or_ids: 要关闭的标签页对象或id，可传入列表或元组，为None时关闭当前页
        :param others: 是否关闭指定标签页之外的
        :return: None
        """
        all_tabs = set(self.tabs)
        if isinstance(tabs_or_ids, str):
            tabs = {tabs_or_ids}
        elif isinstance(tabs_or_ids, ChromiumTab):
            tabs = {tabs_or_ids.tab_id}
        elif tabs_or_ids is None:
            tabs = {self.tab_id}
        elif isinstance(tabs_or_ids, (list, tuple)):
            tabs = set(i.tab_id if isinstance(i, ChromiumTab) else i for i in tabs_or_ids)
        else:
            raise TypeError('tabs_or_ids参数只能传入标签页对象或id。')

        if others:
            tabs = all_tabs - tabs

        end_len = len(set(all_tabs) - set(tabs))
        if end_len <= 0:
            self.quit()
            return

        for tab in tabs:
            self.browser.close_tab(tab)
            sleep(.2)
        end_time = perf_counter() + 3
        while self.tabs_count != end_len and perf_counter() < end_time:
            sleep(.1)

    def quit(self, timeout=5, force=True):
        """关闭浏览器
        :param timeout: 等待浏览器关闭超时时间（秒）
        :param force: 关闭超时是否强制终止进程
        :return: None
        """
        self.browser.quit(timeout, force)

    def _on_disconnect(self):
        """浏览器退出时执行"""
        ChromiumPage._PAGES.pop(self._browser_id, None)

    def __repr__(self):
        return f'<ChromiumPage browser_id={self.browser.id} tab_id={self.tab_id}>'

    # ----------即将废弃-----------
    def close_other_tabs(self, tabs_or_ids=None):
        """关闭传入的标签页以外标签页，默认保留当前页。可传入多个
        :param tabs_or_ids: 要保留的标签页对象或id，可传入列表或元组，为None时保存当前页
        :return: None
        """
        self.close_tabs(tabs_or_ids, True)


def handle_options(addr_or_opts):
    """设置浏览器启动属性
    :param addr_or_opts: 'ip:port'、ChromiumOptions、Driver
    :return: 返回ChromiumOptions对象
    """
    if not addr_or_opts:
        _chromium_options = ChromiumOptions(addr_or_opts)
        if _chromium_options.is_auto_port:
            port, path = PortFinder(_chromium_options.tmp_path).get_port(_chromium_options.is_auto_port)
            _chromium_options.set_address(f'127.0.0.1:{port}')
            _chromium_options.set_user_data_path(path)
            _chromium_options.auto_port(scope=_chromium_options.is_auto_port)

    elif isinstance(addr_or_opts, ChromiumOptions):
        if addr_or_opts.is_auto_port:
            port, path = PortFinder(addr_or_opts.tmp_path).get_port(addr_or_opts.is_auto_port)
            addr_or_opts.set_address(f'127.0.0.1:{port}')
            addr_or_opts.set_user_data_path(path)
            addr_or_opts.auto_port(scope=addr_or_opts.is_auto_port)
        _chromium_options = addr_or_opts

    elif isinstance(addr_or_opts, str):
        _chromium_options = ChromiumOptions()
        _chromium_options.set_address(addr_or_opts)

    elif isinstance(addr_or_opts, int):
        _chromium_options = ChromiumOptions()
        _chromium_options.set_local_port(addr_or_opts)

    else:
        raise TypeError('只能接收ip:port格式或ChromiumOptions类型参数。')

    return _chromium_options


def run_browser(chromium_options):
    """连接浏览器"""
    is_exist = connect_browser(chromium_options)
    try:
        ws = get(f'http://{chromium_options.address}/json/version', headers={'Connection': 'close'})
        if not ws:
            raise BrowserConnectError('\n浏览器连接失败，如使用全局代理，须设置不代理127.0.0.1地址。')
        browser_id = ws.json()['webSocketDebuggerUrl'].split('/')[-1]
    except KeyError:
        raise BrowserConnectError('浏览器版本太旧，请升级。')
    except:
        raise BrowserConnectError('\n浏览器连接失败，如使用全局代理，须设置不代理127.0.0.1地址。')
    return is_exist, browser_id


def get_rename(original, rename):
    if '.' in rename:
        return rename
    else:
        suffix = original[original.rfind('.'):] if '.' in original else ''
        return f'{rename}{suffix}'
