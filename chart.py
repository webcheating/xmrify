import requests
import pandas as pd
import matplotlib.pyplot as plt


def fetch_price(coin_id, days=1, vs_currency="usd"):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
            "vs_currency": vs_currency,
            "days": days
            }

    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()

    data = r.json()
    if "prices" not in data:
        raise RuntimeError(f"[!] bad API response for {coin_id}: {data}")

    df = pd.DataFrame(data["prices"], columns=["ts", "price"])
    df["ts"] = pd.to_datetime(df["ts"], unit="ms")

    #return df[(df["price"] > 0) & (df["price"] < 1_000_000)]
    return df

def generate_chart(output="img/xmr_zec.png", days=1):
    xmr = fetch_price("monero", days)
    zec = fetch_price("zcash", days)

    bg = "#0b1220"
    grid = "#2a3345"
    red = "#ff4d4d"
    blue = "#4da6ff"

    plt.rcParams.update({
        "figure.facecolor": bg,
        "axes.facecolor": bg,
        "xtick.color": "#9aa4bf",
        "ytick.color": "#9aa4bf",
        "font.size": 10
    })

    fig, (ax1, ax2) = plt.subplots(
        2, 1,
        figsize=(8, 5),
        sharex=True,
        gridspec_kw={"hspace": 0.33}
    )

    draw(ax1, xmr, "monero (XMR)", red)
    draw(ax2, zec, "zcash (ZEC)", blue)

    plt.tight_layout()
    plt.savefig(output, dpi=400)
    plt.close()


def draw(ax, df, title, color):
    ax.plot(df["ts"], df["price"], color=color, linewidth=2)
    ax.fill_between(
        df["ts"],
        df["price"],
        df["price"].min(),
        color=color,
        alpha=0.15
    )

    ax.set_title(title, loc="left", color="white", fontsize=12)
    ax.grid(True, axis="y", linestyle="--", alpha=0.35)
    ax.grid(False, axis="x")

    for spine in ax.spines.values():
        spine.set_visible(False)

    # current price bubble
    last_price = df["price"].iloc[-1]
    ax.annotate(
        f"{last_price:.2f}",
        xy=(df["ts"].iloc[-1], last_price),
        xytext=(8, 0),
        textcoords="offset points",
        va="center",
        color="white",
        fontsize=10,
        bbox=dict(
            boxstyle="round,pad=0.35",
            facecolor=color,
            edgecolor="none"
        )
    )

    ax.margins(x=0)
    ax.set_ylabel("")
