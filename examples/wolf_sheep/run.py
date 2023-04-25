from wolf_sheep.server import server
import sys

open_browser: bool = True

if sys.argc >= 2 and sys.argv[1] == 'headless':
    open_browser = False

server.launch(open_browser=open_browser)
