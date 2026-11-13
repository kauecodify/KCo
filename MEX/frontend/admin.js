const API = window.location.origin;

let authToken = sessionStorage.getItem('mex_admin_token') || '';
let currentUser = null;
let selectedInspection = null;
let selectedPart = null;

const $ = (id) => document.getElementById(id);

async function api(path, options = {}) {
    const headers = Object.assign({}, options.headers || {});
    if (!(options.body instanceof FormData) && options.body) {
        headers['Content-Type'] = 'application/json';
    }
    if (authToken) headers['Authorization'] = 'Bearer ' + authToken;
    const res = await fetch(API + path, Object.assign({}, options, { headers }));
    if (res.status === 401 && path !== '/api/auth/login') {
        showLogin();
        throw new Error('Sesion expirada');
    }
    return res;
}

function showLogin() {
    authToken = '';
    sessionStorage.removeItem('mex_admin_token');
    $('login-view').classList.remove('hidden');
    $('app-view').classList.add('hidden');
}

function showApp() {
    $('login-view').classList.add('hidden');
    $('app-view').classList.remove('hidden');
    $('user-label').textContent = currentUser ? currentUser.username.toUpperCase() + ' / ' + currentUser.role.toUpperCase() : '';
    loadAll();
}

async function login() {
    const msg = $('login-msg');
    msg.className = 'msg';
    try {
        const res = await fetch(API + '/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: $('login-user').value.trim(), password: $('login-pass').value }),
        });
        if (!res.ok) throw new Error((await res.json()).detail || 'Fallo de acceso');
        const data = await res.json();
        if (data.role === 'operator') throw new Error('Este panel requiere rol supervisor o administrador');
        authToken = data.access_token;
        sessionStorage.setItem('mex_admin_token', authToken);
        const me = await api('/api/auth/me');
        currentUser = await me.json();
        showApp();
    } catch (e) {
        msg.className = 'msg error';
        msg.textContent = e.message;
    }
}

function setMsg(id, text, ok) {
    const el = $(id);
    el.className = 'msg ' + (ok ? 'ok' : 'error');
    el.textContent = text;
}

function parseKeyValues(text) {
    const out = {};
    text.split('\n').forEach((line) => {
        const idx = line.indexOf(':');
        if (idx > 0) {
            const key = line.slice(0, idx).trim();
            let value = line.slice(idx + 1).trim();
            if (!isNaN(parseFloat(value)) && isFinite(value)) value = parseFloat(value);
            out[key] = value;
        }
    });
    return out;
}

function table(el, headers, rows) {
    if (!rows.length) {
        el.innerHTML = '<tbody><tr><td style="color: var(--text-mute);">Sin registros</td></tr></tbody>';
        return;
    }
    el.innerHTML =
        '<thead><tr>' + headers.map((h) => `<th>${h}</th>`).join('') + '</tr></thead><tbody>' +
        rows.map((r) => '<tr>' + r.map((c) => `<td>${c}</td>`).join('') + '</tr>').join('') + '</tbody>';
}

const STATUS_LABELS = { GREEN: 'APROBADA', AMBER: 'REVISION', RED: 'REPROBADA', GRAY: 'NO IDENTIFICADA' };

async function loadParts() {
    const res = await api('/api/parts?include_inactive=true');
    if (!res.ok) return;
    const parts = await res.json();
    table(
        $('parts-table'),
        ['Codigo', 'Nombre', 'Categoria', 'Version', 'Imagenes', 'Acciones'],
        parts.map((p) => [
            `<span style="color: var(--green);">${p.code}</span>`,
            p.name,
            p.category,
            'v' + p.version,
            p.images.length,
            `<button class="tab" style="min-width:auto; padding:0.25rem 0.6rem;" onclick="openPartDetail(${p.id})">IMAGENES</button>`,
        ])
    );
}

window.openPartDetail = async function (partId) {
    const res = await api('/api/parts/' + partId);
    if (!res.ok) return;
    const part = await res.json();
    selectedPart = part;
    $('part-detail').classList.remove('hidden');
    $('part-detail-title').textContent = 'Imagenes de referencia - ' + part.code;
    $('part-images').innerHTML = part.images
        .map((img) => {
            const name = img.path.split('/').pop();
            return `<div style="text-align:center;">
                <img src="/api/reference/${name}" style="width:110px; height:110px; object-fit:cover; border:1px solid var(--border);">
                <div style="font-size:0.58rem; color:var(--text-mute);">${img.is_primary ? 'PRINCIPAL' : 'secundaria'}</div>
            </div>`;
        })
        .join('');
};

async function createPart() {
    try {
        const criteria = parseKeyValues($('p-criteria').value);
        if ($('p-minconf').value) criteria.min_confidence = parseFloat($('p-minconf').value);
        const res = await api('/api/parts', {
            method: 'POST',
            body: JSON.stringify({
                code: $('p-code').value.trim(),
                name: $('p-name').value.trim(),
                category: $('p-category').value.trim() || 'general',
                dimensions: $('p-dimensions').value.trim(),
                tolerances: $('p-tolerances').value.trim(),
                specifications: parseKeyValues($('p-specs').value),
                approval_criteria: criteria,
            }),
        });
        if (!res.ok) throw new Error((await res.json()).detail || 'Error');
        setMsg('part-msg', 'Pieza ' + $('p-code').value.toUpperCase() + ' cadastrada con exito', true);
        loadParts();
    } catch (e) {
        setMsg('part-msg', e.message, false);
    }
}

async function uploadReference() {
    if (!selectedPart) return setMsg('part-msg', 'Seleccione una pieza primero', false);
    const input = $('ref-file');
    if (!input.files.length) return setMsg('part-msg', 'Seleccione un archivo de imagen', false);
    const form = new FormData();
    form.append('file', input.files[0]);
    const res = await api(`/api/parts/${selectedPart.id}/images`, { method: 'POST', body: form });
    if (!res.ok) return setMsg('part-msg', (await res.json()).detail || 'Error al subir', false);
    setMsg('part-msg', 'Imagen de referencia cargada', true);
    input.value = '';
    openPartDetail(selectedPart.id);
    loadParts();
}

async function loadInspections() {
    const filter = $('insp-status-filter').value;
    const res = await api('/api/inspections?limit=100' + (filter ? '&status_filter=' + filter : ''));
    if (!res.ok) return;
    const items = await res.json();
    table(
        $('inspections-table'),
        ['ID', 'Pieza', 'Estado', 'Confianza', 'Operador', 'Fecha', 'Revision', ''],
        items.map((i) => [
            i.id,
            i.part_code || '--',
            `<span class="st-${i.status}">${STATUS_LABELS[i.status]}</span>`,
            (i.confidence * 100).toFixed(1) + '%',
            i.operator,
            new Date(i.created_at).toLocaleString('es-MX'),
            i.review_status,
            `<button class="tab" style="min-width:auto; padding:0.25rem 0.6rem;" onclick='selectInspection(${JSON.stringify(JSON.stringify(i))})'>REVISAR</button>`,
        ])
    );
}

window.selectInspection = function (json) {
    const i = JSON.parse(json);
    selectedInspection = i;
    $('review-target').className = '';
    $('review-target').innerHTML = `
        <div class="kv"><span class="k">Inspeccion</span><span class="v">${i.id}</span></div>
        <div class="kv"><span class="k">Pieza</span><span class="v">${i.part_code || 'No identificada'}</span></div>
        <div class="kv"><span class="k">Estado</span><span class="v st-${i.status}">${STATUS_LABELS[i.status]}</span></div>
        <div class="kv"><span class="k">Confianza</span><span class="v">${(i.confidence * 100).toFixed(1)}%</span></div>
        <img src="${API}/api/inspections/${i.id}/image" style="max-width: 200px; margin-top: 0.6rem; border: 1px solid var(--border);">`;
    $('review-form').classList.remove('hidden');
};

async function sendReview(decision) {
    if (!selectedInspection) return;
    const res = await api(`/api/inspections/${selectedInspection.id}/review`, {
        method: 'POST',
        body: JSON.stringify({ decision, note: $('review-note').value }),
    });
    if (!res.ok) return alert((await res.json()).detail || 'Error en la revision');
    loadInspections();
}

async function loadUsers() {
    const res = await api('/api/admin/users');
    if (!res.ok) return;
    const users = await res.json();
    table(
        $('users-table'),
        ['Usuario', 'Nombre', 'Rol', 'Planta', 'Activo', 'Accion'],
        users.map((u) => [
            u.username,
            u.full_name || '--',
            u.role,
            u.plant,
            u.active ? 'SI' : 'NO',
            `<button class="tab" style="min-width:auto; padding:0.25rem 0.6rem;" onclick="toggleUser(${u.id})">${u.active ? 'DESACTIVAR' : 'ACTIVAR'}</button>`,
        ])
    );
}

async function createUser() {
    try {
        const res = await api('/api/admin/users', {
            method: 'POST',
            body: JSON.stringify({
                username: $('u-username').value.trim(),
                password: $('u-password').value,
                role: $('u-role').value,
                full_name: $('u-fullname').value.trim(),
            }),
        });
        if (!res.ok) throw new Error((await res.json()).detail || 'Error');
        setMsg('user-msg', 'Usuario creado', true);
        loadUsers();
    } catch (e) {
        setMsg('user-msg', e.message, false);
    }
}

window.toggleUser = async function (id) {
    const res = await api('/api/admin/users/' + id, { method: 'PATCH' });
    if (!res.ok) return alert((await res.json()).detail || 'Error');
    loadUsers();
};

async function loadMetrics() {
    const res = await api('/api/admin/metrics');
    if (!res.ok) return;
    const m = await res.json();
    $('metrics-stats').innerHTML = `
        <div class="stat"><h4>${m.inspections_total}</h4><p>Inspecciones</p></div>
        <div class="stat"><h4>${(m.accuracy * 100).toFixed(1)}%</h4><p>Tasa de aprobacion</p></div>
        <div class="stat"><h4>${m.inspections_pending_review}</h4><p>Pendientes de revision</p></div>
        <div class="stat"><h4>${m.parts_registered}</h4><p>Piezas activas</p></div>`;
    const lat = m.latency || {};
    table(
        $('latency-table'),
        ['Etapa', 'Muestras', 'p50 (ms)', 'p95 (ms)', 'p99 (ms)'],
        Object.entries(lat).map(([stage, s]) => [stage, s.count, s.p50_ms ?? '--', s.p95_ms ?? '--', s.p99_ms ?? '--'])
    );
}

async function loadModels() {
    const res = await api('/api/admin/models');
    if (!res.ok) return;
    const models = await res.json();
    table(
        $('models-table'),
        ['Nombre', 'Version', 'Motor', 'Activo', 'Accion'],
        models.map((m) => [
            m.name,
            m.version,
            m.engine_type,
            m.active ? 'ACTIVO' : '--',
            m.active ? '' : `<button class="tab" style="min-width:auto; padding:0.25rem 0.6rem;" onclick="activateModel(${m.id})">ACTIVAR</button>`,
        ])
    );
}

window.activateModel = async function (id) {
    const res = await api(`/api/admin/models/${id}/activate`, { method: 'POST' });
    if (!res.ok) return alert((await res.json()).detail || 'Error');
    loadModels();
};

async function loadAudit() {
    const res = await api('/api/admin/audit?limit=100');
    if (!res.ok) return;
    const logs = await res.json();
    table(
        $('audit-table'),
        ['Fecha', 'Usuario', 'Accion', 'Entidad', 'Detalle'],
        logs.map((l) => [
            new Date(l.timestamp).toLocaleString('es-MX'),
            l.username,
            l.action,
            l.entity,
            (l.detail || '').slice(0, 60),
        ])
    );
}

function loadAll() {
    loadParts();
    loadInspections();
    loadUsers();
    loadMetrics();
    loadModels();
    loadAudit();
}

document.querySelectorAll('.tab[data-tab]').forEach((btn) => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab[data-tab]').forEach((b) => b.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach((p) => p.classList.remove('active'));
        btn.classList.add('active');
        $('tab-' + btn.dataset.tab).classList.add('active');
    });
});

$('login-btn').addEventListener('click', login);
$('login-pass').addEventListener('keydown', (e) => { if (e.key === 'Enter') login(); });
$('logout-btn').addEventListener('click', showLogin);
$('create-part-btn').addEventListener('click', createPart);
$('upload-ref-btn').addEventListener('click', uploadReference);
$('load-inspections-btn').addEventListener('click', loadInspections);
$('approve-btn').addEventListener('click', () => sendReview('approved'));
$('reject-btn').addEventListener('click', () => sendReview('rejected'));
$('create-user-btn').addEventListener('click', createUser);

if (authToken) {
    api('/api/auth/me')
        .then((r) => (r.ok ? r.json() : Promise.reject()))
        .then((me) => {
            currentUser = me;
            if (me.role === 'operator') return showLogin();
            showApp();
        })
        .catch(showLogin);
} else {
    showLogin();
}
