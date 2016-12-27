#!/usr/bin/env python

# toledo.py
# author:   Christian Sullivan
#           hanzo@freezerpants.com
#           http://freezerpants.com/toledo/
#
# About:    Script to control Amplus LED sign boards
#
# Bugs:     None known so far, but it's nowhere near complete
#           currently only supported is AM04142(16x120)
#
# ToDo:
#           0.0.4.4 Finish implementation of full protocol (set time/date, etc), make help usage more interactive
#           0.0.4.5 Refactor code, peer review
#           0.0.5.0 Package as stand-alone, formal release
#
# License:
#           This software is licensed under a Creative Commons
#           Attribution-Noncommercial-Share Alike 3.0 United States License
#           Please see http://creativecommons.org/licenses/by-nc-sa/3.0/us/
#
#           If you find this software useful, have problems or suggestions,
#           Please email me at hanzo@freezerpants.com
#           If you wish to host this software elsewhere, please provide a link to
#           http://freezerpants.com and credit to Christian Sullivan
#
# Notes:    Requiring the -o flag is a little annoying, and really only useful for
##              the initial progressive code. Eventually we will just assume that the 
##              -o flag has been called.
#

import sys
import getopt
import serial

from operator import xor

    
def main(argv):
    # let's create the defaults
    # probably shouldn't be global
    global _port
    global _message
    global _line
    global _font
    global _iEffect
    global _eEffect
    global _speed
    global _bell
    global _color
    global _dFlag
    global _tFlag
    global _link
    global _page
    global _runpage
    global _sid
    global _raw
    global _version
    global _output
    global _debug
    
    _port       = "COM7"
    _message    = "snicklfritz982342"
    _line       = 1
    _font       = "1"
    _iEffect    = "5"
    _eEffect    = "5"
    _speed      = "3"
    _bell       = "0"
    _color      = "0"
    _dFlag      = "0"
    _tFlag      = "0"
    _link       = "0"
    _page       = "A"
    _runpage    = "A"
    _sid        = "00"
    _raw        = "0"
    _version    = "0.0.4.3"
    _output     = 0
    _debug      = 0
   
    try:
        opts, args = getopt.getopt(argv, "hvof:s:l:m:p:c:", ["help", "raw=", "version", "output", "font=", "sid=", "line=", "message=", "port=", "intro=", "exit=", "speed=", "bell=", "color=", "date", "time", "link=", "page=", "runpage=", "debug"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
        
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        if opt in ("--raw"):
            _raw = arg
            toraw()
            sys.exit()
        if opt in ("-v", "--version"):
            print "toledo version", _version
        if opt == '--debug':
            _debug = 1
            print "set debugging ON"
        if opt in ("-f", "--font"):
            _font = arg
        if opt in ("--intro"):
            _iEffect = arg
        if opt in ("--exit"):
            _eEffect = arg
        if opt in ("--speed"):
            _speed = arg
        if opt in ("--bell"):
            _bell = arg
        if opt in ("-c", "--color"):
            _color = arg
        if opt in ("--date"):
            _dFlag = "1"
            print "adding date"
        if opt in ("--time"):
            _tFlag = "1"
            print "adding time"
        if opt in ("--link"):
            _link = arg
            tolink()
            sys.exit()
        if opt in ("--page"):
            _page = arg
        if opt in ("--runpage"):
            _runpage = arg
            torun()
            sys.exit()
        if opt in ("-p", "--port"):
            _port = arg
        if opt in ("-s", "--sid"):
            _sid = arg
        if opt in ("-l", "--line"):
            _line = arg
        if opt in ("-m", "--message"):
            _message = arg
            toled()
        if opt in ("-o", "--output"):
            if (_message != "snicklfritz982342"):
                _output = 1
                toled()
            else:
                print "Message must be specified"
                sys.exit()
            
    source = "".join(args)

def fontFlag():
    global _font
    if (_font == "1"):
        _font = '<AC>'
    elif (_font == "2"):
        _font = '<AA>'
    elif (_font == "3"):
        _font = '<AB>'
    elif (_font == "4"):
        _font = '<AF>'
    elif (_font == "5"):
        _font = '<AD>'

def introFlag():
    global _iEffect
    if (_iEffect == "1"):
        _iEffect = "<FA>" # immediate
    if (_iEffect == "2"):
        _iEffect = "<FB>" # xopen
    if (_iEffect == "3"):
        _iEffect = "<FC>" # curtain up
    if (_iEffect == "4"):
        _iEffect = "<FD>" # curtain down
    if (_iEffect == "5"):
        _iEffect = "<FE>" # scroll left       
    if (_iEffect == "6"):
        _iEffect = "<FF>" # scroll right
    if (_iEffect == "7"):
        _iEffect = "<FG>" # vopen
    if (_iEffect == "8"):
        _iEffect = "<FH>" #vclose
    if (_iEffect == "9"):
        _iEffect = "<FI>" # scroll up
    if (_iEffect == "10"):
        _iEffect = "<FJ>" # scroll down
    if (_iEffect == "11"):
        _iEffect = "<FK>" # hold
    if (_iEffect == "12"):
        _iEffect = "<FL>" # snow
    if (_iEffect == "13"):
        _iEffect = "<FM>" # twinkle
    if (_iEffect == "14"):
        _iEffect = "<FN>" # block move
    if (_iEffect == "15"):
        _iEffect = "<FP>" # random
    if (_iEffect == "16"):
        _iEffect = "<FR>" # cursive welcome
    return introFlag

def exitFlag():
    global _eEffect
    if (_eEffect == "1"):
        _eEffect = '<FA>' # immediate
    elif (_eEffect == "2"):
        _eEffect = '<FB>' # xopen
    elif (_iEffect == "3"):
        _eEffect = '<FC>' # curtain up
    elif (_eEffect == "4"):
        _eEffect = '<FD>' # curtain down
    elif (_eEffect == "5"):
        _eEffect = '<FE>' # scroll left
    elif (_eEffect == "6"):
        _eEffect = '<FF>' # scroll right
    elif (_eEffect == "7"):
        _eEffect = '<FG>' # vopen
    elif (_eEffect == "8"):
        _eEffect = '<FH>' #vclose
    elif (_eEffect == "9"):
        _eEffect = '<FI>' # scroll up
    elif (_eEffect == "10"):
        _eEffect = '<FJ>' # scroll down
    elif (_eEffect == "11"):
        _eEffect = '<FK>' # hold

def speedFlag():
    global _speed
    if (_speed == "1"):
        _speed = '<Mq>' # slowest
    elif (_speed == "2"):
        _speed = '<Ma>'
    elif (_speed == "3"):
        _speed = '<MQ>'
    elif (_speed == "4"):
        _speed = '<MA>' # fastest
        

def bellFlag():
    global _bell
    if (_bell == "0"):
        _bell = ''     # no bell
    elif (_bell == "1"):
        _bell = '<BA>' # 0.5 sec
    elif (_bell == "2"):
        _bell = '<BB>' # 1.0 sec
    elif (_bell == "3"):
        _bell = '<BC>' # 1.5 sec
    elif (_bell == "4"):
        _bell = '<BD>' # 2.0 sec

def colorFlag():
    global _color
    if (_color == "0"):
        _color = ''
    elif (_color == "red"):
        _color = "<CA>"
    elif (_color == "orange"):
        _color = "<CH>"
    elif (_color == "green"):
        _color = "<CD>"
    elif (_color == "iorange"):
        _color = "<CN>"
    elif (_color == "igreen"):
        _color = "<CM>"
    elif (_color == "ired"):
        _color = "<CL>"
    elif (_color == "rog"):
        _color = "<CP>"
    elif (_color == "gor"):
        _color = "<CQ>"
    elif (_color == "ryg"):
        _color = "<CR>"
    elif (_color == "rainbow"):
        _color = "<CS>"
        
def dateFlag():
    global _dFlag
    if (_dFlag == "0"):
        _dFlag = ''
    elif (_dFlag == "1"):
        _dFlag = "<KD> "

def timeFlag():
    global _tFlag
    if (_tFlag == "0"):
        _tFlag = ''
    elif (_tFlag == "1"):
        _tFlag = "<KT> "
        
def toled():

    #run various functions to get tags
    fontFlag()
    introFlag()
    exitFlag()
    speedFlag()
    bellFlag()
    colorFlag()
    dateFlag()
    timeFlag()

    inMessage = "<L%s><P%s>%s%s<WC>%s%s%s%s%s%s%s" % (_line,_page,_iEffect,_speed,_eEffect,_bell,_color,_dFlag,_tFlag,_font,_message)
    outMessage = checksum(inMessage)
    finalMessage = "<ID%s>%s%s<E>" % (_sid,inMessage, outMessage)
    if (_debug == 1):
        print finalMessage
    
    if (_output ==1):
        serout(finalMessage)
        
def tolink():
    inMessage = "<TA>00010100009912302359%s" % (_link)
    outMessage = checksum(inMessage)
    finalMessage = "<ID%s>%s%s<E>" % (_sid,inMessage,outMessage)
    if (_debug == 1):
        print finalMessage
    serout(finalMessage)
    
def torun():
    # the runpage command is in the protocol, and the sign will return ACK on properly formatted
    ## command - HOWEVER - it will not actually change the running page.
    ## To do this, you must "Link" a single page.
    inMessage = "<RP%s>" % (_runpage)
    outMessage = checksum(inMessage)
    finalMessage = "<ID%s>%s%s<E>" % (_sid,inMessage,outMessage)
    if (_debug == 1):
        print finalMessage
    serout(finalMessage)

def toraw():
    # this is for sending straight up commands using protocol syntax to the LED sign
    ## basically all we do is create the checksum and send it off
    inMessage ="%s" % (_raw)
    outMessage = checksum(inMessage)
    finalMessage = "<ID%s>%s%s<E>" % (_sid,inMessage, outMessage)
    if (_debug == 1):
        print finalMessage
    serout(finalMessage)
    
def checksum(inMessage):
    result = 0    
    postlim = reduce(xor, [ord(c) for c in inMessage])
    result = "%02X" % postlim
    return result

def usage():
    print ""
    print "toledo version", _version
    print "-------------------------------------------------------------------------"
    print " Always use flags --message and --output last"
    print "-------------------------------------------------------------------------"
    print ""
    print "-h (--help)       This screen"
    print "-v (--version)    Show toledo version"
    print "-p (--port=)      Set the port for use (default /dev/tty.usbserial)"
    print "-d (--debug)      Enable debug mode (verbose, call this flag first)"
    print "-s (--sid=)       Which Sign ID is in use (default 00)"
    print "   --intro=       Set the intro effect (1-16)"
    print "   --exit=        Set the exit effect (1-11)"
    print "   --bell=        Add a noise to your sign (0-4)"
    print "   --speed=       Set the movement speed (1-4)"
    print "-f (--font=)      Set the font used (1-5)"
    print "-c (--color=)     Set color on supported boards (red, green, orange,"
    print "                    ired, igreen, iorange, rog, gor, rainbow"
    print "                                     "
    print "    --page=       Which page to progam (A-Z)"
    print "    --runpage=    Run which programmed page (A-Z) (non-functional)"
    print "    --link=       Run which pages in which order (A-Z)"
    print "-l (--line=)      Specify line to program, on supported boards (default 1)"
    print "    --raw=        Send protocol specific commands"
    print "                    Include the FULL string to send, everything between"
    print "                    <IDn> and XOR checksum"
    print "-m (--message=)   Set the desired message (call this flag before output)"
    print "-o (--output)     Output to sign (call this flag last)"
    print ""
    print "-------------------------------------------------------------------------"
    print 'example: ./toledo.py --link="ABACAB" --output'
    print 'example: ./toledo.py -p "/dev/tty.usbserial" -m "Holy Toledo" -o'
    print 'example: ./toledo.py --intro="1" --exit="5" --speed="2" --inverse --page="B" '
    print '          --line="2" --message="Holy Toledo" --output'
    print ""

def serout(finalMessage):
   # set up serial port
    ser = serial.Serial(_port, 9600, timeout=3)
    
    # clear out the buffer 
    ser.flushInput()
    ser.flushOutput()
    
    # the amplus boards need to be "initialized", if after a lengthy period without
    ## programming, they won't respond until they've gotten a valid string,
    ## so we send two "valid" strings
    ser.write (finalMessage)
    ser.write (finalMessage)
    
    # wait for a response, 3s is probably a bit long, and may be reduced in the future
    ## basically we're just watching for NACK or ACK, hence the four bytes
    ## not all amplus boards respond with NACK or ACK
    response = ser.read(4)
    print response
    ser.close 

if __name__ == "__main__":
    main(sys.argv[1:])
