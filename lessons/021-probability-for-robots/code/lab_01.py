import random
import math
import matplotlib.pyplot as plt

# Possible distances in metres.
distances = [0.80, 1.00, 1.20]

# Probabilities for the corresponding distances.
probabilities = [0.20, 0.50, 0.30]

# Calculate the theoretical expected value.
expected_distance = sum(
    distance * probability
    for distance, probability in zip(distances, probabilities)
)

# Calculate the theoretical variance and standard deviation.
variance = sum(
    probability * (distance - expected_distance) ** 2
    for distance, probability in zip(distances, probabilities)
)
standard_deviation = math.sqrt(variance)

# Use a fixed seed so this experiment is repeatable.
random.seed(21)

number_of_trials = 5000
trials = random.choices(
    distances,
    weights=probabilities,
    k=number_of_trials
)

# Count how often each outcome appeared.
counts = []
for distance in distances:
    counts.append(trials.count(distance))

# Convert counts into simulated relative frequencies.
simulated_frequencies = [
    count / number_of_trials
    for count in counts
]

simulated_average = sum(trials) / number_of_trials

print("Theoretical expected distance: {:.3f} m".format(expected_distance))
print("Theoretical standard deviation: {:.3f} m".format(
    standard_deviation
))
print("Simulated average distance: {:.3f} m".format(simulated_average))
print("Counts for 0.80 m, 1.00 m, 1.20 m:", counts)
print("Simulated relative frequencies:", [
    "{:.3f}".format(frequency)
    for frequency in simulated_frequencies
])

# These assertions verify exact claims about the model and program setup.
assert abs(expected_distance - 1.02) < 1e-12
assert abs(standard_deviation - 0.14) < 1e-12
assert len(trials) == number_of_trials
assert sum(counts) == number_of_trials
assert abs(sum(probabilities) - 1.0) < 1e-12
assert abs(sum(simulated_frequencies) - 1.0) < 1e-12

# Plot theoretical probabilities and simulated relative frequencies
# as separate, directly labeled series.
positions = list(range(len(distances)))
bar_width = 0.36

plt.bar(
    [position - bar_width / 2 for position in positions],
    probabilities,
    width=bar_width,
    color="steelblue",
    hatch="//",
    label="Theoretical probability"
)
plt.bar(
    [position + bar_width / 2 for position in positions],
    simulated_frequencies,
    width=bar_width,
    color="white",
    edgecolor="darkorange",
    hatch="..",
    label="Simulated relative frequency"
)

plt.xticks(positions, ["{:.2f} m".format(distance) for distance in distances])
plt.ylim(0, 0.60)
plt.xlabel("Distance traveled")
plt.ylabel("Probability or relative frequency")
plt.title("Theoretical probabilities and simulated frequencies")
plt.legend()
plt.grid(axis="y", alpha=0.3)
plt.show()
