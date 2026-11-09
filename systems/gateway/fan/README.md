# Gateway fan

A Noctua NF-A8 5V PWM on the Radxa Dragon Q6A's 40-pin header, sped up and slowed down by the kernel's thermal framework. There is no daemon. A device-tree overlay adds a `pwm-fan` device and binds it to the CPU, NSP and DDR thermal zones. Wiring, trip temperatures and fan levels are documented in [`q6a-fan.dts`](q6a-fan.dts).

| File | Installed at | Purpose |
| --- | --- | --- |
| `q6a-fan.dts` | `/etc/q6a-fan/q6a-fan.dts` | The overlay: software PWM on GPIO26, tach on GPIO27, trips and fan levels. |
| `q6a-fan-dtb` | `/usr/local/sbin/q6a-fan-dtb` (0755) | Merges the overlay into the stock DTB of a kernel version. |
| `armbian-grub-with-dtb-q6a-fan` | `/etc/kernel/postinst.d/` (0755 once live) | Rebuilds the fan DTB after each kernel install, right after Armbian copies the stock one. |
| `60-q6a-fan-thermal.rules` | `/etc/udev/rules.d/` | Switches the fan's zones to `step_wise`. The default `power_allocator` ignores `pwm-fan`. |
| `grub/custom.cfg` | `/boot/grub/custom.cfg` | Temporary one-shot GRUB entry that boots the fan DTB once. Remove it after go-live. |

GRUB boots `/boot/armbian-dtb-<kernel>` (see `/etc/grub.d/09_linux_with_dtb.sh`), so the fan is live once that file contains the overlay. If the overlay fails to build, the stock DTB stays. The fan then runs at full speed, because U48's pull-up holds its PWM input high.

## Wiring

Shut the board down **and unplug its power** before touching the header. Pins 2 and 4 carry 5V right next to GPIO pins, and 5V on a GPIO damages it.

| Fan pin (wire) | Header pin |
| --- | --- |
| 1 GND (black) | 6 GND |
| 2 +5V (yellow) | 4 5V |
| 3 tach (green) | 18 GPIO27 |
| 4 PWM (blue) | 16 GPIO26 |

Before you connect the blue wire, check the fan's own PWM pull-up. Power the fan with only black and yellow connected and the blue wire's loose end insulated. Then measure blue against GND. At or below 3.6V, connect it. Above 3.6V, leave it unconnected (the fan runs at full speed, and the tach still works) until a buffer is added.

## Test with the one-shot entry

The test boot uses a separate DTB, so a hang or bad behaviour goes away after a power cycle: GRUB boots the normal entry again.

```sh
sudo install -m 0644 q6a-fan.dts /etc/q6a-fan/q6a-fan.dts
sudo install -m 0755 q6a-fan-dtb /usr/local/sbin/q6a-fan-dtb
sudo install -m 0644 60-q6a-fan-thermal.rules /etc/udev/rules.d/
sudo install -m 0644 grub/custom.cfg /boot/grub/custom.cfg   # kernel args must match /proc/cmdline
sudo q6a-fan-dtb "$(uname -r)" "/boot/armbian-dtb-$(uname -r)-fan"
sudo grub-reboot q6a-fan-test && sudo reboot
```

After the test boot:

```sh
grep -l pwmfan /sys/class/hwmon/*/name          # the fan's hwmon directory, called $H below
cat $H/fan1_input $H/pwm1                        # rpm and duty (0-255)
grep -H . /sys/class/thermal/cooling_device*/type | grep pwm-fan
```

1. **Speed sweep.** While no trip is crossed, the thermal core leaves `pwm1` alone. Write `0 51 64 102 153 204 255` to `$H/pwm1` one at a time and read `fan1_input` after about 5 s. Expect 0 rpm at 0, about 400 rpm at 51 (20%), about 2200 rpm at 255, and rising speed in between.
2. **Thermal control.** In `cpuss0-thermal`, find the first fan trip: the `active` trip at `55000` (`grep -H . trip_point_*` in the zone; `fdtoverlay` puts the fan trips before the stock ones, so its index can vary). Lower it below the current temperature: `echo 30000 | sudo tee /sys/class/thermal/thermal_zone<N>/trip_point_<i>_temp`. Within a second the fan's cooling device should go to state 1 and the fan to about 25%. Restore the trip to `55000`, and the fan should stop once the zone is below 51 °C. Trip changes made through sysfs last only until reboot.
3. **Timer load.** At a running fan level, `top` should show no noticeable extra CPU time (pwm-gpio takes two hrtimer interrupts per 40 µs period).

## Go live

```sh
sudo install -m 0755 armbian-grub-with-dtb-q6a-fan /etc/kernel/postinst.d/
sudo q6a-fan-dtb "$(uname -r)"                   # writes /boot/armbian-dtb-<kernel>
sudo rm /boot/grub/custom.cfg "/boot/armbian-dtb-$(uname -r)-fan"
sudo reboot
```

Rerun `sudo q6a-fan-dtb "$(uname -r)"` and reboot after you edit the overlay.

## Rollback

```sh
sudo chmod -x /etc/kernel/postinst.d/armbian-grub-with-dtb-q6a-fan
sudo cp "/usr/lib/linux-image-$(uname -r)/qcom/qcs6490-radxa-dragon-q6a.dtb" "/boot/armbian-dtb-$(uname -r)"
sudo reboot
```

If the board no longer boots, press `e` on the GRUB entry and change its `devicetree` line to `/usr/lib/linux-image-<kernel>/qcom/qcs6490-radxa-dragon-q6a.dtb`.
