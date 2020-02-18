from bluepy import btle
 
print("Connecting...")
dev = btle.Peripheral("00:0A:E2:64:C1:00")
 
print("Services...")
for svc in dev.services:
    print(str(svc))

