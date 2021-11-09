import cv2


class face_detection:
    def __init__(self):
        self.detector = cv2.CascadeClassifier(
            "Resources/haarcascade_frontalface_default.xml")
        self.drone = None
    
    def set_drone(self,drone):
        self.drone = drone

    def detect(self, img):
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.faces = self.detector.detectMultiScale(imgGray, 1.1, 4)
        for (x, y, w, h) in self.faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        return (len(self.faces), img)
    
    def drone_detect(self):
        return self.detect(self.drone.get_frame_read().frame)


if __name__ == "__main__":
    test = face_detection()
    img = cv2.imread("naikaku.jpg")
    nop,img = test.detect(img)

    cv2.imshow("Result", img)
    cv2.waitKey(0)
