
# GUIotp

2FA TOTP GUI client for desktop


## Download

For Windows :

https://github.com/bitlogik/GUIotp/releases/latest

To increase the security, all binaries released are signed with the BitLogiK code signing certificate, bringing even greater confidence in the integrity of the application.

Soon

- Windows installer
- MacOS and Linux binaries


## Development

Requires :

- [Python >= 3.4](https://www.python.org/downloads/)
- [OTPpy library](https://github.com/bitlogik/OTPpy)

For the OTPpy library, with pip :

`python3 -m pip install otppy`


To build the binaries, you only need Python 3.9. Start the Build-Windows.bat script in the *package* directory. Output result in the *dist* directory.