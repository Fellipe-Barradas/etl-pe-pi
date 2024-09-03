import re

BUSCA_PADRAO = re.compile("(LEI|DECRETO|EMENDA CONSTITUCIONAL|RESOLUÇ(Ã|A)O CGFR|LEI COMPLEMENTAR)\s?N(°|º)\s?\d+(\.|\/)?(\d+)?\s?(,|DE)?")
ANEXO_PADRAO = re.compile("ANEXO")
FINAL_PADRAO = re.compile("PALÁCIO DE KARNAK, ", re.IGNORECASE)