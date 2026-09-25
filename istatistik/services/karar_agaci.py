"""
Karar Ağacı Sınıflandırması
sklearn DecisionTreeClassifier; doğruluk metrikleri, confusion matrix, feature importance.
"""
import io
from django.utils.translation import gettext
import numpy as np


def analyze(df, target_col: str, feature_cols: list,
            max_depth: int = 5, test_size: float = 0.2,
            criterion: str = 'gini') -> dict:
    import pandas as pd
    from sklearn.tree import DecisionTreeClassifier, export_text
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
    from sklearn.preprocessing import LabelEncoder

    if target_col not in df.columns:
        raise ValueError(gettext('"%(target_col)s" hedef sütunu bulunamadı.') % {'target_col': target_col})
    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        raise ValueError(gettext('Şu sütunlar bulunamadı: %(v)s') % {'v': ', '.join(missing)})
    if not feature_cols:
        raise ValueError(gettext('En az 1 özellik sütunu seçilmelidir.'))
    if target_col in feature_cols:
        raise ValueError(gettext('Hedef sütun, özellik sütunları arasında olamaz.'))

    sub = df[[target_col] + list(feature_cols)].dropna()
    n = len(sub)
    if n < 10:
        raise ValueError(gettext('En az 10 satır gereklidir, %(n)s satır bulundu.') % {'n': n})

    classes = sorted(sub[target_col].astype(str).unique())
    n_classes = len(classes)
    if n_classes < 2:
        raise ValueError(gettext('Hedef sütunun en az 2 farklı kategorisi olmalıdır.'))
    if n_classes > 20:
        raise ValueError(gettext('Hedef sütunda %(n_classes)s farklı değer var. Karar ağacı en fazla 20 sınıfla çalışır.') % {'n_classes': n_classes})

    le = LabelEncoder()
    y = le.fit_transform(sub[target_col].astype(str))

    X_df = pd.DataFrame(index=sub.index)
    feature_names = []
    for col in feature_cols:
        series = sub[col]
        if series.dtype == object or series.nunique() <= 10:
            dummies = pd.get_dummies(series, prefix=col, drop_first=False, dtype=float)
            X_df = pd.concat([X_df, dummies], axis=1)
            feature_names.extend(list(dummies.columns))
        else:
            X_df[col] = series.astype(float)
            feature_names.append(col)

    X = X_df.values.astype(float)

    test_size = max(0.1, min(0.4, test_size))
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y if n_classes <= 10 else None
    )

    clf = DecisionTreeClassifier(
        criterion=criterion,
        max_depth=max_depth,
        random_state=42,
    )
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    avg = 'binary' if n_classes == 2 else 'weighted'
    accuracy = float(accuracy_score(y_test, y_pred))
    precision = float(precision_score(y_test, y_pred, average=avg, zero_division=0))
    recall = float(recall_score(y_test, y_pred, average=avg, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, average=avg, zero_division=0))

    cm = confusion_matrix(y_test, y_pred).tolist()

    importances = clf.feature_importances_
    fi_sorted = sorted(
        [{'name': name, 'importance': round(float(imp), 4), 'rank': 0}
         for name, imp in zip(feature_names, importances)],
        key=lambda x: x['importance'], reverse=True
    )
    for i, item in enumerate(fi_sorted, 1):
        item['rank'] = i

    tree_text = export_text(clf, feature_names=feature_names, max_depth=5)

    return {
        'target_col': target_col,
        'feature_cols': list(feature_cols),
        'feature_names': feature_names,
        'classes': list(le.classes_),
        'n_classes': n_classes,
        'n': n,
        'n_train': len(X_train),
        'n_test': len(X_test),
        'max_depth_param': max_depth,
        'max_depth_actual': int(clf.get_depth()),
        'n_leaves': int(clf.get_n_leaves()),
        'criterion': criterion,
        'test_size': test_size,
        'accuracy': round(accuracy, 4),
        'precision': round(precision, 4),
        'recall': round(recall, 4),
        'f1': round(f1, 4),
        'confusion_matrix': cm,
        'feature_importances': fi_sorted,
        'tree_text': tree_text,
    }


def build_pdf(result: dict, filename: str, df=None) -> bytes:
    import io as _io
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from .pdf_fonts import register_fonts
    register_fonts()

    buf = _io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    PURPLE = colors.HexColor('#7c3aed')
    title_s = ParagraphStyle('T', parent=styles['Heading1'], fontSize=16, spaceAfter=6, fontName='DejaVuSans')
    h2_s = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, spaceAfter=4, fontName='DejaVuSans')
    norm_s = ParagraphStyle('N', parent=styles['Normal'], fontName='DejaVuSans', fontSize=9)
    mono_s = ParagraphStyle('M', parent=styles['Normal'], fontName='DejaVuSans', fontSize=7,
                             leading=10, leftIndent=0.5*cm)

    story = []
    story.append(Paragraph(gettext('Karar Ağacı Sınıflandırma Raporu'), title_s))
    story.append(Paragraph(gettext('Dosya: %(filename)s') % {'filename': filename}, norm_s))
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph(gettext('Model Özeti'), h2_s))
    summary_rows = [
        [gettext('Hedef Değişken'), result['target_col']],
        [gettext('Sınıflar'), ', '.join(result['classes'])],
        [gettext('Özellik Sayısı'), str(len(result['feature_cols']))],
        [gettext('Eğitim Seti (n)'), str(result['n_train'])],
        [gettext('Test Seti (n)'), str(result['n_test'])],
        [gettext('Kriter'), result['criterion'].capitalize()],
        [gettext('Maks. Derinlik (parametre)'), str(result['max_depth_param'])],
        [gettext('Gerçek Derinlik'), str(result['max_depth_actual'])],
        [gettext('Yaprak Sayısı'), str(result['n_leaves'])],
        [gettext('Doğruluk (Accuracy)'), gettext('%%%(value)s') % {'value': f"{result['accuracy']*100:.1f}"}],
        [gettext('Kesinlik (Precision)'), gettext('%%%(value)s') % {'value': f"{result['precision']*100:.1f}"}],
        [gettext('Duyarlılık (Recall)'), gettext('%%%(value)s') % {'value': f"{result['recall']*100:.1f}"}],
        [gettext('F1 Skoru'), gettext('%%%(value)s') % {'value': f"{result['f1']*100:.1f}"}],
    ]
    sum_tbl = Table(summary_rows, colWidths=[6*cm, 10*cm])
    sum_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), PURPLE),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(sum_tbl)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('Karmaşıklık Matrisi (Confusion Matrix)'), h2_s))
    cm_arr = np.array(result['confusion_matrix'])
    fig, ax = plt.subplots(figsize=(4, 3))
    im = ax.imshow(cm_arr, interpolation='nearest', cmap='Blues')
    plt.colorbar(im, ax=ax)
    ax.set_xticks(range(len(result['classes'])))
    ax.set_yticks(range(len(result['classes'])))
    ax.set_xticklabels(result['classes'], fontsize=8)
    ax.set_yticklabels(result['classes'], fontsize=8)
    ax.set_xlabel(gettext('Tahmin Edilen'), fontsize=9)
    ax.set_ylabel(gettext('Gerçek'), fontsize=9)
    ax.set_title(gettext('Confusion Matrix'), fontsize=10)
    for i in range(cm_arr.shape[0]):
        for j in range(cm_arr.shape[1]):
            ax.text(j, i, str(cm_arr[i, j]), ha='center', va='center',
                    color='white' if cm_arr[i, j] > cm_arr.max() / 2 else 'black', fontsize=10)
    plt.tight_layout()
    img_buf = _io.BytesIO()
    fig.savefig(img_buf, format='PNG', dpi=150, bbox_inches='tight')
    plt.close(fig)
    img_buf.seek(0)
    story.append(Image(img_buf, width=10*cm, height=7.5*cm))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('Değişken Önem Sıralaması (Feature Importance)'), h2_s))
    fi_header = [gettext('Sıra'), gettext('Özellik'), gettext('Önem Skoru'), gettext('Göreli Ağırlık')]
    fi_rows = [fi_header]
    total = sum(f['importance'] for f in result['feature_importances'])
    for f in result['feature_importances'][:15]:
        pct = gettext('%%%(value)s') % {'value': f"{f['importance'] / total * 100:.1f}"} if total > 0 else '—'
        fi_rows.append([str(f['rank']), f['name'], f"{f['importance']:.4f}", pct])
    fi_tbl = Table(fi_rows, colWidths=[1.5*cm, 8*cm, 3*cm, 3.5*cm])
    fi_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PURPLE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(fi_tbl)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('Ağaç Yapısı (ilk 5 seviye)'), h2_s))
    for line in result['tree_text'].split('\n')[:40]:
        story.append(Paragraph(line.replace('<', '&lt;').replace('>', '&gt;'), mono_s))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(gettext('APA Formatında Raporlama'), h2_s))
    # Şablon JS ile ortak msgid'ler; yüzde dile göre (önceden '%85.2' sabit Türkçe)
    pct = lambda x: gettext('%%%(value)s') % {'value': f"{x * 100:.1f}"}
    criterion = gettext('Gini safsızlığı') if result['criterion'] == 'gini' else gettext('Bilgi kazancı (entropy)')
    apa_text = gettext('Karar ağacı sınıflandırma analizi ({criterion} kriteri, maksimum derinlik = {depth}) uygulanmıştır. '
                       'Model, test seti üzerinde {acc} doğruluk oranı elde etmiştir (n_eğitim = {ntrain}, n_test = {ntest}). '
                       'Kesinlik = {prec}, Duyarlılık = {rec}, F1 = {f1} olarak bulunmuştur.').format(
        criterion=criterion, depth=result['max_depth_param'], acc=pct(result['accuracy']),
        ntrain=result['n_train'], ntest=result['n_test'], prec=pct(result['precision']),
        rec=pct(result['recall']), f1=pct(result['f1']))
    if result['feature_importances']:
        top = result['feature_importances'][0]
        apa_text += ' ' + gettext("En önemli yordayıcı değişken '{name}' (önem skoru = {score}) olarak belirlenmiştir.").format(
            name=top['name'], score=f"{top['importance']:.4f}")
    apa_tbl = Table([[Paragraph(apa_text, norm_s)]], colWidths=[16*cm])
    apa_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f3ff')),
        ('BOX', (0, 0), (-1, -1), 1, PURPLE),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(apa_tbl)

    doc.build(story)
    return buf.getvalue()
