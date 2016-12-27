#toledo

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
    
    4.2 Special switches
    
        4.2.1 --raw
        
            --raw Allows you to send protocol level commands to the sign. Basically, you type your string in as it would be sent, without the sid flag, the
            resultant checksum and the end (<E>) tag. An example of this would be 'toledo.py --raw="<L1><PA><FE><MQ><WC><FE><AC>hello world" '
        
        4.2.2 --debug
        
            Basically, this turns on verbose output for the command. However, for this to be truly effective it must be the FIRST switch used.
        
        4.2.3 --message
        
            This is where your message goes. It's important to note two things however. You can encapsulate protocol commands in the message string
            and you must call this immediately before --output (or last, if --output is omitted)
        
        4.2.4 --output
        
            This tells toledo.py to send the command to your designated serial port. It must be the *LAST* switch used.

5. Version History

    0.0.4.3   - Added --color flag for Amplus signs supporting these commands, fixed checksum bug for short strings, cleaned up code
                released 14-4-2008
                
    0.0.4.2   - Supports "full" protocol, either through switch "shortcuts" like --inverse or through sending raw protocol commands with --raw . See --help
                released 12-4-2008
                
    0.0.4.1.1 - Minor fix, fixed typo spotted by RobM
                released 12-4-2008
                
    0.0.4.1   - Re-written from the ground up in python. Notable feature is actually receiving ACK/NACK from sign board
                released 11-4-2008
                
    0.0.3.0   - Initial public release, written in perl, used file handlers for serial comms, frequent BSOD in Win32, buffers issues in *nix, completely deprecated
                released 01-4-2008 (no longer available)
    
    
6. Bugs

    None known of so far....
    
7. Legal

    This software is licensed under a Creative Commons
    Attribution-Noncommercial-Share Alike 3.0 United States License
    Please see http://creativecommons.org/licenses/by-nc-sa/3.0/us/

    If you find this software useful, have problems or suggestions,
    Please email me at hanzo@freezerpants.com
    If you wish to host this software elsewhere, please provide a link to
    http://freezerpants.com and credit to Christian Sullivan
    
8. Contact

    You may contact the author, Christian Sullivan, via email at Hanzo[.at]freezerpants[.dot.]com
    or through his website, http://freezerpants.com/toledo/
