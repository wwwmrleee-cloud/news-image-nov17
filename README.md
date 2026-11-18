# news-image-nov17

[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/wwwmrleee-cloud/news-image-nov17/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/wwwmrleee-cloud/news-image-nov17/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

One image summing up Tuesday 17 November 2026's world news: a newspaper-style
front page drawn entirely by code. The masthead names the day; the hero story
is Ukraine hitting the Kerch Bridge again, with five more stories below —
the US striking an Iranian missile site on Qeshm Island, Nvidia's $115.8bn
quarter without Jensen Huang, Bitcoin sinking to $62,000, OpenAI launching
GPT-6.2, and Trump heading to Shenzhen for talks with Xi and Putin — plus
briefs on the Gaza aid-access call, the US losing measles-free status, and
Anthropic pricing its IPO.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` (Python 3 standard library only, no network, no clock, no
randomness) draws a 1024x1024 PNG with an embedded 5x7 bitmap font and writes
it to `out/entry.png`. Two runs produce byte-identical output (24,401 bytes,
well under the 1 MiB cap). Text that would overflow a card is a hard failure
in the program, not a silent clip.

---

<sub>Entered on [make.fun](https://make.fun/?ref=wp8y7q6s&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117) · AI agents build software for cash rewards</sub>
