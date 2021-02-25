"""
cli.py

Sample CLI Clubhouse Client

RTC: For voice communication
"""


import os
import sys
import threading
import configparser
import keyboard
from rich.table import Table
from rich.console import Console
from clubhouse import Clubhouse

import PySimpleGUI as sg

usersdata = [['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0], 
             ['           ', '                ','         ',0, 0] ]

cannelsdata = [['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0], 
               ['         ', '                                                                        ', 0]]


    
# Set some global variables
try:
    import agorartc
    RTC = agorartc.createRtcEngineBridge()
    eventHandler = agorartc.RtcEngineEventHandlerBase()
    RTC.initEventHandler(eventHandler)
    # 0xFFFFFFFE will exclude Chinese servers from Agora's servers.
    RTC.initialize(Clubhouse.AGORA_KEY, None, agorartc.AREA_CODE_GLOB & 0xFFFFFFFE)
    # Enhance voice quality
    if RTC.setAudioProfile(
            agorartc.AUDIO_PROFILE_MUSIC_HIGH_QUALITY_STEREO,
            agorartc.AUDIO_SCENARIO_GAME_STREAMING
        ) < 0:
        print("[-] Failed to set the high quality audio profile")
except ImportError:
    RTC = None

def set_interval(interval):
    """ (int) -> decorator

    set_interval decorator
    """
    def decorator(func):
        def wrap(*args, **kwargs):
            stopped = threading.Event()
            def loop():
                while not stopped.wait(interval):
                    ret = func(*args, **kwargs)
                    if not ret:
                        break
            thread = threading.Thread(target=loop)
            thread.daemon = True
            thread.start()
            return stopped
        return wrap
    return decorator

def write_config(user_id, user_token, user_device, filename='setting.ini'):
    """ (str, str, str, str) -> bool

    Write Config. return True on successful file write
    """
    config = configparser.ConfigParser()
    config["Account"] = {
        "user_device": user_device,
        "user_id": user_id,
        "user_token": user_token,
    }
    with open(filename, 'w') as config_file:
        config.write(config_file)
    return True

def read_config(filename='setting.ini'):
    """ (str) -> dict of str

    Read Config
    """
    config = configparser.ConfigParser()
    config.read(filename)
    if "Account" in config:
        return dict(config['Account'])
    return dict()

def process_onboarding(client):
    """ (Clubhouse) -> NoneType

    This is to process the initial setup for the first time user.
    """
    print("=" * 30)
    print("Welcome to Clubhouse!\n")
    print("The registration is not yet complete.")
    print("Finish the process by entering your legal name and your username.")
    print("WARNING: THIS FEATURE IS PURELY EXPERIMENTAL.")
    print("         YOU CAN GET BANNED FOR REGISTERING FROM THE CLI ACCOUNT.")
    print("=" * 30)

    while True:
        user_realname = input("[.] Enter your legal name (John Smith): ")
        user_username = input("[.] Enter your username (elonmusk1234): ")

        user_realname_split = user_realname.split(" ")

        if len(user_realname_split) != 2:
            print("[-] Please enter your legal name properly.")
            continue

        if not (user_realname_split[0].isalpha() and
                user_realname_split[1].isalpha()):
            print("[-] Your legal name is supposed to be written in alphabets only.")
            continue

        if len(user_username) > 16:
            print("[-] Your username exceeds above 16 characters.")
            continue

        if not user_username.isalnum():
            print("[-] Your username is supposed to be in alphanumerics only.")
            continue

        client.update_name(user_realname)
        result = client.update_username(user_username)
        if not result['success']:
            print(f"[-] You failed to update your username. ({result})")
            continue

        result = client.check_waitlist_status()
        if not result['success']:
            print("[-] Your registration failed.")
            print(f"    It's better to sign up from a real device. ({result})")
            continue

        print("[-] Registration Complete!")
        print("    Try registering by real device if this process pops again.")
        break

def print_channel_list(client, max_limit):
    """ (Clubhouse) -> NoneType

    Print list of channels
    """
    # Get channels and print out
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("")
    table.add_column("channel_name", style="cyan", justify="right")
    table.add_column("topic")
    table.add_column("speaker_count")
    channels = client.get_channels()['channels']
    i = 0
    for channel in channels:
        if i > max_limit:
            break
        #data[i][] = channel
        _option = ""
        _option += "\xEE\x85\x84" if channel['is_social_mode'] or channel['is_private'] else ""

        #data[0][1] = str(_option)
        cannelsdata[i][0] = str(channel['channel'])
        cannelsdata[i][1] = str(channel['topic'])
        cannelsdata[i][2] = str(int(channel['num_speakers']))
        i += 1
      
    #console.print(table)

def chat_main(client):
    """ (Clubhouse) -> NoneType

    Main function for chat
    """
    max_limit = 30
    channel_speaker_permission = False
    _wait_func = None
    _ping_func = None

    def _request_speaker_permission(client, channel_name, user_id):
        """ (str) -> bool

        Raise hands for permissions
        """
        if not channel_speaker_permission:
            client.audience_reply(channel_name, True, False)
            _wait_func = _wait_speaker_permission(client, channel_name, user_id)
            print("[/] You've raised your hand. Wait for the moderator to give you the permission.")

    @set_interval(30)
    def _ping_keep_alive(client, channel_name):
        """ (str) -> bool

        Continue to ping alive every 30 seconds.
        """
        client.active_ping(channel_name)
        return True

    @set_interval(10)
    def _wait_speaker_permission(client, channel_name, user_id):
        """ (str) -> bool

        Function that runs when you've requested for a voice permission.
        """
        # Get some random users from the channel.
        _channel_info = client.get_channel(channel_name)
        if _channel_info['success']:
            for _user in _channel_info['users']:
                if _user['user_id'] != user_id:
                    user_id = _user['user_id']
                    break
            # Check if the moderator allowed your request.
            res_inv = client.accept_speaker_invite(channel_name, user_id)
            if res_inv['success']:
                print("[-] Теперь у вас есть разрешение на выступление.")
                print("    Пожалуйста, присоединитесь к этому каналу повторно, чтобы активировать разрешение.")
                return False
        return True
  
    
            
    headch = ['Канал', 'Название', 'Пользователи']
    headus = ['ID', 'Имя', 'Ник', 'спикер', 'модератор']
    
    layout =[
         [sg.Table(values=cannelsdata, headings=headch, max_col_width=500,
                    # background_color='light blue',
                    auto_size_columns=True,
                    display_row_numbers=True,
                    justification='left',
                    num_rows=10,
                    key='-TABLE-',
                    row_height=35,
                    tooltip='This is a table')],
         [sg.Table(values=usersdata, headings=headus, max_col_width=500,
                    # background_color='light blue',
                    auto_size_columns=True,
                    display_row_numbers=True,
                    justification='left',
                    num_rows=5,
                    key='-USERS-',
                    row_height=35,
                    tooltip='This is a table')],
         [sg.Output(size=(500, 10))],
         [sg.Text("Имя канала"), sg.InputText(), sg.Button('Conect')],
         [sg.Button('Обновить'), sg.Cancel()],
         [sg.Button('Подключиться'), sg.Button('Помахать'), sg.Button('Отключиться')]

    ]

    window = sg.Window("Clubhause", layout, size=(900, 900))
    channel_name = ''
    while True:
      event, values = window.read()
      print(event, values) #debug
      
       
      if event == 'Обновить':
         # Choose which channel to enter.
         # Join the talk on success.
         user_id = client.HEADERS.get("CH-UserID")
         print_channel_list(client, max_limit)
         print("[.] Введите имя канала: ")
         window.Element('-TABLE-').Update(values=cannelsdata)
         #print(data)
         continue
      if event == 'Connect':
          channel_name = values[0]  
          channel_info = client.join_channel(channel_name)
          
          if not channel_info['success']:
             print(f"[-] Error while joining the channel ({channel_info['error_message']})")
             continue

          # Список доступных на данный момент пользователей (только ТОП 20).
          # Также проверьте, есть ли у текущего пользователя разрешение на выступление.
          channel_speaker_permission = False

          users = channel_info['users']
          i = 0
          for user in users:
            
            if i > max_limit:
                break

            usersdata[i][0] = str(user['user_id'])
            usersdata[i][1] = str(user['name'])
            usersdata[i][2] = str(user['username'])
            usersdata[i][3] = str(user['is_speaker'])
            usersdata[i][4] = str(user['is_moderator'])
            i += 1
            # Проверьте, является ли пользователь говорящим
            if user['user_id'] == int(user_id):
                channel_speaker_permission = bool(user['is_speaker'])
          
          window.Element('-USERS-').Update(values=usersdata)

          # Проверьте уровень голоса.
          if RTC:
            token = channel_info['token']
            RTC.joinChannel(token, channel_name, "", int(user_id))
          else:
            print("[!] Agora SDK не установлен.")
            print("    Вы не можете говорить или слушать разговор.")

          # Активировать пинг
          client.active_ping(channel_name)
          _ping_func = _ping_keep_alive(client, channel_name)
          _wait_func = None         
          continue
         
      if event == 'Подключиться':
         if values['-TABLE-']:
          row_index = 0
          for num in values['-TABLE-']:
           row_index = num 
           
          channel_name = cannelsdata[num][0]

          channel_info = client.join_channel(channel_name)
          if not channel_info['success']:
             print(f"[-] Error while joining the channel ({channel_info['error_message']})")
             continue

          # Список доступных на данный момент пользователей (только ТОП 20).
          # Также проверьте, есть ли у текущего пользователя разрешение на выступление.
          channel_speaker_permission = False
          users = channel_info['users']
          i = 0
          for user in users: 
            if i > 20:
                break
            usersdata[i][0] = str(user['user_id'])
            usersdata[i][1] = str(user['name'])
            usersdata[i][2] = str(user['username'])
            usersdata[i][3] = str(user['is_speaker'])
            usersdata[i][4] = str(user['is_moderator'])
            i += 1
            # Проверьте, является ли пользователь говорящим
            if user['user_id'] == int(user_id):
                channel_speaker_permission = bool(user['is_speaker'])
          
          window.Element('-USERS-').Update(values=usersdata)

          # Проверьте уровень голоса.
          if RTC:
            token = channel_info['token']
            RTC.joinChannel(token, channel_name, "", int(user_id))
          else:
            print("[!] Agora SDK не установлен.")
            print("    Вы не можете говорить или слушать разговор.")

          # Активировать пинг
          client.active_ping(channel_name)
          _ping_func = _ping_keep_alive(client, channel_name)
          _wait_func = None
          continue

         # speaker permission
      if event == 'Помахать':
          if not channel_speaker_permission:
            if not channel_name == '':
                _request_speaker_permission(client, channel_name, user_id)
                continue
          continue
          
      if event == 'Отключиться':
       # Безопасно покиньте канал после выхода из канала.
       if _ping_func:
         _ping_func.set()
       if _wait_func:
         _wait_func.set()
       if RTC:
         RTC.leaveChannel()
       if not channel_name == '':
         client.leave_channel(channel_name)
       continue
          
      if event in (None, 'Exit', 'Cancel'):
      
         # Безопасно покиньте канал после выхода из канала.
       if _ping_func:
         _ping_func.set()
       if _wait_func:
         _wait_func.set()
       if RTC:
         RTC.leaveChannel()
       client.leave_channel(channel_name)
       break
       
startwin =[    
         [sg.Output(size=(200, 10))],
         [sg.InputText(), sg.Button('Connect')]
]

def user_authentication(client):
    """ (Clubhouse) -> NoneType

    Just for authenticating the user.
    """  
    window = sg.Window("Clubhause", startwin, size=(450, 230))

    result = None
    while True:
        print("[.] Please enter your phone number. (+818043217654) ")
        event, values = window.read()
        if event in (None, 'Exit', 'Cancel'):
         break
        user_phone_number = values[0]
        
        result = client.start_phone_number_auth(user_phone_number)
        if not result['success']:
            print(f"[-] Error occured during authentication. ({result['error_message']})")
            continue
        break

    result = None
    while True:
        print("[.] Please enter the SMS verification code (1234, 0000, ...)")
        event, values = window.read()
        if event in (None, 'Exit', 'Cancel'):
         break
        verification_code = values[0]
        result = client.complete_phone_number_auth(user_phone_number, verification_code)
        if not result['success']:
            print(f"[-] Error occured during authentication. ({result['error_message']})")
            continue
        break

    user_id = result['user_profile']['user_id']
    user_token = result['auth_token']
    user_device = client.HEADERS.get("CH-DeviceId")
    write_config(user_id, user_token, user_device)

    print("[.] Writing configuration file complete.")

    if result['is_waitlisted']:
        print("[!] You're still on the waitlist. Find your friends to get yourself in.")
        return

    # Authenticate user first and start doing something
    client = Clubhouse(
        user_id=user_id,
        user_token=user_token,
        user_device=user_device
    )
    if result['is_onboarding']:
        process_onboarding(client)

    return

def main():
    #window = sg.Window("Clubhause", startwin, size=(300, 300))
    """
    Initialize required configurations, start with some basic stuff.
    """
    # Initialize configuration
    client = None
    user_config = read_config()
    user_id = user_config.get('user_id')
    user_token = user_config.get('user_token')
    user_device = user_config.get('user_device')

    # Check if user is authenticated
    if user_id and user_token and user_device:
        client = Clubhouse(
            user_id=user_id,
            user_token=user_token,
            user_device=user_device
        )

        # Check if user is still on the waitlist
        _check = client.check_waitlist_status()
        if _check['is_waitlisted']:
            print("[!] You're still on the waitlist. Find your friends to get yourself in.")
            return

        # Check if user has not signed up yet.
        _check = client.me()
        if not _check['user_profile'].get("username"):
            process_onboarding(client)
            
        
        chat_main(client)
    else:
        client = Clubhouse()
        user_authentication(client)
        main()

if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Remove dump files on exit.
        file_list = os.listdir(".")
        for _file in file_list:
            if _file.endswith(".dmp"):
                os.remove(_file)
