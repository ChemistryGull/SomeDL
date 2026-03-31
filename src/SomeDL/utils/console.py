import json
import time
import threading
from enum import Enum
import platform

from rich.live import Live
from rich.table import Table
from rich.spinner import Spinner
from rich.console import Group, Console
from rich.columns import Columns
from rich.text import Text
from rich.align import Align
from rich import box


active_items: dict[str, dict] = {}  # see active_items_test at the end of the file
thread_lock = threading.Lock()
live_display: Live = None           # set in main()
console = Console()                 # Used for console logs outside of live_display
timers = {}
global_log_level = 4

# Available status: Success, Not found, Failed, Skipped


# --- Use an enum for the status because funny
class Status(str, Enum):
    ACTIVE = "active"
    SUCCESS = "success"
    PART_SUCC = "part_succ"
    NOT_FOUND = "not_found"
    FAILED = "failed"
    SKIPPED = "skipped"
    HIDE = "hide"

characters = {
    "yes": "✔",
    "no": "✖",
}


# === Initialize live_display ===

def init_live(live) -> None:
    global live_display
    live_display = live

    if platform.system().lower() == "windows":
         # The others look better, but they dont work on fuckass windows
        characters["yes"] = "✓"
        characters["no"] = "×"

def clear_live(live) -> None:
    global live_display
    live_display = None

def update_log_level(lvl) -> None:
    global global_log_level
    global_log_level = lvl


# === Special logging ===

def printj(dic, sort_keys = True):
    print(json.dumps(dic, indent=4, sort_keys=sort_keys))

def tStart(name = "default"):
    timers[name] = time.time()

def tEnd(name = "default"):
    now = time.time()
    console.debug(f'\033[94mTIMER {name} = {now - timers.get(name, 0)} s\033[0m')

def log(message: str, label: str = None) -> None:
    # --- only used for testing, such message should not appear in production
    if label:
        out = f'[bright_black]{label}:[/] LOG - {message}'
    else:
        out = f'LOG - {message}'

    if live_display:
        live_display.console.print(out)
    else:
        console.print(out)


# === Logging function ===

def debug(message: str, label: str = None) -> None:
    if global_log_level < 7:
        return
    
    if label:
        out = f'[bright_black]{label}:[/] DEBUG - {message}'
    else:
        out = f'DEBUG - {message}'
    
    if live_display:
        live_display.console.print(out)
    else:
        console.print(out)

def info(message: str, label: str = None) -> None:
    if global_log_level < 6:
        return

    if label:
        out = f'[bright_black]{label}:[/] INFO - {message}'
    else:
        out = f'INFO - {message}'

    if live_display:
        live_display.console.print(out)
    else:
        console.print(out)

def notice(message: str, label: str = None) -> None:
    if global_log_level < 5:
        return

    if label:
        out = f'[bright_black]{label}:[/] NOTICE - {message}'
    else:
        out = f'NOTICE - {message}'

    if live_display:
        live_display.console.print(out)
    else:
        console.print(out)

def warning(message: str, label: str = None) -> None:
    if global_log_level < 4:
        return

    if label:
        out = f'[bright_black]{label}:[/] [yellow]WARNING - {message}[/]'
    else:
        out = f'[yellow]WARNING - {message}[/]'

    if live_display:
        live_display.console.print(out)
    else:
        console.print(out)

def error(message: str, label: str = None) -> None:
    if global_log_level < 3:
        return

    if label:
        out = f'[bright_black]{label}:[/] [red]ERROR - {message}[/]'
    else:
        out = f'[red]ERROR - {message}[/]'

    if live_display:
        live_display.console.print(out)
    else:
        console.print(out)

def critical(message: str, label: str = None) -> None:
    if global_log_level < 2:
        return

    if label:
        out = f'[bright_black]{label}:[/] [red]CRITICAL - {message}[/]'
    else:
        out = f'[red]CRITICAL - {message}[/]'

    if live_display:
        live_display.console.print(out)
    else:
        console.print(out)



# === Live Table ===

def make_table() -> Table:
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold dark_cyan", expand=True)
    table.add_column("Downloading", style="dark_cyan", ratio=1)
    table.add_column("Status: Album / Lyrics / Genre / Copyright / Audio / Album Art / Add Metadata", ratio=3)

    with thread_lock:
        for label, content in active_items.items():
            table.add_row(label, make_column(content))
    return table

def make_column(content):
    parts = []
    for ID, item in content.items():
        # if len(parts) > 0:
        #     parts.append(Text(" | "))
        match item["status"]:
            case Status.ACTIVE:
                # text += " | " + item["message"]

                # parts.append(Text(item["message"]))
                parts.append(Text.from_markup(item["message"]))
                
                parts.append(Spinner("bouncingBar"))
                # parts.append(Spinner("arrow3"))
            case Status.SUCCESS:
                # parts.append(Text("✔", style="green"))
                parts.append(Text(characters["yes"], style="green"))
            case Status.PART_SUCC:
                parts.append(Text("~", style="green"))
            case Status.NOT_FOUND:
                # parts.append(Text("✖", style="yellow"))
                parts.append(Text(characters["no"], style="yellow"))
            case Status.FAILED:
                # parts.append(Text("✖", style="red"))
                parts.append(Text(characters["no"], style="red"))
            case Status.SKIPPED:
                parts.append(Text("-", style="bright_black"))
            # case Status.HIDE: # --- Do not add any text
            #     text += "[dim]-[/]"
    
    return Columns(parts)


def update(label: str, ID: str, status: str, message: str = "Nothing"):
    if not live_display:
        return
    with thread_lock:
        if not active_items.get(label):
            active_items[label] = {ID: {"status": status, "message": message}}
        elif not active_items[label].get(ID):
            active_items[label][ID] = {"status": status, "message": message}
        else:
            active_items[label][ID]["status"] = status
            active_items[label][ID]["message"] = message

            
    live_display.update(make_table())

# --- Removing without message
def remove(label: str):
    if not live_display:
        return
    with thread_lock:
        active_items.pop(label, None)
    live_display.update(make_table())



# --- Removing with message
class Download_status(str, Enum):
    SUCCESS = "success"
    DOWNLOAD_DISABLED = "download_disabled"
    FAILED = "failed"
    ALREADY_DOWNLOADED = "already_downloaded"

def finish(label: str, status):
    if not live_display:
        return
    with thread_lock:
        this_item = active_items.pop(label, None)
    live_display.update(make_table())


    if status is Download_status.ALREADY_DOWNLOADED:
        live_display.console.print(         f'[blue]  Already Downloaded:       {label}[/]')
        return
    

    text = ""
    if this_item:
        counter = 0
        for ID, item in this_item.items():
            counter += 1
            match item["status"]:
                case Status.ACTIVE:
                    text += " | ACTIVE"
                case Status.SUCCESS:
                    text += f" | [green]{characters['yes']}[/]"
                case Status.PART_SUCC:
                    text += " | [green]~[/]"
                case Status.NOT_FOUND:
                    text += f" | [yellow]{characters['no']}[/]"
                case Status.FAILED:
                    text += f" | [red]{characters['no']}[/]"
                case Status.SKIPPED:
                    text += " | [bold bright_black]-[/]"
                case Status.HIDE: # --- Do not add any text
                    counter -= 1
        text += " |  " * (7 - counter)
        text += " |"
        

    if status is Download_status.SUCCESS:
        # live_display.console.print(        f'[green]  Downloaded successfully:  {label}[/] {text}')
        
        if global_log_level > 4:
            live_display.console.print(Columns(
                [
                    f'[green]  Downloaded successfully:  {label}[/]',
                    Align.right(text)
                ],
                expand=True
            ))
        else:
            live_display.console.print(        f'[green]  Downloaded successfully:  {label}[/]')
        
    elif status is Download_status.FAILED:
        # live_display.console.print(          f'[red]  Downloaded failed:        {label}[/] {text}')
        
        if global_log_level > 4:
            live_display.console.print(Columns(
                [
                    f'[red]  Downloaded failed:        {label}[/]',
                    Align.right(text)
                ],
                expand=True
            ))
        else:
            live_display.console.print(          f'[red]  Downloaded failed:        {label}[/]')

    elif status is Download_status.DOWNLOAD_DISABLED:
        # live_display.console.print(f'[bright_yellow]  Downloaded disabled:      {label}[/] {text}')
        if global_log_level > 4:
            live_display.console.print(Columns(
                [
                    f'[bright_yellow]  Downloaded disabled:      {label}[/]',
                    Align.right(text)
                ],
                expand=True
            ))
        else:
            live_display.console.print(f'[bright_yellow]  Downloaded disabled:      {label}[/]')




# === Debug stuff ===

active_items_test = { # Just for debug
    "2/9 Castle Rat - Feed The Dream": {
        "album": {
            "status": "success",
            "message": "Nothing"
        },
        "get_lyrics": {
            "status": "success",
            "message": "Nothing"
        },
        "musicbrainz": {
            "status": "success",
            "message": "Nothing"
        },
        "deezer": {
            "status": "success",
            "message": "Nothing"
        },
        "wait_queue": {
            "status": "hide",
            "message": "Nothing"
        },
        "downloading": {
            "status": "success",
            "message": "Nothing"
        },
        "albumart": {
            "status": "success",
            "message": "Nothing"
        },
        "addmetadata": {
            "status": "success",
            "message": "Nothing"
        }
    },
    "3/9 Castle Rat - Resurrector": {
        "album": {
            "status": "success",
            "message": "Nothing"
        },
        "get_lyrics": {
            "status": "not_found",
            "message": "Nothing"
        },
        "musicbrainz": {
            "status": "success",
            "message": "Nothing"
        },
        "deezer": {
            "status": "success",
            "message": "Nothing"
        },
        "wait_queue": {
            "status": "hide",
            "message": "Nothing"
        },
        "downloading": {
            "status": "success",
            "message": "Nothing"
        },
        "albumart": {
            "status": "success",
            "message": "Nothing"
        },
        "addmetadata": {
            "status": "success",
            "message": "Nothing"
        }
    }
}