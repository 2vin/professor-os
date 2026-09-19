import cv2
import numpy as np
import matplotlib.pyplot as plt


def main():
    # Create a black 240-by-320 pixel image.
    image = np.zeros((240, 320), dtype=np.uint8)

    # Draw two white filled shapes.
    cv2.rectangle(image, (35, 55), (125, 145), 255, -1)

    triangle = np.array([
        [205, 55],
        [275, 150],
        [155, 150]
    ], dtype=np.int32)
    cv2.fillPoly(image, [triangle], 255)

    # The image is already binary, but thresholding makes the pipeline explicit.
    _, mask = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

    # OpenCV 3 and OpenCV 4 return different numbers of values.
    contour_result = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )
    contours = contour_result[0] if len(contour_result) == 2 else contour_result[1]

    # We expect two separate outer contours in this synthetic image.
    assert len(contours) == 2

    # This is an RGB array. Therefore, drawing colors below use RGB order.
    display = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
    measurements = []

    for contour in contours:
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        x, y, width, height = cv2.boundingRect(contour)

        # Five percent of the perimeter is a moderate approximation tolerance.
        epsilon = 0.05 * perimeter
        polygon = cv2.approxPolyDP(contour, epsilon, True)

        # Calculate the centroid with the required zero-area guard.
        M = cv2.moments(contour)
        if M["m00"] != 0:
            center_x = M["m10"] / M["m00"]
            center_y = M["m01"] / M["m00"]
            centroid = (int(round(center_x)), int(round(center_y)))
        else:
            center_x = None
            center_y = None
            centroid = None

        measurements.append({
            "area": area,
            "perimeter": perimeter,
            "box": (x, y, width, height),
            "corners": len(polygon),
            "centroid": centroid
        })

        # display is RGB: green contour, blue box, magenta centroid.
        cv2.drawContours(display, [contour], -1, (0, 255, 0), 2)
        cv2.rectangle(
            display,
            (x, y),
            (x + width, y + height),
            (0, 0, 255),
            1
        )
        if centroid is not None:
            cv2.circle(display, centroid, 4, (255, 0, 255), -1)

    # Identify the shapes by their measured bounding-box locations rather than
    # relying on the order returned by findContours.
    rectangle_measurement = next(
        item for item in measurements
        if item["box"][0] < 100
    )
    triangle_measurement = next(
        item for item in measurements
        if item["box"][0] >= 100
    )

    # Verify the intended geometric claim directly.
    assert rectangle_measurement["area"] > triangle_measurement["area"]
    assert all(item["centroid"] is not None for item in measurements)

    print("Contours found:", len(contours))
    for index, item in enumerate(measurements):
        print(
            "Contour {}: area={:.1f} pixels^2, perimeter={:.1f} pixels, "
            "box={}, centroid={}, approximated corners={}".format(
                index + 1,
                item["area"],
                item["perimeter"],
                item["box"],
                item["centroid"],
                item["corners"]
            )
        )

    print(
        "Verified: rectangle area ({:.1f}) > triangle area ({:.1f})".format(
            rectangle_measurement["area"],
            triangle_measurement["area"]
        )
    )

    plt.figure(figsize=(8, 5))
    plt.imshow(display)
    plt.title("Contours in green, bounding boxes in blue, centroids in magenta")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
