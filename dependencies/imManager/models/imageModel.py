from PIL import Image
from io import BytesIO


class ImageModel:

    def __init__(self):
        # Defines images size
        self.image_width = 400
        self.image_height = 300

    def merge_images(self, img1, img2):
        merged_image = Image.new("RGB", (self.image_width * 2, self.image_height))

        # Defines the images size
        img1.thumbnail((self.image_width, self.image_height), Image.ANTIALIAS)
        img2.thumbnail((self.image_width, self.image_height), Image.ANTIALIAS)

        merged_image.paste(img1)
        merged_image.paste(img2, (self.image_width, 0))

        merged_image.show()

        return merged_image.tobytes()

    @staticmethod
    def convert_bytes_to_image(image_request_bytes):
        try:
            return Image.open(BytesIO(image_request_bytes))
        except IOError as e:
            print("== Unable to convert Bytes to Image ==")
            print(e)
            print("== End of Exception ==")
            return False

