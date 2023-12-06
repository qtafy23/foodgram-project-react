# **[Foodgram](https://foodgram.gotdns.ch/)**


## **Описание**
Благодаря этому проекту можно будет публиковать и смотреть рецепты. Подписываться на понравившихся авторов.
Добавлять рецепты в изранные и список покупок. Также можно скачать список ингредиентов для рецептов в списке покупок.


## **Как запустить проект**

#### Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:qtafy23/foodgram-project-react.git

cd foodgram-project-react
```
#### Установить докер, создать файл .env и запустить проект в контейнере

Инструкция по установке: [Docker](https://docs.docker.com/installation/mac/)

```
cd ../infra/

touch .env
```
Заполнить файл данными из файла env.example
```
docker compose up
```

#### Выполнить миграции ,собрать статику и заполнить базу данных:

```
docker compose exec backend python manage.py migrate

docker compose exec backend python manage.py collectstatic

docker compose exec backend python manage.py load_ingredients
```


### Документация к API

```
http://127.0.0.1/api/docs/
```

### Автор
**Qtafy23**