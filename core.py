"""
Core module for LED sign communication.

This module handles low-level serial communication with Amplus LED sign boards.
"""

import serial


def write_to_sign(message: str, port: str, timeout: int = 3) -> str:
    """
    Write a formatted message to the LED sign via serial port.
    
    Handles serial port initialization, buffer flushing, double-write
    for initialization, and response reading.
    
    Args:
        message: The complete formatted protocol message to send
        port: Serial port name (e.g., "COM7" or "/dev/ttyUSB0")
        timeout: Timeout in seconds for serial operations
        
    Returns:
        The sign's response (ACK/NACK or empty string)
        
    Raises:
        serial.SerialException: If the serial port cannot be opened
    """
    try:
        # Set up serial port with 9600 baud rate
        ser = serial.Serial(port, 9600, timeout=timeout)
        
        # Clear out the buffer
        ser.flushInput()
        ser.flushOutput()
        
        # The Amplus boards need to be "initialized" - if after a lengthy period
        # without programming, they won't respond until they've gotten a valid string,
        # so we send two "valid" strings
        ser.write(message.encode('ascii'))
        ser.write(message.encode('ascii'))
        
        # Wait for a response - watching for NACK or ACK (4 bytes)
        # Not all Amplus boards respond with NACK or ACK
        response = ser.read(4)
        
        # Close the serial port
        ser.close()
        
        # Return the response as a string (decode from bytes)
        return response.decode('ascii', errors='ignore')
        
    except serial.SerialException as e:
        # Re-raise with more context
        raise serial.SerialException(f"Failed to communicate with sign on port {port}: {e}")


def format_final_message(inner_message: str, checksum: str, sign_id: str) -> str:
    """
    Format the complete message with sign ID, inner message, checksum, and end tag.
    
    Args:
        inner_message: The encoded message content
        checksum: Two-character hex checksum
        sign_id: Sign ID (typically "00")
        
    Returns:
        Complete formatted message ready to send
    """
    # Format: <ID{sign_id}>{inner_message}{checksum}<E>
    return f"<ID{sign_id}>{inner_message}{checksum}<E>"
