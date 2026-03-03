"""
Unit tests for core communication module.

These tests verify serial communication functions with mocked serial port.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import serial
from core import write_to_sign, format_final_message


class TestFormatFinalMessage:
    """Tests for format_final_message function."""
    
    def test_format_final_message_basic(self):
        """Test basic message formatting."""
        inner = "<L1><PA><FE><MQ><WC><FE><AC>Hello"
        checksum = "4A"
        sign_id = "00"
        
        result = format_final_message(inner, checksum, sign_id)
        
        assert result == f"<ID00>{inner}4A<E>"
    
    def test_format_final_message_different_sign_id(self):
        """Test message formatting with different sign ID."""
        inner = "<L1><PA><FE><MQ><WC><FE><AC>Test"
        checksum = "2B"
        sign_id = "01"
        
        result = format_final_message(inner, checksum, sign_id)
        
        assert result == f"<ID01>{inner}2B<E>"
    
    def test_format_final_message_structure(self):
        """Test that formatted message has correct structure."""
        inner = "TEST_INNER"
        checksum = "FF"
        sign_id = "99"
        
        result = format_final_message(inner, checksum, sign_id)
        
        # Verify structure: <ID{sign_id}>{inner}{checksum}<E>
        assert result.startswith("<ID99>")
        assert result.endswith("<E>")
        assert "TEST_INNER" in result
        assert "FF" in result


class TestWriteToSign:
    """Tests for write_to_sign function with mocked serial port."""
    
    @patch('core.serial.Serial')
    def test_write_to_sign_success(self, mock_serial_class):
        """Test successful write to sign."""
        # Set up mock
        mock_serial = MagicMock()
        mock_serial_class.return_value = mock_serial
        mock_serial.read.return_value = b'ACK\x00'
        
        # Call function
        message = "<ID00><L1><PA><FE><MQ><WC><FE><AC>Test4A<E>"
        result = write_to_sign(message, "COM7", timeout=3)
        
        # Verify serial port was opened correctly
        mock_serial_class.assert_called_once_with("COM7", 9600, timeout=3)
        
        # Verify buffer was flushed
        mock_serial.flushInput.assert_called_once()
        mock_serial.flushOutput.assert_called_once()
        
        # Verify message was written twice (initialization)
        assert mock_serial.write.call_count == 2
        mock_serial.write.assert_called_with(message.encode('ascii'))
        
        # Verify response was read
        mock_serial.read.assert_called_once_with(4)
        
        # Verify serial port was closed
        mock_serial.close.assert_called_once()
        
        # Verify result
        assert result == 'ACK\x00'
    
    @patch('core.serial.Serial')
    def test_write_to_sign_nack_response(self, mock_serial_class):
        """Test write to sign with NACK response."""
        mock_serial = MagicMock()
        mock_serial_class.return_value = mock_serial
        mock_serial.read.return_value = b'NACK'
        
        message = "<ID00><L1><PA><FE><MQ><WC><FE><AC>Test4A<E>"
        result = write_to_sign(message, "COM7")
        
        assert result == 'NACK'
    
    @patch('core.serial.Serial')
    def test_write_to_sign_empty_response(self, mock_serial_class):
        """Test write to sign with empty response."""
        mock_serial = MagicMock()
        mock_serial_class.return_value = mock_serial
        mock_serial.read.return_value = b''
        
        message = "<ID00><L1><PA><FE><MQ><WC><FE><AC>Test4A<E>"
        result = write_to_sign(message, "COM7")
        
        assert result == ''
    
    @patch('core.serial.Serial')
    def test_write_to_sign_custom_timeout(self, mock_serial_class):
        """Test write to sign with custom timeout."""
        mock_serial = MagicMock()
        mock_serial_class.return_value = mock_serial
        mock_serial.read.return_value = b'ACK\x00'
        
        message = "<ID00><L1><PA><FE><MQ><WC><FE><AC>Test4A<E>"
        write_to_sign(message, "/dev/ttyUSB0", timeout=5)
        
        # Verify timeout was passed correctly
        mock_serial_class.assert_called_once_with("/dev/ttyUSB0", 9600, timeout=5)
    
    @patch('core.serial.Serial')
    def test_write_to_sign_serial_exception(self, mock_serial_class):
        """Test write to sign when serial port cannot be opened."""
        # Simulate serial port error
        mock_serial_class.side_effect = serial.SerialException("Port not found")
        
        message = "<ID00><L1><PA><FE><MQ><WC><FE><AC>Test4A<E>"
        
        with pytest.raises(serial.SerialException, match="Failed to communicate with sign"):
            write_to_sign(message, "INVALID_PORT")
    
    @patch('core.serial.Serial')
    def test_write_to_sign_permission_denied(self, mock_serial_class):
        """Test write to sign when permission is denied."""
        mock_serial_class.side_effect = serial.SerialException("Permission denied")
        
        message = "<ID00><L1><PA><FE><MQ><WC><FE><AC>Test4A<E>"
        
        with pytest.raises(serial.SerialException, match="Failed to communicate with sign"):
            write_to_sign(message, "/dev/ttyUSB0")
    
    @patch('core.serial.Serial')
    def test_write_to_sign_different_port(self, mock_serial_class):
        """Test write to sign with different port names."""
        mock_serial = MagicMock()
        mock_serial_class.return_value = mock_serial
        mock_serial.read.return_value = b'ACK\x00'
        
        message = "<ID00><L1><PA><FE><MQ><WC><FE><AC>Test4A<E>"
        
        # Test Windows port
        write_to_sign(message, "COM3")
        mock_serial_class.assert_called_with("COM3", 9600, timeout=3)
        
        # Test Linux port
        write_to_sign(message, "/dev/ttyUSB0")
        mock_serial_class.assert_called_with("/dev/ttyUSB0", 9600, timeout=3)
        
        # Test Mac port
        write_to_sign(message, "/dev/tty.usbserial")
        mock_serial_class.assert_called_with("/dev/tty.usbserial", 9600, timeout=3)
