# The Doc Tool


## What is it?

It's actually a giant config config loading machine, complete with a cheap plugin
interface, allowing the execution of actions during 'phases'


## What's a Phase?

A walking procedure over all files, geared towards a particular action, such as text generation or file writing.


## Why another Doc tool?

I'm trying to find the perfect tool and after 10 years of dev I find doccing is boring. I've come to enjoy writing good clear functional docs - but there's a massive gap between:

+ Integration of source code and source docs
+ Outbound rendering choices
+ Styling, Plugin injection (general full fat customisation)

I'll use any doc-tool give through a project and with each I've found:

+ A tight coupling to a unique task (e.g. Sphinx or PyDoc)
+ esoteric internal functionality
+ opinionated output / limited extendibility.

And when extending; I'm doing the same things repeatedly:

+ Hook up a highlight syntaxer
+ Build out a demo suite
+ Build some sort of DRY markdown writer

As such, I've written this tool:

+ Read a config using json, toml, yaml
+ Build a box of html using markdown
+ using standard site dev work such as jinja

Finally the _bits in the middle_ are the interesting components.

### My Doc-tool Wishlist

Some feature I would like when writing docs:

+ automatic cross-referencing of files (hyperlinks) without me writing/understanding destination files
+ asset management; copying tagged sources (images, pdfs etc...) to the output - with correct linkage
+ automatic generation of index files, _"sibling" pages_
+ customisable HTML output, e.g. real site dev with jinja
+ in memory data management; no disk writing required
+ multiple independent doc sources processed in association; for larger apps and many doc sources
+ micro-templating for custom html parts with JS/CSS interaction.
+ demo injection/file association with a custom markdown syntax and demo directory.
+ DRY style markdown section snipping across files for less repetition.


### Unique Features:

This lib is more precisely is a "complex config loader (with file redirection) and plugin runner - combined a shared data storage.". With that I've build a range of simple processors to:

+ Iterate all files in an index
+ bridge references across all files through file text inspection
+ a HTML renderer leveraging markdown and jinja


### Technical Loadout:

The tool accepts a range of input files as target directories or config. For each path, a new "config" executes and runs many plugins. Each plugin does its own thing.

1. The Lib: `Generator` to load and run all configs
2. A `Config` to act as a stable dict during plugin execution
3. Many plugins as integrated `Utility` classes.


### Features

I feel the true features are the _lack_ of overhead tooling.

1. Nothing but plugins! to override and work with
2. Micro configurations with an easy API within the Utility
3. No opinion rendering; currently using `jinja`



## Generator

A `Generator` runs all phases in an ordered sequence, calling upon each `Config` when required to execute API functions. The hooked 'utilities' perform any changes to the storage.

The generator maintains the _master storage_, a `dict` holding all references (filenames) with dictionaries of information, populated by loaded `Utility` classes.

The generator does not handle any file related tasks; purely handling the task farming to the internal configs.


## Config

A `Config` unit runs Utilities and provides all the resources such as methods and data for any running `Utility`.

The config has reference to the parent generator but should rarely require interaction.


## Utility

A single utility runs any literal actions, called by the config when required. The pre-defined API methods allow editing of the data structures (with the shared storage) during any pre-render phases.

The `General` and `Writer` and the two core classes for this library, allowing _general_ file collection and parsing, followed by _writing_ to disk. In this case a HTML website leveraging Jinja.


# Simple Integration Demo

Importantly when extending the tooling it should be very easy.

1. Write a python Utility
2. Mount through config file or code
3. Utilise values within the output site.


# Wanted / Considerations

Some elements I have tackled, or are ideas for the future

Easy snippets should look something like this in file:

    ... lorem ipsum
    [@/demos/file1.py]

The syntax is undecided; but the magic reference should inject this file.
Snipping from other files - for example; picking the third item within the content of `other.md`.

    ... lorem ipsum
    [@other.md#3]

Functional doc referencing from the attached source code:

    ... lorem ipsum
    [@lib.module.func.__docs__]

    # some special print routine:
    [@lib.module.func.data|signature_and_doc]


## Multi rendering

Markdown internal processors have a routine to work with multi rendering exposing this should be at the template level.

Currently the process is:

              .html -> template
                          |
    .md -> rendered -> jinja -> output

The jinja template acts as a site template renderer, applying the content rendered HTML.
It would be good to have a recursive renderer, oh which each module may present more markdown, until the file is finished _bubbling_ markdown injections, then the output renderer converts the markdown.


             |-restack -¬
             v          |
    .md -> render -> plugin md -> jinja -> output


## Dependency Tree

For each file with a dependency upon a sibling, assign a tree of 'dependencies'. If a change occurs upon a file, its dependencies may render alterations in the same phase - such as index files and snippet references.

Within the tooling, if a utility builds a change given two associated files, it assigns a dependency address and an optional tagged attribute. When the file changes, the config re-renders the dependencies.

A dependency is a filename association with a filename:

```py
data_store['/index.md'] = {
    'content': "#My Markdown\nSome content."
    # ... attributes
    'depends_upon': ['/todo.md'],
    '__dirty__': False,
}
```

then flagging a change:

```py
data_store['/todo.md']['title'] = 'egg'
data_store['/todo.md']['__dirty__'] = True
```

## Change Detection

Only update files given the last modified (or CRC) of the last state. Thus a _changes_ file may track textual updates automatically.

## Git Read

Grab the content of git commits for change file updates.

---

# Doc Structures

[My] Documentation is written and exported in a few generic ways within a project.

+ A single `readme.md`
+ A top level readme with a relative `docs/`
+ No top-level - but with a `docs/` and a potential `docs/readme.md`
+ Many associated projects, with multiple `[root][app]docs/` for each project within a parent.
