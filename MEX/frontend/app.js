const API = window.location.origin;
const MAX_DIMENSION = 1280;
const JPEG_QUALITY = 0.82;
const QUEUE_KEY = 'mex_offline_queue';

let authToken = sessionStorage.getItem('mex_token') || '';
let stream = null;
let capturing = false;

const $ = (id) => document.getElementById(id);

function setConnection(online) {
    const dot = $('conn-dot');
    const label = $('conn-label');
    dot.className = 'conn-dot ' + (online ? 'online' : 'offline');
    label.textContent = online ? 'EN LINEA' : 'SIN CONEXION';
}

async function checkConnection() {
    try {
        const res = await fetch(API + '/api/health', { cache: 'no-store' });
        setConnection(res.ok);
        if (res.ok) flushQueue();
    } catch (e) {
        setConnection(false);
    }
}

async function api(path, options = {}) {
    const headers = Object.assign({}, options.headers || {});
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
    sessionStorage.removeItem('mex_token');
    $('login-view').classList.remove('hidden');
    $('app-view').classList.add('hidden');
}

function showApp() {
    $('login-view').classList.add('hidden');
    $('app-view').classList.remove('hidden');
    loadHistory();
}

async function login() {
    const msg = $('login-msg');
    msg.className = 'msg';
    msg.textContent = '';
    try {
        const res = await fetch(API + '/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: $('login-user').value.trim(),
                password: $('login-pass').value,
            }),
        });
        if (!res.ok) throw new Error((await res.json()).detail || 'Fallo de acceso');
        const data = await res.json();
        authToken = data.access_token;
        sessionStorage.setItem('mex_token', authToken);
        showApp();
    } catch (e) {
        msg.className = 'msg error';
        msg.textContent = e.message;
    }
}

async function openCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment', width: { ideal: 1920 }, height: { ideal: 1440 } },
            audio: false,
        });
        $('camera-stream').srcObject = stream;
        $('camera-view').classList.add('active');
    } catch (e) {
        alert('No fue posible acceder a la camara: ' + e.message);
    }
}

function closeCamera() {
    if (stream) {
        stream.getTracks().forEach((t) => t.stop());
        stream = null;
    }
    $('camera-view').classList.remove('active');
    $('capture-status').style.display = 'none';
}

function grabFrame() {
    const video = $('camera-stream');
    const scale = Math.min(1, MAX_DIMENSION / Math.max(video.videoWidth, video.videoHeight));
    const canvas = document.createElement('canvas');
    canvas.width = Math.round(video.videoWidth * scale);
    canvas.height = Math.round(video.videoHeight * scale);
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    return new Promise((resolve) => canvas.toBlob((b) => resolve(b), 'image/jpeg', JPEG_QUALITY));
}

async function sendInspection(blob, captureMs, syncedOffline) {
    const form = new FormData();
    form.append('file', blob, 'capture.jpg');
    form.append('capture_ms', captureMs.toFixed(1));
    form.append('device_info', navigator.userAgent.slice(0, 180));
    form.append('synced_offline', syncedOffline ? 'true' : 'false');
    const t0 = performance.now();
    const res = await api('/api/inspections', { method: 'POST', body: form });
    const uploadMs = performance.now() - t0;
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Error en el servidor');
    }
    const data = await res.json();
    data.latency_ms.upload_measured = Math.round(uploadMs);
    return data;
}

function readQueue() {
    return JSON.parse(localStorage.getItem(QUEUE_KEY) || '[]');
}

function writeQueue(items) {
    localStorage.setItem(QUEUE_KEY, JSON.stringify(items));
    updateQueueInfo();
}

function blobToDataUrl(blob) {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.readAsDataURL(blob);
    });
}

function dataUrlToBlob(dataUrl) {
    const [meta, b64] = dataUrl.split(',');
    const mime = meta.match(/:(.*?);/)[1];
    const bin = atob(b64);
    const arr = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
    return new Blob([arr], { type: mime });
}

async function queueOffline(blob, captureMs) {
    const queue = readQueue();
    queue.push({ data_url: await blobToDataUrl(blob), capture_ms: captureMs, queued_at: Date.now() });
    writeQueue(queue);
}

async function flushQueue() {
    const queue = readQueue();
    if (!queue.length) { updateQueueInfo(); return; }
    const remaining = [];
    for (const item of queue) {
        try {
            await sendInspection(dataUrlToBlob(item.data_url), item.capture_ms, true);
        } catch (e) {
            remaining.push(item);
        }
    }
    writeQueue(remaining);
    loadHistory();
}

function updateQueueInfo() {
    const count = readQueue().length;
    $('offline-queue-info').classList.toggle('hidden', count === 0);
    $('queue-count').textContent = count;
}

const STATUS_LABELS = {
    GREEN: 'APROBADA',
    AMBER: 'REVISION',
    RED: 'REPROBADA',
    GRAY: 'NO IDENTIFICADA',
};

function showResult(data, photoUrl) {
    $('result-panel').classList.remove('hidden');
    $('result-badge').textContent = STATUS_LABELS[data.status] || data.status;
    $('result-badge').className = 'result-badge st-' + data.status;
    $('result-photo').src = photoUrl;
    $('r-code').textContent = data.part_code || '--';
    $('r-name').textContent = data.part_name || 'No identificada';
    $('r-conf').textContent = (data.confidence * 100).toFixed(1) + '%';
    $('r-date').textContent = new Date(data.created_at).toLocaleString('es-MX');
    $('r-id').textContent = data.id;
    const lat = data.latency_ms || {};
    $('r-lat').textContent = `inf ${lat.inference_ms ?? '-'} ms / total ${lat.total_ms ?? '-'} ms`;
    const divWrap = $('r-divergences-wrap');
    if (data.divergences && data.divergences.length) {
        divWrap.classList.remove('hidden');
        $('r-divergences').innerHTML = data.divergences.map((d) => `<li>${d}</li>`).join('');
    } else {
        divWrap.classList.add('hidden');
    }
    $('result-panel').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

async function capture() {
    if (capturing) return;
    capturing = true;
    $('capture-status').style.display = 'block';
    const t0 = performance.now();
    try {
        const blob = await grabFrame();
        const captureMs = performance.now() - t0;
        if (!navigator.onLine) {
            await queueOffline(blob, captureMs);
            $('capture-status').textContent = 'SIN CONEXION - GUARDADO EN COLA LOCAL';
            setTimeout(closeCamera, 1200);
            return;
        }
        const data = await sendInspection(blob, captureMs, false);
        const photoUrl = URL.createObjectURL(blob);
        closeCamera();
        showResult(data, photoUrl);
        loadHistory();
    } catch (e) {
        alert('Error en la inspeccion: ' + e.message);
        closeCamera();
    } finally {
        capturing = false;
        $('capture-status').style.display = 'none';
    }
}

async function loadHistory() {
    try {
        const res = await api('/api/inspections?limit=20');
        if (!res.ok) return;
        const items = await res.json();
        const list = $('history-list');
        if (!items.length) {
            list.className = 'empty';
            list.textContent = 'Sin inspecciones registradas';
        } else {
            list.className = '';
            list.innerHTML = items.map((i) => `
                <div class="history-item st-${i.status}" onclick="openInspection('${i.id}')">
                    <div>
                        <div class="code">${i.part_code || 'NO IDENTIFICADA'}</div>
                        <div class="meta">${new Date(i.created_at).toLocaleString('es-MX')} - ${(i.confidence * 100).toFixed(0)}%</div>
                    </div>
                    <span class="st st-${i.status}">${STATUS_LABELS[i.status]}</span>
                </div>`).join('');
        }
        if (items.length) {
            const last = items[0];
            $('last-inspection').className = '';
            $('last-inspection').innerHTML = `
                <div class="kv"><span class="k">Codigo</span><span class="v">${last.part_code || '--'}</span></div>
                <div class="kv"><span class="k">Resultado</span><span class="v st-${last.status}">${STATUS_LABELS[last.status]}</span></div>
                <div class="kv"><span class="k">Confianza</span><span class="v">${(last.confidence * 100).toFixed(1)}%</span></div>
                <div class="kv"><span class="k">Inspeccion</span><span class="v">${last.id}</span></div>`;
        }
    } catch (e) {
        setConnection(false);
    }
}

async function openInspection(id) {
    try {
        const res = await api('/api/inspections/' + id);
        if (!res.ok) return;
        const data = await res.json();
        showResult(data, data.image_path ? API + '/api/inspections/' + id + '/image' : '');
    } catch (e) { /* noop */ }
}

$('login-btn').addEventListener('click', login);
$('login-pass').addEventListener('keydown', (e) => { if (e.key === 'Enter') login(); });
$('scan-btn').addEventListener('click', openCamera);
$('capture-btn').addEventListener('click', capture);
$('close-camera-btn').addEventListener('click', closeCamera);

window.addEventListener('online', () => { checkConnection(); });
window.addEventListener('offline', () => setConnection(false));

if (authToken) {
    showApp();
} else {
    showLogin();
}
checkConnection();
setInterval(checkConnection, 15000);
updateQueueInfo();
