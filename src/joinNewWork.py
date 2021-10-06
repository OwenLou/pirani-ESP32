import network
import esp
import time
def scanWifi(wlan):
    print("Scanning availible wifis...")
    wifiList = wlan.scan()
    for i in range(len(wifiList)):
        print(i, wifiList[i])
    print(len(wifiList), "in all, also in RET.")
    return wifiList

def checkWifi(wlan):
    if wlan.isconnected() == True:
        print("Already connected to Wifi.")
        print('Network config:', wlan.ifconfig())
    else:
        print("Not yet connected.")
        print("Use `wlan.active(True)` to activate and connect.")


def connectWifi(wlan, ssid, passwd):
    wlan.connect(ssid, passwd)
    waitCnt = 0
    while not wlan.isconnected():
        WAIT_CNT_MAX = 100
        WAIT_TIME = 100
        if waitCnt != WAIT_CNT_MAX:
            waitCnt += 1
            time.sleep_ms(WAIT_TIME)
        else:
            print("Time out! %d seconds expired. Please check Wifi Connection Manually."

                 % int(WAIT_CNT_MAX * WAIT_TIME / 1000))
            break
    print('network config:', wlan.ifconfig())

def doWifiConnect(wlan):
    if wlan.isconnected() == True:
        print("Already connected to Wifi")
        print('Network config:', wlan.ifconfig())
        return
    print("Gonna connect WiFi")
    # connect to wifi
    wlan.active(True)
    wifiList = checkWifi(wlan)
    scanWifi(wlan)
    wifiListNum = int(input("Input a number above to connect: "))
    ssid = wifiList[wifiListNum][0].decode('utf-8', 'ignore')
    passwd = input("Please input the password: ")
    print('connecting to network: ', ssid)
    wlan.connect(ssid, passwd)
    waitCnt = 0
    while not wlan.isconnected():
        WAIT_CNT_MAX = 100
        WAIT_TIME = 100
        if waitCnt != WAIT_CNT_MAX:
            waitCnt += 1
            time.sleep_ms(WAIT_TIME)
        else:
            print("Time out! %d seconds expired. Please check Wifi Connection Manually."
                 % int(WAIT_CNT_MAX * WAIT_TIME / 1000))
            break
    print('network config:', wlan.ifconfig())

if __name__ == 'main':
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    doWifiConnect(wlan)

