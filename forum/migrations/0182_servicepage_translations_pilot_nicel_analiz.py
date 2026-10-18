# Adım 9 (18 Ekim 2026): nicel-analiz pilot sayfası için EN/DE çevirisi.
# TR kaynak içerik pazaryeri modeline göre yazılmış (K1: EN/DE'de doğrudan danışmanlık,
# pazaryeri yok) — bu yüzden intro/process_text/ethics_text/FAQ birebir çevrilmedi,
# K1/K3/K4 kararlarına göre yeniden yazıldı. 7 bölüm (metodoloji açıklaması, pazaryeri
# ifadesi içermiyor) doğrudan çevrildi. Korumalı: çeviri zaten varsa dokunmaz.
from django.db import migrations


PAGE_TRANSLATIONS = {
    'en': {
        'title': 'Statistical & Quantitative Data Analysis Support',
        'meta_title': 'Statistical Analysis with SPSS, R, EViews | Analizus',
        'meta_description': (
            "We analyze your thesis or research data using SPSS, R, EViews and SmartPLS — "
            "methodologically sound, with a clear report. Free initial assessment."
        ),
        'intro': (
            "With SPSS, R, EViews, SmartPLS and advanced statistical methods — send us your data, "
            "and our team analyzes and reports it for you."
        ),
        'process_text': (
            "Describe your project, we review your data and methodology needs, and send you a quote "
            "within 5–7 business days depending on project size. Once you accept, we carry out the "
            "analysis and deliver the report."
        ),
        'ethics_text': (
            "Analizus is not a ghostwriting service. We analyze your data and guide you on methodology; "
            "complying with academic integrity rules remains your responsibility."
        ),
    },
    'de': {
        'title': 'Statistische und quantitative Datenanalyse',
        'meta_title': 'Statistische Analyse mit SPSS, R, EViews | Analizus',
        'meta_description': (
            "Wir werten Ihre Abschlussarbeits- oder Forschungsdaten mit SPSS, R, EViews und SmartPLS aus "
            "– methodisch fundiert, mit klarem Bericht. Kostenlose Erstbewertung."
        ),
        'intro': (
            "Mit SPSS, R, EViews, SmartPLS und fortgeschrittenen statistischen Methoden – senden Sie "
            "uns Ihre Daten, unser Team führt die Analyse durch und berichtet die Ergebnisse."
        ),
        'process_text': (
            "Beschreiben Sie Ihr Projekt, wir prüfen Ihre Daten und methodischen Anforderungen und "
            "senden Ihnen je nach Projektumfang innerhalb von 5–7 Werktagen ein Angebot. Nach Ihrer "
            "Zusage führen wir die Analyse durch und liefern den Bericht."
        ),
        'ethics_text': (
            "Analizus ist kein Ghostwriting-Dienst. Wir analysieren Ihre Daten und beraten Sie methodisch; "
            "die Einhaltung der wissenschaftlichen Integritätsregeln liegt in Ihrer Verantwortung."
        ),
    },
}

SECTION_TRANSLATIONS = {
    'on-analizler': {
        'en': ('Preliminary Analysis', (
            "A solid start to the analysis process with data cleaning, missing-data handling and "
            "descriptive statistics. This is the starting point if you are analyzing your dataset for "
            "the first time or want to confirm your data is reliable before further analysis. You "
            "receive a cleaned dataset, a missing-data report and a descriptive statistics table."
        )),
        'de': ('Voranalysen', (
            "Ein solider Einstieg in den Analyseprozess durch Datenbereinigung, Umgang mit fehlenden "
            "Werten und deskriptive Statistik. Dies ist der richtige Startpunkt, wenn Sie Ihren Datensatz "
            "zum ersten Mal analysieren oder vor weiteren Analysen die Datenqualität sicherstellen "
            "möchten. Sie erhalten einen bereinigten Datensatz, einen Bericht zu fehlenden Werten "
            "und eine deskriptive Statistiktabelle."
        )),
    },
    'gecerlik-guvenirlik': {
        'en': ('Validity & Reliability', (
            "Validity and reliability analyses for scale development and adaptation studies. Needed "
            "when you are developing a new scale or adapting an existing one to a different sample. We "
            "report Cronbach's alpha, item-total correlations and, where needed, exploratory/confirmatory "
            "factor analysis results."
        )),
        'de': ('Validität & Reliabilität', (
            "Validitäts- und Reliabilitätsanalysen für Skalenentwicklung und -adaption. "
            "Erforderlich, wenn Sie eine neue Skala entwickeln oder eine bestehende an eine andere "
            "Stichprobe anpassen. Wir berichten Cronbachs Alpha, Trennschärfekoeffizienten und, "
            "falls nötig, explorative/konfirmatorische Faktorenanalysen."
        )),
    },
    'iliski-korelasyon': {
        'en': ('Relationships & Correlation', (
            "Examining relationships between variables through correlation analysis. Used when you want "
            "to see whether a relationship exists between two or more variables, and its direction and "
            "strength. You receive correlation coefficients, significance values and an interpreted "
            "results report."
        )),
        'de': ('Zusammenhänge & Korrelation', (
            "Untersuchung von Zusammenhängen zwischen Variablen mittels Korrelationsanalyse. "
            "Eingesetzt, wenn Sie prüfen möchten, ob zwischen zwei oder mehr Variablen ein "
            "Zusammenhang besteht, sowie dessen Richtung und Stärke. Sie erhalten "
            "Korrelationskoeffizienten, Signifikanzwerte und einen interpretierten Ergebnisbericht."
        )),
    },
    'fark-testleri': {
        'en': ('Difference Tests', (
            "Assessing differences between groups using t-tests, ANOVA and non-parametric tests. Used "
            "when you want to compare two or more groups (e.g. experimental-control, gender, age group) "
            "on a variable. You receive the appropriate test selection, assumption checks and APA-style "
            "interpreted results."
        )),
        'de': ('Unterschiedstests', (
            "Beurteilung von Gruppenunterschieden mittels t-Tests, ANOVA und nichtparametrischen Tests. "
            "Eingesetzt, wenn Sie zwei oder mehr Gruppen (z. B. Experimental-/Kontrollgruppe, "
            "Geschlecht, Altersgruppe) hinsichtlich einer Variable vergleichen möchten. Sie erhalten "
            "die passende Testauswahl, Voraussetzungsprüfungen und im APA-Format interpretierte "
            "Ergebnisse."
        )),
    },
    'regresyon-sem': {
        'en': ('Regression & Structural Equation Modeling', (
            "Regression models and structural equation modeling (SEM) with SmartPLS/AMOS. Used when you "
            "want to test how much one or more variables predict another, or to test complex variable "
            "relationships through a model. You receive model fit indices, path coefficients and the "
            "model diagram as part of the full report."
        )),
        'de': ('Regression & Strukturgleichungsmodellierung', (
            "Regressionsmodelle und Strukturgleichungsmodellierung (SEM) mit SmartPLS/AMOS. Eingesetzt, "
            "wenn Sie prüfen möchten, inwieweit eine oder mehrere Variablen eine andere "
            "vorhersagen, oder komplexe Variablenbeziehungen über ein Modell testen möchten. Sie "
            "erhalten Modellanpassungsindizes, Pfadkoeffizienten und das Modelldiagramm als Teil des "
            "vollständigen Berichts."
        )),
    },
    'zaman-serisi-ekonometri': {
        'en': ('Time Series & Econometrics', (
            "Econometric modeling and time-series analysis with EViews. Used when you want to build a "
            "forecasting or relationship model with data that changes over time (e.g. inflation, sales, "
            "stock price). We report stationarity tests, model estimation and forecast results."
        )),
        'de': ('Zeitreihen & Ökonometrie', (
            "Ökonometrische Modellierung und Zeitreihenanalyse mit EViews. Eingesetzt, wenn Sie mit "
            "sich über die Zeit verändernden Daten (z. B. Inflation, Umsatz, Aktienkurs) "
            "ein Prognose- oder Zusammenhangsmodell erstellen möchten. Wir berichten "
            "Stationaritätstests, Modellschätzung und Prognoseergebnisse."
        )),
    },
    'makine-ogrenmesi': {
        'en': ('Machine Learning', (
            "Machine-learning-supported analysis for classification and prediction models. Used when you "
            "need prediction/classification on large or complex datasets where traditional statistical "
            "methods fall short. You receive model performance metrics (accuracy, F1 score, etc.) and the "
            "code/output files used."
        )),
        'de': ('Maschinelles Lernen', (
            "Durch maschinelles Lernen unterstützte Analyse für Klassifikations- und "
            "Vorhersagemodelle. Eingesetzt, wenn Sie bei großen oder komplexen Datensätzen, bei "
            "denen klassische statistische Methoden an ihre Grenzen stoßen, eine "
            "Vorhersage/Klassifikation benötigen. Sie erhalten Leistungskennzahlen des Modells "
            "(Genauigkeit, F1-Score usw.) sowie den verwendeten Code und die Ausgabedateien."
        )),
    },
}

FAQ_TRANSLATIONS = {
    'Verilerimi nasıl paylaşacağım?': {
        'en': ('How do I share my data?', (
            "After submitting your project request, you share your data securely with our team as part "
            "of the agreed process."
        )),
        'de': ('Wie teile ich meine Daten mit Ihnen?', (
            "Nach Ihrer Projektanfrage teilen Sie Ihre Daten sicher mit unserem Team im Rahmen des "
            "vereinbarten Ablaufs."
        )),
    },
    'Analiz sonucunu nasıl teslim alırım?': {
        'en': ('How do I receive the analysis results?', (
            "You receive the report, output files and explanations according to what was agreed with "
            "our team."
        )),
        'de': ('Wie erhalte ich die Analyseergebnisse?', (
            "Sie erhalten Bericht, Ausgabedateien und Erläuterungen gemäß der mit unserem "
            "Team vereinbarten Leistung."
        )),
    },
}


def create_translations(apps, schema_editor):
    ServicePage = apps.get_model('forum', 'ServicePage')
    ServicePageTranslation = apps.get_model('forum', 'ServicePageTranslation')
    ServicePageSectionTranslation = apps.get_model('forum', 'ServicePageSectionTranslation')
    ServicePageFAQTranslation = apps.get_model('forum', 'ServicePageFAQTranslation')

    try:
        page = ServicePage.objects.get(slug='nicel-analiz')
    except ServicePage.DoesNotExist:
        return

    for lang, fields in PAGE_TRANSLATIONS.items():
        ServicePageTranslation.objects.get_or_create(
            service_page=page, language=lang, defaults=fields,
        )

    for section in page.sections.all():
        translations = SECTION_TRANSLATIONS.get(section.anchor)
        if not translations:
            continue
        for lang, (title, body) in translations.items():
            ServicePageSectionTranslation.objects.get_or_create(
                section=section, language=lang, defaults={'title': title, 'body': body},
            )

    for faq in page.faqs.all():
        translations = FAQ_TRANSLATIONS.get(faq.question)
        if not translations:
            continue
        for lang, (question, answer) in translations.items():
            ServicePageFAQTranslation.objects.get_or_create(
                faq=faq, language=lang, defaults={'question': question, 'answer': answer},
            )


def delete_translations(apps, schema_editor):
    ServicePage = apps.get_model('forum', 'ServicePage')
    ServicePageTranslation = apps.get_model('forum', 'ServicePageTranslation')
    ServicePageSectionTranslation = apps.get_model('forum', 'ServicePageSectionTranslation')
    ServicePageFAQTranslation = apps.get_model('forum', 'ServicePageFAQTranslation')

    try:
        page = ServicePage.objects.get(slug='nicel-analiz')
    except ServicePage.DoesNotExist:
        return

    ServicePageTranslation.objects.filter(service_page=page).delete()
    ServicePageSectionTranslation.objects.filter(section__service_page=page).delete()
    ServicePageFAQTranslation.objects.filter(faq__service_page=page).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0181_servicepage_translations'),
    ]

    operations = [
        migrations.RunPython(create_translations, delete_translations),
    ]
