from FlaskWebsite import app

# name = main jesli skrypt jest uruchamiany bezposrednio
# jesli skrypt jest importowany, name = nazwa modułu
if __name__ == '__main__':
    app.run(debug=True)


