// band.typ -- the belly band for the Confessions pair (Nos. 03 and 04).
// Layout: tools/templates/collection-band.typ
#import "/tools/templates/collection-band.typ": collection-band
#let meta = toml("collection.toml")
// Optional personal titles, one per band, separated by "|" (see the template).
#let titles = sys.inputs.at("titles", default: "").split("|").map(t => t.trim())
#collection-band(meta, meta.titles.map(t => toml("/titles/" + t + "/title.toml")),
  titles: titles)
