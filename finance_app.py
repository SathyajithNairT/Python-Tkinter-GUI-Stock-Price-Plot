import tkinter as tk
import customtkinter as ctk
import yfinance as yf
import math
from datetime import date, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


width = 800
height = 600
title = 'Finance Dashboard'
top_frame_bg = '#323536'
main_frame_bg = '#0D6380'
content_font = ('Ariel', 20)
heading_font = ('Ariel', 30)

days_backwards = 5
historic_data = days_backwards

ctk.set_appearance_mode('Dark')
ctk.set_default_color_theme('blue')


class FinanceDashboard(ctk.CTk):
    global width, height

    def __init__(self):
        super().__init__()

        self.title(title)
        self.geometry(f'{width}x{height}')

        self.set_top_frame()
        self.set_main_frame()
        self.search_field()

        self.grid_rowconfigure(0, weight = 1)
        self.grid_rowconfigure(1, weight = 4)
        self.grid_columnconfigure(0, weight = 1)

    
    def set_top_frame(self):
        self.top_frame = tk.Frame(self, width = width, height = (height / 4), bg = top_frame_bg)
        self.top_frame.grid(row = 0, column = 0, sticky = 'nsew')

    def set_main_frame(self):
        self.main_frame = tk.Frame(self, width = width, height = (height - (height / 4)), bg = main_frame_bg)
        self.main_frame.grid(row = 1, column = 0, sticky = 'nsew')

    def search_field(self):
        global historic_data
        historic_data = days_backwards

        self.search_heading = tk.Label(self, text = 'Search', font = content_font, bg = top_frame_bg, fg = 'white')
        self.search_heading.grid(row = 0, column = 0, sticky = 'wn', padx = (20, 0), pady = (25, 0))
        self.search = ctk.CTkEntry(self.top_frame, width = 400, height = 50, font = content_font, corner_radius = 25)
        self.search.grid(row = 0, column = 0, padx = (150, 0), pady = (20, 0), sticky = 'w')
        self.search.bind('<Return>', self.get_search_value)

    def get_search_value(self, event = None):
        search_value = self.search.get()
        self.fetch_stock_data(search_value)
        
    def fetch_stock_data(self, ticker):
        global historic_data

        today = date.today()
        from_day = today - timedelta(days = historic_data)

        try:
            ticker_data = yf.download(ticker, start = from_day, end = today)

            if len(ticker_data) < days_backwards and historic_data < days_backwards + 10:
                historic_data += 1
                self.fetch_stock_data(ticker)
            else:
                for widget in self.main_frame.winfo_children():
                    widget.destroy()

                chart_data = []
                date_data = []
                for tick in ticker_data['Close']:
                    chart_data.append(float(self.round_price(tick)))
                
                timeframe = ticker_data.index
                date_data = timeframe.strftime('%Y-%m-%d').tolist()

                current_ticker = yf.Ticker(ticker)
                real_time_price = current_ticker.history(period = '1d', interval = '1m')
                latest_price = real_time_price.tail(1)['Close'].tolist()
                latest_close_price = float(self.round_price(latest_price[0]))

                if chart_data[0] is not None:
                    self.display_chart(chart_data, date_data, ticker, latest_close_price)

        except Exception as err:
            for widget in self.main_frame.winfo_children():
                widget.destroy()
            print(f'{err}')

            display_error = 'Could not find the scrip.'
            main_frame_heading = ctk.CTkLabel(self.main_frame, text = display_error, font = heading_font)
            main_frame_heading.grid(row = 0, column = 0, sticky = 'w', padx = (20, 0), pady = 20)

            historic_data = days_backwards

            self.update_idletasks()

    def round_price(self, price):
        rounded = math.floor(price * 20) / 20
        return f"{rounded:.2f}"
    
    def display_chart(self, price_data, date_data, ticker, current_price):
        fig, ax = plt.subplots(figsize = (8, 4), dpi = 100)
        ax.plot(date_data, price_data, marker = 'o', linestyle = '-', color = 'white')
        ax.set_title(f'Prices of {ticker}', color = 'white')
        ax.set_xlabel('Date', color = 'white')
        ax.set_ylabel('Price', color = 'white')
        ax.tick_params(axis = 'x', rotation = 45, colors = 'white')
        ax.tick_params(axis = 'y', colors = 'white')

        ax.set_facecolor('#323536')

        fig.patch.set_facecolor('#000000')
        fig.tight_layout()

        heading = f'{ticker}\nLast Price: {current_price}'
        main_frame_heading = ctk.CTkLabel(self.main_frame, text = heading, font = heading_font)
        main_frame_heading.grid(row = 0, column = 0, sticky = 'w', padx = (20, 0), pady = 20)

        canvas = FigureCanvasTkAgg(fig, master = self.main_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row = 1, column = 0, sticky = 'nsew')

        self.main_frame.grid_rowconfigure(1, weight = 1)
        self.main_frame.grid_rowconfigure(0, weight = 1)
        self.main_frame.grid_columnconfigure(0, weight = 1)

        self.update_idletasks()

if __name__ == '__main__':
    app = FinanceDashboard()
    app.mainloop()

