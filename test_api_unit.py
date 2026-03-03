"""
Unit tests for public API functions.

These tests verify the public API exposed in __init__.py with mocked serial communication.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import serial

# Import the public API functions from the toledo package
import toledo
from toledo import send_message, send_raw_command, link_pages, Effects, Fonts, Colors


class TestSendMessage:
    """Tests for send_message function."""
    
    @patch('toledo.core.serial.Serial')
    def test_send_message_basic(self, mock_serial_class):
        """Test basic message sending with default parameters."""
        # Set up mock
        mock_serial = Mock()
        mock_serial.read.return_value = b'ACK\x00'
        mock_serial_class.return_value = mock_serial
        
        # Call function
        response = send_message("Hello", port="COM7")
        
        # Verify serial port was opened correctly
        mock_serial_class.assert_called_once_with("COM7", 9600, timeout=3)
        
        # Verify write was called twice (initialization)
        assert mock_serial.write.call_count == 2
        
        # Verify the message structure
        written_message = mock_serial.write.call_args_list[0][0][0].decode('ascii')
        assert written_message.startswith("<ID00>")
        assert written_message.endswith("<E>")
        assert "<L1><PA>" in written_message
        assert "Hello" in written_message
        
        # Verify response
        assert response == "ACK\x00"
        
        # Verify cleanup
        mock_serial.close.assert_called_once()
    
    @patch('toledo.core.serial.Serial')
    def test_send_message_with_color(self, mock_serial_class):
        """Test message sending with color parameter."""
        mock_serial = Mock()
        mock_serial.read.return_value = b'ACK\x00'
        mock_serial_class.return_value = mock_serial
        
        response = send_message("Test", port="COM7", color="red")
        
        # Verify color tag is in message
        written_message = mock_serial.write.call_args_list[0][0][0].decode('ascii')
        assert "<CA>" in written_message  # red color tag
    
    @patch('toledo.core.serial.Serial')
    def test_send_message_with_effects(self, mock_serial_class):
        """Test message sending with custom effects."""
        mock_serial = Mock()
        mock_serial.read.return_value = b'ACK\x00'
        mock_serial_class.return_value = mock_serial
        
        response = send_message(
            "Test",
            port="COM7",
            intro_effect=Effects.CURTAIN_UP,
            exit_effect=Effects.CURTAIN_DOWN
        )
        
        # Verify effect tags are in message
        written_message = mock_serial.write.call_args_list[0][0][0].decode('ascii')
        assert "<FC>" in written_message  # curtain up
        assert "<FD>" in written_message  # curtain down
    
    @patch('toledo.core.serial.Serial')
    def test_send_message_with_font(self, mock_serial_class):
        """Test message sending with custom font."""
        mock_serial = Mock()
        mock_serial.read.return_value = b'ACK\x00'
        mock_serial_class.return_value = mock_serial
        
        response = send_message("Test", port="COM7", font=Fonts.FONT_2)
        
        # Verify font tag is in message
        written_message = mock_serial.write.call_args_list[0][0][0].decode('ascii')
        assert "<AA>" in written_message  # font 2
    
    @patch('toledo.core.serial.Serial')
    def test_send_message_with_bell(self, mock_serial_class):
        """Test message sending with bell."""
        mock_serial = Mock()
        mock_serial.read.return_value = b'ACK\x00'
        mock_serial_class.return_value = mock_serial
        
        response = send_message("Alert", port="COM7", bell=2)
        
        # Verify bell tag is in message
        written_message = mock_serial.write.call_args_list[0][0][0].decode('ascii')
        assert "<BB>" in written_message  # bell 2
    
    @patch('toledo.core.serial.Serial')
    def test_send_message_with_page_and_line(self, mock_serial_class):
        """Test message sending with custom page and line."""
        mock_serial = Mock()
        mock_serial.read.return_value = b'ACK\x00'
        mock_serial_class.return_value = mock_serial
        
        response = send_message("Test", port="COM7", page="B", line=5)
        
        # Verify page and line tags are in message
        written_message = mock_serial.write.call_args_list[0][0][0].decode('ascii')
        assert "<L5><PB>" in written_message
    
    @patch('toledo.core.serial.Serial')
    def test_send_message_with_speed(self, mock_serial_class):
        """Test message sending with custom speed."""
        mock_serial = Mock()
        mock_serial.read.return_value = b'ACK\x00'
        mock_serial_class.return_value = mock_serial
        
        response = send_message("Test", port="COM7", speed=1)
        
        # Verify speed tag is in message
        written_message = mock_serial.write.call_args_list[0][0][0].decode('ascii')
        assert "<Mq>" in written_message  # speed 1 (slowest)
    
    @patch('toledo.core.serial.Serial')
    def test_send_message_with_sign_id(self, mock_serial_class):
        """Test message sending with custom sign ID."""
        mock_serial = Mock()
        mock_serial.read.return_value = b'ACK\x00'
        mock_serial_class.return_value = mock_serial
        
        response = send_message("Test", port="COM7", sign_id="01")
        
        # Verify sign ID is in message
        written_message = mock_serial.write.call_args_list[0][0][0].decode('ascii')
        assert written_message.startswith("<ID01>")
    
    @patch('toledo.core.serial.Serial')
    def test_send_message_all_parameters(self, mock_serial_class):
        """Test message sending with all parameters specified."""
        mock_serial = Mock()
        mock_serial.read.return_value = b'ACK\x00'
        mock_serial_class.return_value = mock_serial
        
        response = send_message(
            message="Full Test",
            port="COM7",
            line=3,
            page="C",
            font=3,
            intro_effect=7,
            exit_effect=8,
            speed=4,
            bell=3,
            color="green",
            show_date=False,
            show_time=False,
            sign_id="02"
        )
        
        # Verify message structure
        written_message = mock_serial.write.call_args_list[0][0][0].decode('ascii')
        assert written_message.startswith("<ID02>")
        assert "<L3><PC>" in written_message
        assert "<FG>" in written_message  # intro effect 7
        assert "<FH>" in written_message  # exit effect 8
        assert "<MA>" in written_message  # speed 4
        assert "<BC>" in written_message  # bell 3
        assert "<CD>" in written_message  # green color
        assert "<AB>" in written_message  # font 3
        assert "Full Test" in written_message
        assert written_message.endswith("<E>")
        
        assert response == "ACK\x00"
    
    @patch('toledo.core.serial.Serial')
    def test_send_message_serial_exception(self, mock_serial_class):
        """Test that serial exceptions are propagated."""
        mock_serial_class.side_effect = serial.SerialException("Port not found")
        
        with pytest.raises(serial.SerialException, match="Port not found"):
            send_message("Test", port="INVALID")
    
    @patch('toledo.core.serial.Serial')
    def test_send_message_invalid_color(self, mock_serial_class):
        """Test that invalid color raises ValueError."""
        with pytest.raises(ValueError, match="Invalid color name"):
            send_message("Test", port="COM7", color="blue")
    
    @patch('toledo.core.serial.Serial')
    def test_send_message_invalid_font(self, mock_serial_class):
        """Test that invalid font raises ValueError."""
        with pytest.raises(ValueError, match="Invalid font number"):
            send_message("Test", port="COM7", font=10)
    
    @patch('toledo.core.serial.Serial')
    def test_send_message_invalid_effect(self, mock_serial_class):
        """Test that invalid effect raises ValueError."""
        with pytest.raises(ValueError, match="Invalid intro effect number"):
            send_message("Test", port="COM7", intro_effect=20)


class TestSendRawCommand:
    """Tests for send_raw_command function."""
    
    @patch('toledo.core.serial.Serial')
    def test_send_raw_command_basic(self, mock_serial_class):
        """Test sending a raw command."""
        mock_serial = Mock()
        mock_serial.read.return_value = b'ACK\x00'
        mock_serial_class.return_value = mock_serial
        
        command = "<L1><PA><FE><MQ><WC><FE><AC>Test"
        response = send_raw_command(command, port="COM7")
        
        # Verify serial port was opened
        mock_serial_class.assert_called_once_with("COM7", 9600, timeout=3)
        
        # Verify write was called twice
        assert mock_serial.write.call_count == 2
        
        # Verify the message structure
        written_message = mock_serial.write.call_args_list[0][0][0].decode('ascii')
        assert written_message.startswith("<ID00>")
        assert command in written_message
        assert written_message.endswith("<E>")
        
        # Verify response
        assert response == "ACK\x00"
        
        # Verify cleanup
        mock_serial.close.assert_called_once()
    
    @patch('toledo.core.serial.Serial')
    def test_send_raw_command_with_sign_id(self, mock_serial_class):
        """Test sending a raw command with custom sign ID."""
        mock_serial = Mock()
        mock_serial.read.return_value = b'ACK\x00'
        mock_serial_class.return_value = mock_serial
        
        command = "<L1><PA><FE><MQ><WC><FE><AC>Test"
        response = send_raw_command(command, port="COM7", sign_id="05")
        
        # Verify sign ID is in message
        written_message = mock_serial.write.call_args_list[0][0][0].decode('ascii')
        assert written_message.startswith("<ID05>")
    
    @patch('toledo.core.serial.Serial')
    def test_send_raw_command_different_port(self, mock_serial_class):
        """Test sending a raw command to different port."""
        mock_serial = Mock()
        mock_serial.read.return_value = b'ACK\x00'
        mock_serial_class.return_value = mock_serial
        
        command = "<L1><PA><FE><MQ><WC><FE><AC>Test"
        response = send_raw_command(command, port="/dev/ttyUSB0")
        
        # Verify correct port was used
        mock_serial_class.assert_called_once_with("/dev/ttyUSB0", 9600, timeout=3)
    
    @patch('toledo.core.serial.Serial')
    def test_send_raw_command_serial_exception(self, mock_serial_class):
        """Test that serial exceptions are propagated."""
        mock_serial_class.side_effect = serial.SerialException("Port not found")
        
        with pytest.raises(serial.SerialException, match="Port not found"):
            send_raw_command("<L1><PA>Test", port="INVALID")


class TestLinkPages:
    """Tests for link_pages function."""
    
    @patch('toledo.core.serial.Serial')
    def test_link_pages_basic(self, mock_serial_class):
        """Test basic page linking."""
        mock_serial = Mock()
        mock_serial.read.return_value = b'ACK\x00'
        mock_serial_class.return_value = mock_serial
        
        response = link_pages("ABACAB", port="COM7")
        
        # Verify serial port was opened
        mock_serial_class.assert_called_once_with("COM7", 9600, timeout=3)
        
        # Verify write was called twice
        assert mock_serial.write.call_count == 2
        
        # Verify the message structure
        written_message = mock_serial.write.call_args_list[0][0][0].decode('ascii')
        assert written_message.startswith("<ID00>")
        assert "<TA>00010100009912302359ABACAB" in written_message
        assert written_message.endswith("<E>")
        
        # Verify response
        assert response == "ACK\x00"
        
        # Verify cleanup
        mock_serial.close.assert_called_once()
    
    @patch('toledo.core.serial.Serial')
    def test_link_pages_single_page(self, mock_serial_class):
        """Test linking a single page."""
        mock_serial = Mock()
        mock_serial.read.return_value = b'ACK\x00'
        mock_serial_class.return_value = mock_serial
        
        response = link_pages("A", port="COM7")
        
        # Verify the message contains single page
        written_message = mock_serial.write.call_args_list[0][0][0].decode('ascii')
        assert "<TA>00010100009912302359A" in written_message
    
    @patch('toledo.core.serial.Serial')
    def test_link_pages_with_sign_id(self, mock_serial_class):
        """Test page linking with custom sign ID."""
        mock_serial = Mock()
        mock_serial.read.return_value = b'ACK\x00'
        mock_serial_class.return_value = mock_serial
        
        response = link_pages("ABC", port="COM7", sign_id="03")
        
        # Verify sign ID is in message
        written_message = mock_serial.write.call_args_list[0][0][0].decode('ascii')
        assert written_message.startswith("<ID03>")
    
    @patch('toledo.core.serial.Serial')
    def test_link_pages_different_port(self, mock_serial_class):
        """Test page linking on different port."""
        mock_serial = Mock()
        mock_serial.read.return_value = b'ACK\x00'
        mock_serial_class.return_value = mock_serial
        
        response = link_pages("XYZ", port="/dev/ttyUSB0")
        
        # Verify correct port was used
        mock_serial_class.assert_called_once_with("/dev/ttyUSB0", 9600, timeout=3)
    
    @patch('toledo.core.serial.Serial')
    def test_link_pages_invalid_sequence(self, mock_serial_class):
        """Test that invalid page sequence raises ValueError."""
        with pytest.raises(ValueError, match="All characters must be uppercase letters A-Z"):
            link_pages("abc", port="COM7")
    
    @patch('toledo.core.serial.Serial')
    def test_link_pages_empty_sequence(self, mock_serial_class):
        """Test that empty sequence raises ValueError."""
        with pytest.raises(ValueError, match="Page sequence cannot be empty"):
            link_pages("", port="COM7")
    
    @patch('toledo.core.serial.Serial')
    def test_link_pages_serial_exception(self, mock_serial_class):
        """Test that serial exceptions are propagated."""
        mock_serial_class.side_effect = serial.SerialException("Port not found")
        
        with pytest.raises(serial.SerialException, match="Port not found"):
            link_pages("ABC", port="INVALID")


class TestConstants:
    """Tests for exported constants."""
    
    def test_effects_constants(self):
        """Test that Effects class has expected constants."""
        assert Effects.IMMEDIATE == 1
        assert Effects.XOPEN == 2
        assert Effects.CURTAIN_UP == 3
        assert Effects.CURTAIN_DOWN == 4
        assert Effects.SCROLL_LEFT == 5
        assert Effects.SCROLL_RIGHT == 6
        assert Effects.VOPEN == 7
        assert Effects.VCLOSE == 8
        assert Effects.SCROLL_UP == 9
        assert Effects.SCROLL_DOWN == 10
        assert Effects.HOLD == 11
        assert Effects.SNOW == 12
        assert Effects.TWINKLE == 13
        assert Effects.BLOCK_MOVE == 14
        assert Effects.RANDOM == 15
        assert Effects.CURSIVE_WELCOME == 16
    
    def test_fonts_constants(self):
        """Test that Fonts class has expected constants."""
        assert Fonts.FONT_1 == 1
        assert Fonts.FONT_2 == 2
        assert Fonts.FONT_3 == 3
        assert Fonts.FONT_4 == 4
        assert Fonts.FONT_5 == 5
    
    def test_colors_constants(self):
        """Test that Colors class has expected constants."""
        assert Colors.RED == "red"
        assert Colors.ORANGE == "orange"
        assert Colors.GREEN == "green"
        assert Colors.IORANGE == "iorange"
        assert Colors.IGREEN == "igreen"
        assert Colors.IRED == "ired"
        assert Colors.ROG == "rog"
        assert Colors.GOR == "gor"
        assert Colors.RYG == "ryg"
        assert Colors.RAINBOW == "rainbow"
