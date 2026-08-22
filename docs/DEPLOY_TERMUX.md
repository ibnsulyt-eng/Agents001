# Running Agents001 on Android via Termux

An alternative to the VPS: run everything directly on an Android phone using
[Termux](https://github.com/termux/termux-app), a full Linux userland app. No root
required. This doc captures the exact recipe used to set this up, including the
real problems hit along the way, so it's reproducible if the phone is reset.

## 1. Install Termux (not from the Play Store)

The Play Store build of Termux is deprecated/broken. Get it from the official GitHub
releases instead: https://github.com/termux/termux-app/releases — download the APK
matching your phone's CPU (`arm64-v8a` for basically all modern Android phones), verify
its sha256 against the release's `..._sha256sums` file, then install it (sideload, or
`adb install` if setting up from a PC over ADB).

Optional companion apps, same install method, same GitHub-releases pattern:
- [Termux:API](https://github.com/termux/termux-api) — unlocks `termux-wake-lock`,
  `termux-battery-status`, notifications, clipboard, sensors, etc. from scripts.
- [Termux:Boot](https://github.com/termux/termux-boot) — runs a script automatically
  when the phone reboots.

**MIUI/Xiaomi note:** installing extra APKs via `adb install` may fail with
`INSTALL_FAILED_USER_RESTRICTED`. An on-device confirmation dialog appears — you must
tap "Install" promptly, or enable "Install via USB" under Developer options beforehand.

## 2. Base packages

```
pkg update -y
pkg install -y openssh python git
```

## 3. SSH access (so you can drive it from a PC instead of typing on the phone)

Key-based, no password:

```
mkdir -p ~/.ssh
echo "<your-public-key>" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys
sshd            # starts on port 8022 by default
whoami          # note this username, e.g. u0_a255 — needed to connect
```

From the PC: `ssh -i <private-key> -p 8022 <username>@<phone-ip>` (phone's local IP is
under Settings → About phone → Status, or Wi-Fi network details).

## 4. Clone and install Agents001

```
git clone https://github.com/ibnsulyt-eng/Agents001.git
cd Agents001
```

**Known issue:** `pip install -r requirements.txt` fails building `pydantic-core`
(a dependency of `TikTokLive`) two ways in sequence:

1. `Rust not found` / `Target triple not supported by rustup` — fix: `pkg install rust`
   (Termux's own Rust build, already targets Android correctly — don't let it try to
   auto-install rustup, which doesn't support this triple).
2. `Failed to determine Android API level` — fix: pass the API level explicitly:
   ```
   ANDROID_API_LEVEL=$(getprop ro.build.version.sdk) pip install -r requirements.txt
   ```

## 5. Broader toolkit (optional but recommended)

```
pkg install -y termux-services termux-api cronie tmux nano htop jq ffmpeg sqlite wget openssl
```

If `ffmpeg`'s post-install step fails with a `CANNOT LINK EXECUTABLE` /
`__from_chars_floating_point` error, it's a stale shared-library issue — fix with a full
upgrade first, then retry: `pkg upgrade -y`.

If any `pkg install` hits an interactive "keep your currently-installed version?" prompt
(e.g. on `openssl`) over a non-interactive/SSH session, it hangs — run non-interactively:
```
DEBIAN_FRONTEND=noninteractive pkg install -y -o Dpkg::Options::='--force-confold' <packages>
```

## 6. Persistent services (survive the app/process dying, not just "started once")

`termux-services` provides `sv` (runit) supervision, but its startup hook only fires for
an *interactive* Termux session — a plain non-interactive SSH command won't trigger it.
Start it explicitly and enable services:

```
export SVDIR=$PREFIX/var/service
service-daemon start
sv-enable sshd
sv-enable crond          # note: the service is named "crond", not "cronie"
sv-enable ssh-agent
sv status sshd crond ssh-agent
```

**Gotcha:** if `sshd` was already started manually (as in step 3) before enabling
supervision, the supervised instance will crash-loop (`down: sshd: 1s, ...`) because the
port is already held by the manual process. Find and kill the orphan
(`ps aux | grep sshd`, kill the master PID — not the ones handling your *current*
connection, or you'll disconnect yourself), then the supervised instance binds cleanly.

Each new SSH command starts a fresh non-login shell, so `$SVDIR` doesn't persist between
`ssh host "command1"` and a later `ssh host "command2"` — either export it inline each
time, or rely on the boot script below for the durable setup.

## 7. Auto-start on reboot (needs Termux:Boot installed, see step 1)

```
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/start-services.sh << 'EOF'
#!/data/data/com.termux/files/usr/bin/sh
termux-wake-lock
export SVDIR=/data/data/com.termux/files/usr/var/service
service-daemon start
sleep 2
sv-enable sshd
sv-enable crond
sv-enable ssh-agent
EOF
chmod +x ~/.termux/boot/start-services.sh
```

`termux-wake-lock` (needs Termux:API) stops Android from suspending the process when the
screen locks — important for anything meant to keep running in the background, like the
TikTok monitor.

## 8. Configure and run

```
cd ~/Agents001
cp .env.example .env
nano .env     # fill in GROQ_API_KEY at minimum; TIKTOK_WATCHLIST for the monitor
python main.py "your goal"
python monitor_main.py
```

## Convenience: SSH alias from your PC

```
# ~/.ssh/config
Host agents001-phone
    HostName <phone-ip>
    Port 8022
    User <termux-username>
    IdentityFile ~/.ssh/<your-key>
    StrictHostKeyChecking accept-new
```

Then just `ssh agents001-phone` instead of the full command each time. Note: the phone's
local IP can change (DHCP lease renewal, reconnecting to Wi-Fi) — if the alias stops
connecting, check Settings → Wi-Fi → (network) → IP address on the phone and update
`HostName`.
