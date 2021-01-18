#!/bin/env python3
from time import sleep
from collections import OrderedDict

import subprocess
import uinput    

import keyboard

def main():
    import serial
    port = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.8)
    sleep(.3)

    if port.in_waiting > 0:
        print('needs flushing…', end='')
        port.read_until('\r') # flush
        print('flushed')
        


    def find(string) -> bool:
        retries = 10
        while retries:
            x = port.read(len(string))
            if len(x) == len(string):
                if x.decode('ascii').strip() == string.strip():
                    return True
            #else:
                #print(f'timeout ("{string.strip()}")')
            retries -= 1
            sleep (.4)
        return False

    search_response = OrderedDict({'AT\r':b'OK\r\n',
                                'AT+CGMM\r':  b'OK\r\n',           
                                'AT+CGMR\r':  b'OK\r\n',       
                                
                                'AT*EDME?\r': b'OK\r\n',       
                                'AT*ESVM?\r': b'OK\r\n',
                                # init done
                                'AT*ESVM=0\r': b'OK\r\n',
                                'AT+CKPD=': b'OK\r\n',
                                'AT*ESVM=1\r': b'OK\r\n',
                                })
    init_len = 5
    
    numeric_mode = True

    while True:                       
        buffer = None
        while not buffer:
            buffer = port.read_until(b'\r') # block for timeout    
        key = buffer.decode("ascii")

        if key in search_response.keys():
            # forward search
            init_keys = list(search_response.keys())[:init_len]
            if key in init_keys:
                index = init_keys.index(key)+1
                print(f'keyboard found {index}/{init_len} !')
                if index == 3:
                    print('(Now press SMS key on the chatboard)')
                if index == 5:
                    # SMS or email - ascii mode on
                    numeric_mode = False
            port.write(search_response[key])
        else:
            print(f'got: {repr(key)}') 
            # reverse search
            extended_keys = list(search_response.keys())[init_len:]
            for extended_key in extended_keys:
                if extended_key in key:
                    index = extended_keys.index(extended_key)+1
                    if index == 2: # CKPD
                        key = key.strip()
                        key = key.replace('"', '')
                        value = key.split('=')[1]
                        # repeat ?
                        anti_repeat = True if (value.find('1c') == 0 or value.find('0c') == 0)  else False
                        if anti_repeat:
                            value = value[2:]
                            print('(repeat)')
                        # long press
                        longpress = True if value[-3:] == (',20') else False
                        if longpress:
                            value = value[:-3]
                            print('(longpress)')
                        # character ?
                        char = value[0]
                        if value == len(value) * char:
                            if value == '<':
                                if longpress:
                                    send_key('home', True)
                                else:
                                    send_key('left', True)
                            elif value == '>':
                                if longpress:
                                    send_key('end', True)
                                else:
                                    send_key('right', True)
                            elif value == 'c':
                                if longpress:
                                    send_key('del', True)
                                else:
                                    send_key('backspace', True)
                            elif value == 's':
                                if longpress:
                                    send_key('enter', True)
                                else:
                                    send_key('yes', True)
                            elif value == 'e':
                                if longpress:
                                    send_key('esc', True)
                                    numeric_mode = True
                                else:
                                    send_key('no', True)
                            elif value == '*':
                                send_key('*')
                            else:
                                # digits in alpha mode are strange
                                if not numeric_mode and char.isdigit() and longpress:
                                    pseudo_numeric_mode = True
                                else:
                                    pseudo_numeric_mode = False
                                # normal chars
                                try:
                                    if value.isdigit() and len(value) > 1:
                                        numeric_mode = False
                                        
                                    if numeric_mode == True or pseudo_numeric_mode:
                                        char = value
                                    else:
                                        char = charmap[char][len(value)-1]                                            
                                    print(f'character: {char}')
                                except ValueError:
                                    pass
                                except (IndexError, KeyError):
                                    print(f'skipping: {value}')
                                else:
                                    send_key(char)
                        else:
                            print(f'keypress: {value}')
                        ts.key()
                        
                    port.write(search_response[extended_key])

        
from random import randrange
from playsound import playsound
    
class TypeSounds:
    def __init__(self):
        self.key_paths = ('type1.wav', 'type2.wav', 'type3.wav')
        self.newline = 'ding.wav'
    
    def _random_key(self):
        return randrange(len(self.key_paths))
    
    def _play(self, file):
        playsound(file)
        
    def key(self):
        self._play(self.key_paths[self._random_key()])
        
    def enter(self):
        self._play(self.newline)


def send_key(key, raw = False):
    print(f'<{key}>')
    if raw:
        keyboard.send(key)
    else:
        keyboard.write(key)

nvm_char = '□'

# keymap from T18z manual p.22, https://data2.manualslib.com/pdf2/41/4001/400047-ericsson/t18z.pdf?450a6521678afdc25a1fc91d48d4df46
charmap = {
    '1': ' -?!,.:;"\'<=>()1',
    '2': 'abc' + nvm_char*5+'2'+nvm_char,
    '3': 'def' + nvm_char*2+'3'+nvm_char*2,
    '4': 'ghi' + nvm_char+'4',
    '5': 'jkl' + '5'+ nvm_char,
    '6': 'mno' + nvm_char*4+'6',
    '7': 'pqrs'+ nvm_char+'7'+nvm_char*2,
    '8': 'tuv' + nvm_char*2+'8',
    '9': 'wxyz'+ '9',
    '0': '+&@/'+ nvm_char+'%$£'+ nvm_char*4+'0'+nvm_char*4,
    '#': '#*',
 }

UINPUT_KEY_MAPPING = {
        'q': uinput.KEY_Q,
        'w': uinput.KEY_W,
    }

def init_uinput():
    
    # Make sure uinput kernel module is loaded.
    subprocess.check_call(["modprobe", "uinput"])
    device = uinput.Device(UINPUT_KEY_MAPPING.values())
    
    return device

ts = TypeSounds()

if __name__ == '__main__':    
    #init_uinput()
    main()


# default mode: numeric mode. only works: yes/no, digits, long press causes digit (except for 3/8 → #/*), shifted digits are digits (except for 3/8 → #/*), backspace, arrows

