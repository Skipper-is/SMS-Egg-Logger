# Egg Logger for FarmOS
Egg Logger is a program that is designed to run on a TTGO T-Call ESP32 module.
The module can be purchased from: [AliExpress](https://www.aliexpress.com/item/33045221960.html), or [BangGood](https://www.banggood.com/LILYGO-TTGO-T-Call-V1_3-ESP32-Wireless-Module-GPRS-Antenna-SIM-Card-SIM800L-Board-p-1527048.html?rmmds=search&cur_warehouse=CN).
### TODO
Integrate Egg Logger with micropython-farmOS.py, so token authorisation can be used
## Requirements

 - ESP32 T-Call
 - 2G Sim card (nano)
 - WiFi access
 - FarmOS with a restws_ user, and Basic Authentication enabled (Modules>Basic Authentication Login)
 - A server with PHP and the cURL module enabled
 - Another phone/phones!
 - Some chickens..... (real or imaginary)

## Installation

Download the repository

You need to make a number of changes to the following files:
### eggposter.py
**Wifi**
Put in your WIFI name, and password to 

    wifiSSID = "Add your ssid here"
    wifipswd = "Your password in here"

**Post URL**
This is the URL of the .php file in this repository. This also needs editing (see later...), and uploading to the server (Which needs to have cURL enabled)

**FarmOS Details**
Change the assetJson to URL to the asset, and the ID of the asset - This is the chickens you are recording the data for. Can be a group

    assetJson = [{"uri": "https://url.to.the.asset", "id": "ID of the asset", "resource": "farm_asset"}]

You can get this information through the `/farm_asset.json?type=animal` API endpoint [See the documentation here](https://farmos.org/development/api/#requesting-records)


You're after the id. Mine are `"id": "39"`, so I'd add `"39"` to the json, along with the URL (mine looks like: `/farm/animal/hens`

Next, set the egg ID, this can be found from `/taxonomy_term.json?bundle=farm_quantity_units`
(If it is not there, you may need to add the term)

    egg_id = "43"

You'll need to create an account that begins with restws_ in FarmOS for your login (and with appropriate permissions) (and make sure you've enabled basic authentication in modules)

  Your login details go into `farmOSAuth = ""` but needs to be encoded in base64.
  There are several ways of doing this, easiest is to go to:  [Base64Encode.org](https://www.base64encode.org/) and enter your details there, it needs to be in the following format:
  

    username:password
Enode that, and you'll end up with something like this (this is for "restws_username:pass1234":

    cmVzdHdzX3VzZXJuYW1lOnBhc3MxMjM0

   So, the .py should look like this:
   

    farmOSAuth = "cmVzdHdzX3VzZXJuYW1lOnBhc3MxMjM0"

There are some translation options

    received_text = "Received "
    collected_text = "Collected "
    egg_text = " egg"
    eggs_text = " eggs"
    thank_you_text = "\nThank you!"
    error_message = "Your message wasn't understood\nSorry!"

And don't touch anything else in that file!

### eggposter.php
:EDIT: I have had some success with posting without the eggposter.php, just add your `log.json?type=farm_harvest` API endpoint in as the .py post url
The php file is the middle man between the T-Call and FarmOS. For some reason, the T-Call wouldn't post directly to FarmOS, so I had to mirror the post exactly through a php file, which works...
One change you need to make here:

    $url  =  'https://example.com/farmOS/log.json?type=farm_harvest';
You need to change `example.com/farmOS` to your FarmOS install

## Useage
Once it is set up and working, using it is quite simple:

Send a text to the number of the sim-card in the T-Call with the message:

    x eggs
Where x is the number of eggs, for example `53 eggs`
Can be variations of that as well, these all work:

    EgGs 23
    1 egg
    Add 2 eggs please
If you send `10 eggs 12345` the first lot of numbers will be taken, so 10 eggs. 
If it has been successful, you should get a text back saying so, and the record added to FarmOS
