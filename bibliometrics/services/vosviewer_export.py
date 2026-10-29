"""
VOSviewer uyumlu dışa aktarım (B3-2). Format resmi dokümandan doğrulandı
(https://app.vosviewer.com/docs/file-types/map-and-network-file-type/):
- Map dosyası: tab-ayraçlı, başlık satırlı. `id`+`label` yeterli (diğer
  sütunlar — x/y/cluster — zorunlu değil).
- Network dosyası: başlıksız, `id1\tid2\tweight`.
Bilinçli olarak x/y/cluster GÖNDERMİYORUZ — VOSviewer'ın "Create a map
based on network data" akışında kendi yerleşim+kümeleme algoritmasını
çalıştırmasına izin veriyoruz; bizim asıl katkımız temizlenmiş/doğru
ağırlıklandırılmış kenar verisidir (bkz. plan dosyası gerekçesi).
"""
import io
import zipfile

from django.utils.translation import gettext

from bibliometrics.services.analyzer import (
    keyword_clusters,
    _author_collaboration_graph,
    _country_collaboration_graph,
    _bibliographic_coupling_graph,
)


def _quote_if_needed(label: str) -> str:
    """VOSviewer kuralı: etiket virgül/noktalı virgül içeriyorsa çift tırnağa alınır."""
    if ',' in label or ';' in label:
        return '"%s"' % label.replace('"', '""')
    return label


def _write_map_file(nodes: list) -> str:
    """nodes: [(id, label, weight), ...]"""
    lines = ['id\tlabel\tweight<Occurrences>']
    for node_id, label, weight in nodes:
        lines.append(f'{node_id}\t{_quote_if_needed(label)}\t{weight}')
    return '\n'.join(lines) + '\n'


def _write_network_file(edges: list) -> str:
    """edges: [(id1, id2, weight), ...] — başlıksız."""
    return '\n'.join(f'{a}\t{b}\t{w}' for a, b, w in edges) + '\n'


def _graph_to_files(G) -> tuple:
    """Bir networkx Graph'ı (map_text, network_text) çiftine çevirir.
    Düğüm ağırlığı = derece (kaç farklı düğümle bağlantılı)."""
    node_ids = {node: i + 1 for i, node in enumerate(G.nodes())}
    degrees = dict(G.degree())
    nodes = [(node_ids[n], str(n), degrees.get(n, 0)) for n in G.nodes()]
    edges = [
        (node_ids[u], node_ids[v], data.get('weight', 1))
        for u, v, data in G.edges(data=True)
    ]
    return _write_map_file(nodes), _write_network_file(edges)


# (zip içindeki dosya adı öneki, G üreten fonksiyon)
_NETWORKS = [
    ('anahtar_kelime_es_olusumu', lambda records: keyword_clusters(records)[0]),
    ('yazar_isbirligi', _author_collaboration_graph),
    ('ulke_isbirligi', _country_collaboration_graph),
    ('bibliyografik_eslesme', _bibliographic_coupling_graph),
]


def _readme_text() -> str:
    return gettext(
        'Bu paket, VOSviewer (https://www.vosviewer.com) ile görselleştirmek üzere '
        'dışa aktarılmış ağ verilerini içerir.\n\n'
        'Her ağ için iki dosya vardır: "..._map.txt" (düğümler) ve "..._network.txt" '
        '(bağlantılar). VOSviewer\'ı açın: Dosya > Oluştur > "Ağ verisine dayalı harita" '
        '(Create > Create a map based on network data) sihirbazını seçin, ilgili '
        '"_map.txt" dosyasını ve ardından "_network.txt" dosyasını gösterin. VOSviewer '
        'yerleşim ve kümelemeyi kendisi hesaplayacaktır.\n\n'
        'Veriler Analizus bibliometrik analiz aracında tekilleştirilmiş, yazar adları '
        'birleştirilmiş ve anahtar kelimeler normalize edilmiş kayıtlardan üretilmiştir.'
    )


def build_vosviewer_zip(records: list[dict]):
    """4 ağın (varsa) map+network dosya çiftlerini bir ZIP'e paketler.
    Hiçbir ağ üretilemediyse None döner."""
    buf = io.BytesIO()
    any_network = False

    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for prefix, graph_fn in _NETWORKS:
            try:
                G = graph_fn(records)
            except Exception:
                G = None
            if G is None or G.number_of_nodes() == 0:
                continue
            map_text, network_text = _graph_to_files(G)
            zf.writestr(f'{prefix}_map.txt', map_text)
            zf.writestr(f'{prefix}_network.txt', network_text)
            any_network = True

        if not any_network:
            return None
        zf.writestr('OKUBENI.txt', _readme_text())

    return buf.getvalue()
