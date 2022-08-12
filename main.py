from quart import (
    Quart,
    render_template,
    request,
    redirect,
    make_response,
    send_file,
    Response,
    abort,
)
from configparser import ConfigParser
import argparse
import os
from urllib.parse import urlencode
from wsgiref.util import FileWrapper
from io import BytesIO

from simplytranslate_engines.googletranslate import GoogleTranslateEngine
from simplytranslate_engines.libretranslate import LibreTranslateEngine
from simplytranslate_engines.icibatranslate import IcibaTranslateEngine
from simplytranslate_engines.deepl import DeeplEngine
from simplytranslate_engines.reverso import ReversoTranslateEngine
from simplytranslate_engines.utils import *

import requests


def read_config():
    config.read(config_paths)

    if config.getboolean("google", "Enabled", fallback=True):
        engines.append(GoogleTranslateEngine())

    if config.getboolean("deepl", "Enabled", fallback=False):
        engines.append(DeeplEngine())

    if config.getboolean("iciba", "Enabled", fallback=False):
        engines.append(IcibaTranslateEngine())

    if config.getboolean("reverso", "Enabled", fallback=False):
        engines.append(ReversoTranslateEngine())

    if config.getboolean("libre", "Enabled", fallback=False):
        engines.append(
            LibreTranslateEngine(
                config["libre"]["Instance"],
                # `ApiKey` is not required, so use `get` to get `None` as fallback.
                config["libre"].get("ApiKey"),
            )
        )

    if not engines:
        raise Exception("All translation engines are disabled")


config = ConfigParser()
engines = []
config_paths = [
    "config.conf",
    "/etc/simplytranslate/shared.conf",
    "/etc/simplytranslate/web.conf",
]

# This ain't clean, but it works.
if __name__ != "__main__":
    read_config()

app = Quart(__name__)

app.url_map.strict_slashes = False


def str_to_bool(s, **kwargs):
    if s is None and "default" in kwargs:
        return kwargs["default"]

    return s == "on" or s == "True"


def bool_to_str(b):
    return "True" if b else "False"


def dict_to_prefs(d, **kwargs):
    # For whatever reason, in HTML forms, the values of any unchecked
    # checkboxes are not sent at all, so we have this parameter that basically
    # disables the defaulting for any boolean settings.
    post_form = kwargs.get("post_form")

    return {
        # We don't need to consider `post_form` for `use_text_fields` since
        # it's off by default anyway, unlike `tts_enabled`.
        "use_text_fields": str_to_bool(d.get("use_text_fields")),
        "tts_enabled": str_to_bool(
            d.get("tts_enabled"), default=False if post_form else True
        ),
    }


# NOTE: Legacy Endpoint. Use "/api"
@app.route(
    "/translate/<string:from_language>/<string:to_language>/<string:input_text>/",
)
async def translate(from_language, to_language, input_text):
    return await engines[0].translate(
        input_text, from_language=from_language, to_language=to_language
    )


@app.route("/api/translate/", methods=["GET", "POST"])
async def api_translate():
    if request.method == "POST":
        args = await request.form
    elif request.method == "GET":
        args = request.args

    engine_name = args.get("engine")
    text = args.get("text")
    from_language = args.get("from")
    to_language = args.get("to")

    if from_language == None:
        from_language = "auto"

    if to_language == None:
        to_language = "en"

    engine = get_engine(engine_name, engines, engines[0])

    from_language = await to_lang_code(from_language, engine, type_="source")
    to_language = await to_lang_code(to_language, engine, type_="target")

    return await engine.translate(
        text, from_language=from_language, to_language=to_language
    )


@app.route("/prefs", methods=["POST", "GET"])
async def prefs():
    if request.method == "POST":
        prefs = dict_to_prefs(await request.form, post_form=True)
    elif request.method == "GET":
        prefs = dict_to_prefs(request.cookies)

    use_text_fields = prefs["use_text_fields"]
    tts_enabled = prefs["tts_enabled"]

    if request.method == "GET":
        return await render_template(
            "prefs.html",
            use_text_fields=use_text_fields,
            tts_enabled=tts_enabled,
        )
    elif request.method == "POST":
        response = await make_response(
            await render_template(
                "prefs.html",
                use_text_fields=use_text_fields,
                tts_enabled=tts_enabled,
            )
        )

        response.set_cookie("use_text_fields", bool_to_str(use_text_fields))
        response.set_cookie("tts_enabled", bool_to_str(tts_enabled))

        return response


@app.route("/api/source_languages/")
async def api_source_languages():
    engine_name = request.args.get("engine")
    engine = get_engine(engine_name, engines, engines[0])

    langs = await engine.get_supported_source_languages()
    return "".join(f"{lang}\n{langs[lang]}\n" for lang in langs)


@app.route("/api/target_languages/")
async def api_target_languages():
    engine_name = request.args.get("engine")
    engine = get_engine(engine_name, engines, engines[0])

    langs = await engine.get_supported_target_languages()

    return "".join(f"{lang}\n{langs[lang]}\n" for lang in langs)


@app.route("/api/tts/")
async def api_tts():
    engine_name = request.args.get("engine")
    text = request.args.get("text")
    language = request.args.get("lang")

    engine = get_engine(engine_name, engines, engines[0])

    language = await to_lang_code(
        language, engine, type_="source"
    ) or await to_lang_code(language, engine, type_="target")

    url = await engine.get_tts(text, language)

    USER_AGENT = "Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0"

    if url is not None:
        b = BytesIO(
            requests.get(
                url, headers={"Referrer": None, "User-Agent": USER_AGENT}
            ).content
        )
        w = FileWrapper(b)
        return Response(w, mimetype="audio/mpeg")

    abort(404)


@app.route("/switchlanguages/", methods=["POST"])
async def switchlanguages():
    form = await request.form

    engine_name = request.args.get("engine")

    engine = get_engine(engine_name, engines, engines[0])

    text = form.get("input", "")
    from_lang = await to_lang_code(
        form.get("from_language", "Autodetect"), engine, type_="source"
    )
    to_lang = await to_lang_code(
        form.get("to_language", "English"), engine, type_="target"
    )

    if from_lang == "auto":
        detected_lang = await engine.detect_language(text)

        if detected_lang is not None:
            from_lang = detected_lang

    if from_lang != "auto":
        from_lang, to_lang = to_lang, from_lang

    """
    In case we ever want to also switch the translated text with the to-be-translated text, this is a good start.

    translation = engine.translate(
        text,
        to_language=to_lang,
        from_language=from_lang,
    )
    """

    redirect_params = {
        "engine": engine_name,
        "sl": from_lang,
        "tl": to_lang,
        "text": text,
        "could_not_switch_languages": from_lang == "auto",
    }

    response = await make_response(
        redirect(
            f"/?{urlencode(redirect_params)}",
            code=302,
        ),
    )

    response.set_cookie("from_lang", from_lang)
    response.set_cookie("to_lang", to_lang)

    return response


@app.route("/", methods=["GET", "POST"])
async def index():
    engine_name = request.args.get("engine")

    engine = get_engine(engine_name, engines, engines[0])

    from_lang, to_lang, inp, translation = "", "", "", None

    # This is `True` when the language switch button is pressed, `from_lang` is
    # "auto", and the engine doesn't support language detection.
    could_not_switch_languages = False

    if request.method == "GET":
        # support google format
        inp = request.args.get("text", "")

        from_lang = await to_full_name(
            request.args.get("sl") or request.cookies.get("from_lang") or "auto",
            engine,
            "source",
        )

        to_lang = await to_full_name(
            request.args.get("tl") or request.cookies.get("to_lang") or "en",
            engine,
            "target",
        )

        could_not_switch_languages = str_to_bool(
            request.args.get("could_not_switch_languages")
        )
    elif request.method == "POST":
        form = await request.form

        inp = form.get("input", "")

        from_lang = form.get("from_language", "Autodetect")

        to_lang = form.get("to_language", "English")

    from_l_code = None
    to_l_code = None

    if not (inp == "" or inp.isspace()):
        from_l_code = await to_lang_code(from_lang, engine, type_="source")
        to_l_code = await to_lang_code(to_lang, engine, type_="target")
        translation = await engine.translate(
            inp,
            to_language=to_l_code,
            from_language=from_l_code,
        )

    # TTS
    tts_from = None
    tts_to = None
    # check if the engine even supports TTS
    if await engine.get_tts("auto", "test") is not None:
        if inp:
            params = {"engine": engine_name, "lang": from_l_code, "text": inp}
            tts_from = f"/api/tts/?{urlencode(params)}"

        if translation is not None and translation["translated-text"]:
            params = {
                "engine": engine_name,
                "lang": to_l_code,
                "text": translation["translated-text"],
            }
            tts_to = f"/api/tts/?{urlencode(params)}"

    prefs = dict_to_prefs(request.cookies)

    response = await make_response(
        await render_template(
            "index.html",
            inp=inp,
            translation=translation,
            from_l=from_lang,
            from_l_code=from_l_code,
            tts_from=tts_from,
            tts_to=tts_to,
            to_l=to_lang,
            to_l_code=to_l_code,
            engine=engine.name,
            engines=engines,
            supported_source_languages=await engine.get_supported_source_languages(),
            supported_target_languages=await engine.get_supported_target_languages(),
            use_text_fields=prefs["use_text_fields"],
            tts_enabled=prefs["tts_enabled"],
            could_not_switch_languages=could_not_switch_languages,
        )
    )

    if request.method == "POST":
        response.set_cookie(
            "from_lang", await to_lang_code(from_lang, engine, type_="source")
        )
        response.set_cookie(
            "to_lang", await to_lang_code(to_lang, engine, type_="target")
        )

    return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Specify path of config file")
    args = parser.parse_args()

    if args.config is not None:
        if os.path.isfile(args.config):
            config_paths = [args.config]
        else:
            print(
                f"INFO: Ignoring specified config file path '{args.config}' because the file doesn't exist."
            )

    read_config()

    app.run(
        port=config.getint("network", "port", fallback=5000),
        host=config.get("network", "host", fallback="0.0.0.0"),
    )
