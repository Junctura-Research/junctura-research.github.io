-- Adds a document-type and "as of" line to the top of every research document
-- (HTML and PDF), and, for HTML pages with google-scholar: true, a
-- citation_pdf_url meta tag pointing at the PDF version.

local TYPE_LABELS = {
  ["research-note"] = "Research Note",
  ["intersection-report"] = "Intersection Report",
  ["report-update"] = "Report Update",
}

local MONTHS = { "January", "February", "March", "April", "May", "June", "July",
  "August", "September", "October", "November", "December" }

local function fmt_date(s)
  local y, m, d = s:match("^(%d%d%d%d)%-(%d%d)%-(%d%d)")
  if not y then return s end
  return tostring(tonumber(d)) .. " " .. MONTHS[tonumber(m)] .. " " .. y
end

local SITE_URL = "https://juncturaresearch.com"

function Pandoc(doc)
  local meta = doc.meta
  local parts = {}

  local dtype = meta["document-type"] and pandoc.utils.stringify(meta["document-type"])
  if dtype then
    local label = TYPE_LABELS[dtype]
    if not label then
      error("doc-meta.lua: unknown document-type '" .. dtype ..
        "'. Use research-note, intersection-report or report-update.")
    end
    table.insert(parts, label)
  end

  local asof = meta["as-of"] and pandoc.utils.stringify(meta["as-of"])
  if asof then
    table.insert(parts, "Evidence as of " .. fmt_date(asof))
  end

  local input = quarto.doc.input_file or ""
  local slug = input:match("([^/\\]+)%.qmd$")

  if #parts > 0 then
    local inlines = { pandoc.Strong(pandoc.Str(table.concat(parts, " · "))) }
    if slug and quarto.doc.is_format("html") then
      -- PDF download link next to the type and date line
      table.insert(inlines, pandoc.Str(" · "))
      table.insert(inlines, pandoc.Link("Download PDF", slug .. ".pdf"))
    elseif slug then
      -- In the PDF, point back to the web version and its data appendix
      local url = SITE_URL .. "/research/" .. slug .. ".html"
      table.insert(inlines, pandoc.LineBreak())
      table.insert(inlines, pandoc.Str("Web version: "))
      table.insert(inlines, pandoc.Link(url, url))
    end
    table.insert(doc.blocks, 1, pandoc.Div({ pandoc.Para(inlines) }, pandoc.Attr("", { "doc-meta" })))
  end

  if quarto.doc.is_format("html") and meta["google-scholar"] and slug then
    quarto.doc.include_text("in-header",
      '<meta name="citation_pdf_url" content="' .. SITE_URL ..
      '/research/' .. slug .. '.pdf">')
  end

  return doc
end
