# 🌿 Quantico

Live quantitative trading algorithms for [Robinhood](https://robinhood.com/) in Python 3.

![Quantico](https://i.imgur.com/JABBu3m.jpg)

## What's inside?

This project uses my fork of [Jamonek's](https://github.com/Jamonek/Robinhood) Robinhood Python wrapper to make servers calls warranted by the algorithms in this project given various financial data from the API. Calls include placing buys and sells, making calls and puts, and retrieving instrument data. This repository is a work in progress, and since I obviously don't store my credentials in this repo, anyone can fork it, give it a whirl, and perhaps contribute their own financial knowledge.

## Getting Started

### Installing and Running

1. Clone this repository.
2. Open a terminal window and `cd` to the project.
3. Upgrade your setup tools with `pip3 install --upgrade setuptools --user python`.
4. Install all required dependencies with `pip3 install -r requirements.txt`.
5. Create a file called `.env` and fill it with your credentials:

```
EMAIL=yourEmail@probably.com
PASSWORD=yourPassword123
```

5. Run the driver with `python3 driver/run.py`. It will use `python-dotenv` to load your `EMAIL` and `PASSWORD`, so you don't have to worry about hardcoding these credentials.

### Creating Your Own Algorithm

1. Copy and paste `src/algorithms/__skeleton.py` into the same folder. Rename it to something of your choosing, and be sure to change the class name.
2. Add `from algorithms.your_algorithm import *` to `src/algorithms/__init__.py`.
3. Follow the instructions in the skeleton file to write your algorithm.
4. After writing your algorithm, call it as follows at the bottom of `driver/run.py`:


- If backtesting: `YourAlgorithm(query, my_port, test=True, cash=1000)` ($1000 is the starting cash amount)

- If live trading: `YourAlgorithm(query, my_port)`


5. Run your code with `python3 driver/run.py`.


## Contributing

If you'd like to improve and/or expand the content of this library, feel free to submit pull requests. If you experience any issues with this code, please let me know promptly.

## Authors

* **Anthony Krivonos** - *Developer* - [Portfolio](https://anthonykrivonos.com)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Vicki Shao for all the support and flames! 🔥
