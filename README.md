# chatpyboard
Python utility to interface with Ericsson Chatboard CHA-10 tiny keyboard

--- 
Ever wanted to type with '90s Erricson CHA-10 rubber QWERTY keyboard? Me neither! But it costs so little that I couldn't resist.

I figured this out without an actuall phone, so the info might not be accurate. There are so many quirks, that I'm curious how it works with a real phone.

## Hardware
The keyboard talks serial 9600 8N1, pinout as follows:
_image_

I've connected mine to a USB↔RS232 TTL adapter
  
  ## Software
  It talks AT commands, it poses as… a Mobile Equipment keyboard. It simulates keypresses on a telephone keypad.
  You heard me right, it "presses" numeric keys few times, to get you to the desired letter.
  I found [a keymap of the Ericsson T18z (page 22)](https://data2.manualslib.com/pdf2/41/4001/400047-ericsson/t18z.pdf?450a6521678afdc25a1fc91d48d4df46) to be quite spot-on.
  ### Rx
  For example pressing the key `1` cycles through this sequence: `␣-?!,.:;"\'<=>()1',`. Eg. pressing `?` key given you `111` on the serial. Wrapped in a AT command _elaborate_
  ### Tx
  In terms of communication back to the keyboard, I found that we only need to ACK anything it sends with `OK`
  
  ## Quirks
There are many quirks:
- on power up the keyboard is in numeric mode: it only enters digits
- when pressing a key twice in a row, the keyboard adds `1c` (or `0c`) before the second sequence, to finish "entering" of the current character. `1c` means `space, backspace`
- pressing `SMS` key or `eMail` key causes the keyboard to enter text mode
- there is only one case (size). `shift` key is used to enter special characters printer above keys. But since we have it working, we could replace those special chars with uppercase alpha letters
- the keyboard stall sometimes for some time, queueing keypresses, then releases it in a burst.
- holding `YES`/`NO` is a separate key, which is nice, **but** it causes the keyboard to return to numeric mode. I've mapped longpressing of `YES` to enter.

I planned to use it as a quick snap on keyboard for Raspberry Pis, but it is so bad, that, I won't. I event though about writing a kernel module eventually ← Haha

Anyone knows a list of tiny keyboards? X360 had some attached to the gamepads.
