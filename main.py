from os import urandom
from quart import Quart, render_template, request, redirect, session
from configparser import ConfigParser
from urllib.parse import urlencode

from simplytranslate_engines.googletranslate import GoogleTranslateEngine
from simplytranslate_engines.libretranslate import LibreTranslateEngine
from simplytranslate_engines.utils import *

config = ConfigParser()

config.read(['/etc/simplytranslate/shared.conf', '/etc/simplytranslate/web.conf'])

engines = []

if config.getboolean('google', 'Enabled', fallback=True):
    engines.append(GoogleTranslateEngine())

libretranslate_enabled = config.getboolean('libretranslate', 'Enabled', fallback=None)

if libretranslate_enabled is None:
    print("LibreTranslate is disabled by default; please edit the config file to explicitly state whether it is enabled or not")

if libretranslate_enabled:
    engines.append(
        LibreTranslateEngine(
            config['libretranslate']['Instance'],
            # `ApiKey` is not required, so use `get` to get `None` as fallback.
            config['libretranslate'].get('ApiKey'),
        )
    )

if not engines:
    raise Exception('All translation engines are disabled')

app = Quart(__name__)

app.secret_key = urandom(30)

#NOTE: Legacy Endpoint. Use "/api"
@app.route(
    "/translate/<string:from_language>/<string:to_language>/<string:input_text>/"
)
async def translate(from_language, to_language, input_text):
    return engines[0].translate(
        input_text, from_language=from_language, to_language=to_language
    )

@app.route("/api/translate/")
async def api_translate():
    engine_name = request.args.get("engine")
    text = request.args.get("text")
    from_language = request.args.get("from_language")
    to_language = request.args.get("to_language")

    engine = get_engine(engine_name, engines, engines[0])

    from_language = to_lang_code(from_language, engine)
    to_language = to_lang_code(to_language, engine)


    return engine.translate(
        text, from_language=from_language, to_language=to_language
    )

@app.route("/api/get_languages/")
async def api_get_languages():
    engine_name = request.args.get("engine")
    engine = get_engine(engine_name, engines, engines[0])

    return engine.get_languages()




@app.route("/switchlanguages/", methods=["POST"])
async def switchlanguages():
    form = await request.form

    engine_name = request.args.get("engine")

    engine = get_engine(engine_name, engines, engines[0])

    text = form.get("input", "")
    from_lang = to_lang_code(form.get("from_language", "Autodetect"), engine)
    to_lang = to_lang_code(form.get("to_language", "English"), engine)

    # if the from_lang is not auto,
    if from_lang != "auto":
        tmp_from_lang = from_lang
        from_lang = to_lang
        to_lang = tmp_from_lang

    if session.get("from_lang") and session.get('to_lang'):
        tmp_session_from_lang = session['from_lang']
        session['from_lang'] = session['to_lang']
        session['to_lang'] = tmp_session_from_lang

    use_text_fields = request.args.get("typingiscool") == "True"

    """
    In case we ever want to also switch the translated text with the to-be-translated text, this is a good start.

    translation = engine.translate(
        text,
        to_language=to_lang,
        from_language=from_lang,
    )
    """

    redirect_params = {
        'engine': engine_name,
        'typingiscool': use_text_fields,
        'sl': from_lang,
        'tl': to_lang,
        'text': text
    }

    return redirect(
        f"/?{urlencode(redirect_params)}",
        code=302,
    )

@app.route("/typingiscool/", methods=["POST"])
async def typingiscool():
    form = await request.form

    engine_name = request.args.get("engine")

    engine = get_engine(engine_name, engines, engines[0])

    text = form.get("input", "")
    from_lang = to_lang_code(form.get("from_language", "Autodetect"), engine)
    to_lang = to_lang_code(form.get("to_language", "English"), engine)

    use_text_fields = request.args.get("typingiscool") == "True"
    use_text_fields = not use_text_fields

    redirect_params = {
        'engine': engine_name,
        'typingiscool': use_text_fields,
        'sl': from_lang,
        'tl': to_lang,
        'text': text
    }

    return redirect(
        f"/?{urlencode(redirect_params)}",
        code=302,
    )

@app.route("/", methods=["GET", "POST"])
async def index():
    engine_name = request.args.get("engine")

    engine = get_engine(engine_name, engines, engines[0])

    from_lang, to_lang, inp, translation = "", "", "", None

    if request.method == "GET":
        # support google format
        inp = request.args.get("text", "")

        from_lang = to_full_name(request.args.get("sl", "auto"), engine)

        to_lang = to_full_name(request.args.get("tl", "en"), engine)

        if session.get('from_lang'):
            from_lang = to_full_name(session['from_lang'], engine)
        if session.get('to_lang'):
            to_lang = to_full_name(session['to_lang'], engine)

    elif request.method == "POST":
        form = await request.form

        inp = form.get("input", "")

        from_lang = form.get("from_language", "Autodetect")

        to_lang = form.get("to_language", "English")

        session['from_lang'] = to_lang_code(from_lang, engine)
        session['to_lang'] = to_lang_code(to_lang, engine)

    from_l_code = None
    to_l_code = None

    if not (inp == "" or inp.isspace()):
        from_l_code = to_lang_code(from_lang, engine)
        to_l_code = to_lang_code(to_lang, engine)
        translation = engine.translate(
            inp,
            to_language=to_l_code,
            from_language=from_l_code,
        )

    use_text_fields = request.args.get("typingiscool") == "True"

    return await render_template(
        "index.html",
        inp=inp,
        translation=translation,
        from_l=from_lang,
        from_l_code=from_l_code,
        to_l=to_lang,
        to_l_code=to_l_code,
        engine=engine.name,
        engines=[engine.name for engine in engines],
        supported_languages=engine.get_supported_languages(),
        use_text_fields=use_text_fields,
    )


@app.route("/about", methods=["GET"])
async def about():
    return await render_template("about.html")


if __name__ == "__main__":
    app.run(port=5000, host='0.0.0.0')
