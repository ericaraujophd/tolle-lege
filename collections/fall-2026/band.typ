// band.typ -- the belly band for the Fall 2026 Collection.
// Layout: tools/templates/collection-band.typ
#import "/tools/templates/collection-band.typ": collection-band
#let meta = toml("collection.toml")
#collection-band(meta, meta.notebooks.map(n => toml("/notebooks/" + n + "/notebook.toml")))
