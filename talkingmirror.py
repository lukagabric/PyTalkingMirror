import cv2.cv as cv
import sys
import time
import pygame
import random
import os
from twitter import *

# Parameters for haar detection
# From the API:
# The default parameters (scale_factor=2, min_neighbors=3, flags=0) are tuned
# for accurate yet slow object detection. For a faster operation on real video
# images the settings are:
# scale_factor=1.2, min_neighbors=2, flags=CV_HAAR_DO_CANNY_PRUNING,
# min_size=<minimum possible face size

min_size = (5,5)
haar_scale = 1.2
min_neighbors = 2
haar_flags = 0

smallwidth = 90

def detect_and_draw(img, faceCascade):
    gray = cv.CreateImage((img.width,img.height), 8, 1)
    image_scale = img.width / smallwidth

    small_img = cv.CreateImage((cv.Round(img.width / image_scale), cv.Round (img.height / image_scale)), 8, 1)
    # gray = cv.CreateImage((img.width,img.height), 8, 1)
    image_scale = img.width / smallwidth
    # small_img = cv.CreateImage((cv.Round(img.width / image_scale), cv.Round (img.height / image_scale)), 8, 1)

    # convert color input image to grayscale
    cv.CvtColor(img, gray, cv.CV_BGR2GRAY)

    # scale input image for faster processing
    cv.Resize(gray, small_img, cv.CV_INTER_LINEAR)

    cv.EqualizeHist(small_img, small_img)

    faces = cv.HaarDetectObjects(small_img, faceCascade, cv.CreateMemStorage(0),
            haar_scale, min_neighbors, haar_flags, min_size)

    # if faces:
    #     for ((x, y, w, h), n) in faces:
    #         # the input to cv.HaarDetectObjects was resized, so scale the
    #         # bounding box of each face and convert it to two CvPoints
    #         pt1 = (int(x * image_scale), int(y * image_scale))
    #         pt2 = (int((x + w) * image_scale), int((y + h) * image_scale))
    #         cv.Rectangle(img, pt1, pt2, cv.RGB(255, 0, 0), 3, 8, 0)
    #         print "Face at: ", pt1[0], ",", pt2[0], "\t", pt1[1], ",", pt2[1]

    return True if faces else False


def play_random_sound():
    rnd = random.randint(0, 1)

    soundName = ""
    if rnd == 0:
        soundName = "birds.wav"
    elif rnd == 1:
        soundName = "door.wav"

    pygame.mixer.music.load(soundName)
    pygame.mixer.music.play()


if __name__ == "__main__":

    #print "Press ESC to exit ..."

    # create windows
    #cv.NamedWindow('Camera', cv.CV_WINDOW_AUTOSIZE)

    # create capture device
    capture = cv.CreateCameraCapture(0) # assume we want first device
    cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_WIDTH, 320)
    cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_HEIGHT, 240)
    faceCascade = cv.Load("face.xml")
    lastPlaybackTime = 0

    os.system("amixer sset PCM,0 85%")
    pygame.mixer.init()

    t = Twitter(auth=OAuth("42847711-00HCtUlEc4QSlE4fZ0jcRR362V5dgcIcDcz14Z5ws",
                           "VBBTmH12Fcqp9rKwBi4Szon4skESrGaA9EowBuUO3Yk",
                           "bgSOfSinG0KR4Yi1aP81A",
                           "e3VzkfTzFImVwBWCLosIaK0P9Azx9ixlYAj9Q7pes"))

    if not capture:
        print "Error opening capture device"
        sys.exit(1)

    while True:
        frame = cv.QueryFrame(capture)

        if frame is None:
            break

        #cv.Flip(frame, None, 1)
        foundFace = detect_and_draw(frame, faceCascade)
        #cv.ShowImage('Camera', frame)
        if foundFace:
            if pygame.mixer.music.get_busy():
                lastPlaybackTime = time.time()
            elif time.time() - lastPlaybackTime > 5:
                text1 = None
                text2 = None

                textToSpeech = ""
                textToSpeech = t.statuses.user_timeline(screen_name="pontifex")[0]["text"]

                if (textToSpeech.len() > 80):
                    text1 = textToSpeech[:80]
                    text2 = textToSpeech[80:]
                else:
                    text1 = textToSpeech


                if text1 is not None:
                    speakCommand = "./speech.sh " + text1
                    os.system(speakCommand)

                if text2 is not None:
                    speakCommand = "./speech.sh " + text2
                    os.system(speakCommand)

                print "done"

       # time.sleep(0.1)

        # k = cv.WaitKey(100)
        #
        # if k == 0x1b: # ESC
        #     print 'ESC pressed. Exiting ...'
        #     cv.DestroyWindow("Camera")  # This may not work on a Mac
        #     break
