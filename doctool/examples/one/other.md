title: another
destination_dirs: other/foo/
                  egg/butter
tags: first, other, getting started,
      another,
      last-one
name: another (actually other)
---
# Hello

This is another file, with "another" as the title. linked from [[readme.md]]

---

meta name: {{ meta.name.0 }}
name: {{ name }}
tags {{ tags }}
title: {{ title }}
base template name: {{ base_template_name }}
base markdown template name: {{ base_markdown_template_name }}
filename name: {{ rel_filename }}
destination_filename: {{destination_filename}}
