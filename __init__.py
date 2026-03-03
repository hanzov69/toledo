"""
Toledo - Control Amplus LED sign boards

This module provides a Python API for controlling Amplus LED sign boards.
It can be used both as a command-line tool and as an importable library.

Example usage as a library:
    import toledo
    toledo.send_message("Hello World", port="COM7", color="red")

Example usage as a command-line tool:
    toledo --message "Hello World" --color red --output
"""

from .core import write_to_sign, format_final_message
from .protocol import (
    calculate_checksum,
    encode_message,
    encode_link_command,
    encode_run_page_command,
    INTRO_EFFECTS,
    EXIT_EFFECTS,
    FONTS,
    SPEEDS,
    BELLS,
    COLORS,
)

__version__ = "0.0.4.3"
__author__ = "Christian Sullivan"
__email__ = "hanzo@freezerpants.com"


# Constants exported as classes for cleaner API
class Effects:
    """Effect constants for intro and exit effects."""
    IMMEDIATE = 1
    XOPEN = 2
    CURTAIN_UP = 3
    CURTAIN_DOWN = 4
    SCROLL_LEFT = 5
    SCROLL_RIGHT = 6
    VOPEN = 7
    VCLOSE = 8
    SCROLL_UP = 9
    SCROLL_DOWN = 10
    HOLD = 11
    SNOW = 12
    TWINKLE = 13
    BLOCK_MOVE = 14
    RANDOM = 15
    CURSIVE_WELCOME = 16


class Fonts:
    """Font constants."""
    FONT_1 = 1
    FONT_2 = 2
    FONT_3 = 3
    FONT_4 = 4
    FONT_5 = 5


class Colors:
    """Color constants."""
    RED = "red"
    ORANGE = "orange"
    GREEN = "green"
    IORANGE = "iorange"
    IGREEN = "igreen"
    IRED = "ired"
    ROG = "rog"
    GOR = "gor"
    RYG = "ryg"
    RAINBOW = "rainbow"


def send_message(
    message: str,
    port: str = "COM7",
    line: int = 1,
    page: str = "A",
    font: int = 1,
    intro_effect: int = 5,
    exit_effect: int = 5,
    speed: int = 3,
    bell: int = 0,
    color: str = "",
    show_date: bool = False,
    show_time: bool = False,
    sign_id: str = "00"
) -> str:
    """
    Send a message to the LED sign.
    
    Args:
        message: The text message to display
        port: Serial port name (default: "COM7")
        line: Line number 1-26 (default: 1)
        page: Page letter A-Z (default: "A")
        font: Font number 1-5 (default: 1)
        intro_effect: Intro effect number 1-16 (default: 5 - scroll left)
        exit_effect: Exit effect number 1-11 (default: 5 - scroll left)
        speed: Speed number 1-4 (default: 3)
        bell: Bell duration 0-4 (default: 0 - no bell)
        color: Color name (red, orange, green, etc.) (default: "" - no color)
        show_date: Whether to show date (default: False)
        show_time: Whether to show time (default: False)
        sign_id: Sign ID (default: "00")
        
    Returns:
        The sign's response (ACK/NACK or empty string)
        
    Raises:
        ValueError: If any parameter is invalid
        serial.SerialException: If serial communication fails
        
    Example:
        >>> import toledo
        >>> toledo.send_message("Hello World", port="COM7", color="red")
        'ACK'
    """
    # Encode the message with protocol tags
    inner_message = encode_message(
        message=message,
        line=line,
        page=page,
        font=font,
        intro_effect=intro_effect,
        exit_effect=exit_effect,
        speed=speed,
        bell=bell,
        color=color,
        show_date=show_date,
        show_time=show_time
    )
    
    # Calculate checksum
    checksum = calculate_checksum(inner_message)
    
    # Format final message with sign ID and checksum
    final_message = format_final_message(inner_message, checksum, sign_id)
    
    # Send to sign
    return write_to_sign(final_message, port)


def send_raw_command(
    command: str,
    port: str = "COM7",
    sign_id: str = "00"
) -> str:
    """
    Send a raw protocol command to the LED sign.
    
    This function allows sending pre-formatted protocol commands directly
    to the sign. The command should be the inner message content without
    the sign ID wrapper and checksum, which will be added automatically.
    
    Args:
        command: The raw protocol command (inner message)
        port: Serial port name (default: "COM7")
        sign_id: Sign ID (default: "00")
        
    Returns:
        The sign's response (ACK/NACK or empty string)
        
    Raises:
        serial.SerialException: If serial communication fails
        
    Example:
        >>> import toledo
        >>> toledo.send_raw_command("<L1><PA><FE><MQ><WC><FE><AC>Test", port="COM7")
        'ACK'
    """
    # Calculate checksum for the command
    checksum = calculate_checksum(command)
    
    # Format final message with sign ID and checksum
    final_message = format_final_message(command, checksum, sign_id)
    
    # Send to sign
    return write_to_sign(final_message, port)


def link_pages(
    page_sequence: str,
    port: str = "COM7",
    sign_id: str = "00"
) -> str:
    """
    Link pages in a specific sequence.
    
    This function creates a page linking command that tells the sign
    to display pages in a specific order. For example, "ABACAB" would
    display page A, then B, then A again, then C, then A, then B.
    
    Args:
        page_sequence: Sequence of pages to link (e.g., "ABACAB")
        port: Serial port name (default: "COM7")
        sign_id: Sign ID (default: "00")
        
    Returns:
        The sign's response (ACK/NACK or empty string)
        
    Raises:
        ValueError: If page_sequence is invalid
        serial.SerialException: If serial communication fails
        
    Example:
        >>> import toledo
        >>> toledo.link_pages("ABACAB", port="COM7")
        'ACK'
    """
    # Encode the link command
    link_command = encode_link_command(page_sequence)
    
    # Calculate checksum
    checksum = calculate_checksum(link_command)
    
    # Format final message with sign ID and checksum
    final_message = format_final_message(link_command, checksum, sign_id)
    
    # Send to sign
    return write_to_sign(final_message, port)


__all__ = [
    # Main API functions
    "send_message",
    "send_raw_command",
    "link_pages",
    "calculate_checksum",
    # Constants
    "Effects",
    "Fonts",
    "Colors",
    # Version info
    "__version__",
    "__author__",
    "__email__",
]
