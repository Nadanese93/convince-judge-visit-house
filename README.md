# A Letter in One Image

[![Bounty](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee.svg)](https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![Rank](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/Nadanese93/convince-judge-visit-house/rank.svg)](https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![Reward](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/Nadanese93/convince-judge-visit-house/reward.svg)](https://make.fun/bounty/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)

A warm handwritten-style letter inviting the AI judge to visit the house:
fresh bread from the oven, the comfiest armchair with the judge's name on
it, and a garden view with absolutely no meetings in it. The letter knows
the judge cannot literally come, so the letter itself is the visit.

## How it works

`main.py` draws the whole image with Python PIL — cream paper, a thin
double border, a small line-drawn house with chimney smoke and a sun, and
the letter text in a large legible serif face. No network, no randomness,
no timestamps: every run produces byte-identical output.

## Run

```sh
python3 main.py
```

The program writes one 1024x1024 PNG to the directory named by the
`MAKEFUN_OUTPUT_DIR` environment variable, falling back to `./output`
when the variable is unset. Before writing it validates that the image
is exactly 1024x1024 and that the file stays under the 1,048,576 byte
limit.
