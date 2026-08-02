import sqlite3
import yfinance as yf


# download data from yfinance
ticker = 'MSFT'
dat = yf.download(ticker, period='1mo', interval='1d', auto_adjust=True)

# exit if no data
if dat.empty:
    print("No stock data found.")
    exit()

# flatten the multi-index
dat.columns = dat.columns.get_level_values(0)

# extract data
dates = dat.index.strftime('%Y-%m-%d %H:%M:%S').values
opn = dat["Open"].values
high = dat["High"].values
low = dat["Low"].values
close = dat["Close"].values
volume = dat["Volume"].values

# save data to sqlite
try:
    con = sqlite3.connect('market.db')
    cur = con.cursor()

    # composite primary key to ensure data is unique
    cur.execute("""CREATE TABLE IF NOT EXISTS ohlcv (
                ticker text,
                date text, 
                open real, 
                high real, 
                low real, 
                close real, 
                volume integer,
                PRIMARY KEY (ticker, date)
                )""")

    #cur.execute("DELETE FROM ohlcv")
    rows = [
        (ticker, dates[i], float(opn[i]), float(high[i]), float(low[i]), float(close[i]), int(volume[i]))
        for i in range(len(dates))
    ]

    cur.executemany("INSERT OR IGNORE INTO ohlcv VALUES (?,?,?,?,?,?,?)", rows)

    #cur.execute("DELETE FROM ohlcv")
    con.commit()
finally:
    con.close()