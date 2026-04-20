document.addEventListener('DOMContentLoaded', function () {
    var textarea = document.getElementById('id_content');
    if (!textarea || typeof EasyMDE === 'undefined') return;

    var editor = new EasyMDE({
        element: textarea,
        spellChecker: false,
        autosave: {
            enabled: true,
            uniqueId: 'blog-post-' + (document.getElementById('id_slug') ? document.getElementById('id_slug').value : 'new'),
            delay: 5000,
        },
        toolbar: [
            'bold', 'italic', 'heading', '|',
            'quote', 'unordered-list', 'ordered-list', '|',
            'code', 'table', 'horizontal-rule', '|',
            {
                name: 'formula',
                action: function (editor) {
                    var cm = editor.codemirror;
                    var sel = cm.getSelection();
                    cm.replaceSelection(sel ? '$' + sel + '$' : '$formül$');
                },
                className: 'fa fa-superscript',
                title: 'Formül (KaTeX)',
            },
            '|',
            'preview', 'side-by-side', 'fullscreen', '|',
            'guide',
        ],
        previewRender: function (plainText) {
            return this.parent.markdown(plainText);
        },
        renderingConfig: {
            singleLineBreaks: false,
            codeSyntaxHighlighting: false,
        },
        minHeight: '400px',
        placeholder: 'Markdown formatında yazın...\n\n# Başlık\n## Alt Başlık\n\n**Kalın**, *italik*, `kod`\n\n```python\nkod bloğu\n```\n\nFormül: $\\alpha = .873$',
    });

    // Karakter sayacı
    var counter = document.createElement('div');
    counter.style.cssText = 'text-align: right; font-size: 0.8rem; color: #888; margin-top: 4px;';
    editor.codemirror.getWrapperElement().parentNode.appendChild(counter);

    function updateCounter() {
        var len = editor.value().length;
        var color = len > 45000 ? '#f87171' : len > 40000 ? '#fbbf24' : '#888';
        counter.style.color = color;
        counter.textContent = len.toLocaleString('tr-TR') + ' / 50.000 karakter';
    }

    editor.codemirror.on('change', updateCounter);
    updateCounter();
});
