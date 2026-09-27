#!/usr/bin/env python3

import os
import sys
import json
import shlex
import getpass
import tempfile
import subprocess
import time
import select
import tty
import termios

CAT_FRAMES = []
_campy_frames = [
    "  /\\_____/\\  \n /  o   o  \\ \n(  == ^ ==  )\n \\  '-'  /  \n (__)  (__) \n            ",
    "  /\\_____/\\  \n /  -   -  \\ \n(  == ^ ==  )\n \\  '-'  /  \n (__)  (__) \n            ",
    "  /\\_____/\\  \n /  ^   ^  \\ \n(  == ω ==  )\n \\  '-'  /  \n (__)  (__) \n            ",
    "  /\\_____/\\  \n /  ^   ^  \\ \n(  == ω ==  )\n \\  '-'  /  \n  | ♥ |    \n (__) (__)  ",
]
def _add_cat(idx, count):
    for _ in range(count):
        CAT_FRAMES.append(_campy_frames[idx])
_add_cat(0, 20)
_add_cat(1, 2)
_add_cat(0, 5)
_add_cat(2, 5)
_add_cat(3, 8)
_add_cat(2, 5)

try:
    import pypdf
except ImportError:
    print("Error: pypdf is not installed. Please run: pip3 install pypdf")
    sys.exit(1)

try:
    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.status import Status
    from rich.live import Live
    from rich.text import Text
    from rich.theme import Theme
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import print as rprint
    from rich.align import Align
    from rich.table import Table
except ImportError:
    print("Error: rich is not installed. Please run: pip3 install rich")
    sys.exit(1)

custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "danger": "bold red",
    "success": "bold green",
})
console = Console(theme=custom_theme)

CONFIG_DIR = os.path.expanduser("~/.config/socprint")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return None

def save_config(username, password):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"username": username, "password": password}, f)
    os.chmod(CONFIG_FILE, 0o600)

def run_command(cmd, text, timeout=30):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    idx = 0
    with Live(refresh_per_second=10, console=console) as live:
        while process.poll() is None:
            cat = CAT_FRAMES[idx % len(CAT_FRAMES)]
            table = Table.grid(expand=True)
            table.add_column("Text", justify="left", ratio=1, vertical="middle")
            table.add_column("Donut", justify="left", vertical="middle")
            table.add_row(f"[bold cyan]{text}...[/]", Text(cat, style="yellow", justify="left"))
            live.update(Panel(table, border_style="cyan", padding=(1, 2)))
            idx += 1
            time.sleep(0.1)
    
    out, err = process.communicate()
    class CommandResult:
        def __init__(self, returncode, stdout, stderr):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr
            
    return CommandResult(process.returncode, out.decode('utf-8', 'ignore'), err.decode('utf-8', 'ignore'))

def verify_credentials(username, password):
    ssh_user = username.split('@')[0]
    ssh_host = "stu.comp.nus.edu.sg"
    
    expect_script = f"""
log_user 0
set timeout 15
spawn ssh -o StrictHostKeyChecking=no {ssh_user}@{ssh_host} "echo VERIFIED"
expect {{
    "assword:" {{
        send "$env(SSH_PASS)\\r"
        expect {{
            "VERIFIED" {{ exit 0 }}
            "denied" {{ exit 1 }}
            "Permission denied" {{ exit 1 }}
            timeout {{ exit 2 }}
        }}
    }}
    "VERIFIED" {{ exit 0 }}
    timeout {{ exit 2 }}
}}
"""
    env = os.environ.copy()
    env["SSH_PASS"] = password
    process = subprocess.Popen(['/usr/bin/expect', '-c', expect_script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    
    idx = 0
    console.print()
    with Live(refresh_per_second=10, console=console) as live:
        while process.poll() is None:
            cat = CAT_FRAMES[idx % len(CAT_FRAMES)]
            table = Table.grid(expand=True)
            table.add_column("Text", justify="left", ratio=1, vertical="middle")
            table.add_column("Donut", justify="left", vertical="middle")
            table.add_row(f"[bold cyan]Verifying credentials...[/]", Text(cat, style="yellow", justify="left"))
            live.update(Panel(table, border_style="cyan", padding=(1, 2)))
            idx += 1
            time.sleep(0.1)
            
    return process.returncode == 0

def setup_wizard():
    while True:
        console.clear()
        username = get_input_animated(
            prompt_prefix="[bold blue]❯[/bold blue] [bold]SoC Email / Username:[/bold]",
            title="[bold magenta]Welcome to SoC Print CLI[/bold magenta]",
            subtitle="[dim]Please enter your NUS SoC credentials to continue.[/dim]\n[dim](e.g. username@stu.comp.nus.edu.sg)[/dim]"
        ).strip()
        
        if not username:
            console.print("[danger]Username cannot be empty.[/danger]")
            time.sleep(1.5)
            continue
            
        if "@" in username and not username.endswith("@stu.comp.nus.edu.sg"):
            console.print("[danger]Please use your @stu.comp.nus.edu.sg email, or just enter your username.[/danger]")
            time.sleep(1.5)
            continue
            
        break
    
    console.clear()
    password = get_input_animated(
        prompt_prefix="[bold blue]❯[/bold blue] [bold]Password:[/bold]",
        title="[bold magenta]Welcome to SoC Print CLI[/bold magenta]",
        subtitle="[dim]Please enter your NUS SoC credentials to continue.[/dim]",
        is_password=True
    )
    
    if not password:
        console.print("[danger]Password cannot be empty.[/danger]")
        sys.exit(1)
        
    console.clear()
    if not verify_credentials(username, password):
        console.print("[danger]Authentication failed! Please check your username and password.[/danger]")
        time.sleep(2)
        sys.exit(1)
        
    save_config(username, password)
    console.print("[success]✔ Credentials verified and securely saved.[/success]\n")
    
    with console.status("[cyan]Configuring environment...[/cyan]", spinner="dots"):
        ssh_user = username.split('@')[0]
        ssh_host = "stu.comp.nus.edu.sg"
        script_path = os.path.abspath(__file__)
        
        if sys.platform == "win32":
            pub_key = os.path.expanduser("~/.ssh/id_rsa.pub")
            if not os.path.exists(pub_key): pub_key = os.path.expanduser("~/.ssh/id_ed25519.pub")
            if os.path.exists(pub_key):
                with open(pub_key, "r") as f: key_data = f.read().strip()
                os.system(f'ssh {ssh_user}@{ssh_host} "mkdir -p ~/.ssh && echo {key_data} >> ~/.ssh/authorized_keys"')
            
            ps_profile_dir = os.path.expanduser("~/Documents/WindowsPowerShell")
            os.makedirs(ps_profile_dir, exist_ok=True)
            ps_profile = os.path.join(ps_profile_dir, "Microsoft.PowerShell_profile.ps1")
            try:
                with open(ps_profile, "r") as f: content = f.read()
            except FileNotFoundError: content = ""
            if "function socprinter" not in content:
                with open(ps_profile, "a") as f: f.write(f"\nfunction socprinter {{ python '{script_path}' }}\n")
            
            try:
                wrapper = os.path.join(os.path.dirname(script_path), "socprinter.bat")
                with open(wrapper, "w") as f: f.write(f'@echo off\npython "{script_path}" %*')
            except Exception: pass
        else:
            os.system(f"ssh-copy-id {ssh_user}@{ssh_host} >/dev/null 2>&1")
            
            shells = [
                ("~/.zshrc", f'\nalias socprinter="python3 {script_path}"\n'),
                ("~/.bashrc", f'\nalias socprinter="python3 {script_path}"\n'),
                ("~/.bash_profile", f'\nalias socprinter="python3 {script_path}"\n'),
                ("~/.config/fish/config.fish", f'\nalias socprinter="python3 {script_path}"\n')
            ]
            for shell_file, alias_str in shells:
                path = os.path.expanduser(shell_file)
                if os.path.exists(path):
                    try:
                        with open(path, "r") as f: content = f.read()
                        if "socprinter=" not in content:
                            with open(path, "a") as f: f.write(alias_str)
                    except Exception: pass
        
    console.print(Panel(
        "✔ Installed [bold cyan]socprinter[/bold cyan] terminal alias / wrapper script\n"
        "✔ Configured SSH keys for passwordless printing to SoC queues\n\n"
        "You can now simply type [bold]socprinter[/bold] from any folder to launch this app.",
        title="[bold green]System Integration Complete[/bold green]",
        border_style="green",
        padding=(1, 2)
    ))
    time.sleep(3.5)
    
    return username, password

def get_printer_selection():
    console.print(Panel(
        "1) PSTS   (B&W Duplex) [green][DEFAULT][/green]\n"
        "2) PSTSB  (B&W Duplex)\n"
        "3) PSTSC  (B&W Duplex)\n"
        "4) PSTS   (Color Duplex)\n"
        "5) Custom / Other",
        title="[bold cyan]Select Printer[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    ))
    console.print()
    choice = Prompt.ask("[bold]Enter choice[/bold]", choices=["1", "2", "3", "4", "5", ""], default="1", show_default=False)
    
    if choice == '2':
        return "pstsb-nb", "PSTSB (B&W Duplex)"
    elif choice == '3':
        return "pstsc-nb", "PSTSC (B&W Duplex)"
    elif choice == '4':
        return "psts", "PSTS (Color Duplex)"
    elif choice == '5':
        custom = Prompt.ask("Enter custom printer queue name").strip()
        return custom, custom
    else:
        return "psts-nb", "PSTS (B&W Duplex)"

def merge_pdfs(pdf_list, output_path):
    with console.status(f"[cyan]Merging {len(pdf_list)} PDFs...[/cyan]", spinner="dots"):
        merger = pypdf.PdfWriter()
        old_stderr = os.dup(2)
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, 2)
        os.close(devnull)
        try:
            for pdf in pdf_list:
                merger.append(pdf)
            merger.write(output_path)
        finally:
            os.dup2(old_stderr, 2)
            os.close(old_stderr)

def get_input_animated(prompt_prefix, title, subtitle, is_password=False):
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    user_input = []
    idx = 0
    
    with Live(refresh_per_second=10, console=console) as live:
        try:
            tty.setcbreak(fd)
            while True:
                cat = CAT_FRAMES[idx % len(CAT_FRAMES)]
                display_str = "*" * len(user_input) if is_password else "".join(user_input)
                
                table = Table.grid(expand=True)
                table.add_column("Text", justify="left", ratio=1, vertical="middle")
                table.add_column("Donut", justify="left", vertical="middle")
                table.add_row(subtitle, Text(cat, style="yellow", justify="left"))
                
                content = Group(
                    table,
                    "",
                    f"{prompt_prefix} {display_str}"
                )
                
                live.update(Panel(
                    content,
                    title=title,
                    border_style="blue",
                    padding=(1, 2)
                ))
                
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    char = sys.stdin.read(1)
                    if char == '\n' or char == '\r':
                        break
                    elif char in ('\b', '\x7f'): 
                        if user_input:
                            user_input.pop()
                    elif char == '\x03': # Ctrl+C
                        raise KeyboardInterrupt()
                    elif char == '\x04': # Ctrl+D
                        break
                    else:
                        user_input.append(char)
                else:
                    idx += 1
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
    # Reprint final state properly so it persists in the scrollback buffer
    cat = CAT_FRAMES[idx % len(CAT_FRAMES)]
    final_str = "".join(user_input)
    display_str = "*" * len(user_input) if is_password else final_str
    
    table = Table.grid(expand=True)
    table.add_column("Text", justify="left", ratio=1, vertical="middle")
    table.add_column("Donut", justify="left", vertical="middle")
    table.add_row(subtitle, Text(cat, style="yellow", justify="left"))
    
    content = Group(
        table,
        "",
        f"{prompt_prefix} {display_str}"
    )
    
    console.print(Panel(
        content,
        title=title,
        border_style="blue",
        padding=(1, 2)
    ))
    return final_str

def main():
    cfg = load_config()
    if not cfg:
        username, password = setup_wizard()
    else:
        username = cfg.get("username")
        password = cfg.get("password")
        if not username or not password:
            username, password = setup_wizard()
    
    ssh_host = "stu.comp.nus.edu.sg"
    ssh_user = username.split('@')[0]
    
    auto = False
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == 'reset':
            try: os.remove(CONFIG_FILE)
            except: pass
            console.clear()
            console.print("[success]Signed out successfully. Run 'socprinter' again to log in.[/success]")
            return
        
        auto = "--auto" in sys.argv
        paths_input = " ".join(shlex.quote(f) for f in sys.argv[1:] if f != "--auto")
    else:
        # STEP 1: Main input screen
        console.clear()
        
        paths_input = get_input_animated(
            prompt_prefix="[bold blue]❯[/bold blue] [bold]Drag and drop PDF file(s) here:[/bold]",
            title="[bold blue]SoC Print Manager[/bold blue]",
            subtitle=f"[dim]Logged in as [bold]{username}[/bold] — type 'reset' to sign out[/dim]\n[dim]AI Agents: run [cyan]socprinter <file> --auto[/cyan] to print silently[/dim]"
        ).strip()
        console.print()
        
        if paths_input.lower() == 'reset':
            try: os.remove(CONFIG_FILE)
            except: pass
            console.clear()
            console.print("[success]Signed out successfully. Run 'socprinter' again to log in.[/success]")
            return
        
    if not paths_input:
        console.print("[warning]No files provided.[/warning]")
        return
        
    try:
        files = shlex.split(paths_input)
    except ValueError as e:
        console.print(f"[danger]Error parsing paths: {e}[/danger]")
        return
        
    valid_files = []
    for f in files:
        clean_f = f.strip().strip("'").strip('"')
        if os.path.isfile(clean_f) and clean_f.lower().endswith(".pdf"):
            valid_files.append(clean_f)
            
    if not valid_files:
        console.print("[danger]No valid PDF files found.[/danger]")
        return
        
    # STEP 2: Selection & Printer Settings Screen
    if not auto:
        console.clear()
        file_list_text = "\n".join([f"[cyan]• {os.path.basename(f)}[/cyan]" for f in valid_files])
        console.print(Panel(file_list_text, title="[bold blue]Selected Files[/bold blue]", border_style="blue", padding=(1, 2)))
        console.print()
        
        if not Confirm.ask("Proceed with printing?"):
            console.clear()
            console.print("[warning]Job Cancelled.[/warning]")
            return
            
        console.print()
        printer, printer_desc = get_printer_selection()
    else:
        printer, printer_desc = "psts-nb", "PSTS (B&W Duplex)"
    
    # STEP 3: Execution Screen
    console.clear()
    console.print(Panel(
        f"[bold]Printer:[/] {printer_desc} ({printer})\n"
        f"[bold]Files:[/] {len(valid_files)} document(s)",
        title="[bold cyan]Processing Print Job[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    ))
    console.print()
    
    timestamp = int(time.time())
    final_pdf = None
    
    if len(valid_files) > 1:
        fd, final_pdf = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        merge_pdfs(valid_files, final_pdf)
        pdf_to_send = final_pdf
    else:
        pdf_to_send = valid_files[0]
        
    remote_pdf = f"/tmp/socprint_{timestamp}.pdf"
    
    scp_cmd = f"scp -q {shlex.quote(pdf_to_send)} {ssh_user}@{ssh_host}:{remote_pdf}"
    res = run_command(scp_cmd, f"Uploading to {ssh_host}")
    
    if res and res.returncode != 0:
        console.print(f"[danger]Upload failed: {res.stderr}[/danger]")
        if final_pdf: os.remove(final_pdf)
        return
            
    lpr_cmd = f"ssh {ssh_user}@{ssh_host} 'lpr -P{printer} {remote_pdf} && lpq -P{printer} ; rm -f {remote_pdf}'"
    res = run_command(lpr_cmd, f"Submitting to queue '{printer}'")
        
    # STEP 4: Success Screen
    console.clear()
    if res and res.returncode == 0:
        console.print(Panel(
            res.stdout.strip(), 
            title="[bold green]Print Job Success[/bold green]", 
            border_style="green",
            padding=(1, 2)
        ))
    else:
        console.print(f"[danger]Failed to print![/danger]")
        if res: console.print(res.stderr.strip())
        
    if final_pdf:
        try: os.remove(final_pdf)
        except: pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[warning]Cancelled by user.[/warning]")
        sys.exit(0)
