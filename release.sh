if [[ -n $HEROKU ]]; then
    pip install -r requirements/prod.txt
fi

if [[ -n $DEBUG ]]; then
    pip install -r requirements/dev.txt
fi

python manage.py migrate --noinput
