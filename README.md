# thing
a thing :3

reads source engine logs and takes screenshots when a chat message matches a regex statement
used for gathering evidence to report people who are consistent rule-breakers
developed for tf2 but should work with any source 1 game

simple instructions:
1. add `-condebug -conclearlog` to the game's launch options in steam
2. run the script (or executable), this will generate a new config.yaml file
3. add the path to your console log (by default in tf2, its called `console.log` and its in your tf folder) after `SOURCE_LOG: ` in config.yaml
4. add the path to the folder you want to store screenshots in after `SCREENSHOT_FOLDER: ` in config.yaml
5. set the pattern you want to match in chat that triggers the program after `REGEX_STATEMENT: ` in config.yaml
6. run the script (or executable) again to start the logging
7. launch tf2 (or other source 1 game)