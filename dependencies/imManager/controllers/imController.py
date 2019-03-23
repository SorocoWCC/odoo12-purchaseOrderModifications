from imManager.models import ImageModel
from imManager.models import WebModel


class ImageController:

    def __init__(self, cam1, cam2):
        self.cam1 = self.set_camera(cam1)
        self.cam2 = self.set_camera(cam2)
        self.webM = WebModel()
        self.imageM = ImageModel()

    def get_image(self):
        img1 = self.get_web_image(self.cam1)
        img2 = self.get_web_image(self.cam2)
        image_bytes = self.imageM.merge_images(img1, img2)
        return image_bytes

    def get_web_image(self, cam):
        image = False;
        request_bytes = self.webM.get_request(cam, True)
        print(request_bytes)

        if request_bytes:
            image = self.imageM.convert_bytes_to_image(request_bytes)

        return image

    def set_camera (self, cam):
        test = self.get_camera_url(cam["ip"], cam["user"], cam["passw"])
        print(test)
        return test

    @staticmethod
    def get_camera_url(ip, user, passw, secure=False):
        protocol = ("http", "https")[secure]
        return protocol + "://" + ip + "/cgi-bin/api.cgi?cmd=Snap&channel=0&rs=wuuPhkmUCeI9WG7C&user=" + user + "&password=" + passw
        # http://192.168.2.32/cgi-bin/api.cgi?cmd=Snap&channel=0&rs=wuuPhkmUCeI9WG7C&user=admin&password=lacapri001
