tracks = {
    1: {
        "position": 2.0,
        "velocity": 1.0,
        "missed": 0,
        "history": [2.0],
    }
}

predictions = {}
for track_id, track in tracks.items():
    predictions[track_id] = (
        track["position"] + track["velocity"] * 1.0
    )

track_id = 1
track = tracks[track_id]
track["missed"] += 1
track["position"] = predictions[track_id]
track["history"].append(None)

assert predictions[1] == 3.0
assert tracks[1]["position"] == 3.0
assert tracks[1]["history"] == [2.0, None]

print("Predicted position after a missed frame:",
      tracks[1]["position"])
