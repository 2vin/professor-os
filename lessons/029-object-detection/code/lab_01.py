import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Each detection uses:
# class name, (left, top, right, bottom) in pixels, confidence.
detections = [
    ("crate", (180, 120, 340, 300), 0.86),
    ("cone", (390, 170, 455, 315), 0.73),
    ("beacon", (500, 80, 580, 190), 0.42),
]

threshold = 0.60

accepted = []
for class_name, box, confidence in detections:
    if confidence >= threshold:
        accepted.append((class_name, box, confidence))

# Verify exact simulation facts used in the lesson.
assert len(accepted) == 2
assert accepted[0][0] == "crate"
assert accepted[1][0] == "cone"

crate_box = accepted[0][1]
crate_center_x = (crate_box[0] + crate_box[2]) / 2.0
crate_center_y = (crate_box[1] + crate_box[3]) / 2.0

assert crate_center_x == 260.0
assert crate_center_y == 210.0

print("Confidence threshold:", threshold)
print("Accepted detections:", len(accepted))
print("Accepted classes:", [item[0] for item in accepted])
print("Crate center: ({:.0f} px, {:.0f} px)".format(
    crate_center_x, crate_center_y
))

# Draw a simple camera image.
fig, ax = plt.subplots(figsize=(8, 5))
ax.set_xlim(0, 640)
ax.set_ylim(480, 0)  # Image coordinates: y increases downward.
ax.set_aspect("equal")
ax.set_title("RoboRover's simulated object detections")
ax.set_xlabel("x position (pixels)")
ax.set_ylabel("y position (pixels)")

colors = {
    "crate": "royalblue",
    "cone": "darkorange",
    "beacon": "crimson",
}

for class_name, box, confidence in detections:
    left, top, right, bottom = box
    width = right - left
    height = bottom - top

    # Dashed boxes show candidates that fail the threshold.
    linestyle = "-" if confidence >= threshold else "--"
    alpha = 1.0 if confidence >= threshold else 0.45

    rectangle = Rectangle(
        (left, top),
        width,
        height,
        fill=False,
        linewidth=2,
        linestyle=linestyle,
        edgecolor=colors[class_name],
        alpha=alpha,
    )
    ax.add_patch(rectangle)

    label = "{} {:.2f}".format(class_name, confidence)
    ax.text(
        left,
        max(15, top - 5),
        label,
        color=colors[class_name],
        alpha=alpha,
    )

# Mark the image center.
ax.plot(320, 240, "k+", markersize=10, label="image center")
ax.legend(loc="lower left")
plt.tight_layout()
plt.show()
