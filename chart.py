import requests
import pandas as pd
import matplotlib.pyplot as plt

def fetch_price(coin, days, currency="usd"):
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
    params = {
        "vs_currency": currency,
        "days": days
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    if "prices" not in data:
        raise RuntimeError(f"[!] bad API response during fetch_price() for {coin}\n[*] error data: {data}")
    
    df = pd.DataFrame(data['prices'], columns=['ts', 'price'])
    df['ts'] = pd.to_datetime(df['ts'], unit='ms')
    
    #return df[(df["price"] > 0) & (df["price"] < 1_000_000)]
    return df

def generate_chart(chart_type, coin=None):
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

    days = "1"
    if chart_type == 'dual':
        xmr_price = fetch_price("monero", days)
        zec_price = fetch_price("zcash", days)

        fig, (ax1, ax2) = plt.subplots(
            2, 1,
            figsize=(8, 5),
            sharex=True,
            gridspec_kw={"hspace": 0.30}
        )

        draw(ax1, xmr_price, "monero (XMR)", red)
        draw(ax2, zec_price, "zcash (ZEC)", blue)

        plt.tight_layout()
        plt.savefig("img/xmr_zec.png", dpi=300)
        plt.close()
    elif chart_type == 'single':
        if coin is None:
            raise ValueError("[!] coin is required when chart_type == 'single'")
        
        price = fetch_price(coin, days)
        fig, ax = plt.subplots(figsize=(8, 3))
        if coin == 'monero':
            draw(ax, price, "monero (XMR)", red)
        elif coin == 'zcash':
            draw(ax, price, "zcash (ZEC)", blue)
        else:
            raise ValueError("[!] not supported coin yet")
        
        plt.tight_layout()
        plt.savefig(f"img/{coin}.png", dpi=300)
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

#def generate_chart(coins, chart_type):
#    if chart_type == 'single':
#    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
#    params = {
#        "vs_currency": "usd",
#        "days": 1
#        }
#    
#    data = requests.get(url, params=params, timeout=10).json()
#    if "prices" not in data:
#        raise RuntimeError(f"[!] invalid API response: {data}")
#    else:
#        prices = data["prices"]
#    
#    df = pd.DataFrame(prices, columns=["ts", "price"])
#    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
#    
#    # to sort; can be commented out
#    #df = df[(df["price"] > 50) & (df["price"] < 2000)]
#    
#    bg_color = "#0b1220"
#    grid_color = "#2a3345"
#    line_color = "#ff4d4d"
#    
#    plt.rcParams.update({
#        "figure.facecolor": bg_color,
#        "axes.facecolor": bg_color,
#        "axes.edgecolor": bg_color,
#        "axes.labelcolor": "white",
#        "xtick.color": "#9aa4bf",
#        "ytick.color": "#9aa4bf",
#        "font.size": 11
#    })
#    
#    fig, ax = plt.subplots(figsize=(8, 3))
#    
#    # price line
#    ax.plot(df["ts"], df["price"], color=line_color, linewidth=2)
#    
#    # gradient 
#    x = df["ts"]
#    y = df["price"]
#    
#    ax.fill_between(
#        x,
#        y,
#        y.min(),
#        color=line_color,
#        alpha=0.15
#    )
#    
#    # mesh
#    ax.grid(True, axis="y", linestyle="--", linewidth=0.6, alpha=0.4)
#    ax.grid(False, axis="x")
#    
#    # remove borders
#    for spine in ax.spines.values():
#        spine.set_visible(False)
#    
#    # current price in numbers
#    last_price = y.iloc[-1]
#    ax.annotate(
#        f"{last_price:.1f}",
#        xy=(x.iloc[-1], last_price),
#        xytext=(8, 0),
#        textcoords="offset points",
#        va="center",
#        color="white",
#        fontsize=10,
#        bbox=dict(
#            boxstyle="round,pad=0.35",
#            facecolor=line_color,
#            edgecolor="none"
#        )
#    )
#    
#    ax.set_xlim(x.min(), x.max())
#    ax.margins(x=0)
#    ax.set_xlabel("")
#    ax.set_ylabel("")
#    
#    plt.tight_layout()
#    plt.savefig(f"img/{coin}.png", dpi=300)
#    plt.close()
