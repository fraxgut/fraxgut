#!/usr/bin/env python3
"""Build the three localised pages from README.md.

README.md is the source. Each copy adjusts its asset paths and its
language selector, then applies its own dictionary, so the four pages
never drift apart. Run this after every edit to README.md.
"""

import pathlib
import subprocess
import tempfile

# Paths resolve from this file, so the scripts run from anywhere.
REPO = pathlib.Path(__file__).resolve().parent.parent


def terminus(size):
    """Return a Terminus face, unpacking the console font on demand.

    Terminus ships gzipped in /usr/share/fonts, and FreeType needs it
    unpacked. The copy lands in a temporary directory, never in the
    repository.
    """
    from PIL import ImageFont
    name = {12: "ter-x12b", 16: "ter-x16b"}[size]
    out = pathlib.Path(tempfile.gettempdir()) / f"{name}.pcf"
    if not out.exists():
        src = pathlib.Path("/usr/share/fonts/terminus") / f"{name}.pcf.gz"
        with open(out, "wb") as fh:
            subprocess.run(["gzip", "-dc", str(src)], stdout=fh, check=True)
    return ImageFont.truetype(str(out), size)


SP = str(REPO) + "/"
base = (REPO / "README.md").read_text(encoding="utf-8")
SEL = next(l for l in base.split("\n")
           if l.startswith('<img src="assets/flags/spqr.png"'))
NAMES = {"en": "English", "es": "Spanish", "la": "Latin"}
F = '<img src="../../assets/flags/'
SELECTOR = {
 "en": (f'{F}spqr.png" alt="" height="14"> **[Latine](../la/README.md)** · '
        f'{F}burgundy.png" alt="" height="14"> **[Español](../es/README.md)** · '
        f'{F}england.png" alt="" height="14"> **English**'),
 "es": (f'{F}spqr.png" alt="" height="14"> **[Latine](../la/README.md)** · '
        f'{F}burgundy.png" alt="" height="14"> **Español** · '
        f'{F}england.png" alt="" height="14"> **[English](../en/README.md)**'),
 "la": (f'{F}spqr.png" alt="" height="14"> **Latine** · '
        f'{F}burgundy.png" alt="" height="14"> **[Español](../es/README.md)** · '
        f'{F}england.png" alt="" height="14"> **[English](../en/README.md)**'),
}


def build(lang, pairs):
    s = base.replace(SEL, "@@SEL@@")
    s = s.replace('src="assets/', 'src="../../assets/')
    s = s.replace('href="LICENCE.md"', 'href="../../LICENCE.md"')
    s = s.replace("@@SEL@@", SELECTOR[lang])
    s = s.replace("README.md\n@fraxgut\nCC-BY-SA-4.0\nProfile page in English",
                  f"i18n/{lang}/README.md\n@fraxgut\nCC-BY-SA-4.0\n"
                  f"Profile page in {NAMES[lang]}")
    missing = [o for o, _ in pairs if o not in s]
    for old, new in pairs:
        s = s.replace(old, new)
    target = REPO / "i18n" / lang / "README.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(s, encoding="utf-8")
    print(f"  {lang}: {len(s):,} bytes" + (f"   MISSING {len(missing)}" if missing else ""))
    for m in missing[:5]:
        print("      ", repr(m[:58]))

ES = [
 ("Computer Science and Engineering student at the University of Chile (DCC/FCFM).**\n\n*Focused on systems, open source, Unix-like systems, and software engineering.*",
  "Estudiante de Ingeniería Civil en Computación en la Universidad de Chile (DCC/FCFM).**\n\n*Enfocado en sistemas, código abierto, sistemas tipo Unix e ingeniería de software.*"),
 ("## About", "## Sobre mí"),
 ("I study Computer Science and Engineering at the\n**University of Chile**, in the Department of Computer Science\n(**DCC**) of the Faculty of Physical and Mathematical Sciences\n(**FCFM**).",
  "Estudio Ingeniería Civil en Computación en la **Universidad de\nChile**, en el Departamento de Ciencias de la Computación (**DCC**) de\nla Facultad de Ciencias Físicas y Matemáticas (**FCFM**)."),
 ("My main interests are systems, free and open-source software,\nUnix-like operating systems, and software engineering. I tend to work\nfrom the shell, primarily with **Neovim**.",
  "Mis principales intereses son los sistemas, el software libre y de\ncódigo abierto, los sistemas operativos tipo Unix y la ingeniería de\nsoftware. Suelo trabajar desde la shell, principalmente con **Neovim**."),
 ("## Currently", "## Actualmente"),
 ("My studies at the [**University of Chile**](https://uchile.cl/) are my\nprimary focus, alongside personal software projects and my work at\n[**Venturas**](https://venturas.cl/).",
  "Mis estudios en la [**Universidad de Chile**](https://uchile.cl/) son mi\nfoco principal, junto con proyectos personales de software y mi trabajo\nen [**Venturas**](https://venturas.cl/)."),
 ("## University\n", "## Universidad\n"),
 ("<b>Degree</b></td><td>Computer Science and Engineering<", "<b>Carrera</b></td><td>Ingeniería Civil en Computación<"),
 ("<b>Department</b></td><td>Department of Computer Science (DCC)<", "<b>Departamento</b></td><td>Departamento de Ciencias de la Computación (DCC)<"),
 ("<b>Faculty</b></td><td>Faculty of Physical and Mathematical Sciences (FCFM)<", "<b>Facultad</b></td><td>Facultad de Ciencias Físicas y Matemáticas (FCFM)<"),
 ("<b>University</b></td><td>University of Chile<", "<b>Universidad</b></td><td>Universidad de Chile<"),
 ("## Computing", "## Computación"), ("<b>Systems</b>", "<b>Sistemas</b>"),
 ("<b>Working with</b>", "<b>Trabajando con</b>"), ("<b>Web &amp; markup</b>", "<b>Web y marcado</b>"),
 ("## Projects", "## Proyectos"),
 ("Advanced Gentoo installation documentation for AMD64 musl systems, covering\nOpenRC, LUKS2, Btrfs, LLVM/Clang, ThinLTO, and the Zen kernel.",
  "Documentación avanzada de instalación de Gentoo para sistemas musl en AMD64,\nque cubre OpenRC, LUKS2, Btrfs, LLVM/Clang, ThinLTO y el kernel Zen."),
 ("A personal base16 colour scheme, in full colour and in monochrome.", "Un esquema de color base16 personal, en color y en monocromo."),
 ('alt="The alchemical sign of phosphorus"', 'alt="El signo alquímico del fósforo"'),
 ("[**All public repositories →**]", "[**Todos los repositorios públicos →**]"),
 ("## Enterprises", "## Empresas"), ("Where I keep my commercial projects.", "Donde mantengo mis proyectos comerciales."),
 ("## Contact", "## Contacto"),
 ('badges/email.svg" height="28" alt="Email:', 'badges/email-es.svg" height="28" alt="Correo:'),
 ("Email is the best way to reach me. I answer as soon as I can.",
  "El correo es la mejor forma de contactarme. Respondo apenas puedo."),
 ('alt="GPG key', 'alt="Clave GPG'),
 ("## Support", "## Apoyo"),
 ("You can support my public work through\n[**Liberapay**](https://liberapay.com/fraxgut/) or cryptocurrency.",
  "Puede apoyar mi trabajo público a través de\n[**Liberapay**](https://liberapay.com/fraxgut/) o con criptomonedas."),
 ("**Monero (XMR) preferred.** Write to me for an address.", "**Monero (XMR) de preferencia.** Escríbame para conseguir una dirección."),
 ('alt="The shell"', 'alt="La shell"'), ('alt="Free software"', 'alt="Software libre"'),
 ('alt="Football"', 'alt="Fútbol"'),
 ('alt="Dragon Ball"', 'alt="Dragon Ball"'),
 ("label=VISITORS", "label=VISITAS"), ('alt="Visitor count"', 'alt="Contador de visitas"'),
 ('alt="Licence: CC BY-SA 4.0 or later"', 'alt="Licencia: CC BY-SA 4.0 o posterior"'),
]

LA = [
 ("Computer Science and Engineering student at the University of Chile (DCC/FCFM).**\n\n*Focused on systems, open source, Unix-like systems, and software engineering.*",
  "Discipulus scientiae computatralis in Universitate Chilensi (DCC/FCFM).**\n\n*Studens systematibus, fonti aperto, systematibus generis Unix et arti ingeniariae programmaturae.*"),
 ("## About", "## De me"),
 ("I study Computer Science and Engineering at the\n**University of Chile**, in the Department of Computer Science\n(**DCC**) of the Faculty of Physical and Mathematical Sciences\n(**FCFM**).",
  "Scientiae computatrali in **Universitate Chilensi** studeo, in\nDepartimento Scientiarum Computatralium (**DCC**) Facultatis\nScientiarum Physicarum et Mathematicarum (**FCFM**)."),
 ("My main interests are systems, free and open-source software,\nUnix-like operating systems, and software engineering. I tend to work\nfrom the shell, primarily with **Neovim**.",
  "Praecipue me tenent systemata, programmatura libera et aperta,\nsystemata operandi generis Unix, et ars ingeniaria programmaturae.\nPlerumque e cortice imperatorio laboro, **Neovim** utens."),
 ("## Currently", "## Nunc"),
 ("My studies at the [**University of Chile**](https://uchile.cl/) are my\nprimary focus, alongside personal software projects and my work at\n[**Venturas**](https://venturas.cl/).",
  "Studia mea in [**Universitate Chilensi**](https://uchile.cl/) praecipua\nmihi cura sunt, simul cum operibus programmaturae propriis et labore meo\napud [**Venturas**](https://venturas.cl/)."),
 ("## University\n", "## Universitas\n"),
 ("<b>Degree</b></td><td>Computer Science and Engineering<", "<b>Curriculum</b></td><td>Scientia computatralis et ars ingeniaria<"),
 ("<b>Department</b></td><td>Department of Computer Science (DCC)<", "<b>Departimentum</b></td><td>Scientiarum computatralium (DCC)<"),
 ("<b>Faculty</b></td><td>Faculty of Physical and Mathematical Sciences (FCFM)<", "<b>Facultas</b></td><td>Scientiarum physicarum et mathematicarum (FCFM)<"),
 ("<b>University</b></td><td>University of Chile<", "<b>Universitas</b></td><td>Universitas Chilensis<"),
 ("## Computing", "## Computatio"), ("<b>Editor</b>", "<b>Scriptorium</b>"), ("<b>Systems</b>", "<b>Systemata</b>"),
 ("<b>Working with</b>", "<b>In manibus</b>"), ("<b>Web &amp; markup</b>", "<b>Tela et notatio</b>"),
 ("## Projects", "## Opera"),
 ("Advanced Gentoo installation documentation for AMD64 musl systems, covering\nOpenRC, LUKS2, Btrfs, LLVM/Clang, ThinLTO, and the Zen kernel.",
  "Scriptura provecta de institutione Gentoo in systematibus musl et AMD64,\nquae OpenRC, LUKS2, Btrfs, LLVM/Clang, ThinLTO et nucleum Zen complectitur."),
 ("A personal base16 colour scheme, in full colour and in monochrome.", "Ratio colorum propria secundum base16, tam plena quam unicolor."),
 ('alt="The alchemical sign of phosphorus"', 'alt="Signum alchemicum phosphori"'),
 ("[**All public repositories →**]", "[**Omnia repositoria publica →**]"),
 ("## Enterprises", "## Negotia"), ("Where I keep my commercial projects.", "Ubi opera mea mercatoria servo."),
 ("## Contact", "## Epistulae"),
 ('badges/email.svg" height="28" alt="Email:', 'badges/email-la.svg" height="28" alt="Epistula:'),
 ("Email is the best way to reach me. I answer as soon as I can.",
  "Epistula optima via est ad me contingendum. Respondeo cum primum possum."),
 ('alt="GPG key', 'alt="Clavis GPG'),
 ("## Support", "## Subsidium"),
 ("You can support my public work through\n[**Liberapay**](https://liberapay.com/fraxgut/) or cryptocurrency.",
  "Opus meum publicum per [**Liberapay**](https://liberapay.com/fraxgut/)\nvel per nummos cryptographicos sustinere potes."),
 ("**Monero (XMR) preferred.** Write to me for an address.", "**Monero (XMR) praelatum.** Scribe mihi ut inscriptionem accipias."),
 ('alt="The shell"', 'alt="Cortex imperatorius"'), ('alt="Free software"', 'alt="Programmatura libera"'),
 ('alt="Football"', 'alt="Pediludium"'),
 ("label=VISITORS", "label=HOSPITES"), ('alt="Visitor count"', 'alt="Numerus hospitum"'),
 ('alt="Licence: CC BY-SA 4.0 or later"', 'alt="Licentia: CC BY-SA 4.0 vel posterior"'),
]

build("en", []); build("es", ES); build("la", LA)
