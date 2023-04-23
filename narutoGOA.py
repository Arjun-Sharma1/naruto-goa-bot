import cv2
import numpy as np
from PIL import ImageGrab
from pynput.keyboard import Key, Controller
from pyautogui import *
import time
import pyautogui
from pywinauto.application import Application
import psutil
from PIL import Image

# displayMousePosition()
characterLocation = (675, 435)
keyboard = Controller()
# Attach to the target application by window title
# app = Application().connect(title="Naruto GOA Gekisen (v9.4.0.198)")

# Get the process ID (PID) of the target application
for proc in psutil.process_iter():
    if 'dreamseeker.exe' in proc.name():
        pid = proc.pid

# Make sure that a matching process was found
if 'pid' not in locals():
    print("Could not find the target process")
    exit()

# Attach to the target application using its PID
app = Application(backend='uia').connect(process=pid)

# Get the main window handle of the application
hwnd = app.window().handle

app.top_window().set_focus()
# Get a reference to the main window
window = app.window()
rect = window.rectangle()
region = (rect.left, rect.top, rect.width(), rect.height())
gameRectangle = (0, 50, 1200, 800)

# Define the region of the screen where the arrow keys are located
arrow_keys_region = (600, 300, 150, 150)  # left, top, width, height

# Define step size for character movement
step_size = 42

# Define all image templates
log_template = cv2.imread('test.png', cv2.IMREAD_GRAYSCALE)
# Read the template images
template_up = cv2.imread('up-arrow.png', cv2.IMREAD_GRAYSCALE)
template_down = cv2.imread('down-arrow.png', cv2.IMREAD_GRAYSCALE)
template_left = cv2.imread('left-arrow.png', cv2.IMREAD_GRAYSCALE)
template_right = cv2.imread('right-arrow.png', cv2.IMREAD_GRAYSCALE)
# Read the new templates for highlighted arrows
template_up_highlighted = cv2.imread(
    'up-arrow-highlighted.png', cv2.IMREAD_GRAYSCALE)
template_down_highlighted = cv2.imread(
    'down-arrow-highlighted.png', cv2.IMREAD_GRAYSCALE)
template_left_highlighted = cv2.imread(
    'left-arrow-highlighted.png', cv2.IMREAD_GRAYSCALE)
template_right_highlighted = cv2.imread(
    'right-arrow-highlighted.png', cv2.IMREAD_GRAYSCALE)

# Check if character is next to object
# displayMousePosition()
directions = ['up', 'down', 'left', 'right']


def findClosestLogToPlayer(template, character_x, character_y):
    print("Finding closest Log to player")
    # press a random arrow key
    pyautogui.press(directions[np.random.randint(0, 4)])
    for i in range(100):
        allObjects = list(locateAllOnScreen(
            template, region=gameRectangle, grayscale=True, confidence=0.65))
        minDistance = (-1, 999)
        for i, objectLoc in enumerate(allObjects):
            distanceToObj = np.sqrt(
                (objectLoc[0] - character_x)**2 + (objectLoc[1] - character_y)**2)
            if distanceToObj < minDistance[1]:
                minDistance = (i, distanceToObj)
        # Find the closest match within the maximum distance
        if minDistance[1] <= 350:
            logLocation = allObjects[minDistance[0]]
            logDistance = minDistance[1]
            print("Distance to log: " + str(logDistance) +
                  " and object position: " + str(logLocation))
            return (logDistance, logLocation)
        else:
            # Move in a random direction
            pyautogui.press(directions[np.random.randint(0, 4)])
        time.sleep(3)
    print("No matches within maximum distance.")
    exit()


def hitLog():
    print("Hitting log")
    time.sleep(0.5)
    for _ in range(1000):
        screenshot = pyautogui.screenshot(region=arrow_keys_region)
        np_screenshot = np.array(screenshot)

        # Take a screenshot and convert it to grayscale
        # Convert the image to grayscale
        gray = cv2.cvtColor(np_screenshot, cv2.COLOR_BGR2GRAY)

        # Perform template matching for each arrow key
        result_up = cv2.matchTemplate(gray, template_up, cv2.TM_CCOEFF_NORMED)
        result_down = cv2.matchTemplate(
            gray, template_down, cv2.TM_CCOEFF_NORMED)
        result_left = cv2.matchTemplate(
            gray, template_left, cv2.TM_CCOEFF_NORMED)
        result_right = cv2.matchTemplate(
            gray, template_right, cv2.TM_CCOEFF_NORMED)
        # Perform template matching for the new highlighted arrow templates
        result_up_highlighted = cv2.matchTemplate(
            gray, template_up_highlighted, cv2.TM_CCOEFF_NORMED)
        result_down_highlighted = cv2.matchTemplate(
            gray, template_down_highlighted, cv2.TM_CCOEFF_NORMED)
        result_left_highlighted = cv2.matchTemplate(
            gray, template_left_highlighted, cv2.TM_CCOEFF_NORMED)
        result_right_highlighted = cv2.matchTemplate(
            gray, template_right_highlighted, cv2.TM_CCOEFF_NORMED)

        # Set a threshold for the template matching score
        threshold = 0.64

        # Find the location of each arrow key
        location_up = np.where(result_up >= threshold)
        location_down = np.where(result_down >= threshold)
        location_left = np.where(result_left >= threshold)
        location_right = np.where(result_right >= threshold)
        location_up_highlighted = np.where(result_up_highlighted >= threshold)
        location_down_highlighted = np.where(
            result_down_highlighted >= threshold)
        location_left_highlighted = np.where(
            result_left_highlighted >= threshold)
        location_right_highlighted = np.where(
            result_right_highlighted >= threshold)

        # Combine the locations and templates
        locations = [
            location_up, location_down, location_left, location_right,
            location_up_highlighted, location_down_highlighted, location_left_highlighted, location_right_highlighted
        ]
        templates = [
            template_up, template_down, template_left, template_right,
            template_up_highlighted, template_down_highlighted, template_left_highlighted, template_right_highlighted
        ]
        # if all locations values are below the threshold, no match is found
        if all([val < threshold for val in [result_up.max(), result_down.max(), result_left.max(), result_right.max()]]):
            print("No match found above the threshold.")
            time.sleep(0.5)
            return

        def brightness_difference(image, location, template, matched_score):
            if location[0].size == 0:
                return -1  # Return -1 if no match is found above the threshold

            # Get the first match's coordinates
            y, x = location[0][0], location[1][0]
            h, w = template.shape
            cropped_image = image[y:y+h, x:x+w]
            mean_brightness = np.mean(cropped_image)
            return matched_score - mean_brightness

        matched_scores = [
            np.max(result_up), np.max(result_down), np.max(
                result_left), np.max(result_right),
            np.max(result_up_highlighted), np.max(result_down_highlighted), np.max(
                result_left_highlighted), np.max(result_right_highlighted)
        ]

        brightness_differences = [
            brightness_difference(gray, loc, tmpl, score)
            for loc, tmpl, score in zip(locations, templates, matched_scores)
        ]
        highest_difference_index = np.argmax(brightness_differences) % 4

        highlighted_arrow = directions[highest_difference_index]
        # print(f"The highlighted arrow is pointing {highlighted_arrow}.")

        highlighted_image = gray.copy()
        colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0)]

        for idx, location in enumerate(locations):
            idx = idx % 4  # There are 4 non-highlighted arrows
            w, h = templates[idx].shape[::-1]
            color = colors[idx]
            for pt in zip(*location[::-1]):
                cv2.rectangle(highlighted_image, pt,
                              (pt[0] + w, pt[1] + h), color, 2)

        pyautogui.press(highlighted_arrow)
        time.sleep(0.05)
        # Show the highlighted image
        # cv2.imshow('Highlighted Image', highlighted_image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # time.sleep(2)


def is_next_to_object(character_x, character_y, object_x, object_y):
    if abs(character_x - object_x) <= step_size and abs(character_y - object_y) <= step_size:
        return True
    else:
        return False


def goToClosestLogToPlayer():
    character_x, character_y = characterLocation

    closestLog = findClosestLogToPlayer(log_template, character_x, character_y)
    closetLogX = closestLog[1][0] + 15
    closetLogY = closestLog[1][1] + 20
    moveAttempts = 0
    currDistanceToLog = closestLog[0]
    print("attempting to go to closest log")
    while currDistanceToLog > step_size + 5 and moveAttempts < 8:
        print("move attempt: " + str(moveAttempts) + ", distance to log: " + str(currDistanceToLog))
        moveAttempts += 1
        currDistanceToLog = np.sqrt(
            (closetLogX - character_x)**2 + (closetLogY - character_y)**2)
        # Horizontal Movements
        if character_x + 5 < closetLogX:
            keyboard.press(Key.right)
            time.sleep(0.1)
            keyboard.release(Key.right)
            character_x += step_size
        elif character_x - 5 > closetLogX:
            keyboard.press(Key.left)
            time.sleep(0.1)
            keyboard.release(Key.left)
            character_x -= step_size
        time.sleep(1)
        # Vertical Movements
        if character_y + 5 < closetLogY:
            keyboard.press(Key.down)
            time.sleep(0.1)
            keyboard.release(Key.down)
            character_y += step_size
        elif character_y - 5 > closetLogY:
            keyboard.press(Key.up)
            time.sleep(0.1)
            keyboard.release(Key.up)
            character_y -= step_size

    time.sleep(0.5)

    # Start hitting the Log
    if currDistanceToLog <= step_size:
        print("At log")
        time.sleep(0.5)
        keyboard.press(Key.space)
        time.sleep(0.1)
        keyboard.release(Key.space)
        hitLog()


# Main loop
while True:
    goToClosestLogToPlayer()
