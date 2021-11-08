# -*- coding: utf-8 -*-
# Copyright (c) 2005-2010 ActiveState Software Inc.
# Copyright (c) 2013 Eddy Petrișor

"""Utilities for determining application-specific dirs.

See <https://github.com/ActiveState/appdirs> for details and usage.
"""
# Dev Notes:
# - MSDN on where to store app data files:
#   http://support.microsoft.com/default.aspx?scid=kb;en-us;310294#XSLTH3194121123120121120120
# - Mac OS X: http://developer.apple.com/documentation/MacOSX/Conceptual/BPFileSystem/index.html
# - XDG spec for Un*x: https://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html


import sys
import os

unicode = str

if sys.platform.startswith("java"):
    import platform

    os_name = platform.java_ver()[3][0]
    if os_name.startswith("Windows"):  # "Windows XP", "Windows 7", etc.
        system = "win32"
    elif os_name.startswith("Mac"):  # "Mac OS X", etc.
        system = "darwin"
    else:  # "Linux", "SunOS", "FreeBSD", etc.
        # Setting this to "linux2" is not ideal, but only Windows or Mac
        # are actually checked for and the rest of the module expects
        # *sys.platform* style strings.
        system = "linux2"
else:
    system = sys.platform


def user_data_dir(appname=None, appauthor=None, version=None, roaming=False):
    r"""Return full path to the user-specific data dir for this application.

        "appname" is the name of application.
            If None, just the system directory is returned.
        "appauthor" (only used on Windows) is the name of the
            appauthor or distributing body for this application. Typically
            it is the owning company name. This falls back to appname. You may
            pass False to disable it.
        "version" is an optional version path element to append to the
            path. You might want to use this if you want multiple versions
            of your app to be able to run independently. If used, this
            would typically be "<major>.<minor>".
            Only applied when appname is present.
        "roaming" (boolean, default False) can be set True to use the Windows
            roaming appdata directory. That means that for users on a Windows
            network setup for roaming profiles, this user data will be
            sync'd on login. See
            <http://technet.microsoft.com/en-us/library/cc766489(WS.10).aspx>
            for a discussion of issues.

    Typical user data directories are:
        Mac OS X:               ~/Library/Application Support/<AppName>
        Unix:                   ~/.local/share/<AppName>    # or in $XDG_DATA_HOME, if defined
        Win XP (not roaming):
            C:\Documents and Settings\<username>\Application Data\<AppAuthor>\<AppName>
        Win XP (roaming):
            C:\Documents and Settings\<username>\Local Settings\Application Data\<AppAuthor>\
                <AppName>
        Win 7  (not roaming):   C:\Users\<username>\AppData\Local\<AppAuthor>\<AppName>
        Win 7  (roaming):       C:\Users\<username>\AppData\Roaming\<AppAuthor>\<AppName>

    For Unix, we follow the XDG spec and support $XDG_DATA_HOME.
    That means, by default "~/.local/share/<AppName>".
    """
    if system == "win32":
        if appauthor is None:
            appauthor = appname
        const = roaming and "CSIDL_APPDATA" or "CSIDL_LOCAL_APPDATA"
        path = os.path.normpath(_get_win_folder(const))
        if appname:
            if appauthor is not False:
                path = os.path.join(path, appauthor, appname)
            else:
                path = os.path.join(path, appname)
    elif system == "darwin":
        path = os.path.expanduser("~/Library/Application Support/")
        if appname:
            path = os.path.join(path, appname)
    else:
        path = os.getenv("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
        if appname:
            path = os.path.join(path, appname)
    if appname and version:
        path = os.path.join(path, version)
    return path


def user_config_dir(appname=None, appauthor=None, version=None, roaming=False):
    r"""Return full path to the user-specific config dir for this application.

        "appname" is the name of application.
            If None, just the system directory is returned.
        "appauthor" (only used on Windows) is the name of the
            appauthor or distributing body for this application. Typically
            it is the owning company name. This falls back to appname. You may
            pass False to disable it.
        "version" is an optional version path element to append to the
            path. You might want to use this if you want multiple versions
            of your app to be able to run independently. If used, this
            would typically be "<major>.<minor>".
            Only applied when appname is present.
        "roaming" (boolean, default False) can be set True to use the Windows
            roaming appdata directory. That means that for users on a Windows
            network setup for roaming profiles, this user data will be
            sync'd on login. See
            <http://technet.microsoft.com/en-us/library/cc766489(WS.10).aspx>
            for a discussion of issues.

    Typical user config directories are:
        Mac OS X:               ~/Library/Preferences/<AppName>
        Unix:                   ~/.config/<AppName>     # or in $XDG_CONFIG_HOME, if defined
        Win *:                  same as user_data_dir

    For Unix, we follow the XDG spec and support $XDG_CONFIG_HOME.
    That means, by default "~/.config/<AppName>".
    """
    if system == "win32":
        path = user_data_dir(appname, appauthor, None, roaming)
    elif system == "darwin":
        path = os.path.expanduser("~/Library/Preferences/")
        if appname:
            path = os.path.join(path, appname)
    else:
        path = os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        if appname:
            path = os.path.join(path, appname)
    if appname and version:
        path = os.path.join(path, version)
    return path


class AppDirs(object):
    """Convenience wrapper for getting application dirs."""

    def __init__(
        self, appname=None, appauthor=None, version=None, roaming=False, multipath=False
    ):
        self.appname = appname
        self.appauthor = appauthor
        self.version = version
        self.roaming = roaming
        self.multipath = multipath

    @property
    def user_data_dir(self):
        return user_data_dir(
            self.appname, self.appauthor, version=self.version, roaming=self.roaming
        )

    @property
    def user_config_dir(self):
        return user_config_dir(
            self.appname, self.appauthor, version=self.version, roaming=self.roaming
        )


# ---- internal support stuff


def _get_win_folder_from_registry(csidl_name):
    """This is a fallback technique at best. I'm not sure if using the
    registry for this guarantees us the correct answer for all CSIDL_*
    names.
    """
    import winreg as _winreg

    shell_folder_name = {
        "CSIDL_APPDATA": "AppData",
        "CSIDL_COMMON_APPDATA": "Common AppData",
        "CSIDL_LOCAL_APPDATA": "Local AppData",
    }[csidl_name]

    key = _winreg.OpenKey(
        _winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
    )
    dire, _ = _winreg.QueryValueEx(key, shell_folder_name)
    return dire


def _get_win_folder_with_ctypes(csidl_name):
    import ctypes

    csidl_const = {
        "CSIDL_APPDATA": 26,
        "CSIDL_COMMON_APPDATA": 35,
        "CSIDL_LOCAL_APPDATA": 28,
    }[csidl_name]

    buf = ctypes.create_unicode_buffer(1024)
    ctypes.windll.shell32.SHGetFolderPathW(None, csidl_const, None, 0, buf)

    # Downgrade to short path name if have highbit chars. See
    # <http://bugs.activestate.com/show_bug.cgi?id=85099>.
    has_high_char = False
    for c in buf:
        if ord(c) > 255:
            has_high_char = True
            break
    if has_high_char:
        buf2 = ctypes.create_unicode_buffer(1024)
        if ctypes.windll.kernel32.GetShortPathNameW(buf.value, buf2, 1024):
            buf = buf2

    return buf.value


def _get_win_folder_with_jna(csidl_name):
    import array
    from com.sun import jna
    from com.sun.jna.platform import win32

    buf_size = win32.WinDef.MAX_PATH * 2
    buf = array.zeros("c", buf_size)
    shell = win32.Shell32.INSTANCE
    shell.SHGetFolderPath(
        None,
        getattr(win32.ShlObj, csidl_name),
        None,
        win32.ShlObj.SHGFP_TYPE_CURRENT,
        buf,
    )
    dir = jna.Native.toString(buf.tostring()).rstrip("\0")

    # Downgrade to short path name if have highbit chars. See
    # <http://bugs.activestate.com/show_bug.cgi?id=85099>.
    has_high_char = False
    for c in dir:
        if ord(c) > 255:
            has_high_char = True
            break
    if has_high_char:
        buf = array.zeros("c", buf_size)
        kernel = win32.Kernel32.INSTANCE
        if kernel.GetShortPathName(dir, buf, buf_size):
            dir = jna.Native.toString(buf.tostring()).rstrip("\0")

    return dir


if system == "win32":
    try:
        from ctypes import windll

        windll
    except ImportError:
        try:
            import com.sun.jna

            com.sun.jna
        except ImportError:
            _get_win_folder = _get_win_folder_from_registry
        else:
            _get_win_folder = _get_win_folder_with_jna
    else:
        _get_win_folder = _get_win_folder_with_ctypes
