import cv2
import threading
from queue import Queue

def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1920,
    capture_height=1080,
    display_width=960,
    display_height=540,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

def read_camera(camera_id, queue):
    if camera_id.isdigit():
        video_capture = cv2.VideoCapture(int(camera_id))
    elif camera_id == "csi" or camera_id == "CSI":
        print(gstreamer_pipeline(flip_method=0))
        video_capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
    else:
        print("Invalid input for camera ID.")
        return

    if video_capture.isOpened():
        try:
            while True:
                ret_val, frame = video_capture.read()
                if ret_val:
                    # Put the frame into the queue
                    queue.put(frame)
        finally:
            video_capture.release()
    else:
        print(f"Error: Unable to open camera with ID: {camera_id}")

def show_frame(queue):
    while True:
        # Get the frame from the queue
        frame = queue.get()

        # Display the frame
        cv2.imshow("Camera Stream", frame)

        # Check for the 'q' key to quit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Close the window when the loop ends
    cv2.destroyAllWindows()

def main():
    input_source = input("Enter camera index or 'CSI': ")

    # Create a queue for sharing frames between threads
    frame_queue = Queue()

    # Create a thread for reading the camera
    camera_thread = threading.Thread(target=read_camera, args=(input_source, frame_queue))

    # Create a thread for displaying the frame
    display_thread = threading.Thread(target=show_frame, args=(frame_queue,))

    # Start the threads
    camera_thread.start()
    display_thread.start()

    # Wait for the threads to finish
    camera_thread.join()
    display_thread.join()

if __name__ == "__main__":
    main()
