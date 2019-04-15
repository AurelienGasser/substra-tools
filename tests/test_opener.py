import os
import sys

import pytest

from substratools import opener, exceptions


@pytest.fixture
def tmp_cwd(tmp_path):
    # create a temporary current working directory
    new_dir = tmp_path / "workspace"
    new_dir.mkdir()

    old_dir = os.getcwd()
    os.chdir(new_dir)

    # add cwd to syspath
    sys.path.insert(0, new_dir)

    # reload syspath
    import importlib
    import site
    importlib.reload(site)
    importlib.invalidate_caches()

    yield

    # cleanup
    sys.path.pop(0)
    os.chdir(old_dir)


def write_opener(code):
    with open('opener.py', 'w') as f:
        f.write(code)


def test_load_opener_not_found(tmp_cwd):
    with pytest.raises(exceptions.OpenerModuleNotFound):
        opener.load_from_module()


def test_load_invalid_opener(tmp_cwd):
    invalid_script = """
def get_X():
    raise NotImplementedError
def get_y():
    raise NotImplementedError
"""

    write_opener(invalid_script)

    with pytest.raises(exceptions.InvalidOpener):
        opener.load_from_module()


def test_load_opener_as_module(tmp_cwd):
    script = """
def get_X():
    return 'X'
def get_y():
    return 'y'
def fake_X():
    return 'fakeX'
def fake_y():
    return 'fakey'
def get_pred():
    return 'pred'
def save_pred():
    return 'pred'
"""

    write_opener(script)

    o = opener.load_from_module()
    assert o.get_X() == 'X'


def test_load_opener_as_classt(tmp_cwd):
    script = """
from substratools import Opener
class MyOpener(Opener):
    def get_X(self):
        return 'Xclass'
    def get_y(self):
        return 'yclass'
    def fake_X(self):
        return 'fakeX'
    def fake_y(self):
        return 'fakey'
    def get_pred(self):
        return 'pred'
    def save_pred(self):
        return 'pred'
"""

    write_opener(script)

    o = opener.load_from_module()
    assert o.get_X() == 'Xclass'
