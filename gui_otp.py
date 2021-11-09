""" GUI OTP """


# GUIotp
# Copyright (C) 2021  BitLogiK
# This file is part of GUIotp <https://github.com/bitlogik/GUIotp>.
#
# GUIotp is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GUIotp is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GUIotp.  If not, see <http://www.gnu.org/licenses/>.


import tkinter as tk
import re
import sys
from os import name, path, makedirs

try:
    from ctypes import windll
except ImportError:
    pass
from otppy import OTP
import appdirs


VERSION = "0.1.0"


class OtpFile:
    """User config directory for OTP data"""

    def __init__(self, otp_path, dir_path):
        self.file_path = otp_path
        if not path.isdir(dir_path):
            self.create_path(dir_path)
        if not path.exists(self.file_path):
            self.create_blank_file()

    @classmethod
    def from_appname(cls, app_name, author):
        """
        Get file/directory path of user config
        from the app name and its authors.
        """
        user_dir = appdirs.user_config_dir(app_name, author)
        dir_sep = "/"
        if name == "nt":
            dir_sep = "\\"
        dir_path = user_dir + dir_sep + "data" + dir_sep
        file_path = dir_path + "user.dat"
        return cls(file_path, dir_path)

    @staticmethod
    def create_path(path_create):
        """Create user config directory for the app."""
        makedirs(path_create)

    def create_blank_file(self):
        """Create a blank file in the user config directory."""
        with open(self.file_path, "w", encoding="utf8") as fwrite:
            print("", file=fwrite, end="")

    def read_filelines(self):
        """Read the service file.
        Return lines of the file as a list of string.
        """
        lines = []
        with open(self.file_path, "r", encoding="utf8") as data_file:
            for data_line in data_file:
                lines.append(data_line)
        return lines

    def save_newservice(self, srv_name, srv_secret):
        """Write a new service line in the file."""
        with open(self.file_path, "a", encoding="utf8") as fswrite:
            print(srv_name + "," + srv_secret, file=fswrite)


class GuiApp:
    """GUI part : mainwin and add_win"""

    def __init__(self):

        if "windll" in globals():
            windll.shcore.SetProcessDpiAwareness(2)

        self.add_callback = None
        self.input_name = None
        self.input_secret = None
        self.add_win = None
        self.mainwin = tk.Tk()
        self.mainwin.title("GUI 2FA TOTP")
        file_icon = "res/guiotp-icon.png"
        if hasattr(sys, "_MEIPASS"):
            file_icon = path.join(sys._MEIPASS, file_icon)
        self.mainwin.iconphoto(True, tk.PhotoImage(file=file_icon))
        self.mainwin.minsize(300, 0)
        self.mainwin.resizable(width=False, height=False)
        self.srv_txt = tk.StringVar()
        self.wlabel = tk.Label(
            self.mainwin,
            textvariable=self.srv_txt,
            font=("Arial", 22),
            bg="grey20",
            borderwidth=30,
            padx=10,
        )
        add_btn = tk.Button(
            text="Add a new service", font=("Arial", 14), command=self.add_new_service
        )
        self.wlabel.pack()
        add_btn.pack()
        self.mainwin.wm_attributes("-topmost", 1)

    def start_gui(self):
        """Start the GUI frontend loop."""
        self.mainwin.mainloop()

    def paint_services(self, text, color):
        """Write the text in the app."""
        self.srv_txt.set(text)
        self.wlabel.config(fg=color)

    def add_service(self):
        """Read the new service input."""
        chosen_name = self.input_name.get()
        chosen_secret = self.input_secret.get()
        return chosen_name, chosen_secret

    def close_add(self):
        """Close the add service window."""
        self.add_win.destroy()
        self.input_name = None
        self.input_secret = None
        self.add_win = None

    def register_add_callback(self, callback):
        """Register a callback for the Add button."""
        self.add_callback = callback

    def add_new_service(self):
        """Open the add service window."""
        pad_horz = 24
        pad_vert = 16

        def add_click():
            serv_name, serv_secret = self.add_service()
            self.add_callback(serv_name, serv_secret)

        self.add_win = tk.Toplevel(self.mainwin)
        tk.Label(self.add_win, text="Service name", font=("Arial", 14)).grid(
            row=0, column=0, pady=pad_vert, padx=pad_horz
        )
        tk.Label(self.add_win, text="Shared secret", font=("Arial", 14)).grid(
            row=1, column=0, pady=pad_vert, padx=pad_horz
        )
        self.input_name = tk.Entry(self.add_win, font=("Arial", 14))
        self.input_name.grid(row=0, column=1, pady=pad_vert, padx=pad_horz)
        self.input_secret = tk.Entry(self.add_win, font=("Arial", 14))
        self.input_secret.grid(row=1, column=1, pady=pad_vert, padx=pad_horz)
        tk.Button(
            self.add_win,
            text="Cancel",
            font=("Arial", 12),
            command=self.close_add,
        ).grid(row=2, column=0, pady=pad_vert, padx=pad_horz)
        tk.Button(self.add_win, text="Add", font=("Arial", 14), command=add_click).grid(
            row=2, column=1, pady=pad_vert, padx=pad_horz
        )
        self.add_win.title("Add a new TOTP service")
        self.add_win.resizable(width=False, height=False)
        self.add_win.lift(aboveThis=self.mainwin)


class OtpApp:

    """GUI OTP central class"""

    name_regex = re.compile(r"^[^\,\r\n\t]+$")
    ssecret_regex = re.compile(r"^[A-Z2-7]{2,}={0,6}$")

    def __init__(self):
        self.srv_file = OtpFile.from_appname("otppy", "BitLogiK")
        self.load_services()
        self.gui = GuiApp()
        self.update_otp()
        self.gui.register_add_callback(self.add_service)
        self.gui.start_gui()

    def update_otp(self, refresh=True):
        """Update the TOTP periodically."""
        text = ""
        time_refresh = 99999
        for service in self.services:
            totp = service[1].TOTP()
            text += service[0] + "   " + totp[0] + "\n"
            trefr_prop = totp[1] + 1
            if trefr_prop < time_refresh:
                time_refresh = trefr_prop
        if time_refresh < 6:
            txt_color = "red"
        else:
            txt_color = "LightBlue"
            time_refresh -= 5
        self.gui.paint_services(text[:-1], txt_color)
        if refresh:
            self.gui.mainwin.after(time_refresh * 1000, self.update_otp)

    def validate_name(self, name_str):
        """Validate a service string name validity."""
        return self.name_regex.search(name_str) is not None

    def validate_secret(self, secret_str):
        """Validate a shared secret base32 validity."""
        if secret_str[-1] == "=" and len(secret_str) % 8 != 0:
            return False
        if len(secret_str.rstrip("=")) % 8 not in [0, 2, 4, 5, 7]:
            return False
        return self.ssecret_regex.search(secret_str) is not None

    def save_service(self, srv_name, shared_secret):
        """Save the new service in the file."""
        self.srv_file.save_newservice(srv_name, shared_secret)

    def add_service(self, srv_name, secret):
        """Called back when click Add. Validate data and add a new service."""
        if self.validate_name(srv_name) and self.validate_secret(secret):
            self.save_service(srv_name, secret)
            self.load_services()
            self.update_otp(False)
            self.gui.close_add()

    def load_services(self):
        """Load the services from the lines of the file."""
        servs = []
        data_infos = self.srv_file.read_filelines()
        for data_line in data_infos:
            data = data_line.rstrip("\n\r").split(",")
            if data and data[0]:
                service_otp = OTP.fromb32(data[1], "sha1", 6)
                servs.append([data[0], service_otp])
        self.services = servs


if __name__ == "__main__":
    app = OtpApp()
