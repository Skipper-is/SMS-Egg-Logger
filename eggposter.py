import network
import _thread
import sim800l
import utime


# A file for variables like logins, urls, and wifi details for the T-Call

wifiSSID = "Add your ssid here"
wifipswd = "Your password in here"

postURL = "https://example.com/eggposter.php"  # This is the URL of the eggs php file that the app will try and access

# ========== FarmOS Details ==========

# This is the "Chickens" asset you want to record the eggs to
assetJson = [{"uri": "https://url.to.the.asset", "id": "ID of the asset", "resource": "farm_asset"}]
egg_id = "43"  # This is the id of the egg unit - you can get this from taxonomy_term.json?bundle=farm_quantity_units


farmOSAuth = ""  # Unfortunately, micropython doesn't seem to have the base64 module, so you'll need to encode your username:password using a number of online tools
# Such as https://www.base64encode.org/ - eg: "restws_username:pass1234" would give you "cmVzdHdzX3VzZXJuYW1lOnBhc3MxMjM0" as your farmOSAuth
# TODO: Integrate this with micropython-farmOS.py, so we can use token authentication.

# ========== Messages ==========
# You can cusomise your responses here
received_text = "Received "
collected_text = "Collected "
egg_text = " egg"
eggs_text = " eggs"
thank_you_text = "\nThank you!"
error_message = "Your message wasn't understood\nSorry!"


# ========== Variables ==========

phone = None  # This will be the phone object, when it has been initialised!

# ========== Functions ==========
# The main functions


def do_connect():
    # do_connect will connect to the wifi you specified under egg_details
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("connecting")
        wlan.connect(wifiSSID, wifipswd)
        while not wlan.isconnected():
            pass
    print("network config:", wlan.ifconfig())


def initialisePhone():
    global phone
    phone = sim800l.Phone()
    while True:  # Check if the phone is online
        reply = phone.sendCommand("AT")  # Check to see if the module is active
        if ("OK" in reply):
            phone.sendCommand("AT+CMGF=1")  # These commands are officially sent by the sim800 module, but sometimes it goofs, so we'll send them again to be safe!
            phone.sendCommand("AT+CNMI=1,2,0,0,0")
            break  # And then let us continue!
        else:
            utime.sleep_ms(500)  # If there is no reply, we'll wait a bit more
    checkMessages(10)  # Check the messages with a 10s delay between checking


def checkReturned(returnedString):  # This takes an array from the message processer, and extracts the message and phone number
    number = None
    message = None
    if(len(returnedString) == 2):  # Just sanity check the data
        commandString = returnedString[0]  # The first bit should be the command string, starting with CMT
        commandString = commandString.lower()  # Just make it lower case.. makes everyones life easier if it is all the same
        # Test if it is actually a CMT message:
        if "cmt" in commandString:
            number = commandString.split(",")[0]
            # the response is usually '+CMT: "+441234567890","","19/08/16,15:15:52+04"\r\n4 eggs\r\n
            # So we split it at the , which gives us +CMT: "+441234567890". Next, split it at  the "
            number = number.split('"')[1]  # And take the 2nd half, the phone number!
            # It is a text message, so lets get the actual message:
            message = returnedString[1].lower()  # Second bit of the input string should be the message!
            # Make it lower to rule out people writing "EgGs"...You know what people are like...
    return [number, message]  # Either None, or the actual thing!


def quantityFromMessage(message):

    if ("egg" in message):
        product = "eggs"
        count = getNumber(message)
        return [int(count), product]
    return None


def getNumber(inputString):
    """
    The getnumber function will return a float, so if you pass "bob 12.345", you will have
    12.345 back. This will work (potentiall) in the future with other quantities like milk yields, where
    decimal places are needed. For eggs, this float will be converted back to an int, so you're not adding 1.2 eggs!
    """

    numParse = ""
    for i in range(len(inputString)):  # Iterate through the string, but with range, we iterate through the indexes
        char = inputString[i]
        if (char.isdigit() or char == '.'):
            numParse += char
            try:
                nexti = inputString[i+1]
            except IndexError:  # This is called if the numbers are at the end of the string.
                return(float(numParse))
                break
            if not (nexti.isdigit() or nexti == "."):  # This on is called if the number is at the beginning of the string
                return(float(numParse))
                break


def checkMessages(delay):
    if (type(phone) is not None):  # If the phone has been initialised
        _thread.start_new_thread(getLatest, [delay])
    else:
        print("Phone has not been initialised")


def getLatest(delay):
    # This function will check the latest messages on the SIM every $delay seconds
    while True:
        utime.sleep_ms(delay * 1000)
        response = phone.readAll()  # Get all the messages from the phone
        if (response is not None):  # If there is actually a response on the SIM....
            responseStr = response.decode('utf-8')  # Decode it into utf-8
            splitString = responseStr.splitlines()  # Split it into a string array, based on CR/NLs - May need to
            # check if this still works if someone writes:
            # Hello phone! \r\n
            # I'd like to add 3 eggs please
            # Might not work as the message has a CR/NL....
            for i in splitString:
                if ("CMT" in i):  # Is one of the responses a message response (could also be anything, AT replies, all ready replies etc)
                    index = splitString.index(i)  # And where is that message in the array?
                    message = []
                    message.append(splitString[index])  # Add the command + phone number
                    message.append(splitString[index+1])  # Add the message (command +1)
                    [number, text] = checkReturned(message)  # Get the phone number and the message from the array
                    quantity = quantityFromMessage(text)[0]  # Get the int from the message
                    if ((quantity is not None) and (quantity > 0)):  # Check if it has worked...
                        reply = received_text + str(quantity) + eggs_text + thank_you_text
                        json = createHarvestJSON(quantity)
                        if json is not None:
                            success = postJSON(json)
                            if phone is not None:
                                if not success:
                                    phone.sendText(number, "Sorry, the record couldn't be sent, try again, or ask the administrator")
                                else:
                                    phone.sendText(number, reply)
                            else:
                                print("How did we get the message with no phone?!")
                        else:
                            if phone is not None:
                                phone.sendText(number, error_message)


def createHarvestJSON(count):
    json = {}
    if (type(count) is int):
        if (count > 1):  # more than 1 egg
            json["name"] = collected_text + str(count) + eggs_text
        else:
            json["name"] = collected_text + str(count) + egg_text  # Singular egg... Lonely. And who only get 1 egg per day?!
        json["type"] = "farm_harvest"
        json["done"] = "1"
        json["asset"] = assetJson
        json["quantity"] = [{"measure": "count", "value": str(count), "unit": {"id": egg_id}}]
        return json
    else:
        return None


def postJSON(j, retries=0):
    if retries < 6:  # Only retry the connection 5 times, otherwise, give up TODO: Don't give up silently!
        import urequests as requests
        wlan = network.WLAN(network.STA_IF)
        if wlan.isconnected():  # Check connection
            r = requests.post(url=postURL, json=j, headers={"Authorization": "Basic " + farmOSAuth})  # Send the psot request
            if (r.status_code == 201):  # Check if the response is 201: Created - The correct reponse from FarmOS
                print("success")
                return True
            else:  # Otherwise, retry
                postJSON(j, retries+1)
        else:
            do_connect()
            postJSON(j, retries+1)
    else:
        return False
