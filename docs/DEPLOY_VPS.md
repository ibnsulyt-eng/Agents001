# Deploying to a free VPS (Oracle Cloud Always Free)

Oracle Cloud's "Always Free" tier is genuinely free forever (not a trial credit that
expires) and includes either:
- 2x AMD-based VMs (1 vCPU / 1GB RAM each), or
- 1x Ampere A1 (ARM) VM with up to 4 vCPUs / 24GB RAM total — plenty for this project.

This project is lightweight (a few HTTPS calls per run), so even the smallest free
instance is enough.

## 1. Create the account and instance

1. Sign up at https://signup.oraclecloud.com (requires a card for identity verification,
   but Always Free resources are never billed).
2. Console → **Compute → Instances → Create Instance**.
3. Choose an **Always Free eligible** image (e.g. "Canonical Ubuntu 22.04") and shape
   (an Ampere A1 shape, e.g. 2 vCPU / 12GB RAM, comfortably stays in the free allowance).
4. Under "Add SSH keys", either upload your public key or let Oracle generate a key pair
   for you to download — you'll need the private key to connect.
5. Create the instance and note its **public IP**.
6. Under the instance's **Virtual Cloud Network → Security Lists**, no extra ports need
   opening for this project (it only makes outbound HTTPS calls to the LLM provider).

## 2. Connect and set up the environment

From any machine with SSH (this can be done from a phone/other PC — not required to be
this one):

```bash
ssh -i /path/to/private_key.pem ubuntu@<VPS_PUBLIC_IP>

# Update and install Python (Ubuntu 22.04 ships Python 3.10)
sudo apt update && sudo apt install -y python3-pip python3-venv git
```

## 3. Get the code onto the VPS

Push this repo to GitHub first (from this machine, via `git push`), then on the VPS:

```bash
git clone https://github.com/<your-username>/Agents001.git
cd Agents001
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env   # paste your free Groq (or OpenRouter) API key
```

## 4. Run it

```bash
python main.py "Plan a 3-day beginner itinerary for Tokyo"
```

## 5. (Optional) Run it unattended / on a schedule

To run a goal periodically without an active SSH session, use `cron`:

```bash
crontab -e
# add a line like:
0 * * * * cd /home/ubuntu/Agents001 && .venv/bin/python main.py "check status and summarize" >> run.log 2>&1
```

Or keep a session running in the background with `tmux`:

```bash
sudo apt install -y tmux
tmux new -s agents001
source .venv/bin/activate
python main.py "your goal"
# detach: Ctrl+b then d — reattach later with: tmux attach -t agents001
```

## Notes

- Nothing here needs a GPU or heavy RAM — all inference happens on Groq's/OpenRouter's
  servers over HTTPS; the VPS just runs lightweight Python making API calls.
- Free-tier rate limits: the LLM client already retries with backoff on HTTP 429s, but if
  you hit persistent limits, switch `LLM_PROVIDER` in `.env` to the other provider.
