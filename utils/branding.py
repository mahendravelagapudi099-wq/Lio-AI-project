import sys

def show_banner():
    """
    Displays a terminal-only ASCII startup banner for Leo.
    Fails silently if anything goes wrong or if dependencies are missing.
    """
    try:
        # Check if we are in a terminal
        if not sys.stdout.isatty():
            return

        class Colors:
            RESET = '\033[0m'
            CORAL = '\033[38;5;209m' # Coral/salmon color
            BOLD = '\033[1m'

        banner = f"""{Colors.BOLD}{Colors.CORAL}
 ██╗      ███████╗ ██████╗      █████╗ ███████╗███████╗██╗███████╗████████╗ █████╗ ███╗   ██╗████████╗
 ██║      ██╔════╝██╔═══██╗    ██╔══██╗██╔════╝██╔════╝██║██╔════╝╚══██╔══╝██╔══██╗████╗  ██║╚══██╔══╝
 ██║      █████╗  ██║   ██║    ███████║███████╗███████╗██║███████╗   ██║   ███████║██╔██╗ ██║   ██║   
 ██║      ██╔══╝  ██║   ██║    ██╔══██║╚════██║╚════██║██║╚════██║   ██║   ██╔══██║██║╚██╗██║   ██║   
 ███████╗ ███████╗╚██████╔╝    ██║  ██║███████║███████║██║███████║   ██║   ██║  ██║██║ ╚████║   ██║   
 ╚══════╝ ╚══════╝ ╚═════╝     ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   
{Colors.RESET}"""
        
        print(banner)

    except Exception:
        # Guaranteed silence on failure
        pass

if __name__ == "__main__":
    show_banner()
