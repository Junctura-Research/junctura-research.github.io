-- Adds a line to the top of every research document (HTML and PDF): document
-- type (unless the subtitle already names it), evidence date, update date, and
-- on the web a link to the document's Intersection page and the PDF. Appends
-- the full disclaimer (from _disclaimer.md) to the end of every PDF. For HTML
-- pages with google-scholar: true, adds a citation_pdf_url meta tag; and adds
-- the Intersection's image as the social-share image.
-- Junction -> Intersection comes from _generated/junctions.json, written by
-- scripts/build_pages.py (pre-render).

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

local function read_junctions()
  local dir = quarto.project.directory or "."
  local f = io.open(dir .. "/_generated/junctions.json", "r")
  if not f then return {} end
  local text = f:read("a")
  f:close()
  return quarto.json.decode(text)
end

function Pandoc(doc)
  local meta = doc.meta
  local parts = {}

  local dtype = meta["document-type"] and pandoc.utils.stringify(meta["document-type"])
  local subtitle = meta["subtitle"] and pandoc.utils.stringify(meta["subtitle"]) or ""
  if dtype then
    local label = TYPE_LABELS[dtype]
    if not label then
      error("doc-meta.lua: unknown document-type '" .. dtype ..
        "'. Use research-note, intersection-report or report-update.")
    end
    if not subtitle:find(label, 1, true) then
      table.insert(parts, label)
    end
  end

  local asof = meta["as-of"] and pandoc.utils.stringify(meta["as-of"])
  if asof then
    table.insert(parts, "Evidence as of " .. fmt_date(asof))
  end
  local published = meta["date"] and pandoc.utils.stringify(meta["date"])
  local modified = meta["date-modified"] and pandoc.utils.stringify(meta["date-modified"])
  -- The web page's title block already shows Published and Modified dates
  if not quarto.doc.is_format("html") and modified and published and modified:sub(1, 10) ~= published:sub(1, 10) then
    table.insert(parts, "First published " .. fmt_date(published) .. ", updated " .. fmt_date(modified))
  end

  local junction = meta["junction"] and pandoc.utils.stringify(meta["junction"])
  local jinfo = junction and read_junctions()[junction] or nil

  local input = quarto.doc.input_file or ""
  local slug = input:match("([^/\\]+)%.qmd$")

  if #parts > 0 then
    local inlines = { pandoc.Strong(pandoc.Str(table.concat(parts, " · "))) }
    if slug and quarto.doc.is_format("html") then
      -- Intersection page and PDF download links next to the type and date line
      if jinfo then
        table.insert(inlines, pandoc.Str(" · "))
        table.insert(inlines, pandoc.Link("More in " .. jinfo["intersection-title"],
          "../intersections/" .. jinfo["intersection"] .. ".html"))
      end
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

  -- Printable copies end with the full disclaimer. On web pages it is a link
  -- in the site footer instead.
  if not quarto.doc.is_format("html") then
    local dir = quarto.project.directory or "."
    local f = io.open(dir .. "/_disclaimer.md", "r")
    if not f then error("doc-meta.lua: _disclaimer.md not found in " .. dir) end
    local text = f:read("a")
    f:close()
    local body = pandoc.read(text, "markdown").blocks
    table.insert(body, 1, pandoc.Para({ pandoc.Strong(pandoc.Str("Disclaimer")) }))
    doc.blocks:insert(pandoc.HorizontalRule())
    doc.blocks:insert(pandoc.Div(body, pandoc.Attr("", { "pdf-disclaimer" })))
  end

  if quarto.doc.is_format("html") and jinfo and not meta["image"] then
    local img = SITE_URL .. "/images/intersections/" .. jinfo["image"] .. "-og.jpg"
    quarto.doc.include_text("in-header",
      '<meta property="og:image" content="' .. img .. '">\n' ..
      '<meta property="og:image:width" content="1200">\n' ..
      '<meta property="og:image:height" content="630">\n' ..
      '<meta name="twitter:image" content="' .. img .. '">')
  end

  if quarto.doc.is_format("html") and meta["google-scholar"] and slug then
    quarto.doc.include_text("in-header",
      '<meta name="citation_pdf_url" content="' .. SITE_URL ..
      '/research/' .. slug .. '.pdf">')
  end

  return doc
end
