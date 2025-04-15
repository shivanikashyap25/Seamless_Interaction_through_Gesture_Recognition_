# import mediapipe as mp
# import cv2
# import numpy as np
# import math

# # Constants
# ml = 150
# color_panel_width = 50
# color_panel_height = 450  # Adjusted for more colors in vertical
# shape_panel_height = 50  # Increased height for shapes panel
# curr_tool = None
# curr_color = (0, 0, 0)
# curr_thickness = 4
# rad = 40
# var_inits = False
# prevx, prevy = 0, 0
# undo_stack = []
# redo_stack = []

# # Define panel size for tools
# tool_panel_height = len(["DRAW", "LINE", "RECTANGLE", "CIRCLE", "ELLIPSE", "TRIANGLE", "POLYGON", "STAR", "ERASER"]) * 50
# tools = ["DRAW", "LINE", "RECTANGLE", "CIRCLE", "ELLIPSE", "TRIANGLE", "POLYGON", "STAR", "ERASER"]
# tool_panel_width = 50

# # Define the eraser size
# eraser_size = 20  # Adjust this size as needed

# # Helper functions
# def getTool(y):
#     index = y // 50
#     if index < len(tools):
#         return tools[index]
#     return "none"

# def index_raised(yi, y9):
#     return (y9 - yi) > 40

# def save_undo():
#     if len(undo_stack) > 10:
#         undo_stack.pop(0)
#     undo_stack.append(mask.copy())
#     if redo_stack:
#         redo_stack.clear()

# def undo():
#     if undo_stack:
#         redo_stack.append(mask.copy())
#         return undo_stack.pop()
#     return mask

# def redo():
#     if redo_stack:
#         undo_stack.append(mask.copy())
#         return redo_stack.pop()
#     return mask

# hands = mp.solutions.hands
# hand_landmark = hands.Hands(min_detection_confidence=0.6, min_tracking_confidence=0.6, max_num_hands=1)
# draw = mp.solutions.drawing_utils

# mask = np.ones((480, 640, 3)) * 255
# mask = mask.astype('uint8')

# # Create color selection panel
# color_panel = np.zeros((color_panel_height, color_panel_width, 3), dtype="uint8")
# colors = [
#     (0, 0, 0), (255, 255, 255), (0, 0, 255), (255, 0, 0), (0, 255, 0),  # Black, White, Red, Blue, Green
#     (0, 255, 255), (255, 255, 0), (255, 0, 255), (128, 128, 128)  # Yellow, Cyan, Magenta, Gray
# ]
# color_names = ["Black", "White", "Red", "Blue", "Green", "Yellow", "Cyan", "Magenta", "Gray"]
# for i, color in enumerate(colors):
#     cv2.rectangle(color_panel, (0, i * (color_panel_height // len(colors))),
#                   (color_panel_width, (i + 1) * (color_panel_height // len(colors))), color, -1)
#     cv2.putText(color_panel, color_names[i], (10, i * (color_panel_height // len(colors)) + 30),
#                 cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255) if sum(color) < 400 else (0, 0, 0), 1)

# # Create shapes panel
# shapes_panel = np.zeros((tool_panel_height, tool_panel_width, 3), dtype="uint8")
# for i, tool in enumerate(tools):
#     cv2.rectangle(shapes_panel, (0, i * 50), (tool_panel_width, (i + 1) * 50), (200, 200, 200), -1)
#     cv2.putText(shapes_panel, tool, (5, i * 50 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)

# cap = cv2.VideoCapture(0)
# cv2.namedWindow("paint app", cv2.WND_PROP_FULLSCREEN)
# cv2.setWindowProperty("paint app", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# while True:
#     _, frm = cap.read()
#     frm = cv2.flip(frm, 1)

#     # Remove any additional processing to keep the original camera clarity
#     rgb = cv2.cvtColor(frm, cv2.COLOR_BGR2RGB)

#     op = hand_landmark.process(rgb)

#     if op.multi_hand_landmarks:
#         for i in op.multi_hand_landmarks:
#             draw.draw_landmarks(frm, i, hands.HAND_CONNECTIONS)
#             x, y = int(i.landmark[8].x * 640), int(i.landmark[8].y * 480)

#             # Color selection logic
#             if x < color_panel_width:
#                 if y < color_panel_height:
#                     index = y // (color_panel_height // len(colors))
#                     if index < len(colors):
#                         curr_color = colors[index]
#                         print("Selected color:", curr_color)

#             # Shape selection logic
#             elif x > 640 - tool_panel_width:
#                 if y < tool_panel_height:
#                     curr_tool = getTool(y)
#                     print("Current tool set to:", curr_tool)

#             # Drawing logic
#             if curr_tool and curr_color:
#                 xi, yi = int(i.landmark[12].x * 640), int(i.landmark[12].y * 480)
#                 y9 = int(i.landmark[9].y * 480)

#                 if curr_tool == "DRAW" and index_raised(yi, y9):
#                     cv2.line(mask, (prevx, prevy), (x, y), curr_color, curr_thickness)
#                     prevx, prevy = x, y
#                 else:
#                     prevx, prevy = x, y

#                 if curr_tool == "LINE" and index_raised(yi, y9):
#                     if not var_inits:
#                         xii, yii = x, y
#                         var_inits = True
#                     cv2.line(frm, (xii, yii), (x, y), curr_color, curr_thickness * 2)
#                 elif curr_tool == "LINE" and var_inits:
#                     save_undo()
#                     cv2.line(mask, (xii, yii), (x, y), curr_color, curr_thickness * 2)
#                     var_inits = False

#                 if curr_tool == "RECTANGLE" and index_raised(yi, y9):
#                     if not var_inits:
#                         xii, yii = x, y
#                         var_inits = True
#                     cv2.rectangle(frm, (xii, yii), (x, y), curr_color, curr_thickness * 2)
#                 elif curr_tool == "RECTANGLE" and var_inits:
#                     save_undo()
#                     cv2.rectangle(mask, (xii, yii), (x, y), curr_color, curr_thickness * 2)
#                     var_inits = False

#                 if curr_tool == "CIRCLE" and index_raised(yi, y9):
#                     if not var_inits:
#                         xii, yii = x, y
#                         var_inits = True
#                     radius = int(np.sqrt((xii - x) ** 2 + (yii - y) ** 2))
#                     cv2.circle(frm, (xii, yii), radius, curr_color, curr_thickness * 2)
#                 elif curr_tool == "CIRCLE" and var_inits:
#                     save_undo()
#                     radius = int(np.sqrt((xii - x) ** 2 + (yii - y) ** 2))
#                     cv2.circle(mask, (xii, yii), radius, curr_color, curr_thickness * 2)
#                     var_inits = False

#                 if curr_tool == "ELLIPSE" and index_raised(yi, y9):
#                     if not var_inits:
#                         xii, yii = x, y
#                         var_inits = True
#                     axes = (abs(xii - x), abs(yii - y))
#                     cv2.ellipse(frm, (xii, yii), axes, 0, 0, 360, curr_color, curr_thickness * 2)
#                 elif curr_tool == "ELLIPSE" and var_inits:
#                     save_undo()
#                     axes = (abs(xii - x), abs(yii - y))
#                     cv2.ellipse(mask, (xii, yii), axes, 0, 0, 360, curr_color, curr_thickness * 2)
#                     var_inits = False

#                 if curr_tool == "TRIANGLE" and index_raised(yi, y9):
#                     if not var_inits:
#                         xii, yii = x, y
#                         var_inits = True
#                     points = np.array([[xii, yii], [x, y], [xii, y]], np.int32)
#                     cv2.polylines(frm, [points], isClosed=True, color=curr_color, thickness=curr_thickness * 2)
#                 elif curr_tool == "TRIANGLE" and var_inits:
#                     save_undo()
#                     points = np.array([[xii, yii], [x, y], [xii, y]], np.int32)
#                     cv2.polylines(mask, [points], isClosed=True, color=curr_color, thickness=curr_thickness * 2)
#                     var_inits = False

#                 if curr_tool == "POLYGON" and index_raised(yi, y9):
#                     if not var_inits:
#                         points = [(x, y)]
#                         var_inits = True
#                     else:
#                         points.append((x, y))
#                     for p in points:
#                         cv2.circle(frm, p, 3, curr_color, -1)
#                 elif curr_tool == "POLYGON" and not index_raised(yi, y9):
#                     if var_inits and len(points) > 1:
#                         save_undo()
#                         points = np.array(points, np.int32)
#                         cv2.polylines(mask, [points], isClosed=True, color=curr_color, thickness=curr_thickness * 2)
#                         var_inits = False

#                 if curr_tool == "STAR" and index_raised(yi, y9):
#                     if not var_inits:
#                         xii, yii = x, y
#                         var_inits = True
#                     points = []
#                     for j in range(5):
#                         angle = j * (2 * math.pi) / 5
#                         x1 = xii + int((x - xii) * math.cos(angle))
#                         y1 = yii + int((y - yii) * math.sin(angle))
#                         points.append((x1, y1))
#                     cv2.polylines(frm, [np.array(points)], isClosed=True, color=curr_color, thickness=curr_thickness * 2)
#                 elif curr_tool == "STAR" and var_inits:
#                     save_undo()
#                     points = []
#                     for j in range(5):
#                         angle = j * (2 * math.pi) / 5
#                         x1 = xii + int((x - xii) * math.cos(angle))
#                         y1 = yii + int((y - yii) * math.sin(angle))
#                         points.append((x1, y1))
#                     cv2.polylines(mask, [np.array(points)], isClosed=True, color=curr_color, thickness=curr_thickness * 2)
#                     var_inits = False

#                 if curr_tool == "ERASER" and index_raised(yi, y9):
#                     cv2.circle(mask, (x, y), eraser_size, (255, 255, 255), -1)

#     # Apply the color and shapes panels to the frame
#     frm[:color_panel_height, :color_panel_width] = color_panel
#     frm[:tool_panel_height, 640 - tool_panel_width:] = shapes_panel

#     # Merge the drawing mask with the frame
#     op = cv2.bitwise_and(frm, mask, mask=cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY))
#     frm[:, :, 0] = op[:, :, 0]
#     frm[:, :, 1] = op[:, :, 1]
#     frm[:, :, 2] = op[:, :, 2]

#     cv2.putText(frm, f"Tool: {curr_tool}" if curr_tool else "Select Tool", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
#     cv2.putText(frm, f"Color: {curr_color}" if curr_color else "Select Color", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

#     cv2.imshow("paint app", frm)

#     key = cv2.waitKey(1) & 0xFF
#     if key == ord('q') or key == 27:  # 'Q' or ESC key
#         break
#     elif key == ord('z'):
#         mask = undo()
#     elif key == ord('y'):
#         mask = redo()
#     elif key == ord('s') and (cv2.getWindowProperty('paint app', cv2.WND_PROP_FULLSCREEN) == cv2.WINDOW_FULLSCREEN):
#         cv2.imwrite("painted_image.png", mask)
#         print("Image saved as painted_image.png")

# cv2.destroyAllWindows()
# cap.release()
import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
import math

# Constants
ml = 150
color_panel_width = 50
color_panel_height = 450
shape_panel_height = 50
curr_tool = None
curr_color = (0, 0, 0)
curr_thickness = 4
rad = 40
var_inits = False
prevx, prevy = 0, 0
undo_stack = []
redo_stack = []

tool_panel_height = len(["DRAW", "LINE", "RECTANGLE", "CIRCLE", "ELLIPSE", "TRIANGLE", "POLYGON", "STAR", "ERASER"]) * 50
tools = ["DRAW", "LINE", "RECTANGLE", "CIRCLE", "ELLIPSE", "TRIANGLE", "POLYGON", "STAR", "ERASER"]
tool_panel_width = 50
eraser_size = 20

def getTool(y):
    index = y // 50
    if index < len(tools):
        return tools[index]
    return "none"

def index_raised(yi, y9):
    return (y9 - yi) > 40

def save_undo():
    if len(undo_stack) > 10:
        undo_stack.pop(0)
    undo_stack.append(mask.copy())
    if redo_stack:
        redo_stack.clear()

def undo():
    if undo_stack:
        redo_stack.append(mask.copy())
        return undo_stack.pop()
    return mask

def redo():
    if redo_stack:
        undo_stack.append(mask.copy())
        return redo_stack.pop()
    return mask

hands = mp.solutions.hands
hand_landmark = hands.Hands(min_detection_confidence=0.6, min_tracking_confidence=0.6, max_num_hands=1)
draw = mp.solutions.drawing_utils

mask = np.ones((480, 640, 3)) * 255
mask = mask.astype('uint8')

color_panel = np.zeros((color_panel_height, color_panel_width, 3), dtype="uint8")
colors = [
    (0, 0, 0), (255, 255, 255), (0, 0, 255), (255, 0, 0), (0, 255, 0),
    (0, 255, 255), (255, 255, 0), (255, 0, 255), (128, 128, 128)
]
color_names = ["Black", "White", "Red", "Blue", "Green", "Yellow", "Cyan", "Magenta", "Gray"]
for i, color in enumerate(colors):
    cv2.rectangle(color_panel, (0, i * (color_panel_height // len(colors))),
                  (color_panel_width, (i + 1) * (color_panel_height // len(colors))), color, -1)
    cv2.putText(color_panel, color_names[i], (10, i * (color_panel_height // len(colors)) + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255) if sum(color) < 400 else (0, 0, 0), 1)

shapes_panel = np.zeros((tool_panel_height, tool_panel_width, 3), dtype="uint8")
for i, tool in enumerate(tools):
    cv2.rectangle(shapes_panel, (0, i * 50), (tool_panel_width, (i + 1) * 50), (200, 200, 200), -1)
    cv2.putText(shapes_panel, tool, (5, i * 50 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)

cap = cv2.VideoCapture(0)

def main():
    global curr_tool, curr_color, var_inits, prevx, prevy, mask
    st.title("Hand-tracking Paint App")
    st.write("Use the panels to select tool and color, and draw using your hand.")
    
    run = st.checkbox('Run', value=True)
    stframe = st.empty()

    while run:
        _, frm = cap.read()
        frm = cv2.flip(frm, 1)

        rgb = cv2.cvtColor(frm, cv2.COLOR_BGR2RGB)
        op = hand_landmark.process(rgb)

        if op.multi_hand_landmarks:
            for i in op.multi_hand_landmarks:
                draw.draw_landmarks(frm, i, hands.HAND_CONNECTIONS)
                x, y = int(i.landmark[8].x * 640), int(i.landmark[8].y * 480)

                if x < color_panel_width:
                    if y < color_panel_height:
                        index = y // (color_panel_height // len(colors))
                        if index < len(colors):
                            curr_color = colors[index]

                elif x > 640 - tool_panel_width:
                    if y < tool_panel_height:
                        curr_tool = getTool(y)

                if curr_tool and curr_color:
                    xi, yi = int(i.landmark[12].x * 640), int(i.landmark[12].y * 480)
                    y9 = int(i.landmark[9].y * 480)

                    if curr_tool == "DRAW" and index_raised(yi, y9):
                        cv2.line(mask, (prevx, prevy), (x, y), curr_color, curr_thickness)
                        prevx, prevy = x, y
                    else:
                        prevx, prevy = x, y

                    if curr_tool == "LINE" and index_raised(yi, y9):
                        if not var_inits:
                            xii, yii = x, y
                            var_inits = True
                        cv2.line(frm, (xii, yii), (x, y), curr_color, curr_thickness * 2)
                    elif curr_tool == "LINE" and var_inits:
                        save_undo()
                        cv2.line(mask, (xii, yii), (x, y), curr_color, curr_thickness * 2)
                        var_inits = False

                    if curr_tool == "RECTANGLE" and index_raised(yi, y9):
                        if not var_inits:
                            xii, yii = x, y
                            var_inits = True
                        cv2.rectangle(frm, (xii, yii), (x, y), curr_color, curr_thickness * 2)
                    elif curr_tool == "RECTANGLE" and var_inits:
                        save_undo()
                        cv2.rectangle(mask, (xii, yii), (x, y), curr_color, curr_thickness * 2)
                        var_inits = False

                    if curr_tool == "CIRCLE" and index_raised(yi, y9):
                        if not var_inits:
                            xii, yii = x, y
                            var_inits = True
                        radius = int(np.sqrt((xii - x) ** 2 + (yii - y) ** 2))
                        cv2.circle(frm, (xii, yii), radius, curr_color, curr_thickness * 2)
                    elif curr_tool == "CIRCLE" and var_inits:
                        save_undo()
                        radius = int(np.sqrt((xii - x) ** 2 + (yii - y) ** 2))
                        cv2.circle(mask, (xii, yii), radius, curr_color, curr_thickness * 2)
                        var_inits = False

                    if curr_tool == "ELLIPSE" and index_raised(yi, y9):
                        if not var_inits:
                            xii, yii = x, y
                            var_inits = True
                        axes = (abs(xii - x), abs(yii - y))
                        cv2.ellipse(frm, (xii, yii), axes, 0, 0, 360, curr_color, curr_thickness * 2)
                    elif curr_tool == "ELLIPSE" and var_inits:
                        save_undo()
                        axes = (abs(xii - x), abs(yii - y))
                        cv2.ellipse(mask, (xii, yii), axes, 0, 0, 360, curr_color, curr_thickness * 2)
                        var_inits = False

                    if curr_tool == "TRIANGLE" and index_raised(yi, y9):
                        if not var_inits:
                            xii, yii = x, y
                            var_inits = True
                        points = np.array([[xii, yii], [x, y], [xii, y]], np.int32)
                        cv2.polylines(frm, [points], isClosed=True, color=curr_color, thickness=curr_thickness * 2)
                    elif curr_tool == "TRIANGLE" and var_inits:
                        save_undo()
                        points = np.array([[xii, yii], [x, y], [xii, y]], np.int32)
                        cv2.polylines(mask, [points], isClosed=True, color=curr_color, thickness=curr_thickness * 2)
                        var_inits = False

                    if curr_tool == "POLYGON" and index_raised(yi, y9):
                        if not var_inits:
                            points = [(x, y)]
                            var_inits = True
                        else:
                            points.append((x, y))
                        for p in points:
                            cv2.circle(frm, p, 3, curr_color, -1)
                    elif curr_tool == "POLYGON" and not index_raised(yi, y9):
                        if var_inits and len(points) > 1:
                            save_undo()
                            points = np.array(points, np.int32)
                            cv2.polylines(mask, [points], isClosed=True, color=curr_color, thickness=curr_thickness * 2)
                            var_inits = False

                    if curr_tool == "STAR" and index_raised(yi, y9):
                        if not var_inits:
                            xii, yii = x, y
                            var_inits = True
                        points = []
                        for j in range(5):
                            angle = j * (2 * math.pi) / 5
                            x1 = xii + int((x - xii) * math.cos(angle))
                            y1 = yii + int((y - yii) * math.sin(angle))
                            points.append((x1, y1))
                        cv2.polylines(frm, [np.array(points)], isClosed=True, color=curr_color, thickness=curr_thickness * 2)
                    elif curr_tool == "STAR" and var_inits:
                        save_undo()
                        points = []
                        for j in range(5):
                            angle = j * (2 * math.pi) / 5
                            x1 = xii + int((x - xii) * math.cos(angle))
                            y1 = yii + int((y - yii) * math.sin(angle))
                            points.append((x1, y1))
                        cv2.polylines(mask, [np.array(points)], isClosed=True, color=curr_color, thickness=curr_thickness * 2)
                        var_inits = False

                    if curr_tool == "ERASER" and index_raised(yi, y9):
                        cv2.circle(mask, (x, y), eraser_size, (255, 255, 255), -1)

        frm[:color_panel_height, :color_panel_width] = color_panel
        frm[:tool_panel_height, 640 - tool_panel_width:] = shapes_panel

        op = cv2.bitwise_and(frm, mask, mask=cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY))
        frm[:, :, 0] = op[:, :, 0]
        frm[:, :, 1] = op[:, :, 1]
        frm[:, :, 2] = op[:, :, 2]

        cv2.putText(frm, f"Tool: {curr_tool}" if curr_tool else "Select Tool", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(frm, f"Color: {curr_color}" if curr_color else "Select Color", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        # Convert BGR to RGB for Streamlit
        img_rgb = cv2.cvtColor(frm, cv2.COLOR_BGR2RGB)
        stframe.image(img_rgb)

    cap.release()

if __name__ == "__main__":
    main()
