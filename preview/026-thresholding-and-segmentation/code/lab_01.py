import math
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


def make_simulated_image(width, height):
    """Create a dark floor with two bright circular marker-like regions."""
    image = []

    for y in range(height):
        row = []

        for x in range(width):
            # Base floor brightness.
            value = 45

            # Add a gentle brightness gradient from left to right.
            value += int(25.0 * x / float(width - 1))

            # Add a bright circular region near the left.
            left_distance = (x - 45) ** 2 + (y - 55) ** 2
            if left_distance < 22 ** 2:
                value = 205

            # Add a second, dimmer circular region near the right.
            right_distance = (x - 115) ** 2 + (y - 75) ** 2
            if right_distance < 18 ** 2:
                value = 135

            # Add a repeatable stripe-like lighting disturbance.
            # This stripe is below both circular regions, so it does
            # not overlap either circle.
            if 100 <= y <= 104 and 20 <= x <= 140:
                value += 25

            value = max(0, min(255, value))
            row.append(value)

        image.append(row)

    return image


def threshold_image(image, threshold):
    """Return a 0/1 mask using the rule intensity >= threshold."""
    mask = []

    for row in image:
        mask_row = []
        for value in row:
            if value >= threshold:
                mask_row.append(1)
            else:
                mask_row.append(0)
        mask.append(mask_row)

    return mask


def count_foreground(mask):
    """Count the number of 1-valued pixels."""
    total = 0

    for row in mask:
        total += sum(row)

    return total


# Verify the worked numerical example.
example_image = [
    [20, 35, 40, 180, 210],
    [25, 45, 155, 190, 205],
    [30, 50, 60, 170, 220],
    [15, 40, 130, 160, 200],
]

example_mask = threshold_image(example_image, 150)
assert count_foreground(example_mask) == 9

pixel_side_mm = 2.0
estimated_area_mm2 = count_foreground(example_mask) * pixel_side_mm ** 2
assert estimated_area_mm2 == 36.0

print("Worked example foreground pixels:", count_foreground(example_mask))
print("Worked example estimated area (mm^2):", estimated_area_mm2)

# Create the simulated camera image.
image = make_simulated_image(160, 120)
initial_threshold = 150
mask = threshold_image(image, initial_threshold)

figure, axes = plt.subplots(1, 2, figsize=(10, 5))
plt.subplots_adjust(bottom=0.22)

axes[0].set_title("Simulated grayscale camera image")
image_display = axes[0].imshow(
    image, cmap="gray", vmin=0, vmax=255, interpolation="nearest"
)
axes[0].axis("off")

axes[1].set_title("Binary mask")
mask_display = axes[1].imshow(
    mask, cmap="gray", vmin=0, vmax=1, interpolation="nearest"
)
axes[1].axis("off")

slider_axis = figure.add_axes([0.20, 0.08, 0.60, 0.04])
threshold_slider = Slider(
    slider_axis,
    "Threshold",
    0,
    255,
    valinit=initial_threshold,
    valstep=1
)


def update_display(new_threshold):
    new_mask = threshold_image(image, int(new_threshold))
    foreground_pixels = count_foreground(new_mask)
    total_pixels = len(image) * len(image[0])
    foreground_percentage = 100.0 * foreground_pixels / total_pixels

    mask_display.set_data(new_mask)
    axes[1].set_title(
        "Binary mask: {} pixels ({:.2f}%)".format(
            foreground_pixels,
            foreground_percentage
        )
    )
    figure.canvas.draw_idle()


threshold_slider.on_changed(update_display)

update_display(initial_threshold)
plt.show()
