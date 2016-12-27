# toledo
1. What is toledo?
 1.1 Which signs does toledo support?
2. Installing
 2.1 Win32
 2.2 OS X (Mac)
 2.3 Other systems
3. Running for the first time
 3.1 Win32
 3.2 OS X (Mac)
 3.3 Other systems
4. Usage
 4.1 Switches
 4.2 Special Switches
  4.2.1 --raw
  4.2.2 --debug
  4.2.3 --message
  4.2.4 --output
5. Version History
6. Bugs
7. Legal
8. Contact

1. What is toledo?
    toledo is a simple Python (formerly Perl) script designed to interface with LED Sign boards produced by Amplus Industries, HK.
    At the very heart of it all, the intent is to provide a simple way to send really simple messages from the command line, which is
    quite handy for shell scripting. While really "complicated" message can be sent using toledo, it requires an understanding of the
    (admittedly simple) protocol used by the LED boards.
    
    While Amplus does distribute software for these boards, it suffers from two major problems:
        1. It's windows only. D'oh.
        2. It's a gui, thus it requires user interaction, which is terrible for automatically update server messages, RSS feeds, etc.
    
    1.1 Which signs does toledo support?
        To be perfectly honest, I believe it will support 99% of the amplus boards, but I can't be certain. The reason is, I only have two boards
        to test it against. Thus, the official answer will be:
        AM04142
        AM03128-H13
        (for e-Badge support, see http://freezerpants.com/toledo/)
        
2. Installing
    The basic pre-requisite here is pySerial and Python 2.2 (or greater)
    
    2.1 Win32
        + Download ActivePython : http://www.activestate.com/Products/activepython
        + Download / install pySerial (for Windows) : http://pyserial.sourceforge.net/
        + Place toledo.py somewhere handy, maybe your desktop (or for the adventurous, %SystemDir%\System32\ )
    2.2 OS X (Mac)
        + Verify that you have a current version of Python installed -
            Open Terminal.app and type "python --version"
        + Download / install pySerial : http://pyserial.sourceforge.net/
        + Place toledo.py somewhere handy, maybe your desktop (or ~/ )
    2.3 Other systems
        + Open a console/terminal, verify you have a recent version of Python installed -
            "python --version"
        + Download / install pySerial : http://pyserial.sourceforge.net/
        + Place toledo.py somewhere handy, perhaps ~/
        
3. Running for the first time
    Really all you need to do is edit toledo.py to properly reflect your serial port, and this isn't even strictly necessary

    3.1 Win32
        + Open a command prompt (Start->Run->cmd->OK)
        + From the command prompt, navigate to the super handy place you saved toledo.py
        + use "edit" and open toledo.py
            !!! DO NOT USE NOTEPAD, IT WILL DO VERY BAD THINGS TO TOLEDO.PY !!!
        + Edit the line _port = "COM7" so that COM7 is your COM port, save
        + type toledo.py --version
        + If everything worked, you should see a response, you are now ready to go.
    3.2 OS X (Mac)
        + Edit toledo.py, change the line _port = "COM7" to your com port (probably /dev/tty.usbserial ), save
        + Open Terminal.app
        + From the command prompt, navigate to the super handy place you saved toledo.py
        + type ./toledo.py --version
        + If everything worked, you should see a response, you are now ready to go.
    3.3 Other systems
        + Edit toledo.py, change the line _port = "COM7" to your com port (probably /dev/tty.usbserial ), save
        + From the command prompt, navigate to the super handy place you saved toledo.py
        + type ./toledo.py --version
        + If everything worked, you should see a response, you are now ready to go.
        
4. Usage
    4.1 Switches
        There are two types of switches in toledo. Short switches and long switches. Short switches are denoted by -n , Where n is a single character.
        Long switches are denoted with --command , where command is the full name of the switch.
    
        When using a short switch that takes a parameter, do not use the = . Example, to set the font would be '-f "1"' (remove single quotes)
        When using a long switch that takes a parameter, do use the = . Example, to set the font would be '--font="1"' (remove single quotes)
    
        Short and Long switch can be mixed.
    