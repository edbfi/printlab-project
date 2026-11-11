# Gateway fan

The kernel's thermal framework drives a Noctua NF-A8 5V PWM fan without a daemon. The overlay [q6a-fan.dts](q6a-fan.dts) binds `pwm-fan` to the CPU, NSP and DDR thermal zones and sets the trips and fan levels; the fan starts at 55 °C. Software PWM costs about 50,000 timer interrupts a second while the fan spins. Installed paths are in the [file map](../README.md#file-map).

## Wiring

Shut the gateway down and **unplug its power** before touching the 40-pin header. With the Ethernet and USB ports on the right, pin 1 is at the left end of the inner row, next to the M.2 slot. All four wires go on the outer, even-numbered row.

| Fan wire | Header pin | Outer-row position from the left |
|---|---|---|
| Black, ground | 6 GND | 3rd |
| Yellow, +5V | 4 5V | 2nd |
| Green, tach | 18 GPIO27 | 9th |
| Blue, PWM | 16 GPIO26 | 8th |

The latch ridge on the fan plug covers pins 1–3; PWM is the hole outside it. The overlay explains why the header's level shifter tolerates the fan's PWM pull-up. This fan's PWM voltage at idle has not been measured.

## Device tree and kernel

`q6a-fan-dtb <kernel>` merges the overlay into the stock DTB as `/boot/armbian-dtb-<kernel>`; the kernel hook runs it for each new kernel. The udev rule switches the fan's zones to `step_wise`, because `power_allocator` ignores this fan.

If the build fails, the stock DTB stays and the PWM pull-up runs the fan at full speed. If the driver cannot get the tach interrupt, the fan can stay stopped, leaving only CPU throttling. Check cooling after every kernel upgrade.

After editing the overlay, on Radxa:

```sh
sudo install -m 0644 systems/gateway/fan/q6a-fan.dts /etc/q6a-fan/q6a-fan.dts
sudo q6a-fan-dtb "$(uname -r)"
```

It takes effect at the next reboot. Before rebooting, check that the stock DTB is in `/usr/lib/linux-image-$(uname -r)/qcom/` and that you have [independent access](../../../documentation/OPERATIONS.md#change-procedure). Unattended upgrades can reboot at 02:00 into a rebuilt DTB.

## Inspection

On Radxa:

```sh
fan_hwmon=$(dirname "$(grep -l '^pwmfan$' /sys/class/hwmon/*/name)")
cat "$fan_hwmon/fan1_input" "$fan_hwmon/pwm1"
grep -l '^pwm-fan$' /sys/class/thermal/cooling_device*/type
grep -H . /sys/class/thermal/thermal_zone*/type /sys/class/thermal/thermal_zone*/policy
```

The fan's zones should show `step_wise`, and a nonzero PWM duty a plausible tach reading. Below the first trip the fan is stopped. Do not write trip points or GPIOs while diagnosing.

## Recovery with the stock DTB

[grub/custom-live.cfg](grub/custom-live.cfg) adds a GRUB entry that boots the newest kernel with its stock DTB. GRUB's timeout is zero, so it cannot be picked at the menu; while the gateway runs, select it for the next boot with `sudo grub-reboot q6a-fan-fallback`, then reboot.

To remove the fan configuration for good: remove the kernel hook, copy each `/usr/lib/linux-image-<kernel>/qcom/qcs6490-radxa-dragon-q6a.dtb` over the matching `/boot/armbian-dtb-<kernel>`, keep the GRUB fallback entry, and reboot. On the stock DTB the fan runs at full speed.

If the gateway no longer boots, attach its NVMe to another Linux machine, mount the root partition (`nvme0n1p2` on the gateway), and copy the matching stock DTB over `boot/armbian-dtb-<kernel>`. Check the kernel version and mount path before writing.
