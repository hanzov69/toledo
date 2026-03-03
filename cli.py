"""
Command-line interface module for toledo.

This module provides the CLI entry point and argument parsing for the toledo tool.
"""

import sys
import getopt
from typing import List, Optional, Dict, Any

# Import the public API
from . import send_message, send_raw_command, link_pages, __version__


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entry point for CLI.
    
    Parses arguments and executes appropriate commands.
    
    Args:
        argv: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    if argv is None:
        argv = sys.argv[1:]
    
    try:
        config = parse_arguments(argv)
        
        # Handle special commands that exit immediately
        if config.get("help"):
            print_usage()
            return 0
        
        if config.get("version"):
            print_version()
            return 0
        
        # Handle stdout mode (print command without sending)
        if config.get("stdout"):
            # Import protocol functions for stdout mode
            from . import encode_message, calculate_checksum, format_final_message, encode_link_command
            
            if config.get("link"):
                link_command = encode_link_command(config["link"])
                checksum = calculate_checksum(link_command)
                final_message = format_final_message(link_command, checksum, config["sign_id"])
                print(final_message)
            elif config.get("raw"):
                checksum = calculate_checksum(config["raw"])
                final_message = format_final_message(config["raw"], checksum, config["sign_id"])
                print(final_message)
            elif config.get("runpage"):
                from . import encode_run_page_command
                run_command = encode_run_page_command(config["runpage"])
                checksum = calculate_checksum(run_command)
                final_message = format_final_message(run_command, checksum, config["sign_id"])
                print(final_message)
            else:
                inner_message = encode_message(
                    message=config["message"],
                    line=config["line"],
                    page=config["page"],
                    font=config["font"],
                    intro_effect=config["intro_effect"],
                    exit_effect=config["exit_effect"],
                    speed=config["speed"],
                    bell=config["bell"],
                    color=config["color"],
                    show_date=config["show_date"],
                    show_time=config["show_time"]
                )
                checksum = calculate_checksum(inner_message)
                final_message = format_final_message(inner_message, checksum, config["sign_id"])
                print(final_message)
            return 0
        
        # Handle link command
        if config.get("link"):
            response = link_pages(
                page_sequence=config["link"],
                port=config["port"],
                sign_id=config["sign_id"]
            )
            if response:
                print(response)
            return 0
        
        # Handle raw command
        if config.get("raw"):
            response = send_raw_command(
                command=config["raw"],
                port=config["port"],
                sign_id=config["sign_id"]
            )
            if response:
                print(response)
            return 0
        
        # Handle runpage command
        if config.get("runpage"):
            from . import encode_run_page_command
            run_command = encode_run_page_command(config["runpage"])
            response = send_raw_command(
                command=run_command,
                port=config["port"],
                sign_id=config["sign_id"]
            )
            if response:
                print(response)
            return 0
        
        # Handle regular message sending
        if config.get("output"):
            if not config.get("message") or config["message"] == "snicklfritz982342":
                print("Error: Message must be specified with -m or --message")
                return 1
            
            response = send_message(
                message=config["message"],
                port=config["port"],
                line=config["line"],
                page=config["page"],
                font=config["font"],
                intro_effect=config["intro_effect"],
                exit_effect=config["exit_effect"],
                speed=config["speed"],
                bell=config["bell"],
                color=config["color"],
                show_date=config["show_date"],
                show_time=config["show_time"],
                sign_id=config["sign_id"]
            )
            if response:
                print(response)
            return 0
        
        # If no action specified, just return success
        return 0
        
    except getopt.GetoptError as e:
        print(f"Error: {e}")
        print_usage()
        return 2
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


def parse_arguments(argv: List[str]) -> Dict[str, Any]:
    """
    Parse command-line arguments into configuration dictionary.
    
    Args:
        argv: Command-line arguments
        
    Returns:
        Dictionary of parsed configuration
        
    Raises:
        getopt.GetoptError: If invalid arguments are provided
    """
    # Set up defaults (matching original toledo.py)
    config = {
        "port": "COM7",
        "message": "snicklfritz982342",
        "line": 1,
        "font": 1,
        "intro_effect": 5,
        "exit_effect": 5,
        "speed": 3,
        "bell": 0,
        "color": "",
        "show_date": False,
        "show_time": False,
        "link": None,
        "page": "A",
        "runpage": None,
        "sign_id": "00",
        "raw": None,
        "output": False,
        "debug": False,
        "stdout": False,
        "help": False,
        "version": False,
    }
    
    # Parse command-line options
    short_opts = "hnsvof:s:l:m:p:c:"
    long_opts = [
        "help", "stdout", "raw=", "version", "output", "font=", "sid=",
        "line=", "message=", "port=", "intro=", "exit=", "speed=",
        "bell=", "color=", "date", "time", "link=", "page=", "runpage=", "debug"
    ]
    
    opts, args = getopt.getopt(argv, short_opts, long_opts)
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            config["help"] = True
        elif opt in ("-n", "--stdout"):
            config["stdout"] = True
        elif opt == "--raw":
            config["raw"] = arg
        elif opt in ("-v", "--version"):
            config["version"] = True
        elif opt == "--debug":
            config["debug"] = True
            print("set debugging ON")
        elif opt in ("-f", "--font"):
            config["font"] = int(arg)
        elif opt == "--intro":
            config["intro_effect"] = int(arg)
        elif opt == "--exit":
            config["exit_effect"] = int(arg)
        elif opt == "--speed":
            config["speed"] = int(arg)
        elif opt == "--bell":
            config["bell"] = int(arg)
        elif opt in ("-c", "--color"):
            config["color"] = arg
        elif opt == "--date":
            config["show_date"] = True
            if config["debug"]:
                print("adding date")
        elif opt == "--time":
            config["show_time"] = True
            if config["debug"]:
                print("adding time")
        elif opt == "--link":
            config["link"] = arg
        elif opt == "--page":
            config["page"] = arg
        elif opt == "--runpage":
            config["runpage"] = arg
        elif opt in ("-p", "--port"):
            config["port"] = arg
        elif opt in ("-s", "--sid"):
            config["sign_id"] = arg
        elif opt in ("-l", "--line"):
            config["line"] = int(arg)
        elif opt in ("-m", "--message"):
            config["message"] = arg
        elif opt in ("-o", "--output"):
            config["output"] = True
    
    return config


def print_usage() -> None:
    """Print help text."""
    print("")
    print(f"toledo version {__version__}")
    print("-------------------------------------------------------------------------")
    print(" Always use flags --message and --output last")
    print("-------------------------------------------------------------------------")
    print("")
    print("-h (--help)       This screen")
    print("-v (--version)    Show toledo version")
    print("-p (--port=)      Set the port for use (default COM7)")
    print("-d (--debug)      Enable debug mode (verbose, call this flag first)")
    print("-s (--sid=)       Which Sign ID is in use (default 00)")
    print("   --intro=       Set the intro effect (1-16)")
    print("   --exit=        Set the exit effect (1-11)")
    print("   --bell=        Add a noise to your sign (0-4)")
    print("   --speed=       Set the movement speed (1-4)")
    print("-f (--font=)      Set the font used (1-5)")
    print("-c (--color=)     Set color on supported boards (red, green, orange,")
    print("                    ired, igreen, iorange, rog, gor, rainbow)")
    print("                                     ")
    print("    --page=       Which page to program (A-Z)")
    print("    --runpage=    Run which programmed page (A-Z) (non-functional)")
    print("    --link=       Run which pages in which order (A-Z)")
    print("-l (--line=)      Specify line to program, on supported boards (default 1)")
    print("    --raw=        Send protocol specific commands")
    print("                    Include the FULL string to send, everything between")
    print("                    <IDn> and XOR checksum")
    print("-m (--message=)   Set the desired message (call this flag before output)")
    print("-o (--output)     Output to sign (call this flag last)")
    print("-n (--stdout)     Only print command, no serial connection")
    print("")
    print("-------------------------------------------------------------------------")
    print('example: toledo --link="ABACAB" --output')
    print('example: toledo -p "COM7" -m "Holy Toledo" -o')
    print('example: toledo --intro="1" --exit="5" --speed="2" --page="B"')
    print('          --line="2" --message="Holy Toledo" --output')
    print("")


def print_version() -> None:
    """Print version information."""
    print(f"toledo version {__version__}")


if __name__ == "__main__":
    sys.exit(main())
