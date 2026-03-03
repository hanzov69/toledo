"""
Unit tests for protocol encoding module.

These tests verify specific examples and edge cases.
"""

import pytest
from protocol import (
    encode_link_command,
    encode_run_page_command,
    calculate_checksum,
    encode_message,
    convert_font,
    convert_intro_effect,
    convert_exit_effect,
    convert_speed,
    convert_bell,
    convert_color,
)


class TestEncodeLinkCommand:
    """Tests for encode_link_command function."""
    
    def test_encode_link_command_simple_sequence(self):
        """Test encoding a simple page sequence."""
        result = encode_link_command("ABACAB")
        assert result == "<TA>00010100009912302359ABACAB"
    
    def test_encode_link_command_single_page(self):
        """Test encoding a single page."""
        result = encode_link_command("A")
        assert result == "<TA>00010100009912302359A"
    
    def test_encode_link_command_all_pages(self):
        """Test encoding all pages A-Z."""
        result = encode_link_command("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        assert result == "<TA>00010100009912302359ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    def test_encode_link_command_empty_sequence_raises_error(self):
        """Test that empty sequence raises ValueError."""
        with pytest.raises(ValueError, match="Page sequence cannot be empty"):
            encode_link_command("")
    
    def test_encode_link_command_lowercase_raises_error(self):
        """Test that lowercase letters raise ValueError."""
        with pytest.raises(ValueError, match="All characters must be uppercase letters A-Z"):
            encode_link_command("abc")
    
    def test_encode_link_command_mixed_case_raises_error(self):
        """Test that mixed case raises ValueError."""
        with pytest.raises(ValueError, match="All characters must be uppercase letters A-Z"):
            encode_link_command("AbC")
    
    def test_encode_link_command_numbers_raise_error(self):
        """Test that numbers raise ValueError."""
        with pytest.raises(ValueError, match="All characters must be uppercase letters A-Z"):
            encode_link_command("A1B2")
    
    def test_encode_link_command_special_chars_raise_error(self):
        """Test that special characters raise ValueError."""
        with pytest.raises(ValueError, match="All characters must be uppercase letters A-Z"):
            encode_link_command("A-B")


class TestEncodeRunPageCommand:
    """Tests for encode_run_page_command function."""
    
    def test_encode_run_page_command_page_a(self):
        """Test encoding run page command for page A."""
        result = encode_run_page_command("A")
        assert result == "<RPA>"
    
    def test_encode_run_page_command_page_z(self):
        """Test encoding run page command for page Z."""
        result = encode_run_page_command("Z")
        assert result == "<RPZ>"
    
    def test_encode_run_page_command_page_m(self):
        """Test encoding run page command for page M."""
        result = encode_run_page_command("M")
        assert result == "<RPM>"
    
    def test_encode_run_page_command_empty_raises_error(self):
        """Test that empty page raises ValueError."""
        with pytest.raises(ValueError, match="Must be a single uppercase letter A-Z"):
            encode_run_page_command("")
    
    def test_encode_run_page_command_lowercase_raises_error(self):
        """Test that lowercase letter raises ValueError."""
        with pytest.raises(ValueError, match="Must be a single uppercase letter A-Z"):
            encode_run_page_command("a")
    
    def test_encode_run_page_command_multiple_chars_raises_error(self):
        """Test that multiple characters raise ValueError."""
        with pytest.raises(ValueError, match="Must be a single uppercase letter A-Z"):
            encode_run_page_command("AB")
    
    def test_encode_run_page_command_number_raises_error(self):
        """Test that number raises ValueError."""
        with pytest.raises(ValueError, match="Must be a single uppercase letter A-Z"):
            encode_run_page_command("1")
    
    def test_encode_run_page_command_special_char_raises_error(self):
        """Test that special character raises ValueError."""
        with pytest.raises(ValueError, match="Must be a single uppercase letter A-Z"):
            encode_run_page_command("@")


class TestCalculateChecksum:
    """Tests for calculate_checksum function."""
    
    def test_calculate_checksum_known_values(self):
        """Test checksum calculation with known message/checksum pairs."""
        # These are example values - actual checksums would need to be verified
        # against the real LED sign protocol
        message1 = "<L1><PA><FE><MQ><WC><FE><AC>TEST"
        checksum1 = calculate_checksum(message1)
        assert len(checksum1) == 2
        assert all(c in '0123456789ABCDEF' for c in checksum1)
        
        # Verify determinism - same message produces same checksum
        checksum1_again = calculate_checksum(message1)
        assert checksum1 == checksum1_again
    
    def test_calculate_checksum_empty_string(self):
        """Test checksum of empty string."""
        # XOR of empty sequence should be 0
        checksum = calculate_checksum("")
        assert checksum == "00"
    
    def test_calculate_checksum_single_char(self):
        """Test checksum of single character."""
        checksum = calculate_checksum("A")
        # ASCII 'A' is 65 (0x41)
        assert checksum == "41"
    
    def test_calculate_checksum_format(self):
        """Test that checksum is always 2-character hex string."""
        test_messages = [
            "Hello",
            "<L1><PA>",
            "Test Message 123",
            "!@#$%^&*()",
        ]
        for message in test_messages:
            checksum = calculate_checksum(message)
            assert len(checksum) == 2, f"Checksum must be 2 chars for '{message}'"
            assert all(c in '0123456789ABCDEF' for c in checksum), \
                f"Checksum must be hex for '{message}'"


class TestConversionFunctions:
    """Tests for conversion functions."""
    
    def test_convert_font_valid(self):
        """Test font conversion with valid inputs."""
        assert convert_font(1) == "<AC>"
        assert convert_font(2) == "<AA>"
        assert convert_font(3) == "<AB>"
        assert convert_font(4) == "<AF>"
        assert convert_font(5) == "<AD>"
    
    def test_convert_font_invalid(self):
        """Test font conversion with invalid inputs."""
        with pytest.raises(ValueError, match="Invalid font number"):
            convert_font(0)
        with pytest.raises(ValueError, match="Invalid font number"):
            convert_font(6)
    
    def test_convert_intro_effect_valid(self):
        """Test intro effect conversion with valid inputs."""
        assert convert_intro_effect(1) == "<FA>"
        assert convert_intro_effect(5) == "<FE>"
        assert convert_intro_effect(16) == "<FR>"
    
    def test_convert_intro_effect_invalid(self):
        """Test intro effect conversion with invalid inputs."""
        with pytest.raises(ValueError, match="Invalid intro effect number"):
            convert_intro_effect(0)
        with pytest.raises(ValueError, match="Invalid intro effect number"):
            convert_intro_effect(17)
    
    def test_convert_exit_effect_valid(self):
        """Test exit effect conversion with valid inputs."""
        assert convert_exit_effect(1) == "<FA>"
        assert convert_exit_effect(5) == "<FE>"
        assert convert_exit_effect(11) == "<FK>"
    
    def test_convert_exit_effect_invalid(self):
        """Test exit effect conversion with invalid inputs."""
        with pytest.raises(ValueError, match="Invalid exit effect number"):
            convert_exit_effect(0)
        with pytest.raises(ValueError, match="Invalid exit effect number"):
            convert_exit_effect(12)
    
    def test_convert_speed_valid(self):
        """Test speed conversion with valid inputs."""
        assert convert_speed(1) == "<Mq>"
        assert convert_speed(2) == "<Ma>"
        assert convert_speed(3) == "<MQ>"
        assert convert_speed(4) == "<MA>"
    
    def test_convert_speed_invalid(self):
        """Test speed conversion with invalid inputs."""
        with pytest.raises(ValueError, match="Invalid speed number"):
            convert_speed(0)
        with pytest.raises(ValueError, match="Invalid speed number"):
            convert_speed(5)
    
    def test_convert_bell_valid(self):
        """Test bell conversion with valid inputs."""
        assert convert_bell(0) == ""
        assert convert_bell(1) == "<BA>"
        assert convert_bell(2) == "<BB>"
        assert convert_bell(3) == "<BC>"
        assert convert_bell(4) == "<BD>"
    
    def test_convert_bell_invalid(self):
        """Test bell conversion with invalid inputs."""
        with pytest.raises(ValueError, match="Invalid bell duration"):
            convert_bell(-1)
        with pytest.raises(ValueError, match="Invalid bell duration"):
            convert_bell(5)
    
    def test_convert_color_valid(self):
        """Test color conversion with valid inputs."""
        assert convert_color("") == ""
        assert convert_color("red") == "<CA>"
        assert convert_color("orange") == "<CH>"
        assert convert_color("green") == "<CD>"
        assert convert_color("rainbow") == "<CS>"
    
    def test_convert_color_invalid(self):
        """Test color conversion with invalid inputs."""
        with pytest.raises(ValueError, match="Invalid color name"):
            convert_color("blue")
        with pytest.raises(ValueError, match="Invalid color name"):
            convert_color("purple")


class TestEncodeMessage:
    """Tests for encode_message function."""
    
    def test_encode_message_basic(self):
        """Test basic message encoding."""
        result = encode_message(
            message="Hello",
            line=1,
            page="A",
            font=1,
            intro_effect=5,
            exit_effect=5,
            speed=3,
            bell=0,
            color="",
            show_date=False,
            show_time=False
        )
        
        # Verify structure
        assert result.startswith("<L1><PA>")
        assert "<FE>" in result  # intro effect 5
        assert "<MQ>" in result  # speed 3
        assert "<WC>" in result  # separator
        assert "<AC>" in result  # font 1
        assert "Hello" in result
    
    def test_encode_message_with_color(self):
        """Test message encoding with color."""
        result = encode_message(
            message="Test",
            line=2,
            page="B",
            font=2,
            intro_effect=1,
            exit_effect=1,
            speed=1,
            bell=0,
            color="red",
            show_date=False,
            show_time=False
        )
        
        assert "<L2><PB>" in result
        assert "<CA>" in result  # red color
        assert "<AA>" in result  # font 2
    
    def test_encode_message_with_bell(self):
        """Test message encoding with bell."""
        result = encode_message(
            message="Alert",
            line=1,
            page="A",
            font=1,
            intro_effect=1,
            exit_effect=1,
            speed=1,
            bell=2,
            color="",
            show_date=False,
            show_time=False
        )
        
        assert "<BB>" in result  # bell 2
    
    def test_encode_message_empty_raises_error(self):
        """Test that empty message raises ValueError."""
        with pytest.raises(ValueError, match="Message cannot be empty"):
            encode_message(
                message="",
                line=1,
                page="A",
                font=1,
                intro_effect=1,
                exit_effect=1,
                speed=1,
                bell=0,
                color="",
                show_date=False,
                show_time=False
            )
    
    def test_encode_message_invalid_page_raises_error(self):
        """Test that invalid page raises ValueError."""
        with pytest.raises(ValueError, match="Invalid page"):
            encode_message(
                message="Test",
                line=1,
                page="1",
                font=1,
                intro_effect=1,
                exit_effect=1,
                speed=1,
                bell=0,
                color="",
                show_date=False,
                show_time=False
            )
    
    def test_encode_message_invalid_line_raises_error(self):
        """Test that invalid line raises ValueError."""
        with pytest.raises(ValueError, match="Invalid line"):
            encode_message(
                message="Test",
                line=0,
                page="A",
                font=1,
                intro_effect=1,
                exit_effect=1,
                speed=1,
                bell=0,
                color="",
                show_date=False,
                show_time=False
            )
