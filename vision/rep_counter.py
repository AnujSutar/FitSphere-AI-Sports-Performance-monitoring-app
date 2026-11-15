"""CPU-friendly MediaPipe Pose squat counter. Camera is opened only after explicit user action."""
import math

class SquatCounter:
    def __init__(self, down_angle=100, up_angle=160):
        self.down_angle=down_angle; self.up_angle=up_angle; self.state='up'; self.repetitions=0
    @staticmethod
    def knee_angle(hip,knee,ankle):
        a=(hip[0]-knee[0],hip[1]-knee[1]); b=(ankle[0]-knee[0],ankle[1]-knee[1])
        denom=math.hypot(*a)*math.hypot(*b)
        if not denom: return None
        return math.degrees(math.acos(max(-1,min(1,(a[0]*b[0]+a[1]*b[1])/denom))))
    def update(self,angle):
        if angle is None: return self.repetitions,self.state,'Step into frame'
        if self.state=='up' and angle<=self.down_angle:
            self.state='down'
        elif self.state=='down' and angle>=self.up_angle:
            self.state='up'; self.repetitions+=1
        return self.repetitions,self.state,('Stand tall' if self.state=='up' else 'Squat detected')

def run_camera():
    """Streamlit rerun-loop camera mode; returns graceful error string when unavailable."""
    try:
        import cv2
        import mediapipe as mp
        import streamlit as st
    except ImportError as exc:
        return f'Camera counter dependency missing: {exc.name}. Install OpenCV and a MediaPipe package compatible with your Python version.'
    cap=cv2.VideoCapture(0)
    if not cap.isOpened():
        cap.release(); return 'Camera could not be opened. Check device availability and camera permission.'
    pose=mp.solutions.pose.Pose(model_complexity=0,min_detection_confidence=.55,min_tracking_confidence=.5)
    draw=mp.solutions.drawing_utils; counter=SquatCounter(); frame_slot=st.empty(); metrics=st.empty(); stop=st.button('Stop camera',key='stop_squat_camera')
    try:
        while not stop:
            ok,frame=cap.read()
            if not ok: st.error('Camera frame unavailable.'); break
            frame=cv2.flip(frame,1); rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB); result=pose.process(rgb)
            angle=None
            if result.pose_landmarks:
                lm=result.pose_landmarks.landmark; P=mp.solutions.pose.PoseLandmark
                # Use the more visible side; visibility threshold avoids counting from occluded joints.
                side=P.RIGHT_HIP if lm[P.RIGHT_HIP].visibility>=lm[P.LEFT_HIP].visibility else P.LEFT_HIP
                knee=P.RIGHT_KNEE if side==P.RIGHT_HIP else P.LEFT_KNEE; ankle=P.RIGHT_ANKLE if side==P.RIGHT_HIP else P.LEFT_ANKLE
                if min(lm[side].visibility,lm[knee].visibility,lm[ankle].visibility)>.55:
                    angle=counter.knee_angle((lm[side].x,lm[side].y),(lm[knee].x,lm[knee].y),(lm[ankle].x,lm[ankle].y))
                draw.draw_landmarks(frame,result.pose_landmarks,mp.solutions.pose.POSE_CONNECTIONS)
            reps,state,feedback=counter.update(angle)
            cv2.putText(frame,f'Squats: {reps}  |  {feedback}',(18,35),cv2.FONT_HERSHEY_SIMPLEX,.8,(80,210,255),2)
            frame_slot.image(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB),channels='RGB'); metrics.caption(f'Repetitions: {reps} · Knee angle: {angle:.0f}°' if angle is not None else f'Repetitions: {reps} · {feedback}')
            stop=st.button('Stop camera',key=f'stop_squat_{reps}_{state}')
    finally:
        cap.release(); pose.close()
    return None
