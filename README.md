# 📊 Quantico

Live quantitative trading algorithms for [Robinhood](https://robinhood.com/) in Python 3.

![Robinhood Logo](https://timedotcom.files.wordpress.com/2018/08/robinhood_ios-android.jpg?quality=85)

## What's inside?

This project uses my fork of [Jamonek's](https://github.com/Jamonek/Robinhood) Robinhood Python wrapper to make servers calls warranted by the algorithms in this project given various financial data from the API. Calls include placing buys and sells, making calls and puts, and retrieving instrument data. This repository is a work in progress, and since I obviously don't store my credentials in this repo, anyone can fork it, give it a whirl, and perhaps contribute their own financial knowledge.

## Getting Started

### Installing and Running

1. Clone this repository.
2. Open a terminal window and `cd` to the project.
3. Create a file called `.env` and input your credentials:

```
USERNAME=yourEmail@probably.com
PASSWORD=yourPassword123
```

4. Run tests in the `tests/tests.py` file. It will use `dotenv` to load your `USERNAME` and `PASSWORD`, so you don't have to worry about hardcoding these credentials.
5. `cd` to `tests`. Start the tests script with `python tests.py`.

As this project evolves, I will give users the option to run their algorithms on a REST server, as well as better constructed script files.

## Contributing

If you'd like to improve and/or expand the content of this library, feel free to submit pull requests. If you experience any issues with this code, please let me know promptly.

## Authors

* **Anthony Krivonos** - *Developer* - [Portfolio](https://anthonykrivonos.com)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Vicki Shao for all the support and flames! 🔥
