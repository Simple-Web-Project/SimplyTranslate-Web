# SimplyTranslate Web

This is a simple web interface for SimplyTranslate

## List of Instances
You can find a list of instances here: [SimplyTranslate Project Page](https://simple-web.org/projects/simplytranslate.html)

If you want to integrate a list of instances in your project, you can use this endpoint to always have an up-to-date list of all instances known to us: [https://simple-web.org/instances/simplytranslate](https://simple-web.org/instances/simplytranslate)


If you want to add your own instance here, please either send me an email directly to simpleweb@metalune.xyz or tell us about it in our IRC channel #simple-web on [Libera.Chat](https://libera.chat)

## How to install/use

### Clone the repository
```sh
git clone https://codeberg.org/SimpleWeb/SimplyTranslate-Web
cd SimplyTranslate-Web
```

### Install the dependencies
```sh
pip install -r requirements.txt
```

### Run the main.py
```sh
# Directly
python3 main.py
# Using uvicorn
uvicorn main:app --port 5000
```

### Configuration
You can configure SimplyTranslate by editing these files:
Either this in the project directory:
```
config.conf
```
Shared Between all supported SimplyTranslate Frontends (like SimplyTranslate-Gemini):
```
/etc/simplytranslate/shared.conf
```
Configuration file specifically for this frontend:
```
/etc/simplytranslate/web.conf
```
Or if you want to specify your own config file path you can just pass the argument `-c` or `--config`

## How to contribute
1. Setup git-email: https://git-send-email.io
2. Clone the repo you want: `git clone https://codeberg.org/SimpleWeb/SimplyTranslate-Web`
3. Branch it: `git checkout -b my-cool-changes`
4. Add your changes: `git add .` and commit them `git commit -m "My Cool Changes"`
5. Set mail-to: `git config sendemail.to '~metalune/simplytranslate-devel@lists.sr.ht'`
6. Send your commit: `git send-email master`

## API
[Documentation](./api.md)

## Contact

To get in contact with the developers, visit us on the #simple-web IRC channel on [Libera.Chat](https://libera.chat)

## Legal Notice
SimplyTranslate does not host any content. All content on SimplyTranslate is from Google Translate, DeepL, ICIBA, Reverso and LibreTranslate. SimplyTranslate is not affiliated with Google Translate, DeepL, ICIBA, Reverso or LibreTranslate that SimplyTranslate relays.

Trademarks belong to their respective owners. Google Translate is a trademark of Google LLC. DeepL is a trademark of DeepL SE. Reverso is a trademark of Reverso. LibreTranslate is a trademark of LibreTranslate.

The creators of this repository assume no liability for the accuracy and timeliness of any information provided above. Trademark owner information was researched to the best of the author's knowledge at the time of curation and may be outdated or incorrect.

## License

SimplyTranslate-Web is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

SimplyTranslate-Web is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
