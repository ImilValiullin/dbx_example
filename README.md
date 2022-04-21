Официальный репозиторий на GitHub:
https://github.com/databrickslabs/dbx

# dbx by databricks project example for python

Этот проект является простым примером для иллюстрации работы dbx, запуска job-task на Azure Databricks.  
Код проекта (`dbx_example/src/`) намеренно имеет "размазанную" структуру для имитации сложного многоуровневого проекта.  
Результатом успешной работы будет файл по пути `/tmp/dbx/dbx_example/check_file.txt` (см. `/dbx_example/your_project/src/config/main_config.yml`)

## Quick start

В проекте для создания и настройки виртуального окружения используется библиотека `python3-venv` 

---
0. Клонируем проект
```
git clone https://coderepo.corp.tander.ru/valiullin_ir/dbx_example.git
cd dbx_example/
```
1. Создаем и активируем виртуальное окружение
```
python3.8 -m venv .env-dbx
source .env-dbx/bin/activate
```
> Обратите внимание, виртуальное окружение создается вне папки проекта

2. Обновляем pip и устанавливаем библиотеки для работы с dbx
```
pip install --upgrade pip
pip install -r your_project/requirements_dbx.txt
```
3. Для корректной работы dbx скопируйте файл `.databrickscfg` в домашнюю директорию пользователя
```
cp your_project/.databrickscfg ~/
```
> В файле необходимо указать свои host и token:
> * host - URL-адрес вашей рабочей области databricks (https://docs.microsoft.com/ru-ru/azure/databricks/workspace/workspace-details#per-workspace-url)
> * token - персональный токен (https://docs.databricks.com/dev-tools/api/latest/authentication.html#generate-a-personal-access-token)

4. Конфигурируем проект
```
cd your_project/
cp .dbx/project_example.json .dbx/project.json
```
> Для корректной работы отредактируйте файл `project.json` - замените `blob_container` в адресе `dbfs:/mnt/blob_container/dbx/dbx_example` на название вашего контейнера
> или если у вас нет примонтированных контейнеров, то можно указать путь в файловой системе Databricks (например: `/Shared/dbx/artifact/dbx_example`)

5. Конфигурируем настройки развертыватывания кода

- 5.1 На случай когда нужно запустить на job-кластере
 ```
cp conf/deployment_new_cls.json conf/deployment.json 
 ```
- 5.2 На случай когда нужно запустить на интерактивном кластере
```
python refresh_cluster.py
cp conf/deployment_job_existing_cls.json conf/deployment.json
```
6. Развертываем (deploy) код и запускаем
```
dbx deploy
dbx launch --job=job_dbx_example --trace
```
7. Отслеживаем ход выполнения job-task в GUI Databricks или терминале (опция `--trace`)
8. Знаком успешного выполнения будет `Succeeded` в GUI или `Job run finished successfully` в терминале
---

## Подробное описание содержимого конфиг-файлов

1. Настройки сборки кода в пакет *.whl `/your_project/setup.py`
```
name="dbx_example"          # название пакета (название проекта)
packages=find_packages()    # что должно попасть в пакет (в данном примере попадут все директории в которых встретится __init__.py)
setup_requires=["wheel"]    # тип пакета
version="0.0.1"             # версия проекта
description=""              # краткое описание проекта
author=""                   # автор
```

> Если по коду будет возникать ошибка импорта модулей, а по логике импорт будет верны:
> - скорее всего вы забыли `__init__.py` и модуль не попал в сборку;
> - адресация к модулям должна начинается с корневой директории проекта.

2. Конфигурация развертыватывания кода `/dbx_example/your_projectconf/deployment.json`
```
"strict_path_adjustment_policy": true   # опция для корректного парсинга путей
"name": "job_dbx_example"               # название для job-task
"spark_python_task": {                  
    "python_file": "file://main.py",    # точка входа с относительным путем от корневой папки проекта
	"parameters": [
	    "file:fuse://src/config/main_config.yml"    # конфиг-файл с относительным путем от корневой папки проекта
	]
}
```
> Если job-task не может найти путь к конфиг-файлу:
> - не включена опция `strict_path_adjustment_policy`;
> - адресация осуществляется не через `fuse:`.

3. Расположение файлов проекта `/dbx_example/your_project/.dbx/project.json`:

```
"workspace_dir": "/Shared/dbx/projects/dbx_example"    # расположение файлов эксперимента
"artifact_location": "dbfs:/mnt/blob_container/dbx/dbx_example" # расположение артефакта
```
`workspace_dir` - расположение метаданных о сборке и развертывании проекта

`artifact_location` - физическое расположение проекта (желательно указать blob storage `/mnt/blob_container/dbx`)

## Немного о структуре проекта
Для корректной работы dbx в вашем проекте необходимо придерживаться следующей структуры проекта:

```
dbx_example                 # папка со всеми компанентами 
  | - .env-dbx              # папка с виртуальным окружением для работы dbx
  | - your_project_dir      # папка с вашим проектом
       |- .dbx              # см. выше
       |- conf              # см. выше
       |- main.py           # точка входа в проект
       |- requirements.txt  # требования для работы проекта
       |- other_dirs        # другие папки вашего проекта
```

## Зависимости для проекта
Job databricks самостоятельно найдет файл `requirements.txt` внутри корневой директории вашего проекта и установит на кластер указанные библиотеки.

## Файл refresh_cluster.py
При запуске расчета на существующем (`interactive`) кластере необходимо предварительно удалять все библиотеки которые остались с предыдущего запуска,
иначе возникнет "вечная" установка и(или) кластер уйдет в autoterminate.
Для решения данной проблемы существует скрипт `refresh_cluster.py`. 
При вызове скрипта кластер определяется автоматически в зависимости от содержания `/conf/deployment.json`, либо вы можете передать `Cluster ID` (пример: `python3.8 refresh_cluster.py "0403-140913-piv5opcm"`).

Скрипт выполняет следующие действия:
1. Получает `credentials` из вашего конфига `.databrickscfg`
2. Получает список библиотек(пакетов) установленных на указанный кластер
3. Удаляет все библиотеки(пакеты)
4. Осуществляет `terminate` кластера, если он был включен 
