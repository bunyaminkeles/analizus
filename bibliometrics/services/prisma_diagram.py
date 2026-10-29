"""
PRISMA tarzı kayıt akış diyagramı (B3-3).
report_notes.py'nin ürettiği notes['flow'] ([(etiket, sayı), ...]) listesini
dikey kutu+ok diyagramına çevirir. analyzer.py'nin global rcParams'ına
bağımlı değil — export_builder.py/vosviewer_export.py gibi bağımsız modül.
"""
import io
import textwrap

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from django.utils.formats import number_format
from django.utils.translation import gettext

_BOX_COLOR = '#1e3a5f'
_LAST_BOX_COLOR = '#059669'
_ARROW_COLOR = '#475569'


def build_prisma_png(flow: list) -> bytes:
    """flow boşsa None döner (çağıran atlar)."""
    if not flow:
        return None

    n = len(flow)
    box_h, gap = 1.0, 0.55
    fig_h = n * box_h + (n - 1) * gap + 0.7
    fig, ax = plt.subplots(figsize=(6.5, fig_h))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, fig_h)
    ax.axis('off')

    y = fig_h - 0.35
    for i, (label, count) in enumerate(flow):
        is_last = i == n - 1
        face = _LAST_BOX_COLOR if is_last else _BOX_COLOR
        box = mpatches.FancyBboxPatch(
            (0.5, y - box_h), 9, box_h,
            boxstyle='round,pad=0.08,rounding_size=0.12',
            facecolor=face, edgecolor='white', linewidth=1.5,
        )
        ax.add_patch(box)
        wrapped = textwrap.fill(label, 42)
        ax.text(5, y - box_h * 0.38, wrapped, ha='center', va='center',
                color='white', fontsize=10.5, fontweight='bold')
        ax.text(5, y - box_h * 0.78, number_format(count, force_grouping=True) + ' ' + gettext('kayıt'),
                ha='center', va='center', color='white', fontsize=13, fontweight='bold')
        if i < n - 1:
            ax.annotate('', xy=(5, y - box_h - gap), xytext=(5, y - box_h),
                        arrowprops=dict(arrowstyle='-|>', color=_ARROW_COLOR, lw=2))
        y -= box_h + gap

    ax.set_title(gettext('Kayıt Akış Diyagramı'), fontsize=14, fontweight='bold',
                color=_BOX_COLOR, pad=12)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    buf.seek(0)
    return buf.read()
