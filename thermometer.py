import io
import sys
import serial
import random
from time import sleep

filename = "thermometer.py"
ser = None
serio = None
verbose = True  # Set this to True to see all of the incoming serial data


def usage():
    """Displays information on the command-line parameters for this script"""
    print("Usage: " + filename + " <serialPort>\n")
    print("For example:\n")
    print("  Windows : " + filename + " COM14")
    print("  OS X    : " + filename + " /dev/tty.usbserial-DN009WNO")
    print("  Linux   : " + filename + " /dev/ttyACM0")
    return


def checkargs():
    """Validates the command-line arguments for this script"""
    if len(sys.argv) < 2:
        print("ERROR: Missing serialPort")
        usage()
        sys.exit(-1)
    if len(sys.argv) > 2:
        print("ERROR: Too many arguments (expected 1).")
        usage()
        sys.exit(-2)


def errorhandler(err, exitonerror=True):
    """Display an error message and exit gracefully on "ERROR\r\n" responses"""
    print("ERROR: " + err.message)
    if exitonerror:
        ser.close()
        sys.exit(-3)


def atcommand(command, delayms=0):
    """Executes the supplied AT command and waits for a valid response"""
    serio.write(command + "\n")
    if delayms:
        sleep(delayms/1000)
    rx = None
    while rx != "OK\r\n" and rx != "ERROR\r\n":
        rx = serio.readline(2000)
        if verbose:
            print(rx.rstrip("\r\n"))
    # Check the return value
    if rx == "ERROR\r\n":
        raise ValueError("AT Parser reported an error on '" + command.rstrip() + "'")


if __name__ == '__main__':
    # Make sure we received a single argument (comPort)
    checkargs()

    # This will automatically open the serial port (no need for ser.open)
    ser = serial.Serial(port=sys.argv[1], baudrate=9600, rtscts=True)
    serio = io.TextIOWrapper(io.BufferedRWPair(ser, ser, 1),
                             newline='\r\n',
                             line_buffering=True)

    # Add the thermometer service and characteristic definitions
    try:
        atcommand("AT+FACTORYRESET", 1000)  # Wait 1s for this to complete
        atcommand("AT+GATTCLEAR")
        atcommand("AT+GATTADDSERVICE=UUID=0x1809")
        atcommand("AT+GATTADDCHAR=UUID=0x2A1C, PROPERTIES=0x20, MIN_LEN=2, MAX_LEN=3, VALUE=00-40")
        atcommand("AT+GATTADDCHAR=UUID=0x2A1D, PROPERTIES=0x02, MIN_LEN=1, VALUE=00-02")
        atcommand("AT+GATTADDCHAR=UUID=0x2A21, PROPERTIES=0x20, MIN_LEN=1, VALUE=00-00")
        atcommand("AT+GATTADDCHAR=UUID=0x2A19, PROPERTIES=0x10, MIN_LEN=2, VALUE=00-64")
        atcommand("AT+GAPSETADVDATA=00-0a-e2-64-c3-cd-18-0a-18")
        # Perform a system reset and wait 1s to come back online
        atcommand("ATZ", 1000)
        # Update the value every second
        while True:
            atcommand("AT+GATTCHAR=1,00-%02X" % random.randint(50, 100), 1000)
    except ValueError as err:
        # One of the commands above returned "ERROR\n"
        errorhandler(err)
    except KeyboardInterrupt:
        # Close gracefully on CTRL+C
        ser.close()
        sys.exit()
