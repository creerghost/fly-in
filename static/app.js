/* ── fly-in Frontend ── */

// ── DOM ──
const mapInput = document.getElementById('map-input');
const runBtn = document.getElementById('run-btn');
const canvas = document.getElementById('sim-canvas');
const ctx = canvas.getContext('2d');
const statusDot = document.querySelector('.status-dot');
const statusText = document.getElementById('status-text');
const errorBox = document.getElementById('error-box');
const errorText = document.getElementById('error-text');
const resultsSection = document.getElementById('results-section');
const playbackBar = document.getElementById('playback-bar');
const turnLog = document.getElementById('turn-log');
const turnCurrent = document.getElementById('turn-current');
const turnTotal = document.getElementById('turn-total');
const turnSlider = document.getElementById('turn-slider');

// ── State ──
let simData = null;        // full API response
let zonePositions = {};    // {name: {x, y, zone}}
let droneStates = [];      // array of {droneId: {zone, transit}} per turn
let currentTurn = 0;
let isPlaying = false;
let animProgress = 1;      // 0..1 animation between turns
let animFrameId = null;
let lastFrameTime = 0;

// ── Config ──
const ZONE_RADIUS = 22;
const DRONE_RADIUS = 8;
const DRONE_COLORS = [
    '#00d4ff', '#ff6b6b', '#ffd93d', '#6bcb77',
    '#a855f7', '#ff8c42', '#4ecdc4', '#ff69b4',
    '#00ff88', '#ff4dff', '#ffa500', '#87ceeb'
];
const ZONE_TYPE_COLORS = {
    normal: '#4a9eff',
    blocked: '#ef4444',
    restricted: '#a855f7',
    priority: '#00d4ff'
};

// ── Resize canvas ──
function resizeCanvas() {
    const area = document.getElementById('canvas-area');
    canvas.width = area.clientWidth;
    canvas.height = area.clientHeight - (playbackBar.style.display !== 'none' ? 52 : 0);
    if (simData) drawFrame();
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

// ── Status helpers ──
function setStatus(text, type) {
    statusText.textContent = text;
    statusDot.className = 'status-dot' + (type ? ' ' + type : '');
}

function showError(msg) {
    errorBox.style.display = 'flex';
    errorText.textContent = msg;
}

function hideError() { errorBox.style.display = 'none'; }

// ── API ──
async function runSimulation() {
    const content = mapInput.value.trim();
    if (!content) { showError('Map content is empty'); return; }

    hideError();
    runBtn.disabled = true;
    runBtn.classList.add('loading');
    setStatus('Running...', 'running');
    stopPlayback();

    try {
        const res = await fetch('/runs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ map_content: content })
        });
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || 'Simulation failed');
        }
        simData = data;
        onSimulationComplete();
    } catch (e) {
        setStatus('Error', 'error');
        showError(e.message);
    } finally {
        runBtn.disabled = false;
        runBtn.classList.remove('loading');
    }
}

// ── Post-simulation setup ──
function onSimulationComplete() {
    setStatus('Complete', '');
    computeZonePositions();
    buildDroneStates();
    currentTurn = 0;
    animProgress = 1;

    // Stats
    document.getElementById('stat-drones').textContent = simData.nb_drones;
    document.getElementById('stat-turns').textContent = simData.turns_total;

    // Turn log
    turnLog.innerHTML = '';
    for (const t of simData.turns) {
        const el = document.createElement('div');
        el.className = 'turn-entry';
        el.dataset.turn = t.turn;
        el.innerHTML = `<span class="turn-num">T${t.turn}</span>${t.movements.join('  ')}`;
        turnLog.appendChild(el);
    }

    // Playback
    turnSlider.max = simData.turns.length;
    turnSlider.value = 0;
    turnTotal.textContent = simData.turns.length;
    turnCurrent.textContent = '0';
    resultsSection.style.display = 'flex';
    playbackBar.style.display = 'flex';
    resizeCanvas();
    drawFrame();
}

// ── Zone positioning ──
function computeZonePositions() {
    const zones = simData.zones;
    const pad = 80;
    const w = canvas.width;
    const h = canvas.height;

    const xs = zones.map(z => z.x);
    const ys = zones.map(z => z.y);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);
    const rangeX = maxX - minX || 1;
    const rangeY = maxY - minY || 1;

    const scaleX = (w - 2 * pad) / rangeX;
    const scaleY = (h - 2 * pad) / rangeY;
    const scale = Math.min(scaleX, scaleY);

    const cx = w / 2;
    const cy = h / 2;
    const graphCx = (minX + maxX) / 2;
    const graphCy = (minY + maxY) / 2;

    zonePositions = {};
    for (const z of zones) {
        zonePositions[z.name] = {
            x: cx + (z.x - graphCx) * scale,
            y: cy - (z.y - graphCy) * scale,   // flip y
            zone: z
        };
    }
}

// ── Build drone states per turn ──
function buildDroneStates() {
    const startName = simData.zones.find(z => z.role === 'start').name;
    droneStates = [];

    // Turn 0: all at start
    const init = {};
    for (let i = 1; i <= simData.nb_drones; i++) {
        init[`D${i}`] = { zone: startName, transit: null };
    }
    droneStates.push(cloneState(init));

    let current = cloneState(init);
    for (const turnData of simData.turns) {
        const next = cloneState(current);
        for (const mov of turnData.movements) {
            const parts = mov.split('-');
            const droneId = parts[0];
            if (parts.length === 2) {
                next[droneId] = { zone: parts[1], transit: null };
            } else if (parts.length >= 3) {
                next[droneId] = { zone: parts[1], transit: parts[2] };
            }
        }
        droneStates.push(next);
        current = cloneState(next);
    }
}

function cloneState(s) {
    const c = {};
    for (const [k, v] of Object.entries(s)) c[k] = { ...v };
    return c;
}

// ── Drawing ──
function drawFrame() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawGrid();
    drawConnections();
    drawZones();
    drawDrones();
}

function drawGrid() {
    ctx.strokeStyle = 'rgba(0, 212, 255, 0.03)';
    ctx.lineWidth = 1;
    const step = 40;
    for (let x = 0; x < canvas.width; x += step) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += step) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
    }
}

function drawConnections() {
    if (!simData) return;
    for (const conn of simData.connections) {
        const a = zonePositions[conn.from];
        const b = zonePositions[conn.to];
        if (!a || !b) continue;

        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.strokeStyle = 'rgba(100, 116, 139, 0.35)';
        ctx.lineWidth = 2;
        ctx.stroke();

        // capacity label
        const mx = (a.x + b.x) / 2;
        const my = (a.y + b.y) / 2;
        ctx.font = '10px Inter';
        ctx.fillStyle = 'rgba(100, 116, 139, 0.5)';
        ctx.textAlign = 'center';
        ctx.fillText(`cap:${conn.capacity}`, mx, my - 6);
    }
}

function drawZones() {
    for (const [name, pos] of Object.entries(zonePositions)) {
        const z = pos.zone;
        const isStart = z.role === 'start';
        const isEnd = z.role === 'end';
        const color = ZONE_TYPE_COLORS[z.type] || '#4a9eff';

        // Glow
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, ZONE_RADIUS + 4, 0, Math.PI * 2);
        ctx.fillStyle = (isStart || isEnd)
            ? `rgba(${isStart ? '34,197,94' : '245,158,11'}, 0.15)`
            : `${color}11`;
        ctx.fill();

        // Circle
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, ZONE_RADIUS, 0, Math.PI * 2);
        ctx.fillStyle = '#0d1220';
        ctx.fill();
        ctx.strokeStyle = isStart ? '#22c55e' : isEnd ? '#f59e0b' : color;
        ctx.lineWidth = isStart || isEnd ? 3 : 2;
        ctx.stroke();

        // Icon for start/end
        ctx.font = isStart || isEnd ? 'bold 13px Inter' : '11px Inter';
        ctx.fillStyle = isStart ? '#22c55e' : isEnd ? '#f59e0b' : color;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(isStart ? '▶' : isEnd ? '◎' : '', pos.x, pos.y);

        // Label
        ctx.font = '500 12px Inter';
        ctx.fillStyle = '#e2e8f0';
        ctx.textBaseline = 'top';
        ctx.fillText(name, pos.x, pos.y + ZONE_RADIUS + 8);

        // Zone type badge
        ctx.font = '9px Inter';
        ctx.fillStyle = 'rgba(100, 116, 139, 0.6)';
        ctx.fillText(z.type, pos.x, pos.y + ZONE_RADIUS + 22);
    }
}

function getDroneVisualPos(state) {
    if (state.transit) {
        const za = zonePositions[state.zone];
        const zb = zonePositions[state.transit];
        if (za && zb) return { x: (za.x + zb.x) / 2, y: (za.y + zb.y) / 2 };
    }
    const zp = zonePositions[state.zone];
    return zp ? { x: zp.x, y: zp.y } : null;
}

function drawDrones() {
    if (!droneStates.length) return;

    const fromState = currentTurn > 0 ? droneStates[currentTurn - 1] : droneStates[0];
    const toState = droneStates[currentTurn];
    const droneIds = Object.keys(toState);

    droneIds.forEach((id, idx) => {
        const to = toState[id];
        const from = fromState ? fromState[id] : to;
        const color = DRONE_COLORS[idx % DRONE_COLORS.length];

        const fromPos = getDroneVisualPos(from);
        const toPos = getDroneVisualPos(to);
        if (!toPos) return;

        let x, y;

        if (animProgress < 1 && fromPos) {
            // Smoothly interpolate from previous position to current
            const t = easeInOutCubic(animProgress);
            x = fromPos.x + (toPos.x - fromPos.x) * t;
            y = fromPos.y + (toPos.y - fromPos.y) * t;
        } else {
            x = toPos.x;
            y = toPos.y;
        }

        // Offset drones so they don't overlap at same zone
        const samePos = droneIds.filter(did => {
            const ds = toState[did];
            return ds.zone === to.zone && ds.transit === to.transit;
        });
        if (samePos.length > 1) {
            const myIdx = samePos.indexOf(id);
            const angle = (myIdx / samePos.length) * Math.PI * 2 - Math.PI / 2;
            x += Math.cos(angle) * 14;
            y += Math.sin(angle) * 14;
        }

        // Glow
        const grad = ctx.createRadialGradient(x, y, 0, x, y, DRONE_RADIUS * 3);
        grad.addColorStop(0, color + '40');
        grad.addColorStop(1, color + '00');
        ctx.beginPath();
        ctx.arc(x, y, DRONE_RADIUS * 3, 0, Math.PI * 2);
        ctx.fillStyle = grad;
        ctx.fill();

        // Drone circle
        ctx.beginPath();
        ctx.arc(x, y, DRONE_RADIUS, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = '#0d1220';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Label
        ctx.font = 'bold 9px Inter';
        ctx.fillStyle = '#fff';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(id, x, y);
    });
}

function easeInOutCubic(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

// ── Playback ──
function getSpeed() {
    return parseInt(document.getElementById('speed-select').value);
}

function goToTurn(turn) {
    currentTurn = Math.max(0, Math.min(turn, droneStates.length - 1));
    animProgress = 1;
    turnCurrent.textContent = currentTurn;
    turnSlider.value = currentTurn;
    highlightTurnLog();
    drawFrame();
}

function highlightTurnLog() {
    document.querySelectorAll('.turn-entry').forEach(el => {
        el.classList.toggle('active', parseInt(el.dataset.turn) === currentTurn);
    });
    const active = turnLog.querySelector('.turn-entry.active');
    if (active) active.scrollIntoView({ block: 'nearest' });
}

function startPlayback() {
    if (currentTurn >= droneStates.length - 1) currentTurn = 0;
    isPlaying = true;
    document.getElementById('btn-play').textContent = '⏸';
    setStatus('Playing', 'running');
    animProgress = 0;
    lastFrameTime = performance.now();
    animFrameId = requestAnimationFrame(animationLoop);
}

function stopPlayback() {
    isPlaying = false;
    document.getElementById('btn-play').textContent = '⏵';
    if (animFrameId) cancelAnimationFrame(animFrameId);
    animFrameId = null;
    if (simData) setStatus('Complete', '');
}

function animationLoop(timestamp) {
    if (!isPlaying) return;

    const delta = timestamp - lastFrameTime;
    const speed = getSpeed();
    animProgress += delta / speed;
    lastFrameTime = timestamp;

    if (animProgress >= 1) {
        animProgress = 1;
        drawFrame();
        currentTurn++;
        if (currentTurn >= droneStates.length) {
            currentTurn = droneStates.length - 1;
            stopPlayback();
            goToTurn(currentTurn);
            return;
        }
        turnCurrent.textContent = currentTurn;
        turnSlider.value = currentTurn;
        highlightTurnLog();
        animProgress = 0;
    }

    drawFrame();
    animFrameId = requestAnimationFrame(animationLoop);
}

// ── Events ──
runBtn.addEventListener('click', runSimulation);

document.getElementById('btn-play').addEventListener('click', () => {
    isPlaying ? stopPlayback() : startPlayback();
});

document.getElementById('btn-forward').addEventListener('click', () => {
    stopPlayback();
    if (currentTurn < droneStates.length - 1) goToTurn(currentTurn + 1);
});

document.getElementById('btn-back').addEventListener('click', () => {
    stopPlayback();
    if (currentTurn > 0) goToTurn(currentTurn - 1);
});

document.getElementById('btn-reset').addEventListener('click', () => {
    stopPlayback();
    goToTurn(0);
});

document.getElementById('btn-end').addEventListener('click', () => {
    stopPlayback();
    goToTurn(droneStates.length - 1);
});

turnSlider.addEventListener('input', (e) => {
    stopPlayback();
    goToTurn(parseInt(e.target.value));
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'TEXTAREA') return;
    if (e.key === ' ') { e.preventDefault(); isPlaying ? stopPlayback() : startPlayback(); }
    if (e.key === 'ArrowRight') goToTurn(currentTurn + 1);
    if (e.key === 'ArrowLeft') goToTurn(currentTurn - 1);
});
