from pycoingecko import CoinGeckoAPI
from rich import print
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.style import Style
from rich.progress import track
from rich.align import Align

# Create an instance of the CoinGeckoAPI client
cg = CoinGeckoAPI()
console = Console()

# Get the top 5 cryptocurrencies by market capitalization
# top_cryptos = cg.get_coins_markets(vs_currency='usd', order='market_cap_desc')


prefered_cryptos = ['bitcoin', 
                    'ethereum', 
                    'ripple', 
                    'terra-luna', 
                    'gala', 
                    'mina-protocol',
                    'fantom', 
                    'cardano', 
                    'decentraland', 
                    'tezos', 
                    'aave', 
                    'vechain']


# Get the top 5 exchanges
exchanges = cg.get_exchanges_list()

def get_user_input():
    print(Align.center('\n*******************************************************'))
    print(Align.center('*   Enter a crypto value to check for Arbitrage Opportunities   *'))
    print(Align.center('* Type "go", then Enter, to get started, after entering values  *'))
    print(Align.center('*******************************************************\n'))
    user_list = []
    while True:
        user_input = input("Enter Crypto: ")
        if user_input.lower() == 'go':
            break
        user_list.append(user_input)
        print(user_list)

    if len(user_list) >= 0:
        top_cryptos = cg.get_coins_markets(ids=user_list, vs_currency='usd', order='market_cap_desc')
    else:
        top_cryptos = cg.get_coins_markets(ids=prefered_cryptos, vs_currency='usd', order='market_cap_desc')
    return top_cryptos


# print(top_cryptos)
def get_top_cryptos(top_cryptos):
    table = Table(title="Cryptocurrencies by Market Capitalization")
    table.add_column("Coin", justify="left", style="cyan", no_wrap=True)
    table.add_column("Price", justify="right", style="green", no_wrap=True)
    table.add_column("Market Cap", justify="right", style="purple", no_wrap=True)
    table.add_column("Ath", justify="right", style="orange3", no_wrap=True)
    table.add_column("Atl", justify="right", style="bold red", no_wrap=True)
    table.add_column("Price Change", justify="right", style="cyan", no_wrap=True)
    for crypto in track(top_cryptos, description='Processing...'):
        formatted_marketcap = str(f"${crypto['market_cap']:,.2f}")
        alltime_high_formatted = str(f"${crypto['ath']:,.2f}")
        alltime_low_formatted = str(f"${crypto['atl']:,.2f}")
        price_change_formatted = Text(str(f"{crypto['price_change_percentage_24h']:.2f}%"))
        if crypto['price_change_percentage_24h'] > 0:
            price_change_formatted.stylize("bold green")
        elif crypto['price_change_percentage_24h'] < 0:
            price_change_formatted.stylize("bold red")
        crypto_name = str(crypto['name'])
        crypto_price = str(f"${crypto['current_price']:,.2f}")
        table.add_row(crypto_name, 
                      crypto_price, 
                      formatted_marketcap, 
                      alltime_high_formatted, 
                      alltime_low_formatted, 
                      price_change_formatted)

    console.print(Align.center(table))
        

def top_gainers_percentages(top_cryptos):
    top_gainers = []
    top_gainers_percentages = []
    table = Table(title="Top Gainers in the last 24 hours")
    table.add_column("Coin", justify="left", style="cyan", no_wrap=True)
    table.add_column("Current Price", justify="right", style="purple", no_wrap=True)
    table.add_column("Percentage", justify="center", style="bold green", no_wrap=True)
    print(Align.center('\n---------------$$$-----------------\n'))
    # print(f'Top Gainers (>5%) in the last 24 hours')
    for crypto in top_cryptos:
        price_change_formatted = f"{crypto['price_change_percentage_24h']:.2f}%"
        if crypto['price_change_percentage_24h'] > 5:
            crypt_name = str(crypto['name'])
            crypt_percentage = str(f"{crypto['price_change_percentage_24h']:.2f}%")
            crypto_price = str(f"${crypto['current_price']:,.2f}")
            table.add_row(crypt_name,crypto_price, crypt_percentage)
    console.print(Align.center(table))


def arbitrage_opportunity(top_cryptos):
    print(Align.center('\n***********-----------%ARB-OPP%-----------*************\n'))
    print("This can take a while to complete if alot of cryptos are slected")
    table = Table(title="Arbitrace Opportunities")
    table.add_column("Coin", justify="left", style="cyan", no_wrap=True)
    table.add_column("Buy From", justify="left", style="green", no_wrap=True)
    table.add_column("Buy Price", justify="center", style="bold green", no_wrap=True)
    table.add_column("Sell On", justify="left", style="red", no_wrap=True)
    table.add_column("Sell Price", justify="center", style="bold red", no_wrap=True)
    table.add_column("Arb Profit", justify="right", style="bold green", no_wrap=True)
# Fetch prices for each cryptocurrency from each exchange
    for crypto in track(top_cryptos, description='Processing...'):
        crypto_name = crypto['name']
        crypto_id = str(crypto['id'])
        prices = {}
        for exchange in exchanges[:5]:
            exchange_id = exchange['id']
            exchange_name = exchange['name']
            ticker = cg.get_exchanges_tickers_by_id(exchange_id, coin_ids=crypto_id)
            if ticker:
                try:
                    price = ticker['tickers'][0]['converted_last']['usd']
                    prices[exchange_name] = price
                except IndexError:
                    pass
        if len(prices) >= 2:
            sorted_prices = sorted(prices.items(), key=lambda x: x[1])
            buy_exchange, buy_price = sorted_prices[0]
            sell_exchange, sell_price = sorted_prices[-1]
            profit_percentage = ((sell_price - buy_price) / buy_price) * 100
            buy_exc = str(buy_exchange)
            buy_p = str(f"${buy_price:,.2f}")
            sell_exc = str(sell_exchange)
            sell_p = str(f"${sell_price:,.2f}")
            profit_p = str(f"{profit_percentage:.2f}%")
        else:
            print("Insufficient data to find arbitrage opportunity")
        table.add_row(crypto_name, 
                      buy_exc,
                      buy_p,
                      sell_exc,
                      sell_p,
                      profit_p)
    console.print(Align.center(table))

        


if __name__ == '__main__':
    print(Align.center('\nWelcome to the Arbitrage Opportunity Checker!'))
    user_i = get_user_input()
    get_top_cryptos(user_i)
    top_gainers_percentages(user_i)
    arbitrage_opportunity(user_i)
    print('\n************************\n')
    print(Align.center('Would you like to check for other cryptocurrencies? [y/n]'))
    while True:
        if input().lower() == 'n':
            break
        else:
            get_user_input()