# USAGE
# python movie_mood.py --input "http://192.168.0.30:8000/video.mjpg"

# import the necessary packages
import argparse
import imutils
import time
import cv2
import numpy as np

from imutils.video import FPS
from imutils.video import WebcamVideoStream

from phue import Bridge
from rgbxy import Converter

def rgb_to_hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = (df/mx)*100
    v = mx*100
    return h, s, v

hue_brige = Bridge('192.168.0.3')#
converter = Converter()
# If the app is not registered and the button is not pressed,
# press the button and call connect() (this only needs to be run a single time)
#hue_brige.connect()

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True,
	help="path to input video")
ap.add_argument("-c", "--crop", type=str, default="0 0 0 0",
                help="size and position of TV screen in image (x y w h)")
ap.add_argument("-y", "--display", type=int, default=1,
	help="whether or not to display output frame to screen")
ap.add_argument("-l", "--light",
                help="Hue light name to adjust", required=True)
ap.add_argument("-s", "--skip_frames" , type=int, default=1000,
        help="number of frames to skip")
args = vars(ap.parse_args())

# start the file video stream thread and allow the buffer to
# start to fill
print("[INFO] starting video file thread...")
stream = WebcamVideoStream(src=args["input"]).start()
fps = FPS().start()
time.sleep(1.0)

if (args["crop"] is not None):
    crop_size_split = args["crop"].split()
    img_x = int(crop_size_split[0])
    img_y = int(crop_size_split[1])
    img_w = int(crop_size_split[2])
    img_h = int(crop_size_split[3])

light_names = args["light"].split(",")
print(light_names)

if (args["skip_frames"] is not None):
    reset_rate = args["skip_frames"]

x = 0
y = 0
prevx = 0
prevy = 0

# loop over frames from the video file stream
while True:
    
    fps.update()
    #print(fps._numFrames)
    #if (fps._numFrames > reset_rate):
    #    fps.stop()
    #    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
    #    fps._numFrames = 0
    #    stream = WebcamVideoStream(src=args["input"]).start()
    #    fps.start()

    frame = stream.read()
    print(frame.shape)

    # crop image area for TV screen
    print(img_x,img_y,img_w,img_h)
    crop_img = frame[img_y:img_y+img_h, img_x:img_x+img_w]

    #find mean pixel value
    mean, stddev = cv2.meanStdDev(crop_img)
    b = int(mean[0])
    g = int(mean[1])
    r = int(mean[2])
    print("BGR: ",b,g,r)

    #convert to hue xy colorspace
    x,y = converter.rgb_to_xy(r, g, b)

    print(x,y)

    print(abs(prevx-x),abs(prevy-y))

    if ((abs(prevx-x) > 0.03) or (abs(prevy-y) > 0.03)):
        print("setting hue")
        prevx = x
        prevy = y

        #set hue light to mean hsv
        for light_name in light_names:
            hue_brige.set_light(light_name,'xy',[x,y])
            #hue_brige.set_light(light_name,'bri',30)

    colour_image = np.zeros((img_h,img_w,3), np.uint8)

    colour_image[:] = (b,g,r)      # (B, G, R)

    #print("resizing for processing...")
    # convert the input frame from BGR to RGB then resize it to have
    # a width of 750px (to speedup processing)
    #frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #frame_v_small = imutils.resize(frame_rgb, width=450)
    #frame_small = imutils.resize(frame_rgb, width=750)
    #scaling_v_small = frame_rgb.shape[1] / float(frame_v_small.shape[1])
    #scaling_small = frame_rgb.shape[1] / float(frame_small.shape[1])

    # check to see if we are supposed to display the output frame to
    # the screen
    if args["display"] > 0:
        cv2.imshow("Image_crop", crop_img)
        cv2.imshow("Color_map", colour_image)
        	
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

    #fps.update()

# close the video file pointers
stream.stop()
fps.stop()

