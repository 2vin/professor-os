M = cv2.moments(contour)

if M["m00"] != 0:
    center_x = M["m10"] / M["m00"]
    center_y = M["m01"] / M["m00"]
else:
    center_x = None
    center_y = None
