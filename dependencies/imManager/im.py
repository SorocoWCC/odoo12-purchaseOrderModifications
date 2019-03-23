from .controllers import ImageController


class IM:

    def __init__(self, cam1 = {}, cam2 = {}):
        self.initClass = False

        if cam1 and cam2:
            self.imCtrl = ImageController(cam1, cam2)
            self.initClass = True

    def get_image(self):
        if self.initClass:
            return self.imCtrl.get_image()
        else:
            return self.initClass

