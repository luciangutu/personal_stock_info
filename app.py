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

                balance_sheet = stock.get_balance_sheet()

                total_assets = balance_sheet.loc['TotalAssets', :]
                latest_total_assets = round(total_assets.iloc[0])
                stock_info['totalAssets'] = latest_total_assets

                total_liabilities_short = balance_sheet.loc['TotalLiabilitiesNetMinorityInterest', :]
                total_liabilities_long = balance_sheet.loc['TotalNonCurrentLiabilitiesNetMinorityInterest', :]
                stock_info['totalLiabilities'] = round(total_liabilities_short.iloc[0] + total_liabilities_long.iloc[0])

                stock_info['longName'] = stock.info.get('longName', '0')
                stock_info['website'] = stock.info.get('website', '0')

                # Price
                stock_info['currentPrice'] = stock.info.get('currentPrice', '0')
                stock_info['regularMarketDayLow'] = stock.info.get('regularMarketDayLow', '0')
                stock_info['regularMarketDayHigh'] = stock.info.get('regularMarketDayHigh', '0')
                stock_info['regularMarketPreviousClose'] = stock.info.get('regularMarketPreviousClose', '0')

                # Financial
                stock_info['sharesOutstanding'] = stock.info.get('sharesOutstanding', 0)
                stock_info['trailingPE'] = stock.info.get('trailingPE', '0')
                stock_info['forwardPE'] = stock.info.get('forwardPE', '0')
                stock_info['priceToSalesTrailing12Months'] = stock.info.get('priceToSalesTrailing12Months', '0')
                stock_info['bookValue'] = stock.info.get('bookValue', '0')
                stock_info['priceToBook'] = stock.info.get('priceToBook', '0')
                stock_info['earningsQuarterlyGrowth'] = stock.info.get('earningsQuarterlyGrowth', '0')
                stock_info['trailingEps'] = stock.info.get('trailingEps', '0')
                stock_info['forwardEps'] = stock.info.get('forwardEps', '0')
                stock_info['pegRatio'] = stock.info.get('pegRatio', '0')
                stock_info['totalRevenue'] = round(stock.info.get('totalRevenue', '0'))
                stock_info['totalDebt'] = round(stock.info.get('totalDebt', '0'))
                stock_info['debtToEquity'] = stock.info.get('debtToEquity', '0')
                stock_info['revenuePerShare'] = stock.info.get('revenuePerShare', '0')
                stock_info[
                    'grossProfits'] = round(stock.info.get('grossProfits', 0)) if 'grossProfits' in stock.info else 0
                stock_info[
                    'freeCashflow'] = round(stock.info.get('freeCashflow', 0)) if 'freeCashflow' in stock.info else 0
                stock_info['operatingCashflow'] = round(stock.info.get('operatingCashflow', 0))

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
