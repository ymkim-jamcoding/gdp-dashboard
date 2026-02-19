import streamlit as st
from streamlit_webrtc import VideoProcessorBase, webrtc_streamer
from pathlib import Path
import cv2


@st.cache_resource
def get_cascades():
    face_cascade = cv2.CascadeClassifier(
        str(Path(cv2.data.haarcascades) / 'haarcascade_frontalface_default.xml')
    )
    eye_cascade = cv2.CascadeClassifier(
        str(Path(cv2.data.haarcascades) / 'haarcascade_eye.xml')
    )
    return face_cascade, eye_cascade


class EyeTrackerProcessor(VideoProcessorBase):
    def __init__(self):
        self.face_cascade, self.eye_cascade = get_cascades()

    def recv(self, frame):
        img = frame.to_ndarray(format='bgr24')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
        overlay = img.copy()

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y + h, x:x + w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=6)

            for (ex, ey, ew, eh) in eyes:
                x1 = x + ex
                y1 = y + ey
                x2 = x + ex + ew
                y2 = y + ey + eh
                cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), -1)
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 200, 0), 2)

        cv2.addWeighted(overlay, 0.35, img, 0.65, 0, img)
        return frame.from_ndarray(img, format='bgr24')


def render_eye_tracking():
    st.title('Eye Tracking')
    st.caption('Allow camera access to highlight your eyes in green.')

    webrtc_streamer(
        key='eye-tracking',
        video_processor_factory=EyeTrackerProcessor,
        media_stream_constraints={'video': True, 'audio': False},
        async_processing=True,
    )
