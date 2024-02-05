# -*- coding:utf-8 -*-
"""
@Author   : g1879
@Contact  : g1879@qq.com
@Copyright: (c) 2024 by g1879, Inc. All Rights Reserved.
@License  : BSD 3-Clause.
"""
from pathlib import Path
from typing import Union, Tuple, List, Any, Literal, Optional

from .._base.base import DrissionElement, BaseElement
from .._elements.session_element import SessionElement
from .._pages.chromium_base import ChromiumBase
from .._pages.chromium_frame import ChromiumFrame
from .._pages.chromium_page import ChromiumPage
from .._pages.chromium_tab import ChromiumTab
from .._pages.web_page import WebPage
from .._units.clicker import Clicker
from .._units.rect import ElementRect
from .._units.scroller import ElementScroller
from .._units.selector import SelectElement
from .._units.setter import ChromiumElementSetter
from .._units.states import ShadowRootStates, ElementStates
from .._units.waiter import ElementWaiter

PIC_TYPE = Literal['jpg', 'jpeg', 'png', 'webp', True]


class ChromiumElement(DrissionElement):

    def __init__(self, page: ChromiumBase, node_id: int = None, obj_id: str = None, backend_id: int = None):
        self._tag: str = ...
        self.page: Union[ChromiumPage, WebPage] = ...
        self._node_id: int = ...
        self._obj_id: str = ...
        self._backend_id: int = ...
        self._doc_id: str = ...
        self._scroll: ElementScroller = ...
        self._clicker: Clicker = ...
        self._select: SelectElement = ...
        self._wait: ElementWaiter = ...
        self._rect: ElementRect = ...
        self._set: ChromiumElementSetter = ...
        self._states: ElementStates = ...
        self._pseudo: Pseudo = ...

    def __repr__(self) -> str: ...

    def __call__(self,
                 locator: Union[Tuple[str, str], str],
                 index: int = 1,
                 timeout: float = None) -> ChromiumElement: ...

    def __eq__(self, other: ChromiumElement) -> bool: ...

    @property
    def tag(self) -> str: ...

    @property
    def html(self) -> str: ...

    @property
    def inner_html(self) -> str: ...

    @property
    def attrs(self) -> dict: ...

    @property
    def text(self) -> str: ...

    @property
    def raw_text(self) -> str: ...

    # -----------------d模式独有属性-------------------
    @property
    def set(self) -> ChromiumElementSetter: ...

    @property
    def states(self) -> ElementStates: ...

    @property
    def rect(self) -> ElementRect: ...

    @property
    def pseudo(self) -> Pseudo: ...

    @property
    def shadow_root(self) -> Union[None, ShadowRoot]: ...

    @property
    def sr(self) -> Union[None, ShadowRoot]: ...

    @property
    def scroll(self) -> ElementScroller: ...

    @property
    def click(self) -> Clicker: ...

    def parent(self,
               level_or_loc: Union[tuple, str, int] = 1,
               index: int = 1) -> ChromiumElement: ...

    def child(self,
              locator: Union[Tuple[str, str], str, int] = '',
              index: int = 1,
              timeout: float = None,
              ele_only: bool = True) -> Union[ChromiumElement, str]: ...

    def prev(self,
             locator: Union[Tuple[str, str], str, int] = '',
             index: int = 1,
             timeout: float = None,
             ele_only: bool = True) -> Union[ChromiumElement, str]: ...

    def next(self,
             locator: Union[Tuple[str, str], str, int] = '',
             index: int = 1,
             timeout: float = None,
             ele_only: bool = True) -> Union[ChromiumElement, str]: ...

    def before(self,
               locator: Union[Tuple[str, str], str, int] = '',
               index: int = 1,
               timeout: float = None,
               ele_only: bool = True) -> Union[ChromiumElement, str]: ...

    def after(self,
              locator: Union[Tuple[str, str], str, int] = '',
              index: int = 1,
              timeout: float = None,
              ele_only: bool = True) -> Union[ChromiumElement, str]: ...

    def children(self,
                 locator: Union[Tuple[str, str], str] = '',
                 timeout: float = None,
                 ele_only: bool = True) -> List[Union[ChromiumElement, str]]: ...

    def prevs(self,
              locator: Union[Tuple[str, str], str] = '',
              timeout: float = None,
              ele_only: bool = True) -> List[Union[ChromiumElement, str]]: ...

    def nexts(self,
              locator: Union[Tuple[str, str], str] = '',
              timeout: float = None,
              ele_only: bool = True) -> List[Union[ChromiumElement, str]]: ...

    def befores(self,
                locator: Union[Tuple[str, str], str] = '',
                timeout: float = None,
                ele_only: bool = True) -> List[Union[ChromiumElement, str]]: ...

    def afters(self,
               locator: Union[Tuple[str, str], str] = '',
               timeout: float = None,
               ele_only: bool = True) -> List[Union[ChromiumElement, str]]: ...

    @property
    def wait(self) -> ElementWaiter: ...

    @property
    def select(self) -> SelectElement: ...

    @property
    def value(self) -> None: ...

    def check(self, uncheck: bool = False, by_js: bool = False) -> None: ...

    def attr(self, name: str) -> Union[str, None]: ...

    def remove_attr(self, name: str) -> None: ...

    def property(self, name: str) -> Union[str, int, None]: ...

    def run_js(self, script: str, *args, as_expr: bool = False, timeout: float = None) -> Any: ...

    def run_async_js(self, script: str, *args, as_expr: bool = False) -> None: ...

    def ele(self,
            locator: Union[Tuple[str, str], str],
            index: int = 1,
            timeout: float = None) -> ChromiumElement: ...

    def eles(self,
             locator: Union[Tuple[str, str], str],
             timeout: float = None) -> List[ChromiumElement]: ...

    def s_ele(self,
              locator: Union[Tuple[str, str], str] = None,
              index: int = 1) -> SessionElement: ...

    def s_eles(self, locator: Union[Tuple[str, str], str] = None) -> List[SessionElement]: ...

    def _find_elements(self,
                       locator: Union[Tuple[str, str], str],
                       timeout: float = None,
                       index: Optional[int] = 1,
                       relative: bool = False,
                       raise_err: bool = False) -> Union[ChromiumElement, ChromiumFrame,
    List[Union[ChromiumElement, ChromiumFrame]]]: ...

    def style(self, style: str, pseudo_ele: str = '') -> str: ...

    def src(self, timeout: float = None, base64_to_bytes: bool = True) -> Union[bytes, str, None]: ...

    def save(self, path: [str, bool] = None, name: str = None, timeout: float = None) -> str: ...

    def get_screenshot(self,
                       path: [str, Path] = None,
                       name: str = None,
                       as_bytes: PIC_TYPE = None,
                       as_base64: PIC_TYPE = None,
                       scroll_to_center: bool = True) -> Union[str, bytes]: ...

    def input(self, vals: Any, clear: bool = True, by_js: bool = False) -> None: ...

    def _set_file_input(self, files: Union[str, list, tuple]) -> None: ...

    def clear(self, by_js: bool = False) -> None: ...

    def _input_focus(self) -> None: ...

    def focus(self) -> None: ...

    def hover(self, offset_x: int = None, offset_y: int = None) -> None: ...

    def drag(self, offset_x: int = 0, offset_y: int = 0, duration: float = 0.5) -> None: ...

    def drag_to(self, ele_or_loc: Union[tuple, ChromiumElement], duration: float = 0.5) -> None: ...

    def _get_obj_id(self, node_id: int = None, backend_id: int = None) -> str: ...

    def _get_node_id(self, obj_id: str = None, backend_id: int = None) -> int: ...

    def _get_backend_id(self, node_id: int) -> int: ...

    def _get_ele_path(self, mode: str) -> str: ...


class ShadowRoot(BaseElement):

    def __init__(self, parent_ele: ChromiumElement, obj_id: str = None, backend_id: int = None):
        self._obj_id: str = ...
        self._node_id: int = ...
        self._backend_id: int = ...
        self.page: ChromiumPage = ...
        self.parent_ele: ChromiumElement = ...
        self._states: ShadowRootStates = ...

    def __repr__(self) -> str: ...

    def __call__(self,
                 locator: Union[Tuple[str, str], str],
                 timeout: float = None) -> ChromiumElement: ...

    def __eq__(self, other: ShadowRoot) -> bool: ...

    @property
    def states(self) -> ShadowRootStates: ...

    @property
    def tag(self) -> str: ...

    @property
    def html(self) -> str: ...

    @property
    def inner_html(self) -> str: ...

    def run_js(self, script: str, *args, as_expr: bool = False, timeout: float = None) -> Any: ...

    def run_async_js(self, script: str, *args, as_expr: bool = False, timeout: float = None) -> None: ...

    def parent(self, level_or_loc: Union[str, int] = 1, index: int = 1) -> ChromiumElement: ...

    def child(self,
              locator: Union[Tuple[str, str], str] = '',
              index: int = 1) -> ChromiumElement: ...

    def next(self,
             locator: Union[Tuple[str, str], str] = '',
             index: int = 1) -> ChromiumElement: ...

    def before(self,
               locator: Union[Tuple[str, str], str] = '',
               index: int = 1) -> ChromiumElement: ...

    def after(self,
              locator: Union[Tuple[str, str], str] = '',
              index: int = 1) -> ChromiumElement: ...

    def children(self, locator: Union[Tuple[str, str], str] = '') -> List[ChromiumElement]: ...

    def nexts(self, locator: Union[Tuple[str, str], str] = '') -> List[ChromiumElement]: ...

    def befores(self, locator: Union[Tuple[str, str], str] = '') -> List[ChromiumElement]: ...

    def afters(self, locator: Union[Tuple[str, str], str] = '') -> List[ChromiumElement]: ...

    def ele(self,
            locator: Union[Tuple[str, str], str],
            index: int = 1,
            timeout: float = None) -> ChromiumElement: ...

    def eles(self,
             locator: Union[Tuple[str, str], str],
             timeout: float = None) -> List[ChromiumElement]: ...

    def s_ele(self,
              locator: Union[Tuple[str, str], str] = None,
              index: int = 1) -> SessionElement: ...

    def s_eles(self, locator: Union[Tuple[str, str], str]) -> List[SessionElement]: ...

    def _find_elements(self,
                       locator: Union[Tuple[str, str], str],
                       timeout: float = None,
                       index: Optional[int] = 1,
                       relative: bool = False,
                       raise_err: bool = None) -> Union[ChromiumElement, ChromiumFrame, str,
    List[Union[ChromiumElement, ChromiumFrame, str]]]: ...

    def _get_node_id(self, obj_id: str) -> int: ...

    def _get_obj_id(self, back_id: int) -> str: ...

    def _get_backend_id(self, node_id: int) -> int: ...


def find_in_chromium_ele(ele: ChromiumElement,
                         loc: Union[str, Tuple[str, str]],
                         index: Optional[int] = 1,
                         timeout: float = None,
                         relative: bool = True) -> Union[ChromiumElement, List[ChromiumElement]]: ...


def find_by_xpath(ele: ChromiumElement,
                  xpath: str,
                  index: Optional[int],
                  timeout: float,
                  relative: bool = True) -> Union[ChromiumElement, List[ChromiumElement]]: ...


def find_by_css(ele: ChromiumElement,
                selector: str,
                index: Optional[int],
                timeout: float) -> Union[ChromiumElement, List[ChromiumElement],]: ...


def make_chromium_eles(page: Union[ChromiumBase, ChromiumPage, WebPage, ChromiumTab, ChromiumFrame],
                       _ids: Union[tuple, list, str, int],
                       index: Optional[int] = 1,
                       is_obj_id: bool = True
                       ) -> Union[ChromiumElement, ChromiumFrame, List[Union[ChromiumElement, ChromiumFrame]]]: ...


def make_js_for_find_ele_by_xpath(xpath: str, type_txt: str, node_txt: str) -> str: ...


def run_js(page_or_ele: Union[ChromiumBase, ChromiumElement, ShadowRoot],
           script: str,
           as_expr: bool,
           timeout: float,
           args: tuple = ...) -> Any: ...


def parse_js_result(page: ChromiumBase,
                    ele: ChromiumElement,
                    result: dict,
                    end_time: float): ...


def convert_argument(arg: Any) -> dict: ...


class Pseudo(object):
    def __init__(self, ele: ChromiumElement):
        self._ele: ChromiumElement = ...

    @property
    def before(self) -> str: ...

    @property
    def after(self) -> str: ...
