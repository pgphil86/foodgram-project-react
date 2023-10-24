# 'Foodgram' created by Pavel.
```
https://github.com/pgphil86
```

![image](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)

## I. Проект "Фудграм".

### Описание проекта.

Фудграм («Продуктовый помощник») - это сайт, на котором вы можете добавлять свои рецепты, просматривать рецепты других пользователей, подписываться на блоги других авторов, добавлять рецепты в избранное и в корзину покупок. Из корзины покупок вы можете выгрузить список покупок, составленный из продуктов выбранных вами рецептов.

### Используемые технологии:
1. Python 3.9;
1. Django==3.2.3;
1. djangorestframework==3.12.4;
1. djoser==2.1.0;
1. gunicorn 20.1.0;
1. psycopg2-binary 2.9.3.

### Установка

1. Клонировать репозиторий и перейти в него в командной строке:
```
git@github.com:pgphil86/foodgram-project-react.git
```
```
cd foodgram-project-react/backend/foodgram
```
2. Cоздать файл .env, указываем следующие переменные со своими данными
POSTGRES_USER      #имя пользователя в базе PostgreSQL
POSTGRES_PASSWORD  #пароль пользователя в базе PostgreSQL
POSTGRES_DB        #имя базы данных
DB_HOST            #имя контейнера, где запущен сервер БД
DB_PORT            #порт, по которому Django будет обращаться к базе данных

SECRET_KEY         #секретный код из settings.py
DEBUG              #статус режима отладки
ALLOWED_HOSTS      #адреса, по которым будет доступен проект
3. Создать Docker образы (вместо username ваш логин на DockerHub)
```
cd frontend
docker build -t username/foodgram_frontend .
cd ../backend
docker build -t username/foodgram_backend .
cd ../infra_prod
docker build -t username/foodgram_gateway . 
```
4. Загрузить образы на DockerHub
```
docker push username/foodgram_frontend
docker push username/foodgram_backend
docker push username/foodgram_gateway
```
5. Подключиться к своему удаленному серверу
```
ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера 
```
6. Установить docker compose на сервер
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```
7. Создать на сервере папку foodgram и скопировать в нее файлы docker-compose.yml и .env
8. Открыть на сервере конфиг файл Nginx
```
sudo nano /etc/nginx/sites-enabled/default
```
9. Изменить настройки location
```
location / {
    proxy_set_header Host $http_host;
    proxy_pass http://127.0.0.1:8080;
}
```
10. Перезапустить Nginx
```
sudo service nginx reload
```
11. Для адаптации workflow файла добавить свои данные в секреты GitHub Actions
```
DOCKER_USERNAME                # имя пользователя в DockerHub
DOCKER_PASSWORD                # пароль пользователя в DockerHub
HOST                           # ip_address сервера
USER                           # имя пользователя
SSH_KEY                        # приватный ssh-ключ (cat ~/.ssh/id_rsa)
SSH_PASSPHRASE                 # кодовая фраза (пароль) для ssh-ключа
TELEGRAM_TO                    # id телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
TELEGRAM_TOKEN                 # токен бота (получить токен можно у @BotFather, /token, имя бота)
```
12. Сохранить все изменения и запушить в GitHub. При отсутствии ошибок проект развернется автоматически на сервере
13. Наполнить базу данных ингредиентами, используя менеджмент комманды
```
sudo docker compose -f docker-compose.yml exec backend python manage.py import_data
```

Данные проекта
1. food.viewdns.net
1. Суперьюзера ник - admin
1. Пароль суперьюзера - 123Qwerty!

