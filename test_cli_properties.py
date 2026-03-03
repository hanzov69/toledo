"""
Property-based tests for CLI backward compatibility.

These tests use Hypothesis to verify CLI backward compatibility across randomized inputs.
"""

import pytest
from hypothesis import given, strategies as st, settings
from io import StringIO
import sys

from protocol import (
    encode_message,
    calculate_checksum,
    encode_link_command,
    encode_run_page_command,
    FONTS,
    INTRO_EFFECTS,
    EXIT_EFFECTS,
    SPEEDS,
    BELLS,
    COLORS,
)
from core import format_final_message


# Strategies for generating valid CLI arguments
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
valid_sign_ids = st.text(
    alphabet=st.characters(whitelist_categories=('Nd',)),
    min_size=2,
    max_size=2
)
valid_ports = st.sampled_from(["COM7", "/dev/ttyUSB0", "/dev/tty.usbserial"])


def simulate_original_toledo(
    message, line, page, font, intro_effect, exit_effect,
    speed, bell, color, show_date, show_time, sign_id
):
    """
    Simulate the original toledo.py behavior to generate the expected message format.
    
    This function replicates the logic from the original toledo.py script
    to produce the same protocol message format.
    
    Args:
        message: The text message to display
        line: Line number (1-based)
        page: Page letter (A-Z)
        font: Font number (1-5)
        intro_effect: Intro effect number (1-16)
        exit_effect: Exit effect number (1-11)
        speed: Speed number (1-4)
        bell: Bell duration (0-4)
        color: Color name or "0" for no color
        show_date: Whether to show date
        show_time: Whether to show time
        sign_id: Sign ID (typically "00")
        
    Returns:
        The complete formatted message that the original script would produce
    """
    # Convert font
    font_map = {1: '<AC>', 2: '<AA>', 3: '<AB>', 4: '<AF>', 5: '<AD>'}
    font_tag = font_map[font]
    
    # Convert intro effect
    intro_map = {
        1: "<FA>", 2: "<FB>", 3: "<FC>", 4: "<FD>", 5: "<FE>",
        6: "<FF>", 7: "<FG>", 8: "<FH>", 9: "<FI>", 10: "<FJ>",
        11: "<FK>", 12: "<FL>", 13: "<FM>", 14: "<FN>", 15: "<FP>", 16: "<FR>"
    }
    intro_tag = intro_map[intro_effect]
    
    # Convert exit effect
    exit_map = {
        1: '<FA>', 2: '<FB>', 3: '<FC>', 4: '<FD>', 5: '<FE>',
        6: '<FF>', 7: '<FG>', 8: '<FH>', 9: '<FI>', 10: '<FJ>', 11: '<FK>'
    }
    exit_tag = exit_map[exit_effect]
    
    # Convert speed
    speed_map = {1: '<Mq>', 2: '<Ma>', 3: '<MQ>', 4: '<MA>'}
    speed_tag = speed_map[speed]
    
    # Convert bell
    bell_map = {0: '', 1: '<BA>', 2: '<BB>', 3: '<BC>', 4: '<BD>'}
    bell_tag = bell_map[bell]
    
    # Convert color
    color_map = {
        "": '', "red": "<CA>", "orange": "<CH>", "green": "<CD>",
        "iorange": "<CN>", "igreen": "<CM>", "ired": "<CL>",
        "rog": "<CP>", "gor": "<CQ>", "ryg": "<CR>", "rainbow": "<CS>"
    }
    color_tag = color_map[color]
    
    # Date and time flags
    date_tag = "<KD> " if show_date else ''
    time_tag = "<KT> " if show_time else ''
    
    # Build the inner message (matching original format)
    # Original format: "<L%s><P%s>%s%s<WC>%s%s%s%s%s%s%s" % 
    #                  (_line,_page,_iEffect,_speed,_eEffect,_bell,_color,_dFlag,_tFlag,_font,_message)
    inner_message = f"<L{line}><P{page}>{intro_tag}{speed_tag}<WC>{exit_tag}{bell_tag}{color_tag}{date_tag}{time_tag}{font_tag}{message}"
    
    # Calculate checksum (XOR of all characters)
    from functools import reduce
    from operator import xor
    checksum_value = reduce(xor, [ord(c) for c in inner_message])
    checksum = "%02X" % checksum_value
    
    # Build final message
    final_message = f"<ID{sign_id}>{inner_message}{checksum}<E>"
    
    return final_message


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
    sign_id=valid_sign_ids,
    port=valid_ports,
)
def test_cli_backward_compatibility(
    message, line, page, font, intro_effect, exit_effect,
    speed, bell, color, show_date, show_time, sign_id, port
):
    """
    Property 2: CLI Backward Compatibility
    
    **Validates: Requirements 1.5, 1.6**
    
    For any valid command-line invocation that worked in the original toledo.py,
    the refactored version should produce equivalent behavior (same message format
    sent to the sign).
    
    Feature: conda-packaging-setup, Property 2
    """
    # Generate the expected message using the original toledo.py logic
    expected_message = simulate_original_toledo(
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
        sign_id=sign_id
    )
    
    # Generate the message using the refactored implementation
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
    checksum = calculate_checksum(inner_message)
    actual_message = format_final_message(inner_message, checksum, sign_id)
    
    # Verify the messages are identical
    assert actual_message == expected_message, \
        f"Refactored implementation produces different message.\nExpected: {expected_message}\nActual: {actual_message}"
    
    # Verify message structure
    assert actual_message.startswith(f"<ID{sign_id}>"), \
        f"Message must start with sign ID tag"
    assert actual_message.endswith("<E>"), \
        f"Message must end with <E> tag"
    
    # Verify the message contains the original text
    assert message in actual_message, \
        f"Message must contain the original text: {message}"


@settings(max_examples=100)
@given(
    page_sequence=st.text(
        alphabet=st.characters(whitelist_categories=('Lu',), min_codepoint=65, max_codepoint=90),
        min_size=1,
        max_size=26
    ),
    sign_id=valid_sign_ids,
)
def test_cli_link_backward_compatibility(page_sequence, sign_id):
    """
    Property 2: CLI Backward Compatibility (Link Command)
    
    **Validates: Requirements 1.5, 1.6**
    
    For link commands, the refactored version should produce the same
    message format as the original toledo.py.
    
    Feature: conda-packaging-setup, Property 2
    """
    # Generate expected message using original logic
    # Original format: inMessage = "<TA>00010100009912302359%s" % (_link)
    inner_message = f"<TA>00010100009912302359{page_sequence}"
    
    # Calculate checksum (original method)
    from functools import reduce
    from operator import xor
    checksum_value = reduce(xor, [ord(c) for c in inner_message])
    checksum = "%02X" % checksum_value
    
    expected_message = f"<ID{sign_id}>{inner_message}{checksum}<E>"
    
    # Generate message using refactored implementation
    link_command = encode_link_command(page_sequence)
    actual_checksum = calculate_checksum(link_command)
    actual_message = format_final_message(link_command, actual_checksum, sign_id)
    
    # Verify the messages are identical
    assert actual_message == expected_message, \
        f"Refactored link command produces different message.\nExpected: {expected_message}\nActual: {actual_message}"


@settings(max_examples=100)
@given(
    page=valid_pages,
    sign_id=valid_sign_ids,
)
def test_cli_runpage_backward_compatibility(page, sign_id):
    """
    Property 2: CLI Backward Compatibility (Run Page Command)
    
    **Validates: Requirements 1.5, 1.6**
    
    For run page commands, the refactored version should produce the same
    message format as the original toledo.py.
    
    Feature: conda-packaging-setup, Property 2
    """
    # Generate expected message using original logic
    # Original format: inMessage = "<RP%s>" % (_runpage)
    inner_message = f"<RP{page}>"
    
    # Calculate checksum (original method)
    from functools import reduce
    from operator import xor
    checksum_value = reduce(xor, [ord(c) for c in inner_message])
    checksum = "%02X" % checksum_value
    
    expected_message = f"<ID{sign_id}>{inner_message}{checksum}<E>"
    
    # Generate message using refactored implementation
    run_command = encode_run_page_command(page)
    actual_checksum = calculate_checksum(run_command)
    actual_message = format_final_message(run_command, actual_checksum, sign_id)
    
    # Verify the messages are identical
    assert actual_message == expected_message, \
        f"Refactored run page command produces different message.\nExpected: {expected_message}\nActual: {actual_message}"


@settings(max_examples=100)
@given(
    raw_command=st.text(
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='<>='
        ),
        min_size=1,
        max_size=50
    ),
    sign_id=valid_sign_ids,
)
def test_cli_raw_backward_compatibility(raw_command, sign_id):
    """
    Property 2: CLI Backward Compatibility (Raw Command)
    
    **Validates: Requirements 1.5, 1.6**
    
    For raw commands, the refactored version should produce the same
    message format as the original toledo.py.
    
    Feature: conda-packaging-setup, Property 2
    """
    # Generate expected message using original logic
    # Original format: inMessage ="%s" % (_raw)
    inner_message = raw_command
    
    # Calculate checksum (original method)
    from functools import reduce
    from operator import xor
    checksum_value = reduce(xor, [ord(c) for c in inner_message])
    checksum = "%02X" % checksum_value
    
    expected_message = f"<ID{sign_id}>{inner_message}{checksum}<E>"
    
    # Generate message using refactored implementation
    actual_checksum = calculate_checksum(raw_command)
    actual_message = format_final_message(raw_command, actual_checksum, sign_id)
    
    # Verify the messages are identical
    assert actual_message == expected_message, \
        f"Refactored raw command produces different message.\nExpected: {expected_message}\nActual: {actual_message}"
