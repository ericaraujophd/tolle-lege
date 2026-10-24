// band.typ -- the belly band for the Fall 2026 Collection.
// Layout: tools/templates/collection-band.typ
#import "/tools/templates/collection-band.typ": collection-band
#let meta = toml("collection.toml")
// Optional personal titles, one per band, separated by "|" (see the template).
#let titles = sys.inputs.at("titles", default: "").split("|").map(t => t.trim())
#collection-band(meta, meta.notebooks.map(n => toml("/notebooks/" + n + "/notebook.toml")),
  titles: titles)
