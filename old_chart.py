import requests
import pandas as pd
import matplotlib.pyplot as plt

def generate_chart(coin):
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": 1
        }
    
    data = requests.get(url, params=params, timeout=10).json()
    if "prices" not in data:
        raise RuntimeError(f"[!] invalid API response: {data}")
    else:
        prices = data["prices"]
    
    df = pd.DataFrame(prices, columns=["ts", "price"])
    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    
    # to sort; can be commented out
    #df = df[(df["price"] > 50) & (df["price"] < 2000)]
    
    bg_color = "#0b1220"
    grid_color = "#2a3345"
    line_color = "#ff4d4d"
    
    plt.rcParams.update({
        "figure.facecolor": bg_color,
        "axes.facecolor": bg_color,
        "axes.edgecolor": bg_color,
        "axes.labelcolor": "white",
        "xtick.color": "#9aa4bf",
        "ytick.color": "#9aa4bf",
        "font.size": 11
    })
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # price line
    ax.plot(df["ts"], df["price"], color=line_color, linewidth=2)
    
    # gradient 
    x = df["ts"]
    y = df["price"]
    
    ax.fill_between(
        x,
        y,
        y.min(),
        color=line_color,
        alpha=0.15
    )
    
    # mesh
    ax.grid(True, axis="y", linestyle="--", linewidth=0.6, alpha=0.4)
    ax.grid(False, axis="x")
    
    # remove borders
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # current price in numbers
    last_price = y.iloc[-1]
    ax.annotate(
        f"{last_price:.1f}",
        xy=(x.iloc[-1], last_price),
        xytext=(8, 0),
        textcoords="offset points",
        va="center",
        color="white",
        fontsize=10,
        bbox=dict(
            boxstyle="round,pad=0.35",
            facecolor=line_color,
            edgecolor="none"
        )
    )
    
    ax.set_xlim(x.min(), x.max())
    ax.margins(x=0)
    ax.set_xlabel("")
    ax.set_ylabel("")
    
    plt.tight_layout()
    plt.savefig(f"img/{coin}.png", dpi=500)
    plt.close()
