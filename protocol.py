"""
Protocol module for LED sign message encoding.

This module handles protocol encoding, message formatting, checksum calculation,
and conversion of effects, fonts, colors, and other parameters to protocol tags.
"""

from operator import xor
from typing import Optional


# Protocol constant mappings
INTRO_EFFECTS = {
    1: "<FA>",  # immediate
    2: "<FB>",  # xopen
    3: "<FC>",  # curtain up
    4: "<FD>",  # curtain down
    5: "<FE>",  # scroll left
    6: "<FF>",  # scroll right
    7: "<FG>",  # vopen
    8: "<FH>",  # vclose
    9: "<FI>",  # scroll up
    10: "<FJ>", # scroll down
    11: "<FK>", # hold
    12: "<FL>", # snow
    13: "<FM>", # twinkle
    14: "<FN>", # block move
    15: "<FP>", # random
    16: "<FR>", # cursive welcome
}

EXIT_EFFECTS = {
    1: "<FA>",  # immediate
    2: "<FB>",  # xopen
    3: "<FC>",  # curtain up
    4: "<FD>",  # curtain down
    5: "<FE>",  # scroll left
    6: "<FF>",  # scroll right
    7: "<FG>",  # vopen
    8: "<FH>",  # vclose
    9: "<FI>",  # scroll up
    10: "<FJ>", # scroll down
    11: "<FK>", # hold
}

FONTS = {
    1: "<AC>",
    2: "<AA>",
    3: "<AB>",
    4: "<AF>",
    5: "<AD>",
}

SPEEDS = {
    1: "<Mq>",  # slowest
    2: "<Ma>",
    3: "<MQ>",
    4: "<MA>",  # fastest
}

BELLS = {
    0: "",
    1: "<BA>",  # 0.5 sec
    2: "<BB>",  # 1.0 sec
    3: "<BC>",  # 1.5 sec
    4: "<BD>",  # 2.0 sec
}

COLORS = {
    "red": "<CA>",
    "orange": "<CH>",
    "green": "<CD>",
    "iorange": "<CN>",
    "igreen": "<CM>",
    "ired": "<CL>",
    "rog": "<CP>",
    "gor": "<CQ>",
    "ryg": "<CR>",
    "rainbow": "<CS>",
}


def calculate_checksum(message: str) -> str:
    """
    Calculate XOR checksum for a protocol message.
    
    Args:
        message: The protocol message to checksum
        
    Returns:
        Two-character hex string representing the checksum
    """
    from functools import reduce
    
    # Handle empty message
    if not message:
        return "00"
    
    # XOR all character codes in the message
    checksum_value = reduce(xor, [ord(c) for c in message])
    
    # Format as two-character uppercase hex string
    return "%02X" % checksum_value


def encode_message(
    message: str,
    line: int,
    page: str,
    font: int,
    intro_effect: int,
    exit_effect: int,
    speed: int,
    bell: int,
    color: str,
    show_date: bool,
    show_time: bool
) -> str:
    """
    Encode a message with all protocol tags.
    
    Args:
        message: The text message to display
        line: Line number (1-based)
        page: Page letter (A-Z)
        font: Font number (1-5)
        intro_effect: Intro effect number (1-16)
        exit_effect: Exit effect number (1-11)
        speed: Speed number (1-4)
        bell: Bell duration (0-4)
        color: Color name (red, green, orange, etc.)
        show_date: Whether to show date
        show_time: Whether to show time
        
    Returns:
        The inner message (without sign ID wrapper and checksum)
    """
    # Validate and convert parameters
    font_tag = convert_font(font)
    intro_tag = convert_intro_effect(intro_effect)
    exit_tag = convert_exit_effect(exit_effect)
    speed_tag = convert_speed(speed)
    bell_tag = convert_bell(bell)
    color_tag = convert_color(color)
    
    # Validate page
    if not page or len(page) != 1 or not page.isalpha() or not page.isupper():
        raise ValueError(f"Invalid page: {page}. Must be a single uppercase letter A-Z.")
    
    # Validate line
    if line < 1 or line > 26:
        raise ValueError(f"Invalid line: {line}. Valid range is 1-26.")
    
    # Validate message
    if not message:
        raise ValueError("Message cannot be empty.")
    
    # Build date/time flags
    date_tag = "<KD> " if show_date else ""
    time_tag = "<KT> " if show_time else ""
    
    # Format: <L{line}><P{page}>{intro}{speed}<WC>{exit}{bell}{color}{date}{time}{font}{message}
    encoded = (
        f"<L{line}><P{page}>"
        f"{intro_tag}{speed_tag}<WC>"
        f"{exit_tag}{bell_tag}{color_tag}{date_tag}{time_tag}{font_tag}{message}"
    )
    
    return encoded


def encode_link_command(page_sequence: str) -> str:
    """
    Encode a page linking command.
    
    Args:
        page_sequence: Sequence of pages to link (e.g., "ABACAB")
        
    Returns:
        The encoded link command
        
    Raises:
        ValueError: If page_sequence is empty or contains invalid characters
    """
    if not page_sequence:
        raise ValueError("Page sequence cannot be empty.")
    
    # Validate that all characters are uppercase letters A-Z
    if not all(c.isalpha() and c.isupper() for c in page_sequence):
        raise ValueError(f"Invalid page sequence: {page_sequence}. All characters must be uppercase letters A-Z.")
    
    # Format: <TA>00010100009912302359{page_sequence}
    # The fixed prefix appears to be a time/date configuration followed by the page sequence
    return f"<TA>00010100009912302359{page_sequence}"


def encode_run_page_command(page: str) -> str:
    """
    Encode a run page command.
    
    Args:
        page: Page letter to run (A-Z)
        
    Returns:
        The encoded run page command
        
    Raises:
        ValueError: If page is not a single uppercase letter
    """
    if not page or len(page) != 1 or not page.isalpha() or not page.isupper():
        raise ValueError(f"Invalid page: {page}. Must be a single uppercase letter A-Z.")
    
    # Format: <RP{page}>
    return f"<RP{page}>"


def convert_font(font: int) -> str:
    """
    Convert font number to protocol tag.
    
    Args:
        font: Font number (1-5)
        
    Returns:
        Protocol tag for the font
        
    Raises:
        ValueError: If font number is invalid
    """
    if font not in FONTS:
        raise ValueError(f"Invalid font number: {font}. Valid range is 1-5.")
    return FONTS[font]


def convert_intro_effect(effect: int) -> str:
    """
    Convert intro effect number to protocol tag.
    
    Args:
        effect: Intro effect number (1-16)
        
    Returns:
        Protocol tag for the intro effect
        
    Raises:
        ValueError: If effect number is invalid
    """
    if effect not in INTRO_EFFECTS:
        raise ValueError(f"Invalid intro effect number: {effect}. Valid range is 1-16.")
    return INTRO_EFFECTS[effect]


def convert_exit_effect(effect: int) -> str:
    """
    Convert exit effect number to protocol tag.
    
    Args:
        effect: Exit effect number (1-11)
        
    Returns:
        Protocol tag for the exit effect
        
    Raises:
        ValueError: If effect number is invalid
    """
    if effect not in EXIT_EFFECTS:
        raise ValueError(f"Invalid exit effect number: {effect}. Valid range is 1-11.")
    return EXIT_EFFECTS[effect]


def convert_speed(speed: int) -> str:
    """
    Convert speed number to protocol tag.
    
    Args:
        speed: Speed number (1-4)
        
    Returns:
        Protocol tag for the speed
        
    Raises:
        ValueError: If speed number is invalid
    """
    if speed not in SPEEDS:
        raise ValueError(f"Invalid speed number: {speed}. Valid range is 1-4.")
    return SPEEDS[speed]


def convert_bell(bell: int) -> str:
    """
    Convert bell duration to protocol tag.
    
    Args:
        bell: Bell duration (0-4)
        
    Returns:
        Protocol tag for the bell (empty string for 0)
        
    Raises:
        ValueError: If bell duration is invalid
    """
    if bell not in BELLS:
        raise ValueError(f"Invalid bell duration: {bell}. Valid range is 0-4.")
    return BELLS[bell]


def convert_color(color: str) -> str:
    """
    Convert color name to protocol tag.
    
    Args:
        color: Color name (red, orange, green, iorange, igreen, ired, rog, gor, ryg, rainbow)
        
    Returns:
        Protocol tag for the color (empty string for empty color)
        
    Raises:
        ValueError: If color name is invalid
    """
    if color == "":
        return ""
    if color not in COLORS:
        valid_colors = ", ".join(COLORS.keys())
        raise ValueError(f"Invalid color name: {color}. Valid colors are: {valid_colors}.")
    return COLORS[color]
