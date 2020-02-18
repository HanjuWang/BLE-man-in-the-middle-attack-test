import pygatt
import logging
import binascii
import time


# Many devices, e.g. Fitbit, use random addressing - this is required to connect.
ADDRESS_TYPE = pygatt.BLEAddressType.random
DEVICE_ADDRESS = "00:0a:e2:64:c3:cd"


def indication_callback(handle, value):
    print("indication, handle %d: %s " % (handle, value))


def pytest(address=DEVICE_ADDRESS, type=pygatt.BLEAddressType.public):
    try:
        adapter = pygatt.BGAPIBackend(serial_port='COM4')
        adapter.start()

        print("===== adapter.scan() =====")
        devices = adapter.scan()
        for dev in devices:
            # print dev
            print ("address: %s, name: %s " % (dev['address'], dev['name']))

        print ("===== adapter.connect() =====")
        device = adapter.connect(address, address_type=type)
        print ("address: " + str(device._address))
        print ("handle : " + str(device._handle))
        print ("rssi   : " + str(device.get_rssi()))

        print ("====== device.discover_characteristics() =====")
        for uuid in device.discover_characteristics().keys():
            try:
                print("Read UUID %s (handle %d): %s" %
                      (uuid, device.get_handle(uuid), binascii.hexlify(device.char_read(uuid))))
            except:
                print("Read UUID %s (handle %d): %s" %
                      (uuid, device.get_handle(uuid), "!deny!"))

        print ("====== device.char_read() / device.char_read_handle() =====")
        print ("2a00: " + device.char_read("c9155f2a-026f-b6bc-cf9b-39aa19b11190"))
        print ("2a00: " + device.char_read_handle(3))

        print ("====== device.subscribe() =====")
        device.subscribe("c9155f2a-026f-b6bc-cf9b-39aa19b11190",
                         callback=indication_callback, indication=True)
        # device.receive_notification(8, "test")

        print ("====== device.char_write_handle() =====")
        in_buf = map(ord, "hello world, hello BLE!!!")
        # send via uuid & handle, maximum is 20 bytes
        device.char_write("c9155f2a-026f-b6bc-cf9b-39aa19b11190", in_buf[:20])
        device.char_write_handle(0x08, in_buf[20:])

        while (True):
            time.sleep(0.1)
    finally:
        adapter.stop()


if __name__ == "__main__":
    # logging.basicConfig()
    # logging.getLogger('pygatt').setLevel(logging.DEBUG)
    pytest()