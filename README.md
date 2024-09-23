# 🤖 blogBot

###### A Python bot to automate actions on blog websites with human-like behavior

blogBot is a sophisticated web automation tool designed to simulate human-like behavior on blog websites. It leverages Selenium WebDriver for browser automation and includes advanced features such as VPN connection, ad interaction, and dynamic scrolling.

## ✨ Features

- 🌐 VPN connection support for anonymity
- 🖱️ Human-like scrolling and mouse movements
- 📊 Ad detection and interaction
- 🛡️ Handling of various overlay types (e.g., privacy overlays, ad support modals)
- 📸 Screenshot capture for visual logging
- 🎨 Action highlighting for debugging
- 🔄 Robust error handling and session reconnection
- 🧠 Intelligent navigation and content interaction

## 🛠️ Prerequisites

- Python 3.7+
- Chrome browser
- ChromeDriver (compatible with your Chrome version)
- Windscribe VPN (optional, for VPN functionality)

## 🚀 Installation

1. Clone this repository:
   ```
   git clone https://github.com/barhouum7/blogBot.git
   cd blogBot
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Copy the `.env.example` file to `.env` and fill in your VPN credentials if you plan to use the VPN feature.

## 🎮 Usage

To run the bot:

```
from bot import BlogBot

url = "https://www.example-blog.com"
bot = BlogBot(url, use_vpn=True, vpn_location="US")
bot.run()
```

## ⚙️ Configuration

You can configure the bot's behavior by modifying the parameters in the `BlogBot` class initialization:

- `url`: The target blog website URL
- `use_vpn`: Whether to use a VPN connection (requires Windscribe VPN)
- `vpn_location`: The desired VPN server location
- `window_size`: The browser window size

## 📝 Logging

The bot uses Python's built-in logging module to provide detailed information about its actions. Logs are saved in the `bot.log` file.

## 🧪 Testing

To run the test suite:

```
pytest tests/
```

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/barhouum7/blogBot/issues).

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for educational purposes only. Make sure to comply with the terms of service of any website you interact with and respect their robots.txt file. The authors are not responsible for any misuse of this software.

## 🙏 Acknowledgements

- [Selenium](https://www.selenium.dev/) for providing the WebDriver API
- [Windscribe](https://windscribe.com/) for VPN functionality

## 📞 Contact

Ibrahim BHMBS - [@barhouum7](https://twitter.com/barhouum7) - contactibo@duck.com

Project Link: [https://github.com/barhouum7/blogBot](https://github.com/barhouum7/blogBot)
