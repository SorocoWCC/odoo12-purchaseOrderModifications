from imManager import IM

test = IM({"ip": "192.168.2.32", "user": "admin", "passw": "lacapri001"}, {"ip": "192.168.2.153", "user": "admin", "passw": "lacapri001"})

res = test.get_image()

print(res)
