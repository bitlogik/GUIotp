
# GUIotp


2FA OTP app : generator GUI client for desktop.

GUIotp is a simple and free desktop application for 2-Factors Authentication codes. It generates Time-based One-Time Passwords needed to login. This 2-steps verification provides a stronger security for your web accounts.

GUIotp works with many of online services you use, including Google, Facebook, GitHub, and many more. It can also work with your private company security if they implement the standard TOTP protocol.

GUIotp is free and open source software, licensed under the GPL 3.0 license.


## Download

For Windows :

https://github.com/bitlogik/GUIotp/releases/latest

To increase the security, all binaries released are signed with the BitLogiK code signing certificate, bringing even greater confidence in the integrity of the application.


Soon

- MacOS and Linux binaries


## Development

Requires :

- [Python >= 3.4](https://www.python.org/downloads/)
- [OTPpy library](https://github.com/bitlogik/OTPpy)

For the OTPpy library, with pip :

`python3 -m pip install otppy`


To build the binaries, you only need Python 3.10. Start the Build-Windows.bat script in the *package* directory. Output result in the *dist* directory.