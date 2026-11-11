# Gateway fan

A Noctua NF-A8 5V PWM fan is controlled by the kernel thermal framework, without a daemon. The overlay binds `pwm-fan` to CPU, NSP and DDR zones; [q6a-fan.dts](q6a-fan.dts) defines trip temperatures and fan levels. Active cooling begins at 55 °C. Software PWM generates about 50,000 timer interrupts per second while running and consumes CPU time even at low duty.

## Wiring

Shut down and **unplug power** before touching the 40-pin header. With Ethernet/USB ports on the right, pin 1 is at the left end of the inner row by M.2; all four connections use the outer, even-numbered row.

| Fan wire | Header pin | Outer-row position from left |
|---|---|---|
| Black, ground | 6 GND | 3rd |
| Yellow, +5V | 4 5V | 2nd |
| Green, tach | 18 GPIO27 | 9th |
| Blue, PWM | 16 GPIO26 | 8th |

The fan plug's latch ridge covers pins 1–3; PWM is the hole outside it. GPIO voltage compatibility depends on the circuit described in the overlay. The fan's idle PWM voltage has not been measured; a GPIO pull-low test does not establish it. Do not treat this wiring as an electrically verified general-purpose design.

## Installed files

| Source | Destination |
|---|---|
| `q6a-fan.dts` | `/etc/q6a-fan/q6a-fan.dts` |
| `q6a-fan-dtb` | `/usr/local/sbin/q6a-fan-dtb` (0755) |
| `armbian-grub-with-dtb-q6a-fan` | `/etc/kernel/postinst.d/` (0755) |
| `60-q6a-fan-thermal.rules` | `/etc/udev/rules.d/` |
| `grub/custom-live.cfg` | `/boot/grub/custom.cfg` |

Other files are root-owned 0644. The builder needs `cpp` and device-tree-compiler tools (`dtc`, `fdtoverlay`, `fdtget`). The kernel hook merges the overlay into `/boot/armbian-dtb-<kernel>` after Armbian copies the stock DTB. Udev selects `step_wise`; `power_allocator` does not drive this fan.

If overlay building fails or tools are absent, the stock DTB remains and the PWM pull-up lets the fan run at full speed. A failed tach IRQ request during driver probe is different: the fan can stop, leaving CPU throttling as protection. Verify cooling after kernel updates. [Unexplained early boot resets](../../../documentation/OPERATIONS.md#current-faults) remain a separate unresolved fault.

## Inspection and updates

Read fan speed/duty and thermal policy on Radxa:

```sh
fan_hwmon=$(dirname "$(grep -l '^pwmfan$' /sys/class/hwmon/*/name)")
cat "$fan_hwmon/fan1_input" "$fan_hwmon/pwm1"
grep -l '^pwm-fan$' /sys/class/thermal/cooling_device*/type
grep -H . /sys/class/thermal/thermal_zone*/type /sys/class/thermal/thermal_zone*/policy
```

The CPU/NSP/DDR zones should use `step_wise`; a nonzero PWM duty should have a plausible tach reading. The fan is normally stopped below its thermal thresholds.

Overlay edits require `sudo q6a-fan-dtb "$(uname -r)"` and a scoped reboot to take effect. Before reboot, validate the generated DTB, retained stock image and independent recovery access. The kernel hook also rebuilds after package upgrades, which can lead to an unattended reboot. Do not make thermal-trip or GPIO writes as incidental diagnostics.

`grub/custom.cfg` supplies an optional one-shot `q6a-fan-test` entry using a separate `-fan` DTB. It is not the installed live file; its kernel and boot arguments require validation before use. GRUB's zero-second timeout means the fallback cannot be selected interactively during a failed boot.

## Recovery

While the gateway is running, `sudo grub-reboot q6a-fan-fallback` selects the newest kernel with its stock DTB for the **next** reboot. Arrange the reboot separately; do not repeatedly reboot to diagnose connectivity.

For permanent software removal, disable the fan kernel hook, restore each `/boot/armbian-dtb-<kernel>` from its matching `/usr/lib/linux-image-<kernel>/qcom/qcs6490-radxa-dragon-q6a.dtb`, retain the stock fallback entry and reboot within the recovery window. Preserve the source and snapshots until stock operation is checked. A stock DTB normally leaves the fan running at full speed.

If the board cannot boot, attach its NVMe to another Linux machine, mount the gateway root partition (`nvme0n1p2` on the gateway), and copy the matching stock DTB over `boot/armbian-dtb-<kernel>`. Verify kernel versions and mount paths before writing. This restores boot configuration; it does not resolve the unknown reset cause.
