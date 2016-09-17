#!/usr/bin/env python

# See: http://www.tuxradar.com/content/code-project-build-ncurses-ui-python
# See: http://kodi.wiki/view/JSON-RPC_API/v6
# See: https://docs.python.org/2/howto/curses.html
# See: https://docs.python.org/2/library/curses.html#functions
from os import system
import curses
import requests
import json
import ConfigParser

config = ConfigParser.ConfigParser()
config.readfp(open(r'config.ini'))
base_url= config.get('Kodi', 'server')
port = config.get('Kodi', 'port')
url = "http://{}:{}/jsonrpc".format(base_url,port)

headers = {'content-type': 'application/json'}



def send_input_command(cmd):
  payload = json.dumps({"jsonrpc": "2.0", 
                        "method": cmd})
  return requests.request("POST", url, data=payload, headers=headers)


def send_player_command(cmd, **kwargs):
  payload = json.dumps({"jsonrpc": "2.0", 
                        "method": cmd,
                        "id": 1,
                        "params": kwargs})
  return requests.request("POST", url, data=payload, headers=headers)


def get_addon_detail(addon_id):
  payload= json.dumps({"jsonrpc": "2.0", 
      "method": "Addons.GetAddonDetails", 
      "params": {
          "addonid": addon_id,
          "properties": ["description", "summary", "enabled", "version"]
      },
      "id":1
    })
  r = requests.request("POST", url, data=payload, headers=headers)
  return r.json()


def get_addons():
  payload = json.dumps({"jsonrpc": "2.0", 
                        "method": "Addons.GetAddons",
                        "id": 1,
                        "params": {"properties": ["description", "summary", "enabled", "version"]}})
  r = requests.request("POST", url, data=payload, headers=headers)
  return r.json()


def get_param(prompt_string):
     screen.clear()
     screen.border(1)
     screen.addstr(2, 2, prompt_string)
     screen.refresh()
     input = screen.getstr(10, 10, 60)
     return input

def addons_list(switch_window):
  screen = curses.initscr()
  screen.keypad(1)
  response = get_addons()
  x = 0
  items_per_page=15
  if not 'error' in response:  
    addons = response['result']['addons']
    pages = len(addons)/items_per_page 
    current_page = 0
    start_idx = 0 
    end_idx = start_idx+items_per_page
    selected_idx = 0
    while x != ord('Q'):
      start_idx= current_page*items_per_page
      end_idx = start_idx+items_per_page
      if end_idx > len(addons):
        end_idx = len(addons)
      screen.clear()
      screen.border(0)
      screen.addstr(1, 2, "{}/{} Page. N=Previous,n=Next,Q=Exit,g/return=Execute".format(current_page,pages))
      for idx,addon in enumerate(addons[start_idx:end_idx]):
        enabled='True' if addon['enabled'] else 'False'
        if selected_idx == idx:
          screen.addstr(3+idx, 2, str(' | '.join([addon['addonid'], addon['summary'], enabled])), curses.A_STANDOUT)
        else:
          screen.addstr(3+idx, 2, str(' | '.join([addon['addonid'], addon['summary'], enabled])))
      screen.refresh()
      x = screen.getch()
      if x == ord('n'):
        current_page += 1
        if current_page >= pages:
          current_page = pages
      if x == ord('N'):
        current_page -= 1
        if current_page < 0:
          current_page = 0
      if x == curses.KEY_DOWN: 
        selected_idx +=1
        if selected_idx >= (end_idx - start_idx):
          selected_idx = 0
      if x == curses.KEY_UP:
        selected_idx -=1
        if selected_idx < 0:
          selected_idx = (end_idx - start_idx)-1

      if x == ord('g') or x == 10:
        addon = addons[start_idx+selected_idx]
        send_player_command("Addons.ExecuteAddon", addonid=addon['addonid'])
        x = ord('Q')
        screen.clear()

  globals()[switch_window['previous']](None)


def main_window(switch_window=None):
  x = 0
  while x != ord('Q') and switch_window==None:
       screen = curses.initscr()
       curses.cbreak()
       curses.noecho()  
       screen.clear()
       screen.keypad(1)
       screen.border(0)
       screen.addstr(2, 2,  "Navigation...")
       screen.addstr(4, 4,  "w or up: Up")
       screen.addstr(5, 4,  "a or right: Left")
       screen.addstr(6, 4,  "s or down: Down")
       screen.addstr(7, 4,  "d or right: Right")
       screen.addstr(8, 4,  "g or return: Select")
       screen.addstr(9, 4,  "b or q or backspace: Back")
       screen.addstr(10, 4, "h or escape: Home")
       screen.addstr(11, 4, "m: Context Menu")
       screen.addstr(12, 4, "L: List Addons")
       screen.addstr(2, 54, "------------ Media Controls ---------- ")
       screen.addstr(4, 54, "p or spacebar: Play/Pause")
       screen.addstr(5, 54, "f: Full Screen")
       screen.addstr(6, 54, "X: Stop")
       screen.addstr(7, 54, "-: Volume Down")
       screen.addstr(8, 54, "+: Volume Up")

       screen.addstr(14, 4, "Q: Exit")

       screen.refresh()
       
       x = screen.getch()

       if x == ord('w') or x == curses.KEY_UP:
           send_input_command("Input.Up")


       if x == ord('a') or x == curses.KEY_LEFT:
           send_input_command("Input.Left")
   
       if x == ord('s') or x == curses.KEY_DOWN:
           send_input_command("Input.Down")

       if x == ord('d') or x == curses.KEY_RIGHT:
           send_input_command("Input.Right")

       if x == ord('g') or x == 10:
           send_input_command("Input.Select")
       
       if x == ord('h') or x == 27:
           send_input_command("Input.Home")

       if x == ord('m'):
           send_input_command("Input.ContextMenu")

       if x == ord('b') or x == ord('q') or x == curses.KEY_BACKSPACE:
           send_input_command("Input.Back")
       
       if x == ord('p') or x == ord(' '):
           send_player_command("Player.PlayPause", playerid=0)

       if x == ord('f'):
           send_player_command("GUI.SetFullscreen", fullscreen=True)

       if x == ord('X'):
           send_player_command("Player.Stop", playerid=0)

       if x == ord('-') or x == ord('_'):
           send_player_command("Application.SetVolume", volume='decrement')

       if x == ord('+') or x == ord('='):
           send_player_command("Application.SetVolume", volume='increment')

       if x == ord('L'):
           switch_window = {'next': 'addons_list',
                            'previous': 'main_window'}

         
  if switch_window == None:
    curses.endwin()
    curses.nocbreak() 
    screen.keypad(0)
    curses.echo()
    screen.clear()
  else:
    globals()[switch_window['next']](switch_window)

if __name__ == "__main__":
  main_window(None)
