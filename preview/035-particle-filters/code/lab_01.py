import random
from collections import Counter

import matplotlib.pyplot as plt

# A corridor with one colour at each integer position.
WORLD = [
    "red", "green", "blue", "yellow", "red",
    "blue", "green", "yellow", "blue", "red",
    "green", "blue", "yellow", "red", "green",
    "blue", "yellow", "red", "blue", "green"
]

NUMBER_OF_PARTICLES = 400
COMMAND = 2
STEPS = 6

random.seed(7)

# The real robot starts at position 3.
true_position = 3

# Begin with no location preference: particles are spread uniformly.
particles = [
    random.randrange(len(WORLD))
    for _ in range(NUMBER_OF_PARTICLES)
]

history = []
observations = []
diagnostics = []

for step in range(STEPS):
    # Move the real robot with motion noise.
    true_position += COMMAND + random.choice([-1, 0, 1])
    true_position = max(0, min(len(WORLD) - 1, true_position))

    # Predict: move every particle with independent motion noise.
    predicted_particles = []
    for particle in particles:
        moved = particle + COMMAND + random.choice([-1, 0, 1])
        moved = max(0, min(len(WORLD) - 1, moved))
        predicted_particles.append(moved)

    particles = predicted_particles

    # The real sensor samples an observation from the stated
    # four-colour confusion model.
    true_colour = WORLD[true_position]
    colour_choices = ["red", "green", "blue", "yellow"]
    observation_weights = [
        0.85 if colour == true_colour else 0.05
        for colour in colour_choices
    ]
    observation = random.choices(
        colour_choices,
        weights=observation_weights,
        k=1
    )[0]
    observations.append(observation)

    # Update: assign a likelihood to every particle.
    # The observed colour has probability 0.85 if it is the
    # particle's predicted colour; each alternative has probability 0.05.
    weights = []
    for particle in particles:
        if WORLD[particle] == observation:
            weights.append(0.85)
        else:
            weights.append(0.05)

    # These checks verify the particle and weight counts.
    assert len(particles) == NUMBER_OF_PARTICLES
    assert len(weights) == NUMBER_OF_PARTICLES

    # Resampling: high-weight hypotheses are selected more often.
    particles = random.choices(
        particles,
        weights=weights,
        k=NUMBER_OF_PARTICLES
    )

    # Store the post-resampling set for optional history visualizations.
    history.append(list(particles))

    # ESS describes the diversity of support before resampling.
    weight_sum = sum(weights)
    squared_weight_sum = sum(weight * weight for weight in weights)
    effective_sample_size = (
        weight_sum * weight_sum / squared_weight_sum
    )
    diagnostics.append({
        "step": step + 1,
        "observation": observation,
        "effective_sample_size": effective_sample_size
    })

# Verify the simulation produced one particle set per time step.
assert len(history) == STEPS
assert len(observations) == STEPS
assert len(diagnostics) == STEPS

# Estimate the final particle distribution.
particle_mean = sum(particles) / float(len(particles))
particle_mode = Counter(particles).most_common(1)[0][0]
final_ess = diagnostics[-1]["effective_sample_size"]

print("Simulation checks passed.")
print("Number of particles:", NUMBER_OF_PARTICLES)
print("Number of observations:", len(observations))
print("Final particle mean: {:.2f}".format(particle_mean))
print("Final particle mode:", particle_mode)
print("Final pre-resampling ESS: {:.2f}".format(final_ess))

# Draw the final particle distribution and the true position.
plt.figure(figsize=(10, 5))
plt.hist(
    particles,
    bins=range(len(WORLD) + 1),
    align="left",
    rwidth=0.85,
    color="steelblue",
    edgecolor="black"
)
plt.axvline(
    true_position,
    color="crimson",
    linewidth=3,
    label="True robot position"
)
plt.xticks(range(len(WORLD)))
plt.xlabel("Corridor position (cells)")
plt.ylabel("Number of particles")
plt.title("RoboRover particle filter after repeated sensing")
plt.legend()
plt.tight_layout()
plt.show()
