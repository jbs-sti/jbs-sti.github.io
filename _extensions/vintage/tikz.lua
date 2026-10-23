--[[
Schémas TikZ : une seule source pour le HTML et le PDF.

Dans un .qmd :

```{.tikz fig-cap="Légende." fig-alt="Description pour les lecteurs d'écran."}
\begin{tikzpicture}
  \node[poste] {A};
\end{tikzpicture}
```

- PDF (LaTeX) : le code est inséré tel quel, il est donc vectoriel et
  composé avec les polices du document.
- Autres formats (HTML) : le code est compilé en DVI par `latex`, puis
  converti en SVG par `dvisvgm` (tous deux fournis par TeX Live). Les
  glyphes sont convertis en tracés : le SVG ne dépend d'aucune police.

Les styles communs (`poste`, `routeur`, `message`…) sont dans
`tikz-vintage.tex`, chargé dans les deux cas.
]]

local dossier = pandoc.path.directory(PANDOC_SCRIPT_FILE)
local styles = pandoc.path.join({dossier, 'tikz-vintage.tex'})

local function compiler_svg(code)
  local source = table.concat({
    '\\documentclass[tikz,border=2pt]{standalone}',
    '\\usepackage[T1]{fontenc}',
    '\\usepackage{lmodern}',
    '\\usepackage[french]{babel}',
    '\\input{' .. styles .. '}',
    '\\begin{document}',
    code,
    '\\end{document}',
  }, '\n')
  return pandoc.system.with_temporary_directory('tikz', function(tmp)
    return pandoc.system.with_working_directory(tmp, function()
      local f = io.open('schema.tex', 'w')
      f:write(source)
      f:close()
      local ok, err = pcall(pandoc.pipe, 'latex',
        {'-interaction=nonstopmode', '-halt-on-error', 'schema.tex'}, '')
      if not ok then
        local log = io.open('schema.log')
        local detail = log and log:read('a') or tostring(err)
        error('Schéma TikZ : échec de la compilation LaTeX.\n' .. detail:sub(-2000))
      end
      pandoc.pipe('dvisvgm', {'--no-fonts', '--exact-bbox', '--output=schema.svg', 'schema.dvi'}, '')
      local svg = io.open('schema.svg', 'rb')
      local data = svg:read('a')
      svg:close()
      return data
    end)
  end)
end

function CodeBlock(cb)
  if not cb.classes:includes('tikz') then
    return nil
  end
  local legende = cb.attributes['fig-cap']
  local alt = cb.attributes['fig-alt'] or ''
  local caption = legende and pandoc.read(legende, 'markdown').blocks or {}
  local contenu
  if FORMAT:match('latex') then
    contenu = pandoc.RawBlock('latex', '{\\centering\n' .. cb.text .. '\n\\par}')
  else
    local nom = 'tikz-' .. pandoc.sha1(cb.text) .. '.svg'
    pandoc.mediabag.insert(nom, 'image/svg+xml', compiler_svg(cb.text))
    contenu = pandoc.Plain({pandoc.Image(alt, nom, '', {['fig-alt'] = alt})})
  end
  return pandoc.Figure({contenu}, caption, pandoc.Attr(cb.identifier))
end
