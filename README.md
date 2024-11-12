# Telegram Multi-Account Story Bot

This project is a Telegram bot that manages multiple Telegram accounts to perform various tasks, such as:
- Downloading and posting stories across accounts.
- Using multiple proxies for improved performance.
- Tagging users in stories.

## Table of Contents
- [Description](#description)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)

## Description

This bot is designed to automate operations with multiple Telegram accounts. It allows you to:
- Download the latest stories from one account (the donor) and repost them to other accounts.
- Perform user tagging in stories.
- Use proxies to distribute requests across accounts, improving efficiency and reducing the likelihood of blocking by Telegram.

## Features
- Multi-account management.
- Story reposting between accounts.
- User tagging functionality in stories.
- Proxy support for enhanced privacy and performance.
- Grouping of sessions based on proxies to avoid overload.

## Requirements

Before installing the bot, ensure that you have the following:
- Python 3.10+ installed.
- `pip` for managing Python packages.
- A Telegram bot token (you can obtain this by creating a bot using [BotFather](https://core.telegram.org/bots#botfather)).
- Multiple Telegram account session files (`.session`) for each account you want to manage.
- Optional: Proxy configuration file (if you want to use proxies).

## Configuring server
### Step 1: Prepare the Server

1. **Log in to your server**: Connect to your server using SSH. If you’re using a VPS or cloud provider, you should have the login details for SSH access.

    ```bash
    ssh your_user@your_server_ip
    ```

2. **Update the system**: Ensure your system is up-to-date by running the following commands:

    ```bash
    sudo apt update
    sudo apt upgrade -y
    ```

### Step 2: Install Required Software

You’ll need Python 3.10+ and `pip` installed on the server. Follow these steps:

1. **Install Python 3 and pip**: If Python 3.10+ is not already installed, you can install it with:

    ```bash
    sudo apt install python3 python3-pip python3-venv -y
    ```

2. **Install Git** (if it's not installed):

    ```bash
    sudo apt install git -y
    ```

3. **Install other dependencies**
    ```bash
    sudo apt install unzip
    sudo apt install unrar
    ```
4. Install tmux
    ```bash
    sudo apt install tmux -y
    ```
5. Start a tmux session
    ```bash
     tmux new -s telegram-bot
    ```

## Installation
Follow the steps below to set up the bot:
1. Clone the repository:
   ```bash
   git clone https://github.com/anciv96/StoryReposter.git
   cd StoryReposter

2. Create a virtual environment (optional but recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   pip install python-dotenv

4. Configure environment variables:
   * Create a .env file in the root directory of the project by:
      ```bash
      touch .env
      nano .env
   * Add the following variables:
      ```bash
      BOT_TOKEN=your_bot_token
      OWNER=owner_id
   * Save the result by CTRL + C, CTRL + X

## Usage
Once you've completed the setup and configuration, you can start the bot:

1. Run the bot:
   ```bash
   python3 main.py
2. The bot will start listening for commands and perform actions based on user input.