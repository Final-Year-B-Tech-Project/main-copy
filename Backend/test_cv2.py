import sys
print(f"Python version: {sys.version}")
try:
    import cv2
    print(f"OpenCV version: {cv2.__version__}")
    if hasattr(cv2, 'dnn'):
        print("cv2.dnn exists")
        if hasattr(cv2.dnn, 'DictValue'):
            print("cv2.dnn.DictValue exists")
        else:
            print("ERROR: cv2.dnn.DictValue MISSING")
    else:
        print("ERROR: cv2.dnn MISSING")
except Exception as e:
    print(f"Error importing cv2: {e}")
