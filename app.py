from flask import Flask, render_template, request
import yfinance as yf

app = Flask(__name__)


def dcf(free_cash_flow, shares_outstanding):
    required_rate = 0.07
    perpetual_rate = 0.02
    cash_flow_growth_rate = 0.03

    years = [1, 2, 3, 4]

    future_free_cash_flow = []
    discount_factor = []
    discounted_future_free_cash_flow = []

    terminal_value = round(free_cash_flow[-1] * (1 + perpetual_rate) / (required_rate - perpetual_rate))

    for year in years:
        cash_flow = round(free_cash_flow[-1] * (1 + cash_flow_growth_rate) ** year)
        future_free_cash_flow.append(cash_flow)
        discount_factor.append((1 + required_rate) ** year)

    for i in range(0, len(years)):
        discounted_future_free_cash_flow.append(round(future_free_cash_flow[i] / discount_factor[i]))

    discounted_terminal_value = round(terminal_value / (1 + required_rate) ** len(years))
    discounted_future_free_cash_flow.append(discounted_terminal_value)

    today_value = sum(discounted_future_free_cash_flow)
    fair_value = round(today_value / shares_outstanding, 2)
    return fair_value


@app.route('/', methods=['GET', 'POST'])
def index():
    stock_info = {}

    if request.method == 'POST':
        stock_ticker = request.form['stock_ticker']

        if stock_ticker:
            try:
                stock = yf.Ticker(stock_ticker)

                try:
                    balance_sheet = stock.get_balance_sheet()
                    total_assets = balance_sheet.loc['TotalAssets', :]
                    latest_total_assets = round(total_assets.iloc[0])

                    stock_info['totalAssets'] = f"{latest_total_assets:,}"
                except KeyError:
                    print(f"Total assets data not available for {stock_ticker}.")
                    stock_info['totalAssets'] = 0

                stock_info['longName'] = stock.info.get('longName', 'N/A')
                stock_info['website'] = stock.info.get('website', 'N/A')

                # Price
                stock_info['currentPrice'] = stock.info.get('currentPrice', 'N/A')
                stock_info['regularMarketDayLow'] = stock.info.get('regularMarketDayLow', 'N/A')
                stock_info['regularMarketDayHigh'] = stock.info.get('regularMarketDayHigh', 'N/A')
                stock_info['regularMarketPreviousClose'] = stock.info.get('regularMarketPreviousClose', 'N/A')

                # Financial
                stock_info['sharesOutstanding'] = stock.info.get('sharesOutstanding', 0)
                stock_info['trailingPE'] = stock.info.get('trailingPE', 'N/A')
                stock_info['forwardPE'] = stock.info.get('forwardPE', 'N/A')
                stock_info['priceToSalesTrailing12Months'] = stock.info.get('priceToSalesTrailing12Months', 'N/A')
                stock_info['bookValue'] = stock.info.get('bookValue', 'N/A')
                stock_info['priceToBook'] = stock.info.get('priceToBook', 'N/A')
                stock_info['earningsQuarterlyGrowth'] = stock.info.get('earningsQuarterlyGrowth', 'N/A')
                stock_info['trailingEps'] = stock.info.get('trailingEps', 'N/A')
                stock_info['forwardEps'] = stock.info.get('forwardEps', 'N/A')
                stock_info['pegRatio'] = stock.info.get('pegRatio', 'N/A')
                stock_info['totalRevenue'] = f"{stock.info.get('totalRevenue', 'N/A'):,}"
                stock_info['totalDebt'] = f"{stock.info.get('totalDebt', 'N/A'):,}"
                stock_info['debtToEquity'] = stock.info.get('debtToEquity', 'N/A')
                stock_info['revenuePerShare'] = stock.info.get('revenuePerShare', 'N/A')
                stock_info[
                    'grossProfits'] = f"{stock.info.get('grossProfits', 'N/A'):,}" if 'grossProfits' in stock.info else 'N/A'
                stock_info[
                    'freeCashflow'] = f"{stock.info.get('freeCashflow', 'N/A'):,}" if 'freeCashflow' in stock.info else 'N/A'
                stock_info['operatingCashflow'] = f"{stock.info.get('operatingCashflow', 'N/A'):,}"

                cashflow_data = stock.cashflow
                free_cash_flow_data = cashflow_data.loc['Free Cash Flow'].tail(4)
                free_cash_flow = [round(item) for item in free_cash_flow_data]
                free_cash_flow.reverse()
                stock_info['dcf'] = dcf(free_cash_flow, stock_info['sharesOutstanding'])

            except:
                stock_info['error'] = 'Error fetching stock information'

    return render_template('index.html', stock_info=stock_info)


if __name__ == '__main__':
    app.run(debug=True)
