# Gateway fan

A Noctua NF-A8 5V PWM on the Radxa Dragon Q6A's 40-pin header, sped up and slowed down by the kernel's thermal framework. There is no daemon. A device-tree overlay adds a `pwm-fan` device and binds it to the CPU, NSP and DDR thermal zones. Wiring, trip temperatures and fan levels are documented in [`q6a-fan.dts`](q6a-fan.dts).

| File | Installed at | Purpose |
| --- | --- | --- |
| `q6a-fan.dts` | `/etc/q6a-fan/q6a-fan.dts` | The overlay: software PWM on GPIO26, tach on GPIO27, trips and fan levels. |
| `q6a-fan-dtb` | `/usr/local/sbin/q6a-fan-dtb` (0755) | Merges the overlay into the stock DTB of a kernel version. |
| `armbian-grub-with-dtb-q6a-fan` | `/etc/kernel/postinst.d/` (0755 once live) | Rebuilds the fan DTB after each kernel install, right after Armbian copies the stock one. |
| `60-q6a-fan-thermal.rules` | `/etc/udev/rules.d/` | Switches the fan's zones to `step_wise`. The default `power_allocator` ignores `pwm-fan`. |
| `grub/custom.cfg` | `/boot/grub/custom.cfg` while testing | The fallback entry plus a one-shot entry that boots the fan DTB once. |
| `grub/custom-live.cfg` | `/boot/grub/custom.cfg` once live | Only the fallback entry: the newest kernel with the stock DTB. |
| `grub/99-q6a-fan.cfg` | `/etc/default/grub.d/` | Shows the GRUB menu for 3 s (Armbian sets 0), so the fallback can be picked with an HDMI screen and a USB keyboard. |

GRUB boots `/boot/armbian-dtb-<kernel>` (see `/etc/grub.d/09_linux_with_dtb.sh`), so the fan is live once that file contains the overlay. If the overlay fails to build, the stock DTB stays. The fan then runs at full speed, because U48's pull-up holds its PWM input high. The one exception is a failed tach IRQ request at probe: the fan then stops, and only CPU throttling is left. After every kernel upgrade, check that a `pwm-fan` cooling device exists (step 1 below).

## Wiring

Shut the board down **and unplug its power** before touching the header. Pins 2 and 4 carry 5V right next to GPIO pins.

Hold the board with the Ethernet and USB ports on the right, so the header runs along the far edge. Pin 1 is at the left end of the inner row, by the M.2 slot. Every fan wire goes in the outer row (even pins), counted from the left:

| Fan pin (wire) | Header pin | Outer-row position |
| --- | --- | --- |
| 1 GND (black) | 6 GND | 3rd |
| 2 +5V (yellow) | 4 5V | 2nd |
| 3 tach (green) | 18 GPIO27 | 9th |
| 4 PWM (blue) | 16 GPIO26 | 8th |

On the fan plug, the latch ridge covers pins 1-3; pin 4 (PWM) is the hole outside it. Why the PWM wire may go straight to the header is explained in `q6a-fan.dts`.

## Check the wiring with the stock DTB

With the fan wired, boot normally. The fan runs at full speed, because nothing drives its PWM input yet. GPIO26 and GPIO27 are lines 26 and 27 of `gpiochip4` (named `PIN_16` and `PIN_18`):

```sh
sudo timeout 2 gpiomon -c gpiochip4 -e falling 27 | wc -l   # tach: rpm ≈ count × 15, so ≈ 147 at 2200 rpm
sudo timeout 5 gpioset -c gpiochip4 26=0                   # PWM low: the fan stops, then returns to full speed
```

## Test with the one-shot entry

The test boot uses a separate DTB, so a hang or bad behaviour goes away after a power cycle (the hardware watchdog and `kernel.panic = 10` also reboot on their own). GRUB then boots the normal entry again.

```sh
sudo install -D -m 0644 q6a-fan.dts /etc/q6a-fan/q6a-fan.dts
sudo install -m 0755 q6a-fan-dtb /usr/local/sbin/q6a-fan-dtb
sudo install -m 0644 60-q6a-fan-thermal.rules /etc/udev/rules.d/
sudo install -m 0644 grub/99-q6a-fan.cfg /etc/default/grub.d/
sudo install -m 0644 grub/custom.cfg /boot/grub/custom.cfg  # kernel version and args must match /proc/cmdline
sudo update-grub
sudo q6a-fan-dtb "$(uname -r)" "/boot/armbian-dtb-$(uname -r)-fan"
sudo grub-reboot q6a-fan-test && sudo reboot
```

After the test boot, find the fan and its zones:

```sh
H=$(dirname "$(grep -l '^pwmfan$' /sys/class/hwmon/*/name)")
cat "$H/fan1_input" "$H/pwm1"                     # rpm and duty (0-255)
grep -l '^pwm-fan$' /sys/class/thermal/cooling_device*/type
zones=$(grep -lE '^(cpuss[01]|nspss[01]|ddr)-thermal$' /sys/class/thermal/thermal_zone*/type | xargs -n1 dirname)
grep . $(printf '%s/policy ' $zones)                # all step_wise
```

1. **Speed sweep.** `step_wise` steps a manually set duty back down whenever a zone's temperature falls, so pause it first. `user_space` never touches the fan, and the zones' hot and critical trips still apply:

   ```sh
   for z in $zones; do echo user_space | sudo tee "$z/policy" >/dev/null; done
   for d in 0 51 64 102 153 204 255; do echo $d | sudo tee "$H/pwm1" >/dev/null; sleep 6; echo "$d $(cat "$H/fan1_input")"; done
   echo 0 | sudo tee "$H/pwm1" >/dev/null
   for z in $zones; do echo step_wise | sudo tee "$z/policy" >/dev/null; done
   ```

   Expect 0 rpm at 0, about 400 rpm at 51 (20%), about 2200 rpm at 255, and a steady rise in between. Erratic or too-high readings at middle duties would point to PWM noise on the tach wire.
2. **Thermal control.** In `cpuss0-thermal`, find the first fan trip: the `active` trip at `55000`. `fdtoverlay` puts the fan trips before the stock ones in reverse order, so it is normally `trip_point_4`; confirm before writing. Set it 5 °C below the current temperature, then add a little load so the temperature moves:

   ```sh
   Z=$(dirname "$(grep -l '^cpuss0-thermal$' /sys/class/thermal/thermal_zone*/type)")
   grep -H . $Z/trip_point_4_type $Z/trip_point_4_temp        # active, 55000
   echo $(( $(cat $Z/temp) - 5000 )) | sudo tee $Z/trip_point_4_temp
   timeout 20 sh -c 'yes >/dev/null & yes >/dev/null & wait'
   cat "$H/pwm1"                                               # 64 (state 1)
   echo 55000 | sudo tee $Z/trip_point_4_temp
   ```

   The fan should go to state 1 within a few seconds of the load starting. After the trip is restored, it stops on a later falling reading. On kernel 6.18.2 this can take a while (see `q6a-fan.dts`). Trip changes made through sysfs last only until reboot.
3. **Timer load.** At any running fan level, `pwm-gpio` takes 50,000 timer interrupts a second on one CPU. That time counts as `hi` in `top` (press `1` for each CPU), not as a process. Check that one CPU's `hi` stays at a few percent, that `dmesg | grep 'hrtimer: interrupt took'` is empty, and that printers can still browse while the fan runs.

## Go live

```sh
sudo install -m 0755 armbian-grub-with-dtb-q6a-fan /etc/kernel/postinst.d/
sudo q6a-fan-dtb "$(uname -r)"                     # writes /boot/armbian-dtb-<kernel>
sudo install -m 0644 grub/custom-live.cfg /boot/grub/custom.cfg
sudo rm "/boot/armbian-dtb-$(uname -r)-fan"
sudo reboot
```

Rerun `sudo q6a-fan-dtb "$(uname -r)"` and reboot after you edit the overlay. After a kernel upgrade, run the `grep` checks above and confirm `fan1_input` reads a speed whenever `pwm1` is above 0.

## Rollback

```sh
sudo chmod -x /etc/kernel/postinst.d/armbian-grub-with-dtb-q6a-fan
for f in /boot/armbian-dtb-*; do
	k=${f#/boot/armbian-dtb-}
	[ -f "/usr/lib/linux-image-$k/qcom/qcs6490-radxa-dragon-q6a.dtb" ] &&
		sudo cp "/usr/lib/linux-image-$k/qcom/qcs6490-radxa-dragon-q6a.dtb" "$f"
done
sudo reboot
```

If the board no longer boots, connect an HDMI screen and a USB keyboard and power it on. In the 3 s GRUB menu, choose **Armbian, newest kernel, stock DTB (Q6A fan fallback)**, then roll back as above.
