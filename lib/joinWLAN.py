import network
import esp
import time


def man():
    print("Connect to Wifi with some fool Funcs by zklou.")
    print("Modules required: network, esp, time")
    print("First, establish a wlan obj:")
    print("\t>>> wlan = network.WLAN(network.STA_IF)")
    print("\t>>> wlan.active(True)")
    print("Avaliable subFunctions:")
    print("\tscanWifi(wlan):  return the RET of wlan.scan()")
    print("\tcheckWifi(wlan):  check if connected")
    print("\tconnectWifi(wlan, ssid, passwd):  connect and wait")

def scanWifi(wlan):
    print("Scanning availible wifis...")
    wifiList = wlan.scan()
    for i in range(len(wifiList)):
        print(i, wifiList[i])
    print("Total:", (wifiList), "wifis in all, also in RET.")
    return wifiList

def checkWifi(wlan):
    if wlan.isconnected() == True:
        print("Already connected to Wifi.")
        print('Network config:', wlan.ifconfig())
    else:
        print("Not yet connected.")

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

