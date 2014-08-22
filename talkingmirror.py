import cv2.cv as cv
import sys
import time
import random
import os
from twitter import *
import argparse


# Parameters for haar detection
# From the API:
# The default parameters (scale_factor=2, min_neighbors=3, flags=0) are tuned
# for accurate yet slow object detection. For a faster operation on real video
# images the settings are:
# scale_factor=1.2, min_neighbors=2, flags=CV_HAAR_DO_CANNY_PRUNING,
# min_size=<minimum possible face size

#opencv
min_size = (5,5)
haar_scale = 1.2
min_neighbors = 2
haar_flags = 0
smallwidth = 90

#args
opencv_preview = False
verbose = False
run_mode = 0


def detect_and_draw(img, face_cascade):
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

    faces = cv.HaarDetectObjects(small_img, face_cascade, cv.CreateMemStorage(0),
            haar_scale, min_neighbors, haar_flags, min_size)

    if opencv_preview and faces:
         for ((x, y, w, h), n) in faces:
             # the input to cv.HaarDetectObjects was resized, so scale the
             # bounding box of each face and convert it to two CvPoints
             pt1 = (int(x * image_scale), int(y * image_scale))
             pt2 = (int((x + w) * image_scale), int((y + h) * image_scale))
             cv.Rectangle(img, pt1, pt2, cv.RGB(255, 0, 0), 3, 8, 0)
             if verbose:
                print "Face at: ", pt1[0], ",", pt2[0], "\t", pt1[1], ",", pt2[1]

    return True if faces else False


def get_random_tweet():
    usernames = ["pontifex", "BarackObama", "Inspire_Us"]
    random_index = random.randint(0, len(usernames) - 1)
    username = usernames[random_index]
    tweet_index = random.randint(0, 1)
    tweet = t.statuses.user_timeline(screen_name=username)[tweet_index]
    return (tweet["text"]).encode("ascii", "ignore"), (tweet["user"]["name"]).encode("ascii", "ignore")


def speak(text):
    speak_command = './speech.sh "' + text + '"'

    if verbose:
        print speak_command

    if run_mode == 0:
        os.system(speak_command)


def read_random_tweet():
    text, name = get_random_tweet()

    if verbose:
        print "Name: " + name
        print "Text: " + text

    speech_lines = []

    #less than 100 characters in one iteration
    if len(text) < 100:
        speech_lines.append(text)
    else:
        #split into lines less than 100 characters long
        words = text.split()

        current_line = ""

        for word in words:
            future_current_line = word if len(current_line) == 0 else current_line + " " + word

            if len(future_current_line) < 100:
                current_line = future_current_line
            else:
                speech_lines.append(current_line)
                current_line = word

        speech_lines.append(current_line)

    if speech_lines is not None and len(speech_lines) > 0:
        #read the lines
        speak("Tweet by " + name)

        for line in speech_lines:
            speak(line)


def clear_capture_buffer(capture):
    for i in range(4):
        cv.QueryFrame(capture)


if __name__ == "__main__":
    #arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--preview", action="store_true", help="show opencv preview")
    parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")
    parser.add_argument("-r", "--runmode", type=int, default=0, help="run mode: 0 - Raspberry Pi; 1 - Mac")
    args = parser.parse_args()
    opencv_preview = args.preview
    verbose = args.verbose
    run_mode = args.runmode

    if opencv_preview:
        #show window
        print "Press ESC to exit ..."
        cv.NamedWindow('Camera', cv.CV_WINDOW_AUTOSIZE)

    # create capture device
    capture = cv.CreateCameraCapture(0) # assume we want first device
    cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_WIDTH, 320)
    cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_HEIGHT, 240)
    face_cascade = cv.Load("face.xml")
    last_playback_time = 0

    if run_mode == 0:
        #set sound volume
        os.system("amixer sset PCM,0 85%")

    #setup twitter client
    t = Twitter(auth=OAuth("42847711-00HCtUlEc4QSlE4fZ0jcRR362V5dgcIcDcz14Z5ws",
                           "VBBTmH12Fcqp9rKwBi4Szon4skESrGaA9EowBuUO3Yk",
                           "bgSOfSinG0KR4Yi1aP81A",
                           "e3VzkfTzFImVwBWCLosIaK0P9Azx9ixlYAj9Q7pes"))

    if not capture:
        print "Error opening capture device"
        sys.exit(1)

    #main loop
    while True:
        frame = cv.QueryFrame(capture)

        if frame is None:
            break

        if opencv_preview:
            cv.Flip(frame, None, 1)

        found_face = detect_and_draw(frame, face_cascade)

        if opencv_preview:
            cv.ShowImage('Camera', frame)

        if found_face:
            read_random_tweet()
            #buffer needs to be cleared because it stores around 4 more images of the currently captured face
            #which would result into false detection
            clear_capture_buffer(capture)

        if opencv_preview:
            k = cv.WaitKey(100)

            if k == 0x1b: # ESC
                print 'ESC pressed. Exiting ...'
                cv.DestroyWindow("Camera")
                break
