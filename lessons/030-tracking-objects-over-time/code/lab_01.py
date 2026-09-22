import math
import matplotlib.pyplot as plt


def track_detections(frames, dt=1.0, match_threshold=1.5,
                     max_missed=2):
    """Track one-dimensional detections with greedy nearest matching."""
    tracks = {}
    next_track_id = 1
    association_log = []

    for frame_index, detections in enumerate(frames):
        # Predict where every existing track should be in this frame.
        predictions = {}
        for track_id, track in tracks.items():
            predictions[track_id] = (
                track["position"] + track["velocity"] * dt
            )

        # Build every possible track-detection pair within the threshold.
        candidates = []
        for track_id, predicted_position in predictions.items():
            for detection_index, detection in enumerate(detections):
                distance = abs(detection - predicted_position)
                if distance <= match_threshold:
                    candidates.append(
                        (distance, track_id, detection_index)
                    )

        # Greedily accept closest pairs, never reusing a track or detection.
        candidates.sort()
        matched_tracks = set()
        matched_detections = set()

        for distance, track_id, detection_index in candidates:
            if track_id in matched_tracks:
                continue
            if detection_index in matched_detections:
                continue

            detection = detections[detection_index]
            track = tracks[track_id]

            # Estimate velocity using the time since the last successful
            # measurement, not merely the time since the last prediction.
            elapsed_measurements = (
                track["missed"] + 1
            ) * dt
            track["velocity"] = (
                detection - track["last_measured_position"]
            ) / elapsed_measurements
            track["position"] = detection
            track["last_measured_position"] = detection
            track["missed"] = 0
            track["time_since_measurement"] = 0.0
            track["history"].append(detection)

            matched_tracks.add(track_id)
            matched_detections.add(detection_index)
            association_log.append(
                (frame_index, track_id, detection_index)
            )

        # Unmatched tracks survive briefly as propagated predictions.
        tracks_to_delete = []
        for track_id, track in tracks.items():
            if track_id not in matched_tracks:
                track["missed"] += 1
                track["time_since_measurement"] += dt
                track["position"] = predictions[track_id]
                track["history"].append(None)

                if track["missed"] >= max_missed:
                    tracks_to_delete.append(track_id)

        for track_id in tracks_to_delete:
            del tracks[track_id]

        # Any unused detection starts a new track.
        for detection_index, detection in enumerate(detections):
            if detection_index not in matched_detections:
                tracks[next_track_id] = {
                    "position": detection,
                    "last_measured_position": detection,
                    "velocity": 0.0,
                    "missed": 0,
                    "time_since_measurement": 0.0,
                    "history": [None] * frame_index + [detection],
                }
                next_track_id += 1

    return tracks, association_log


frames = [
    [1.1, 7.9],
    [2.0, 7.0],
    [3.1, 6.1],
    [4.0, 5.0],
    [5.0, 4.0],
]

tracks, association_log = track_detections(frames)

# Verification: these are checked by the program, not merely claimed.
assert len(tracks) == 2
assert abs(tracks[1]["position"] - 5.0) < 1e-9
assert abs(tracks[2]["position"] - 4.0) < 1e-9
assert len(association_log) == 8

print("Track 1 final position: {:.1f}".format(tracks[1]["position"]))
print("Track 2 final position: {:.1f}".format(tracks[2]["position"]))
print("Successful associations:", len(association_log))

for track_id in sorted(tracks):
    history = tracks[track_id]["history"]
    x_values = []
    y_values = []
    for frame_index, position in enumerate(history):
        if position is not None:
            x_values.append(frame_index)
            y_values.append(position)
    plt.plot(x_values, y_values, marker="o", label="Track {}".format(track_id))

plt.xlabel("Frame number")
plt.ylabel("Position along line (m)")
plt.title("RoboRover: object tracks over time")
plt.grid(True)
plt.legend()
plt.show()
