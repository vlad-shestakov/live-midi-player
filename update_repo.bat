@rem Получает и обновляет текущую ветку из origin.master репозитория
@rem Текущее состояние файлов репозитория сбрасывает
git fetch origin --force
git checkout master
git reset --hard origin/master