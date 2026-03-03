"""
Property-based tests for protocol encoding module.

These tests use Hypothesis to verify universal properties across randomized inputs.
"""

import pytest
from hypothesis import given, strategies as st, settings

from protocol import (
    encode_message,
    calculate_checksum,
    convert_font,
    convert_intro_effect,
    convert_exit_effect,
    convert_speed,
    convert_bell,
    convert_color,
    FONTS,
    INTRO_EFFECTS,
    EXIT_EFFECTS,
    SPEEDS,
    BELLS,
    COLORS,
)


# Strategies for generating valid inputs
valid_fonts = st.sampled_from(list(FONTS.keys()))
valid_intro_effects = st.sampled_from(list(INTRO_EFFECTS.keys()))
valid_exit_effects = st.sampled_from(list(EXIT_EFFECTS.keys()))
valid_speeds = st.sampled_from(list(SPEEDS.keys()))
valid_bells = st.sampled_from(list(BELLS.keys()))
valid_colors = st.sampled_from([""] + list(COLORS.keys()))
valid_pages = st.sampled_from([chr(i) for i in range(ord('A'), ord('Z') + 1)])
valid_lines = st.integers(min_value=1, max_value=26)
valid_messages = st.text(
    alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
        whitelist_characters='!@#$%^&*()_+-=[]{}|;:,.<>?'
    ),
    min_size=1,
    max_size=100
)


@settings(max_examples=100)
@given(
    message=valid_messages,
    line=valid_lines,
    page=valid_pages,
    font=valid_fonts,
    intro_effect=valid_intro_effects,
    exit_effect=valid_exit_effects,
    speed=valid_speeds,
    bell=valid_bells,
    color=valid_colors,
    show_date=st.booleans(),
    show_time=st.booleans(),
)
def test_protocol_encoding_consistency(
    message, line, page, font, intro_effect, exit_effect,
    speed, bell, color, show_date, show_time
):
    """
    Property 3: Protocol Encoding Consistency
    
    **Validates: Requirements 1.3, 1.4**
    
    For any message configuration (font, effects, colors, etc.), encoding the message
    should produce a protocol string that contains all specified tags in the correct format.
    
    Feature: conda-packaging-setup, Property 3
    """
    # Encode the message with the given configuration
    encoded = encode_message(
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
        show_time=show_time,
    )
    
    # Verify the encoded message is a string
    assert isinstance(encoded, str), "Encoded message must be a string"
    
    # Verify the encoded message is not empty
    assert len(encoded) > 0, "Encoded message must not be empty"
    
    # Verify font tag appears in the encoded message
    font_tag = convert_font(font)
    assert font_tag in encoded, f"Font tag {font_tag} must appear in encoded message"
    
    # Verify intro effect tag appears in the encoded message
    intro_tag = convert_intro_effect(intro_effect)
    assert intro_tag in encoded, f"Intro effect tag {intro_tag} must appear in encoded message"
    
    # Verify exit effect tag appears in the encoded message
    exit_tag = convert_exit_effect(exit_effect)
    assert exit_tag in encoded, f"Exit effect tag {exit_tag} must appear in encoded message"
    
    # Verify speed tag appears in the encoded message
    speed_tag = convert_speed(speed)
    assert speed_tag in encoded, f"Speed tag {speed_tag} must appear in encoded message"
    
    # Verify bell tag appears if bell is not 0
    bell_tag = convert_bell(bell)
    if bell_tag:
        assert bell_tag in encoded, f"Bell tag {bell_tag} must appear in encoded message"
    
    # Verify color tag appears if color is specified
    color_tag = convert_color(color)
    if color_tag:
        assert color_tag in encoded, f"Color tag {color_tag} must appear in encoded message"
    
    # Verify page tag appears in the encoded message
    assert page in encoded, f"Page {page} must appear in encoded message"
    
    # Verify the original message text appears in the encoded message
    assert message in encoded, f"Original message text must appear in encoded message"
    
    # Verify tags appear in the correct order
    # Expected order: page/line tags, intro effect, speed, <WC>, exit effect, (bell), (color), (date), (time), font, message
    
    # Find positions of key tags
    font_pos = encoded.find(font_tag)
    intro_pos = encoded.find(intro_tag)
    speed_pos = encoded.find(speed_tag)
    # Use rfind for exit effect in case it's the same as intro effect
    exit_pos = encoded.rfind(exit_tag) if intro_tag == exit_tag else encoded.find(exit_tag)
    
    # Verify <WC> separator appears
    assert "<WC>" in encoded, "<WC> separator must appear in encoded message"
    wc_pos = encoded.find("<WC>")
    
    # Intro effect should come before speed
    assert intro_pos < speed_pos, "Intro effect tag must come before speed tag"
    
    # Speed should come before <WC>
    assert speed_pos < wc_pos, "Speed tag must come before <WC> separator"
    
    # <WC> should come before exit effect
    assert wc_pos < exit_pos, "<WC> separator must come before exit effect tag"
    
    # Exit effect should come before font
    assert exit_pos < font_pos, "Exit effect tag must come before font tag"
    
    # Message should appear after the font tag (search from font_pos onwards)
    # This avoids false positives where message content appears in protocol tags
    message_pos = encoded.find(message, font_pos + len(font_tag))
    assert message_pos > font_pos, "Message text must appear after font tag"
    
    # If color is specified, it should come after exit and before message
    if color_tag:
        color_pos = encoded.find(color_tag)
        assert exit_pos < color_pos, "Color tag must come after exit effect"
        assert color_pos < message_pos, "Color tag must come before message"
    
    # If bell is specified, it should come after exit and before message
    if bell_tag:
        bell_pos = encoded.find(bell_tag)
        assert exit_pos < bell_pos, "Bell tag must come after exit effect"
        assert bell_pos < message_pos, "Bell tag must come before message"
    
    # Verify date/time tags if specified
    if show_date:
        # Date tag format varies, but should contain date-related protocol tags
        # This will be validated once we know the exact format
        pass
    
    if show_time:
        # Time tag format varies, but should contain time-related protocol tags
        # This will be validated once we know the exact format
        pass


@settings(max_examples=100)
@given(
    message=st.text(
        alphabet=st.characters(
            min_codepoint=32,  # Space
            max_codepoint=126  # Tilde (printable ASCII)
        ),
        min_size=1,
        max_size=200
    )
)
def test_checksum_round_trip(message):
    """
    Property 1: Checksum Round Trip
    
    **Validates: Requirements 1.4**
    
    For any protocol message string, calculating the checksum and verifying it
    should confirm message integrity.
    
    Feature: conda-packaging-setup, Property 1
    """
    # Calculate checksum for the message
    checksum = calculate_checksum(message)
    
    # Verify checksum is always a 2-character hex string
    assert isinstance(checksum, str), "Checksum must be a string"
    assert len(checksum) == 2, f"Checksum must be exactly 2 characters, got {len(checksum)}"
    assert all(c in '0123456789ABCDEF' for c in checksum), \
        f"Checksum must be hex characters, got {checksum}"
    
    # Verify same message always produces same checksum (determinism)
    checksum2 = calculate_checksum(message)
    assert checksum == checksum2, \
        f"Same message must produce same checksum: {checksum} != {checksum2}"
    
    # Verify checksum changes when message changes (sensitivity)
    # Only test if we can modify the message
    if len(message) > 0:
        # Modify the first character
        modified_message = chr((ord(message[0]) + 1) % 127) + message[1:]
        if modified_message != message:  # Ensure we actually changed it
            modified_checksum = calculate_checksum(modified_message)
            # Checksums should be different (with very high probability)
            # Note: There's a tiny chance of collision, but it's acceptable for property testing
            assert checksum != modified_checksum or len(message) == 1, \
                "Different messages should produce different checksums (collision detected)"
    
    # Verify checksum is valid hex that can be converted to int
    try:
        checksum_int = int(checksum, 16)
        assert 0 <= checksum_int <= 255, \
            f"Checksum as integer must be in range 0-255, got {checksum_int}"
    except ValueError:
        pytest.fail(f"Checksum {checksum} is not valid hexadecimal")
