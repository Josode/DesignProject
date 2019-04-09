# import the necessary packages
from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import time
import cv2
import recyclable_test

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", type=str, default="barcodes.csv",
                help="path to output CSV file containing barcodes")
args = vars(ap.parse_args())

# initialize the video stream and allow the camera sensor to warm up
print("Starting video stream...")
vs = VideoStream(src=1).start()
# Use following line to initialize video stream when using PIq
# vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

# open the output CSV file for writing and initialize the set of
# barcodes found so far
csv = open(args["output"], "w")
found = set()

# used to isolate the constant output of the same item into one single command to the rotating arm.
previous_barcode_data = ""

print("press 'q' to quit.")
# loop over the frames from the video stream
while True:
    # grab the frame from the threaded video stream and resize it to
    # have a maximum width of 400 pixels
    frame = vs.read()
    frame = imutils.resize(frame, width=400)

    # find the barcodes in the frame and decode each of the barcodes
    barcodes = pyzbar.decode(frame)

    # loop over the detected barcodes
    for barcode in barcodes:
        # extract the bounding box location of the barcode and draw
        # the bounding box surrounding the barcode on the image
        (x, y, w, h) = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # the barcode data is a bytes object so if we want to draw it
        # on our output image we need to convert it to a string first
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type

        # run through sorter
        if recyclable_test.is_recyclable(barcodeData) is True and previous_barcode_data != barcodeData:
            print(barcodeData, "is recyclable!")
            # INSERT COMMAND TO TURN PLATFORM ON BIN
        elif recyclable_test.is_recyclable(barcodeData) is None and previous_barcode_data != barcodeData:
            print(barcodeData, "is not recyclable.")
            # INSERT COMMAND TO TURN PLATFORM ON BIN

        # draw the barcode data and barcode type on the image
        text = "{} ({})".format(barcodeData, barcodeType)
        cv2.putText(frame, text, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # if the barcode text is currently not in our CSV file, write
        # the timestamp + barcode to disk and update the set
        if barcodeData not in found:
            csv.write("{},{}\n".format(datetime.datetime.now(),
                                       barcodeData))
            csv.flush()
            found.add(barcodeData)

        previous_barcode_data = barcodeData

    # show the output frame
    cv2.imshow("Blaster Boizz Barcode Scanner", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# close the output CSV file do a bit of cleanup
print("Closing...")
csv.close()
cv2.destroyAllWindows()
vs.stop()