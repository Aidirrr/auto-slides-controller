import cv2
import mediapipe as mp
import pyautogui


class SlideController:
    def __init__(self):
        # Initialize MediaPipe Hand solution
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils

        # Configure hand detection
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        # Gesture recognition parameters
        self.prev_gesture_cooldown = 0
        self.next_gesture_cooldown = 0
        self.cooldown_duration = 30  # Frame cooldown to prevent rapid triggering

        # Notification tracking
        self.notification_duration = 30  # Frames to show notification
        self.current_notification = ""
        self.notification_counter = 0

    def is_swipe_right(self, hand_landmarks):
        """Detect right swipe gesture (next slide)"""
        # Get tip positions of index and thumb
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]

        # Check conditions for right swipe
        return (
            # Index tip is to the right of thumb tip
                index_tip.x > thumb_tip.x and
                # Ensure horizontal movement is significant
                abs(index_tip.x - thumb_tip.x) > 0.1 and
                # Ensure vertical alignment is relatively stable
                abs(index_tip.y - thumb_tip.y) < 0.1
        )

    def is_swipe_left(self, hand_landmarks):
        """Detect left swipe gesture (previous slide)"""
        # Get tip positions of index and thumb
        index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        wrist = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST]

        # Check conditions for left swipe
        return (
            # Index tip is to the left of thumb tip
                index_tip.x < thumb_tip.x and
                # Ensure horizontal movement is significant
                abs(index_tip.x - thumb_tip.x) > 0.1 and
                # Ensure vertical alignment is relatively stable
                abs(index_tip.y - thumb_tip.y) < 0.1
        )

    def control_slides(self):
        # Open webcam
        cap = cv2.VideoCapture(0)

        # Get webcam dimensions
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        while cap.isOpened():
            # Read frame from webcam
            success, image = cap.read()
            if not success:
                break

            # Flip the image horizontally for a later selfie-view display
            image = cv2.flip(image, 1)

            # Convert the BGR image to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Process the image and find hands
            results = self.hands.process(rgb_image)

            # Draw a semi-transparent overlay for notifications
            overlay = image.copy()

            # Draw the hand annotations on the image
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks
                    self.mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS
                    )

                    # Next slide gesture (right swipe)
                    if self.is_swipe_right(hand_landmarks) and self.next_gesture_cooldown <= 0:
                        pyautogui.press('right')
                        print("SLIDE: Next slide")
                        self.current_notification = "NEXT SLIDE >"
                        self.notification_counter = self.notification_duration
                        self.next_gesture_cooldown = self.cooldown_duration

                    # Previous slide gesture (left swipe)
                    elif self.is_swipe_left(hand_landmarks) and self.prev_gesture_cooldown <= 0:
                        pyautogui.press('left')
                        print("SLIDE: Previous slide")
                        self.current_notification = "< PREVIOUS SLIDE"
                        self.notification_counter = self.notification_duration
                        self.prev_gesture_cooldown = self.cooldown_duration

            # Decrement cooldown counters
            self.next_gesture_cooldown = max(0, self.next_gesture_cooldown - 1)
            self.prev_gesture_cooldown = max(0, self.prev_gesture_cooldown - 1)

            # Display persistent notification
            if self.notification_counter > 0:
                # Create a semi-transparent overlay
                cv2.rectangle(overlay, (0, 0), (width, 100), (0, 0, 0), -1)

                # Blend the overlay
                alpha = 0.5
                cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

                # Display notification text
                cv2.putText(image,
                            self.current_notification,
                            (width // 2 - 200, 70),  # Centered text
                            cv2.FONT_HERSHEY_SIMPLEX,  # Font
                            1.5,  # Font scale (increased)
                            (0, 255, 0),  # Color (Green)
                            3)  # Thickness (increased)

                # Decrement notification counter
                self.notification_counter -= 1

            # Display the image
            cv2.imshow('Slide Controller', image)

            # Exit on 'q' key press
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

        # Cleanup
        cap.release()
        cv2.destroyAllWindows()


# Run the slide controller
if __name__ == "__main__":
    controller = SlideController()
    controller.control_slides()