const source = document.getElementById('BodyHtml');
const container = document.getElementById('visual-fields');
const rebuild = () => {
    const doc = new DOMParser().parseFromString(source.value, 'text/html');
    container.replaceChildren();
    const sync = () => { source.value = doc.body.innerHTML; };
    const add = (title, value, update, multiline = false) => {
        const label = document.createElement('label');
        label.textContent = title;
        const input = document.createElement(multiline ? 'textarea' : 'input');
        input.value = value;
        if (multiline) input.rows = 2;
        input.addEventListener('input', () => { update(input.value); sync(); });
        label.appendChild(input); container.appendChild(label);
    };
    doc.body.querySelectorAll('h1,h2,h3,h4,h5,h6,p,a,span,li,button').forEach(node => {
        if (node.children.length || !node.textContent.trim()) return;
        add(node.tagName.toLowerCase() + ' · ' + node.textContent.trim().slice(0,55), node.textContent.trim(), value => { node.textContent = value; }, node.tagName === 'P');
        if (node.tagName === 'A') add('Bağlantı adresi', node.getAttribute('href') || '', value => node.setAttribute('href', value));
    });
    doc.body.querySelectorAll('img').forEach((node, i) => {
        add('Görsel ' + (i + 1) + ' · dosya yolu', node.getAttribute('src') || '', value => node.setAttribute('src', value));
        add('Görsel ' + (i + 1) + ' · açıklama', node.getAttribute('alt') || '', value => node.setAttribute('alt', value));
    });
};
if (source && container) { rebuild(); source.addEventListener('change', rebuild); }
