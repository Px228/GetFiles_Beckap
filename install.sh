#!/bin/bash

# Создать папку на Рабочем столе с именем "server"
mkdir -p ~/Desktop/server

# Перейти в папку "server"
cd ~/Desktop/server

# Добавить SSH-ключ в агент
eval "$(sudo -u px ssh-agent -s)"
sudo -u px ssh-add ~/.ssh/id_rsa  # Убедитесь, что это правильный путь к вашему SSH-ключу

# Клонировать репозиторий
sudo -u px git clone git@github.com:Px228/GetFiles_Beckap.git

# Создать файл службы systemd
echo "[Unit]
Description=My Python Script
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/px/Desktop/server/GetFiles_Beckap/app.py
WorkingDirectory=/home/px/Desktop/server/GetFiles_Beckap
StandardOutput=inherit
StandardError=inherit
Restart=always
User=px

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/my_flask_app.service

# Перезагрузить службы systemd
sudo systemctl daemon-reload

# Включить службу
sudo systemctl enable my_flask_app.service

# Запустить службу
sudo systemctl start my_flask_app.service
