# Docs

The markdown doc reader with _REAL_ extendability for docs.

1. Target a directory of source, and docs.
2. gather all doc files
3. Gather references

A file

1. Markdown with Cogs
2. render by location
3. through jinja


### Target

Building will need the config. This shouldn't change during buildout for master
properties.

A user should be able to present:

+ A single file
+ A directory

A single file may be:

+ A target .md file
+ A Config file

When given a directory, it should be tested for a config file, else the directory
is used with a blank config.

### Config Load

The config file should be:

+ through the cli.
+ A named file such as "appname.json"
+ pyproject.toml
+ a `.docs` file

All files should resolve as a python dictionary, given:

+ Json, toml, yaml
+ Python classing

All dict data is leveraged through a facade class. The user may extend the class
as an active config.

### Doc File Scanning

Once the config is loaded; the base path is rechecked and scanned for all files.
Next is the output directory; resolved through the config and stored for later.

+ All files are indexed and text aggregated
+ Asset directories are marked

### Cross Reference

The cross referencing stage should build a tree of file sibling associations, words,
tags and phrases - general linkage across files.


### Render

Once all assets are prepared and cross-referenced, the renderer may produce finished
html (or any output format) through a translator.

Each new file is dumped into the output directory; with any changes:

+ Directory building, file index naming
+ Through a Jinga template
+ With html/css/js injections


# Other Notes

Mostly this extends the markdown writer, with a host of config features to allow
much deeper doc design.
