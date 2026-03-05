from vcdvcd import VCDVCD
import matplotlib.pyplot as plt

vcd = VCDVCD("xor_waveform.vcd")

signals = vcd.signals   # ← FIXED

plt.figure(figsize=(20, 6))
offset = 0

for signal in signals:
    tv = vcd[signal].tv   # time-value pairs

    times = []
    values = []

    for t, v in tv:
        times.append(t)
        values.append(int(v) + offset)

    plt.step(times, values, where="post", label=signal)
    offset += 2

plt.xlabel("Time")
plt.xlim(0, 60)
plt.title("Waveform")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("waveform.png")
plt.show()