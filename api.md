# SimplyTranslate Web API
## How to access the API
By going to the path `/api/`.\
Ex: https://simplytranslate.org/api/target_languages.

## Translate
Path `/api/translate/`
#### Arguments
* `engine`
    * `google`

        Google Translate
    * `libre`

        Libre Translate

* `from`

    Choose the From-Language (Source Language). It's based on the engine.
* `to`

    Choose the To-Language (Target Language). It's based on the engine.

* `text`

    The original text (input).

Ex: https://simplytranslate.org/api/translate/?engine=google&from=en&to=es&text=Hello.

## Get Languages
Path `/api/get_languages/`
#### Arguments
* `engine`
    * `google`

        Google Translate
    * `libre`

        Libre Translate

Ex: https://simplytranslate.org/api/get_languages/?engine=google.

## Text-To-Speech (TTS)
Path `/api/tts/`
#### Arguments
* `engine`
    * `google`

        Google Translate
    * `libre`

        Libre Translate

* `lang`

    Choose the language. It's based on the engine.

* `text`

    Input.

Ex: https://simplytranslate.org/api/tts/?engine=google&lang=en&text=Hello.