import sqlite3
import yfinance as yf
import pandas as pd

# Data class
class Data:
    def __init__(self, ticker: str='AAPL',
                 start: pd.Timestamp=pd.Timestamp(f"{pd.Timestamp.now().year}-01-01"),
                 end: pd.Timestamp=pd.Timestamp.now()):

        self.ticker = ticker
        self.start = start
        self.end = end

        # save data to sqlite
        try:
            self.con = sqlite3.connect('market.db')
            self.cur = self.con.cursor()
            self.dat = pd.DataFrame

            # composite primary key to ensure data is unique
            self.cur.execute("""CREATE TABLE IF NOT EXISTS ohlcv (
                        ticker text,
                        date text, 
                        open real, 
                        high real, 
                        low real, 
                        close real, 
                        volume integer,
                        PRIMARY KEY (ticker, date)
                        )""")
        finally:
            self.con.commit()

        # download data from yfinance
        ticker = ticker
        self.dat = yf.download(ticker,
                               start=start.strftime('%Y-%m-%d'),
                               end=end.strftime('%Y-%m-%d'),
                               interval='1d',
                               auto_adjust=True)
        self.dat = self.dat.dropna()

        # exit if no data
        if self.dat.empty:
            print("No stock data found.")
            exit()

        # flatten the multi-index
        self.dat.columns = self.dat.columns.get_level_values(0)

        # extract data
        dates = self.dat.index.strftime('%Y-%m-%d %H:%M:%S').values
        opn = self.dat["Open"].values
        high = self.dat["High"].values
        low = self.dat["Low"].values
        close = self.dat["Close"].values
        volume = self.dat["Volume"].values

        # save data to sqlite
        try:
            # cur.execute("DELETE FROM ohlcv")
            rows = [
                (ticker, dates[i], float(opn[i]), float(high[i]), float(low[i]), float(close[i]), int(volume[i]))
                for i in range(len(dates))
            ]

            self.cur.executemany("INSERT OR IGNORE INTO ohlcv VALUES (?,?,?,?,?,?,?)", rows)
            # cur.execute("DELETE FROM ohlcv")

        finally:
            self.con.commit()

    def retrieve_row(self, ticker: str, date: pd.Timestamp):
        row = pd.read_sql_query("SELECT * FROM ohlcv WHERE ticker = ? AND date = ?",
                                self.con, params=(ticker, date.strftime('%Y-%m-%d %H:%M:%S')))
        return row

    def retrieve_rows(self, ticker: str, start: pd.Timestamp, end: pd.Timestamp):
        rows = pd.read_sql_query("SELECT * FROM ohlcv WHERE ticker = ? AND date BETWEEN ? AND ? ORDER BY date",
                                 self.con, params=(ticker,
                                                   start.strftime('%Y-%m-%d %H:%M:%S'),
                                                   end.strftime('%Y-%m-%d %H:%M:%S')))
        return rows