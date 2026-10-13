#let resume = json(bytes(sys.inputs.resume))
#let basics = resume.at("basics", default: (:))

#set document(title: basics.at("name", default: "CV"))
#set page(paper: "us-letter", margin: (x: 0.6in, y: 0.5in))
#set text(font: "New Computer Modern", size: 11pt)
#set par(justify: false, leading: 0.5em, spacing: 0.55em)
#set list(indent: 0pt, spacing: 0.4em)

#show heading.where(level: 1): it => block(above: 0.8em, below: 0.5em)[
  #set text(size: 14pt, weight: "regular")
  #smallcaps(it.body)
  #v(-0.6em)
  #line(length: 100%, stroke: 0.4pt)
]

// Renders **bold** spans so highlights stay plain Markdown in the JSON
#let rich(s) = {
  for (i, part) in s.split("**").enumerate() {
    if calc.odd(i) { strong(part) } else { part }
  }
}

#let fmt-date(s) = {
  let (y, m, d) = s.split("-").map(int)
  datetime(year: y, month: m, day: d).display("[month repr:short] [year]")
}

#let date-range(entry) = {
  let start = entry.at("startDate", default: none)
  let end = entry.at("endDate", default: none)
  if start == none { return [] }
  [#fmt-date(start) -- #if end == none [Present] else [#fmt-date(end)]]
}

#let row(left, right) = block(spacing: 0.45em, grid(
  columns: (1fr, auto),
  left, right,
))

// Font Awesome codepoints; fonts are bundled in src/fonts
#let icon(code, brand: false) = text(
  font: if brand { "Font Awesome 7 Brands" } else { "Font Awesome 7 Free Solid" },
  size: 0.9em,
  str.from-unicode(code),
)
#let network-icons = (linkedin: 0xf0e1, github: 0xf09b)
#let with-icon(code, body) = [#icon(code) #body]

#let sep = [ #h(0.3em)#text(size: 12pt)[·]#h(0.3em) ]

// Header
#let loc = basics.at("location", default: (:))
#let place = ("city", "countryCode").filter(k => k in loc).map(k => loc.at(k))
#let contact = ()
#if place.len() > 0 { contact.push(with-icon(0xf015, place.join(", "))) }
#if "phone" in basics {
  contact.push(with-icon(0xf095, link("tel:" + basics.phone, basics.phone)))
}
#if "email" in basics {
  contact.push(with-icon(0xf0e0, link("mailto:" + basics.email, basics.email)))
}
#let profiles = basics.at("profiles", default: ()).filter(p => "url" in p)
#let strip-scheme(url) = url.replace(regex("^https?://(www\.)?"), "")
#let profile-link(p) = {
  let code = network-icons.at(lower(p.at("network", default: "")), default: none)
  let label = link(p.url, strip-scheme(p.url))
  if code == none { label } else [#icon(code, brand: true) #label]
}

#align(center)[
  #text(size: 24pt, basics.at("name", default: ""))
  #v(-0.6em)
  #contact.join(sep) \
  #profiles.map(profile-link).join(sep)
]

#if "summary" in basics [
  = Profile
  #basics.summary
]

#let skills = resume.at("skills", default: ())
#if skills.len() > 0 [
  = Technical Skills
  #set text(size: 10pt)
  // Fill column-major like LaTeX multicols, which Typst's columns() does not balance
  #let half = calc.ceil(skills.len() / 2)
  #let skill-list(items) = list(
    ..items.map(s => {
      let keywords = s.at("keywords", default: ()).join(", ")
      if "name" in s [*#s.name*: #keywords] else [#keywords]
    }),
  )
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 1em,
    skill-list(skills.slice(0, half)), skill-list(skills.slice(half)),
  )
]

#let education = resume.at("education", default: ())
#if education.len() > 0 [
  = Education
  #for edu in education [
    #row(strong(edu.at("institution", default: "")), emph(date-range(edu)))
    #row(
      emph((edu.at("studyType", default: none), edu.at("area", default: none))
        .filter(x => x != none)
        .join(" of ")),
      if "score" in edu [Grade: #edu.score],
    )
    #let courses = edu.at("courses", default: ())
    #if courses.len() > 0 {
      set text(size: 10pt)
      [*Relevant Modules:* #courses.join(", ")]
    }
  ]
]

#let work = resume.at("work", default: ())
#if work.len() > 0 [
  = Experience
  #for job in work [
    #row(strong(job.at("name", default: "")), job.at("location", default: none))
    #row(emph(job.at("position", default: "")), emph(date-range(job)))
    #for h in job.at("highlights", default: ()) [
      - #rich(h)
    ]
  ]
]

#let projects = resume.at("projects", default: ())
#if projects.len() > 0 [
  = Projects
  #set text(size: 10pt)
  #for p in projects [
    - #if "name" in p [*#p.name*: ]#rich(p.at("description", default: ""))
  ]
]
