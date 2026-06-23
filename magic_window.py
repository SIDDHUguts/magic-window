import cv2
import mediapipe as mp
import numpy as np
import time

# --- Configuration Constants ---
SMOOTHING_FACTOR = 0.25 # Smoothing coefficient (0 to 1) for movement (lower = smoother)
CYCLE_INTERVAL = 4.0    # Auto-cycle interval in seconds
TARGET_FPS = 60         # Target frames per second
FRAME_WIDTH = 640       # Capture width
FRAME_HEIGHT = 480      # Capture height

# Min/Max constraints for the magic window size
MIN_WINDOW_SIZE = 100
MAX_WINDOW_SIZE = 500

# --- Custom Filters ---

def apply_invert(roi):
    """
    Applies a high-contrast inverted color (X-ray style) filter.
    """
    return cv2.bitwise_not(roi)

def apply_metallic_emboss(roi):
    """
    Applies a 3D topographical emboss/edge detection filter with a metallic silver look.
    """
    # Convert to grayscale first
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Emboss convolution kernel
    emboss_kernel = np.array([
        [-2, -1,  0],
        [-1,  1,  1],
        [ 0,  1,  2]
    ], dtype=np.float32)
    
    # Filter image
    embossed = cv2.filter2D(gray, -1, emboss_kernel)
    
    # Shift grayscale values and clip to valid uint8 bounds
    embossed_shifted = cv2.add(embossed, 128)
    embossed_clipped = np.clip(embossed_shifted, 0, 255).astype(np.uint8)
    
    # Convert back to BGR for display in the main feed
    return cv2.cvtColor(embossed_clipped, cv2.COLOR_GRAY2BGR)

def apply_ascii_art(roi, cols=22, rows=22):
    """
    Renders the region of interest as a green ASCII art text block over a black background.
    """
    h, w = roi.shape[:2]
    
    # Downsample to get a low-resolution grid
    small = cv2.resize(roi, (cols, rows), interpolation=cv2.INTER_AREA)
    gray_small = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    
    # Create a blank black canvas
    ascii_canvas = np.zeros((h, w, 3), dtype=np.uint8)
    
    # Character map from dark to bright
    chars = " .:-=+*#%@"
    num_chars = len(chars)
    
    cell_w = w / cols
    cell_h = h / rows
    
    for r in range(rows):
        for c in range(cols):
            val = gray_small[r, c]
            
            # Skip dark cells to optimize rendering speed
            if val < 20:
                continue
                
            char_idx = int((val / 255.0) * (num_chars - 1))
            char = chars[char_idx]
            
            # Compute character center coordinates
            x = int(c * cell_w + cell_w * 0.15)
            y = int(r * cell_h + cell_h * 0.8)
            
            # Render character in green (BGR: 0, 255, 0)
            cv2.putText(
                ascii_canvas, char, (x, y), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 255, 0), 1, cv2.LINE_AA
            )
            
    return ascii_canvas

def main():
    # --- MediaPipe Hands Initialization ---
    mp_hands = mp.solutions.hands
    # model_complexity=0 is crucial to keep resource usage minimal and achieve 60 FPS
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,  # Track up to two hands
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    # --- Webcam Initialization ---
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open webcam. Please verify it is connected.")
        return
        
    # Configure capture properties for high frame rate
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, TARGET_FPS)
    
    # Read properties back to verify support
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    camera_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"[INFO] Camera initialized: {actual_width}x{actual_height} @ {camera_fps} FPS target.")
    
    # --- Filter Registry ---
    filters = [
        ("Invert / X-Ray", apply_invert),
        ("Metallic Emboss", apply_metallic_emboss),
        ("ASCII Art", apply_ascii_art)
    ]
    current_filter_idx = 0
    
    # --- State Variables ---
    # Start the magic window in the center of the screen with a default size
    box_center_x = actual_width // 2
    box_center_y = actual_height // 2
    box_size = 220
    
    prev_time = time.time()
    last_cycle_time = time.time()
    fps_display = 0.0
    frame_count = 0
    fps_update_interval = 0.5 # update FPS text every 0.5s to prevent jitter
    fps_last_update = time.time()
    
    # Debouncing state for index-middle finger touch gesture
    prev_trigger_touch_active = False
    
    print("\nControls:")
    print("  [TOUCH Index & Middle Fingers] - Cycle Filter")
    print("  [SPACE] or [C]                 - Cycle Filter (Keyboard)")
    print("  [ESC] or [Q]                   - Exit Application\n")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("[WARNING] Empty camera frame skipped.")
            continue
            
        # Flip the image horizontally for a natural mirror-like reflection
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        # Convert BGR to RGB (MediaPipe expects RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        # Track pinch points of detected hands
        # Pinch point = average of Thumb Tip (Landmark 4) and Index Tip (Landmark 8)
        pinch_points = []
        trigger_touch_active = False  # Track if index-middle touch gesture is active
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Get landmarks
                thumb = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                
                # Convert normalized coords to pixels
                thumb_x, thumb_y = int(thumb.x * w), int(thumb.y * h)
                index_x, index_y = int(index.x * w), int(index.y * h)
                middle_x, middle_y = int(middle.x * w), int(middle.y * h)
                
                # Calculate pinch point (Thumb-Index midpoint)
                pinch_x = (thumb_x + index_x) // 2
                pinch_y = (thumb_y + index_y) // 2
                pinch_points.append((pinch_x, pinch_y))
                
                # Detect Index-Middle Touch Gesture ("Press two fingers")
                # Calculate normalized distance in 2D space
                touch_dist = np.sqrt((index.x - middle.x)**2 + (index.y - middle.y)**2)
                is_touching = touch_dist < 0.038
                
                if is_touching:
                    trigger_touch_active = True
                
                # --- Visual Feedback Drawing ---
                # Draw thumb-index pinch lines (Blue)
                cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (255, 120, 0), 1)
                cv2.circle(frame, (thumb_x, thumb_y), 4, (255, 120, 0), -1)
                cv2.circle(frame, (index_x, index_y), 4, (255, 120, 0), -1)
                
                # Draw green feedback dot at pinch center
                cv2.circle(frame, (pinch_x, pinch_y), 5, (0, 255, 0), -1)
                
                # Draw index-middle touch tracker (Green if touching/switching, Red/Pink if open)
                touch_color = (0, 255, 0) if is_touching else (140, 140, 240)
                touch_thickness = 2 if is_touching else 1
                cv2.line(frame, (index_x, index_y), (middle_x, middle_y), touch_color, touch_thickness)
                cv2.circle(frame, (middle_x, middle_y), 4, touch_color, -1)
                
        # --- Bounding Box Position & Size Solver ---
        target_center_x, target_center_y = box_center_x, box_center_y
        target_size = box_size
        
        num_hands_tracked = len(pinch_points)
        
        if num_hands_tracked == 2:
            # Dual hand logic: center is midpoint between hands, size is distance between hands
            p1, p2 = pinch_points[0], pinch_points[1]
            target_center_x = (p1[0] + p2[0]) // 2
            target_center_y = (p1[1] + p2[1]) // 2
            
            # Compute distance
            hand_distance = np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
            target_size = int(hand_distance)
            
            # Clamp box size to reasonable limits
            target_size = max(MIN_WINDOW_SIZE, min(target_size, MAX_WINDOW_SIZE))
            
            # Draw a dotted connection line between hands in BGR gold/bronze
            cv2.line(frame, p1, p2, (124, 168, 201), 1, cv2.LINE_AA)
            cv2.putText(
                frame, f"Size: {target_size}px", (target_center_x - 35, target_center_y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (124, 168, 201), 1, cv2.LINE_AA
            )
            
        elif num_hands_tracked == 1:
            # Single hand logic: box follows hand, size remains unchanged
            target_center_x, target_center_y = pinch_points[0]
            
        # --- Smooth Motion Filtering ---
        # Apply Exponential Moving Average (EMA) to prevent window size/position jitter
        box_center_x = int(SMOOTHING_FACTOR * target_center_x + (1.0 - SMOOTHING_FACTOR) * box_center_x)
        box_center_y = int(SMOOTHING_FACTOR * target_center_y + (1.0 - SMOOTHING_FACTOR) * box_center_y)
        box_size = int(SMOOTHING_FACTOR * target_size + (1.0 - SMOOTHING_FACTOR) * box_size)
        
        # --- Bounding Box Extraction & Clamping ---
        half_sz = box_size // 2
        
        # Determine ROI corners
        x1 = box_center_x - half_sz
        y1 = box_center_y - half_sz
        x2 = box_center_x + half_sz
        y2 = box_center_y + half_sz
        
        # Clamp bounds to make sure the box doesn't go off-screen (prevents indexing crashes)
        x1 = max(0, min(x1, w - 1))
        y1 = max(0, min(y1, h - 1))
        x2 = max(1, min(x2, w))
        y2 = max(1, min(y2, h))
        
        # --- Gesture-Based Filter Cycling (Edge Trigger) ---
        current_time = time.time()
        if trigger_touch_active and not prev_trigger_touch_active:
            current_filter_idx = (current_filter_idx + 1) % len(filters)
            last_cycle_time = current_time # Reset auto-cycle timer
            
        prev_trigger_touch_active = trigger_touch_active
        
        # --- Auto-Cycle Filter Logic ---
        if current_time - last_cycle_time >= CYCLE_INTERVAL:
            current_filter_idx = (current_filter_idx + 1) % len(filters)
            last_cycle_time = current_time
            
        # --- Apply Selected Filter to ROI ---
        filter_name, filter_func = filters[current_filter_idx]
        
        # Extract the region of interest
        roi = frame[y1:y2, x1:x2]
        
        # If the ROI is valid (size > 0), filter and blend it back
        if roi.size > 0:
            filtered_roi = filter_func(roi)
            frame[y1:y2, x1:x2] = filtered_roi
            
        # --- Draw UI Overlay Elements ---
        # Draw a beautiful gold/bronze border around the magic window
        cv2.rectangle(frame, (x1, y1), (x2, y2), (124, 168, 201), 2)
        
        # Calculate actual FPS
        frame_count += 1
        elapsed = current_time - prev_time
        prev_time = current_time
        
        if current_time - fps_last_update >= fps_update_interval:
            fps_display = frame_count / (current_time - fps_last_update)
            frame_count = 0
            fps_last_update = current_time
            
        # Draw HUD Box (Dark Glass translucent effect using a filled polygon overlay)
        hud_bg = frame.copy()
        cv2.rectangle(hud_bg, (10, 10), (320, 100), (20, 20, 20), -1) # Dark solid box
        # Blend the solid box with the frame to create an elegant semi-transparent glass panel
        cv2.addWeighted(hud_bg, 0.6, frame, 0.4, 0, frame)
        
        # Render HUD texts
        cv2.putText(
            frame, f"Filter: {filter_name}", (20, 35), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA
        )
        
        # Render FPS Tracker (Highlight green if >= 55 FPS, orange if >= 30, red if lower)
        fps_color = (0, 255, 0) if fps_display >= 55 else ((0, 165, 255) if fps_display >= 30 else (0, 0, 255))
        cv2.putText(
            frame, f"FPS: {fps_display:.1f} / {TARGET_FPS} target", (20, 60), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, fps_color, 1, cv2.LINE_AA
        )
        
        # Render quick controls
        cv2.putText(
            frame, "[Touch Index/Middle] Cycle  [ESC] Exit", (20, 85), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1, cv2.LINE_AA
        )
        
        # Show output window
        cv2.imshow("SAmaniacLabs - Magic Window Filter", frame)
        
        # --- Handle Key Inputs ---
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'): # ESC or Q to quit
            break
        elif key == ord(' ') or key == ord('c'): # SPACE or C to cycle filter manually
            current_filter_idx = (current_filter_idx + 1) % len(filters)
            last_cycle_time = current_time # Reset auto-cycle timer
            
    # --- Cleanup ---
    cap.release()
    cv2.destroyAllWindows()
    hands.close()

if __name__ == "__main__":
    main()
