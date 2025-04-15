import os
import cv2
import PIL
import numpy as np
import google.generativeai as genai
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from mediapipe.python.solutions import hands, drawing_utils
from dotenv import load_dotenv
import warnings

# Suppress TensorFlow and other warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow logs
warnings.filterwarnings("ignore", category=UserWarning, module='tensorflow')

# Load environment variables
load_dotenv()

# Configure Generative AI Library once
api_key = os.getenv('GOOGLE_API_KEY') 
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("GOOGLE_API_KEY not found. Please check your environment variables.")

class Calculator:
    def __init__(self):  
        # Initialize webcam for video capture and set properties
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 950)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 550)
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, 130)

        # Initialize canvas image
        self.imgCanvas = np.zeros((550, 950, 3), dtype=np.uint8)

        # Initialize MediaPipe Hands object
        self.mphands = hands.Hands(max_num_hands=1, min_detection_confidence=0.75)

        # Initialize drawing origin and time
        self.p1, self.p2 = None, None  # Start without an initial point
        self.drawing = False  # Flag to determine if drawing mode is active

        # Create finger positions list
        self.fingers = []

    def streamlit_config(self):
        # Configure Streamlit page settings
        st.set_page_config(page_title='Calculator', layout="wide")
        page_background_color = """
        <style>
        [data-testid="stHeader"] { background: rgba(0,0,0,0); }
        .block-container { padding-top: 0rem; }
        </style>
        """
        st.markdown(page_background_color, unsafe_allow_html=True)
        st.markdown(f'<h1 style="text-align: center;">Virtual Calculator</h1>', unsafe_allow_html=True)
        add_vertical_space(1)

    def process_frame(self):
        # Capture frame from webcam
        success, img = self.cap.read()
        if not success:
            st.warning("Failed to read from webcam.")
            return None
        img = cv2.resize(img, (950, 550))
        self.img = cv2.flip(img, 1)
        self.imgRGB = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        return self.img

    def process_hands(self):
        # Process hand landmarks and draw them
        result = self.mphands.process(image=self.imgRGB)
        self.landmark_list = []

        if result.multi_hand_landmarks:
            for hand_lms in result.multi_hand_landmarks:
                drawing_utils.draw_landmarks(self.img, hand_lms, hands.HAND_CONNECTIONS)
                for id, lm in enumerate(hand_lms.landmark):
                    h, w, c = self.img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    self.landmark_list.append([id, cx, cy])

    def identify_fingers(self):
        # Identify open/closed fingers
        self.fingers = []
        if self.landmark_list:
            for id in [4, 8, 12, 16, 20]:
                if id != 4:  # Other fingers
                    self.fingers.append(1 if self.landmark_list[id][2] < self.landmark_list[id - 2][2] else 0)
                else:  # Thumb
                    self.fingers.append(1 if self.landmark_list[id][1] < self.landmark_list[id - 2][1] else 0)

    def handle_drawing_mode(self):
        # Handle drawing modes and eraser functionality
        if sum(self.fingers) == 2 and self.fingers[0] == self.fingers[1] == 1:
            # Drawing mode with index finger
            cx, cy = self.landmark_list[8][1], self.landmark_list[8][2]
            if not self.drawing:
                # Start a new drawing, reset points
                self.p1, self.p2 = cx, cy
                self.drawing = True  # Set drawing flag
            cv2.line(self.imgCanvas, (self.p1, self.p2), (cx, cy), (255, 0, 255), 5)
            self.p1, self.p2 = cx, cy  # Update points

        elif sum(self.fingers) == 3 and self.fingers[0] == self.fingers[1] == self.fingers[2] == 1:
            # Condition for analyzing or resetting the points
            self.p1, self.p2 = None, None
            self.drawing = False  # Reset drawing flag

        elif sum(self.fingers) == 2 and self.fingers[0] == self.fingers[2] == 1:
            # Eraser mode with middle finger
            cx, cy = self.landmark_list[12][1], self.landmark_list[12][2]
            if not self.drawing:
                self.p1, self.p2 = cx, cy
                self.drawing = True  # Set drawing flag
            cv2.line(self.imgCanvas, (self.p1, self.p2), (cx, cy), (0, 0, 0), 15)
            self.p1, self.p2 = cx, cy

        elif sum(self.fingers) == 2 and self.fingers[0] == self.fingers[4] == 1:
            # Clear canvas mode with thumb and pinky finger
            self.imgCanvas = np.zeros((550, 950, 3), dtype=np.uint8)
            self.drawing = False  # Reset drawing flag

        else:
            # When no valid drawing mode is detected, reset points
            self.p1, self.p2 = None, None
            self.drawing = False  # Reset drawing flag

    def blend_canvas_with_feed(self):
        # Blend canvas with camera feed
        img = cv2.addWeighted(self.img, 0.7, self.imgCanvas, 1, 0)
        imgGray = cv2.cvtColor(self.imgCanvas, cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, imgInv)
        self.img = cv2.bitwise_or(img, self.imgCanvas)

    def analyze_image_with_genai(self):
        # Analyze the image with GenAI
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')
        imgCanvas = cv2.cvtColor(self.imgCanvas, cv2.COLOR_BGR2RGB)
        imgCanvas = PIL.Image.fromarray(imgCanvas)
        prompt = ("Analyze the image and provide the following:\n"
                  "* The mathematical equation represented in the image.\n"
                  "* The solution to the equation.\n"
                  "* A short and sweet explanation of the steps taken to arrive at the solution.")
        response = model.generate_content([prompt, imgCanvas])
        return response.text if response else "No response from AI model."

    def run(self):
        # Streamlit UI for controlling the flow
        if st.button('Start Drawing'):
            self.run_drawing_mode()

        # Release the webcam on close
        self.cap.release()
        cv2.destroyAllWindows()

    def run_drawing_mode(self):
        col1, _, col3 = st.columns([0.8, 0.02, 0.18])
        with col1:
            stframe = st.empty()
        with col3:
            st.markdown(f'<h5 style="text-position:center;color:green;">OUTPUT:</h5>', unsafe_allow_html=True)
            result_placeholder = st.empty()

        while True:
            # Read the frames and process hands detection
            img = self.process_frame()
            if img is None:
                break
            self.process_hands()
            self.identify_fingers()
            self.handle_drawing_mode()
            self.blend_canvas_with_feed()
            stframe.image(self.img, channels="RGB")

            # If AI processing condition is met, analyze image
            if sum(self.fingers) == 5:  # All fingers up
                result_placeholder.text("Analyzing...")
                analysis_result = self.analyze_image_with_genai()
                result_placeholder.text(analysis_result)
                self.imgCanvas = np.zeros((550, 950, 3), dtype=np.uint8)

def main():
    calculator = Calculator()
    calculator.streamlit_config()
    calculator.run()

if __name__ == "__main__":
    main()


