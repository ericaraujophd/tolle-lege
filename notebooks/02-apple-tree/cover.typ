// cover.typ -- Notebook 02, Apple Tree. Layout: tools/templates/notebook-cover.typ
// The art is art.svg in this folder: black silhouette shapes only, passed as
// bytes so the template can place it (see the template header).
#import "/tools/templates/notebook-cover.typ": notebook-cover
#notebook-cover(toml("notebook.toml"), read("art.svg", encoding: none))
