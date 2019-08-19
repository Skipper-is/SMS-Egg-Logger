# Egg Logger for FarmOS
Egg Logger is a program that is designed to run on a TTGO T-Call ESP32 module.
The module can be purchased from: [AliExpress](https://www.aliexpress.com/item/33045221960.html), or [BangGood](https://www.banggood.com/LILYGO-TTGO-T-Call-V1_3-ESP32-Wireless-Module-GPRS-Antenna-SIM-Card-SIM800L-Board-p-1527048.html?rmmds=search&cur_warehouse=CN).
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
### egg_poster.py
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

You need to enter your FarmOS username and password here:

    farmOSUsername = "restws_username"
    farmOSPassword = "password"
You'll need to create an account that begins with restws_ in FarmOS for this (and with appropriate permissions)

There are some translation options

    received_text = "Received "
    collected_text = "Collected "
    egg_text = " egg"
    eggs_text = " eggs"
    thank_you_text = "\nThank you!"
    error_message = "Your message wasn't understood\nSorry!"

And don't touch anything else in that file!

### eggposter.php
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
If it has been successful, you should get a text back saying so, and the record added to FarmOS
