# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

# Copyright 2017-2018 Michal Siedlaczek <michal.siedlaczek@gmail.com>

# This file is part of qutebrowser.
#
# qutebrowser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# qutebrowser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with qutebrowser.  If not, see <http://www.gnu.org/licenses/>.

import logging

from PyQt5.QtCore import QLibraryInfo
from qutebrowser.browser.webengine import spell
from qutebrowser.utils import usertypes


def test_version(message_mock, caplog):
    assert spell.version('en-US-8-0.bdic') == (8, 0)
    assert spell.version('pl-PL-3-0.bdic') == (3, 0)
    with caplog.at_level(logging.WARNING):
        assert spell.version('malformed_filename') is None
    msg = message_mock.getmsg(usertypes.MessageLevel.warning)
    expected = ("Found a dictionary with a malformed name: malformed_filename")
    assert msg.text == expected


def test_dictionary_dir(monkeypatch):
    monkeypatch.setattr(QLibraryInfo, 'location', lambda _: 'datapath')
    assert spell.dictionary_dir() == 'datapath/qtwebengine_dictionaries'


def test_local_filename_dictionary_does_not_exist(tmpdir, monkeypatch):
    monkeypatch.setattr(
        spell, 'dictionary_dir', lambda: '/some-non-existing-dir')
    assert not spell.local_filename('en-US')


def test_local_filename_dictionary_not_installed(tmpdir, monkeypatch):
    monkeypatch.setattr(spell, 'dictionary_dir', lambda: str(tmpdir))
    assert not spell.local_filename('en-US')


def test_local_filename_dictionary_not_installed_with_malformed(tmpdir, monkeypatch, caplog):
    monkeypatch.setattr(spell, 'dictionary_dir', lambda: str(tmpdir))
    (tmpdir / 'en-US.bdic').ensure()
    with caplog.at_level(logging.WARNING):
        assert not spell.local_filename('en-US')


def test_local_filename_dictionary_installed(tmpdir, monkeypatch):
    monkeypatch.setattr(spell, 'dictionary_dir', lambda: str(tmpdir))
    for lang_file in ['en-US-11-0.bdic', 'en-US-7-1.bdic', 'pl-PL-3-0.bdic']:
        (tmpdir / lang_file).ensure()
    assert spell.local_filename('en-US') == 'en-US-11-0'
    assert spell.local_filename('pl-PL') == 'pl-PL-3-0'


def test_local_filename_dictionary_installed_with_malformed(tmpdir, monkeypatch, caplog):
    monkeypatch.setattr(spell, 'dictionary_dir', lambda: str(tmpdir))
    for lang_file in ['en-US-11-0.bdic', 'en-US-7-1.bdic', 'en-US.bdic']:
        (tmpdir / lang_file).ensure()
    with caplog.at_level(logging.WARNING):
        assert spell.local_filename('en-US') == 'en-US-11-0'
