import matplotlib.pyplot as plt


def image_shape(image):
    """Return height, width, and number of channels."""
    height = len(image)
    width = len(image[0])
    channels = len(image[0][0])
    return height, width, channels


def average_channels(image):
    """Return the average red, green, and blue values."""
    height, width, channels = image_shape(image)
    totals = [0, 0, 0]

    for row in image:
        for pixel in row:
            for channel in range(channels):
                totals[channel] += pixel[channel]

    number_of_pixels = height * width
    return [
        totals[channel] / number_of_pixels
        for channel in range(channels)
    ]


def normalized_pixel(pixel):
    """Convert an 8-bit RGB pixel to values from 0.0 to 1.0."""
    return [value / 255.0 for value in pixel]


def main():
    # RoboRover's small test image:
    # blue background, one-pixel orange marker, and dark ground.
    sky = (35, 140, 210)
    marker = (230, 150, 40)
    ground = (80, 65, 35)

    image = [
        [sky, sky, sky, sky, sky],
        [sky, sky, marker, sky, sky],
        [ground, ground, ground, ground, ground],
        [ground, ground, ground, ground, ground]
    ]

    height, width, channels = image_shape(image)
    averages = average_channels(image)
    selected_pixel = image[1][2]
    normalized = normalized_pixel(selected_pixel)

    print("Image shape: {} rows x {} columns x {} channels".format(
        height, width, channels
    ))
    print("Average RGB values: {}".format(averages))
    print("Selected pixel at row 1, column 2: {}".format(selected_pixel))
    print("Normalized selected pixel: {}".format(normalized))

    # Verification checks make the important claims executable.
    assert (height, width, channels) == (4, 5, 3)
    assert selected_pixel == marker
    assert normalized == [
        marker[0] / 255.0,
        marker[1] / 255.0,
        marker[2] / 255.0
    ]

    expected_averages = [
        (9 * sky[0] + marker[0] + 10 * ground[0]) / 20.0,
        (9 * sky[1] + marker[1] + 10 * ground[1]) / 20.0,
        (9 * sky[2] + marker[2] + 10 * ground[2]) / 20.0
    ]
    assert averages == expected_averages

    # Matplotlib accepts the nested RGB structure as image data.
    plt.figure(figsize=(7, 4))
    plt.imshow(image, interpolation="nearest")
    plt.title("RoboRover's RGB pixel array")
    plt.xlabel("Column index")
    plt.ylabel("Row index")
    plt.xticks(range(width))
    plt.yticks(range(height))
    plt.grid(True, color="white", linewidth=0.8)
    plt.show()


if __name__ == "__main__":
    main()
