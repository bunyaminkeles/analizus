(function () {
    'use strict';

    var isAuthenticated = false;
    var loginUrl = '';
    var body = null;
    var categoryEl = null;
    var diffEl = null;
    var currentQuestion = null;

    function initQuiz() {
        var app = document.getElementById('axQuizApp');
        if (!app) {
            var bodyEl = document.getElementById('axQuizBody');
            if (bodyEl) {
                app = bodyEl.closest('#axQuizApp');
            }
        }
        if (!app) return;

        isAuthenticated = app.dataset.authenticated === 'true';
        loginUrl = app.dataset.loginUrl || '/login/?next=/';
        body = document.getElementById('axQuizBody');
        categoryEl = document.getElementById('axQuizCategory');
        diffEl = document.getElementById('axQuizDifficulty');

        loadNext();
    }

    var FALLBACK = [
        {
            id: -1,
            category: 'İstatistik Temelleri',
            difficulty: 'Kolay',
            question: 'Cronbach Alpha katsayısı asgari olarak kaç ve üzerinde olduğunda güvenilirlik "kabul edilebilir" sayılır?',
            options: { A: '0.50', B: '0.60', C: '0.70', D: '0.90' },
            correct_answer: 'C',
            explanation: 'Nunnally (1978)\'e göre α ≥ .70 "kabul edilebilir güvenilirlik" olarak değerlendirilir.'
        },
        {
            id: -2,
            category: 'Normallik Testi',
            difficulty: 'Orta',
            question: 'Shapiro-Wilk testi genellikle hangi örneklem büyüklüklerinde tercih edilir?',
            options: { A: 'n > 2000', B: 'n < 50', C: 'n ≤ 50', D: 'n = 100' },
            correct_answer: 'C',
            explanation: 'Shapiro-Wilk küçük örneklemler (n ≤ 50) için daha güçlüdür. Büyük örneklemde Kolmogorov-Smirnov tercih edilir.'
        },
        {
            id: -3,
            category: 'Temel İstatistik',
            difficulty: 'Kolay',
            question: 'Bir veri setindeki ortanca (medyan) neyi ifade eder?',
            options: { A: 'En sık tekrarlayan değeri', B: 'Tüm değerlerin toplamının sayıya bölümünü', C: 'Sıralı dizinin tam ortasındaki değeri', D: 'En büyük ile en küçük değerin farkını' },
            correct_answer: 'C',
            explanation: 'Medyan, verilerin sıralandığında tam ortaya denk gelen değerdir; uç değerlere (aykırı değer) karşı dirençlidir.'
        },
        {
            id: -4,
            category: 'Regresyon',
            difficulty: 'Orta',
            question: 'Çoklu doğrusal regresyonda R² değeri ne anlama gelir?',
            options: { A: 'Bağımsız değişkenler arası korelasyon', B: 'Bağımlı değişkendeki varyansın bağımsız değişkenlerle açıklanan oranı', C: 'Standart hata katsayısı', D: 'Model anlamlılık düzeyi' },
            correct_answer: 'B',
            explanation: 'R² (determinasyon katsayısı), modelin bağımlı değişkendeki toplam varyansı ne kadar açıkladığını gösterir.'
        }
    ];

    function getCsrf() {
        var match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? decodeURIComponent(match[1]) : '';
    }

    function diffClass(d) {
        if (d === 'Kolay') return 'ax-quiz-badge--easy';
        if (d === 'Zor')   return 'ax-quiz-badge--hard';
        return 'ax-quiz-badge--medium';
    }

    function renderQuestion(q) {
        currentQuestion = q;
        categoryEl.textContent = q.category;
        diffEl.textContent     = q.difficulty;
        diffEl.className       = 'ax-quiz-badge ' + diffClass(q.difficulty);

        var opts = ['A', 'B', 'C', 'D'].map(function (l) {
            return '<button class="ax-quiz-opt" data-answer="' + l + '">' +
                       '<span class="ax-quiz-opt__letter">' + l + '</span>' +
                       '<span>' + q.options[l] + '</span>' +
                   '</button>';
        }).join('');

        var skipHtml = isAuthenticated
            ? '<button class="ax-quiz-skip" id="axSkip">Soruyu Geç →</button>'
            : '<span></span>';

        body.innerHTML =
            '<p class="ax-quiz-question">' + q.question + '</p>' +
            '<div class="ax-quiz-options">' + opts + '</div>' +
            '<div class="ax-quiz-feedback" id="axFb">' +
                '<div class="ax-quiz-feedback__icon" id="axFbIcon"></div>' +
                '<p class="ax-quiz-feedback__text" id="axFbText"></p>' +
                '<p class="ax-quiz-feedback__expl" id="axFbExpl"></p>' +
            '</div>' +
            '<div class="ax-quiz-footer">' +
                skipHtml +
                '<button class="ax-quiz-next" id="axNext">Sonraki Soru →</button>' +
            '</div>';

        body.querySelectorAll('.ax-quiz-opt').forEach(function (btn) {
            btn.addEventListener('click', function () { handleAnswer(btn); });
        });

        var skip = document.getElementById('axSkip');
        if (skip) skip.addEventListener('click', loadNext);

        var nextBtn = document.getElementById('axNext');
        if (nextBtn) nextBtn.addEventListener('click', loadNext);
    }

    function handleAnswer(btn) {
        if (!isAuthenticated) {
            window.location.href = loginUrl;
            return;
        }

        body.querySelectorAll('.ax-quiz-opt').forEach(function (b) { b.disabled = true; });
        var skip = document.getElementById('axSkip');
        if (skip) skip.style.display = 'none';

        var qid    = currentQuestion.id;
        var answer = btn.dataset.answer;

        if (qid < 0) {
            showResult({
                success: true,
                is_correct: answer === currentQuestion.correct_answer,
                correct_answer: currentQuestion.correct_answer,
                explanation: currentQuestion.explanation,
                badge_awarded: null
            }, btn);
            return;
        }

        fetch('/api/quiz/answer/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrf() },
            body: JSON.stringify({ question_id: qid, answer: answer })
        })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.requires_login) {
                window.location.href = loginUrl;
                return;
            }
            showResult(data, btn);
        })
        .catch(function () {
            showResult({
                success: true,
                is_correct: false,
                correct_answer: null,
                explanation: 'Cevap sunucuya gönderilemedi. Bağlantınızı kontrol edin.',
                badge_awarded: null
            }, btn);
        });
    }

    function showResult(data, btn) {
        if (!data.success) return;

        body.querySelectorAll('.ax-quiz-opt').forEach(function (b) {
            if (b.dataset.answer === data.correct_answer) b.classList.add('is-correct');
        });
        if (!data.is_correct) btn.classList.add('is-wrong');

        var fb = document.getElementById('axFb');
        var icon = document.getElementById('axFbIcon');
        var text = document.getElementById('axFbText');
        var expl = document.getElementById('axFbExpl');

        if (data.is_correct) {
            fb.classList.remove('ax-quiz-feedback--wrong');
            icon.textContent = '✓';
            text.textContent = 'Doğru! +10 puan kazandın.';
            text.style.color = 'var(--ax-accent-secondary)';
        } else {
            fb.classList.add('ax-quiz-feedback--wrong');
            icon.textContent = '✗';
            text.textContent = data.correct_answer
                ? 'Yanlış. Doğru cevap: ' + data.correct_answer
                : 'Yanlış.';
            text.style.color = 'var(--ax-accent-danger)';
        }

        expl.textContent = data.explanation || '';
        if (data.badge_awarded) {
            expl.innerHTML += '<br><span style="color:var(--ax-accent-warning)">🏆 Yeni rozet: ' + data.badge_awarded + '</span>';
        }

        fb.style.display = 'block';
        var nextBtn = document.getElementById('axNext');
        if (nextBtn) nextBtn.style.display = 'inline-flex';
    }

    function pickFallback() {
        var idx = Math.floor(Math.random() * FALLBACK.length);
        return FALLBACK[idx];
    }

    function loadNext() {
        var next = document.getElementById('axNext');
        if (next) { next.disabled = true; next.textContent = 'Yükleniyor...'; }

        var controller = new AbortController();
        var timeout = setTimeout(function () { controller.abort(); }, 4000);

        fetch('/api/quiz/random/', { signal: controller.signal })
            .then(function (r) {
                clearTimeout(timeout);
                if (!r.ok) { throw new Error('non-ok'); }
                return r.json();
            })
            .then(function (data) {
                if (data.success) {
                    renderQuestion(data.question);
                } else {
                    renderQuestion(pickFallback());
                }
            })
            .catch(function () {
                clearTimeout(timeout);
                renderQuestion(pickFallback());
            });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initQuiz);
    } else {
        initQuiz();
    }
}());
