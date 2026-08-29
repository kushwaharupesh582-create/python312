// ============================================================
// ARYA AI - COMPLETE WITH ALL CONSOLE LOGS
// ============================================================

console.log('🚀 ARYA AI - Initializing...');
console.log('📅', new Date().toLocaleString());

// ============================================================
// THEME MANAGEMENT
// ============================================================

function getISTHour() {
    const now = new Date();
    const utcHours = now.getUTCHours();
    const utcMinutes = now.getUTCMinutes();
    let istHours = utcHours + 5;
    let istMinutes = utcMinutes + 30;
    if (istMinutes >= 60) {
        istMinutes -= 60;
        istHours += 1;
    }
    if (istHours >= 24) {
        istHours -= 24;
    }
    const result = istHours + istMinutes / 60;
    console.log(`🕐 Current IST: ${Math.floor(result)}:${String(Math.round((result % 1) * 60)).padStart(2, '0')}`);
    return result;
}

function getThemeFromTime() {
    const hour = getISTHour();
    let theme;
    if (hour >= 4 && hour < 19) {
        theme = 'light';
    } else {
        theme = 'dark';
    }
    console.log(`🌓 Theme from time: ${theme} (hour: ${hour.toFixed(2)})`);
    return theme;
}

let themeToastTimeout = null;
let scheduledSwitchTimeout = null;

function showThemeToast(theme) {
    console.log(`💬 Toast: Switching to ${theme} mode`);
    const toast = document.getElementById('themeToast');
    if (!toast) return;
    const icon = theme === 'light' ? '☀️' : '🌙';
    const label = theme === 'light' ? 'Light Mode' : 'Dark Mode';
    toast.innerHTML = `<i>${icon}</i> Switching to ${label}`;
    toast.classList.add('show');
    clearTimeout(themeToastTimeout);
    themeToastTimeout = setTimeout(() => {
        toast.classList.remove('show');
    }, 2000);
}

function applyTheme(theme) {
    console.log(`🎨 Applying theme: ${theme}`);
    const body = document.body;
    if (theme === 'light') {
        body.classList.add('light-mode');
        body.classList.remove('dark-mode');
    } else {
        body.classList.remove('light-mode');
        body.classList.add('dark-mode');
    }
    const toggleBtn = document.getElementById('themeToggle');
    if (toggleBtn) {
        toggleBtn.innerHTML = theme === 'light' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    }
    localStorage.setItem('arya-theme', theme);
    const aryaImage = document.getElementById('aryaImage');
    if (aryaImage) {
        const imgPath = `/static/arya_${theme}.png`;
        console.log(`🖼️ Setting image: ${imgPath}`);
        aryaImage.src = imgPath;
    }
    console.log(`✅ Theme applied: ${theme}`);
}

function getCurrentTheme() {
    const theme = document.body.classList.contains('light-mode') ? 'light' : 'dark';
    console.log(`🔍 Current theme: ${theme}`);
    return theme;
}

function switchThemeBasedOnTime(showToast = true) {
    const targetTheme = getThemeFromTime();
    const current = getCurrentTheme();
    console.log(`🔄 Theme check: target=${targetTheme}, current=${current}`);
    if (targetTheme !== current) {
        console.log(`🔄 Switching theme from ${current} to ${targetTheme}`);
        applyTheme(targetTheme);
        if (showToast) {
            showThemeToast(targetTheme);
        }
        return true;
    }
    console.log(`✅ Theme already correct: ${current}`);
    return false;
}

function scheduleNextSwitch() {
    const now = new Date();
    const utcHours = now.getUTCHours();
    const utcMinutes = now.getUTCMinutes();
    const istTotalMinutes = utcHours * 60 + utcMinutes + 330;
    const targetMinutes = [240, 1140];
    let nextSwitchMinutes = null;
    let nextSwitchLabel = '';
    for (const t of targetMinutes) {
        let diff = t - istTotalMinutes;
        if (diff < 0) diff += 1440;
        if (nextSwitchMinutes === null || diff < nextSwitchMinutes) {
            nextSwitchMinutes = diff;
            nextSwitchLabel = t === 240 ? '4:00 AM' : '7:00 PM';
        }
    }
    const delayMs = nextSwitchMinutes * 60 * 1000;
    console.log(`⏰ Next theme switch at ${nextSwitchLabel} (in ${Math.round(delayMs/1000/60)} minutes)`);
    clearTimeout(scheduledSwitchTimeout);
    scheduledSwitchTimeout = setTimeout(() => {
        console.log(`⏰ Scheduled switch triggered!`);
        switchThemeBasedOnTime(true);
        scheduleNextSwitch();
    }, delayMs);
}

// ============================================================
// CIRCUIT BACKGROUND (simplified with logs)
// ============================================================
console.log('🔌 Initializing Circuit Background...');
class CircuitBackground {
    constructor() {
        this.canvas = document.getElementById('circuitCanvas');
        if (!this.canvas) {
            console.warn('⚠️ circuitCanvas not found');
            return;
        }
        console.log('✅ Circuit canvas found');
        this.ctx = this.canvas.getContext('2d');
        this.nodes = [];
        this.wires = [];
        this.mouseX = -1000;
        this.mouseY = -1000;
        this.init();
        this.animate();
        document.addEventListener('mousemove', (e) => {
            this.mouseX = e.clientX;
            this.mouseY = e.clientY;
        });
    }

    init() {
        console.log('🎯 Initializing circuit nodes...');
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        const nodeCount = 45;
        for (let i = 0; i < nodeCount; i++) {
            this.nodes.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                radius: 2 + Math.random() * 3,
                speedX: (Math.random() - 0.5) * 0.3,
                speedY: (Math.random() - 0.5) * 0.3,
                phase: Math.random() * Math.PI * 2,
                type: Math.floor(Math.random() * 3)
            });
        }
        this.updateWires();
        console.log(`✅ Created ${this.nodes.length} nodes, ${this.wires.length} wires`);
    }

    updateWires() {
        this.wires = [];
        for (let i = 0; i < this.nodes.length; i++) {
            for (let j = i + 1; j < this.nodes.length; j++) {
                const dx = this.nodes[i].x - this.nodes[j].x;
                const dy = this.nodes[i].y - this.nodes[j].y;
                const dist = Math.sqrt(dx*dx + dy*dy);
                if (dist < 180) {
                    this.wires.push({
                        n1: i, n2: j, dist: dist, maxDist: 180,
                        speed: 0.5 + Math.random() * 0.5,
                        phase: Math.random() * Math.PI * 2,
                        glow: 0.2 + Math.random() * 0.3
                    });
                }
            }
        }
    }

    drawLogicGate(x, y, type, size, progress) {
        const ctx = this.ctx;
        ctx.save();
        ctx.translate(x, y);
        const colors = ['#a855f7', '#ec4899', '#22d3ee', '#c084fc', '#f472b6'];
        const color = colors[Math.floor(Math.random() * colors.length)];
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.shadowColor = color;
        ctx.shadowBlur = 10;
        if (type === 0) {
            ctx.beginPath();
            ctx.arc(0, 0, size, 0, Math.PI * 2);
            ctx.stroke();
            ctx.shadowBlur = 5;
            ctx.beginPath();
            ctx.arc(0, 0, size * 0.5, 0, Math.PI * 2 * progress);
            ctx.stroke();
        } else if (type === 1) {
            ctx.beginPath();
            ctx.moveTo(0, -size);
            ctx.lineTo(size, 0);
            ctx.lineTo(0, size);
            ctx.lineTo(-size, 0);
            ctx.closePath();
            ctx.stroke();
            ctx.shadowBlur = 5;
            ctx.beginPath();
            ctx.moveTo(0, -size * 0.3);
            ctx.lineTo(size * 0.3, 0);
            ctx.lineTo(0, size * 0.3);
            ctx.lineTo(-size * 0.3, 0);
            ctx.closePath();
            ctx.stroke();
        } else {
            ctx.strokeRect(-size, -size, size * 2, size * 2);
            ctx.shadowBlur = 5;
            ctx.beginPath();
            ctx.moveTo(-size, -size);
            ctx.lineTo(size, size);
            ctx.stroke();
        }
        ctx.restore();
    }

    draw() {
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;
        ctx.clearRect(0, 0, w, h);
        ctx.fillStyle = 'rgba(10, 10, 18, 0.3)';
        ctx.fillRect(0, 0, w, h);

        this.wires.forEach(wire => {
            const n1 = this.nodes[wire.n1];
            const n2 = this.nodes[wire.n2];
            const dx = n2.x - n1.x;
            const dy = n2.y - n1.y;
            const dist = Math.sqrt(dx*dx + dy*dy);
            if (dist > 0 && dist < wire.maxDist) {
                const alpha = 1 - (dist / wire.maxDist);
                const midX = (n1.x + n2.x) / 2;
                const midY = (n1.y + n2.y) / 2;
                const mouseDist = Math.sqrt(Math.pow(this.mouseX - midX, 2) + Math.pow(this.mouseY - midY, 2));
                const isNearMouse = mouseDist < 100;
                ctx.beginPath();
                ctx.moveTo(n1.x, n1.y);
                ctx.lineTo(n2.x, n2.y);
                ctx.strokeStyle = isNearMouse ? `rgba(168, 85, 247, ${alpha * 0.8})` : `rgba(168, 85, 247, ${alpha * 0.3})`;
                ctx.lineWidth = isNearMouse ? 2.5 : 1;
                ctx.shadowColor = '#a855f7';
                ctx.shadowBlur = isNearMouse ? 20 : 5;
                ctx.stroke();
                const numDots = isNearMouse ? 6 : 3;
                for (let i = 0; i < numDots; i++) {
                    const t = (i / numDots + (Date.now() / 2000 * wire.speed) % 1) % 1;
                    const px = n1.x + dx * t;
                    const py = n1.y + dy * t;
                    ctx.beginPath();
                    ctx.arc(px, py, isNearMouse ? 3 : 1.5, 0, Math.PI * 2);
                    ctx.fillStyle = isNearMouse ? `rgba(168, 85, 247, ${0.8 + Math.sin(Date.now()/300 + i) * 0.2})` : `rgba(168, 85, 247, ${0.4 + Math.sin(Date.now()/500 + i) * 0.2})`;
                    ctx.shadowColor = '#a855f7';
                    ctx.shadowBlur = isNearMouse ? 15 : 5;
                    ctx.fill();
                }
            }
        });

        this.nodes.forEach((node) => {
            node.x += node.speedX;
            node.y += node.speedY;
            if (node.x < 0 || node.x > w) node.speedX *= -1;
            if (node.y < 0 || node.y > h) node.speedY *= -1;
            const mouseDist = Math.sqrt(Math.pow(this.mouseX - node.x, 2) + Math.pow(this.mouseY - node.y, 2));
            const isHovered = mouseDist < 30;
            if (isHovered) {
                const progress = (Math.sin(Date.now() / 500 + node.phase) + 1) / 2;
                this.drawLogicGate(node.x, node.y, node.type, node.radius * 3, progress);
            } else {
                ctx.beginPath();
                if (node.type === 0) ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
                else if (node.type === 1) {
                    ctx.moveTo(node.x, node.y - node.radius);
                    ctx.lineTo(node.x + node.radius, node.y);
                    ctx.lineTo(node.x, node.y + node.radius);
                    ctx.lineTo(node.x - node.radius, node.y);
                    ctx.closePath();
                } else {
                    ctx.rect(node.x - node.radius, node.y - node.radius, node.radius * 2, node.radius * 2);
                }
                const brightness = 0.3 + Math.sin(Date.now() / 1000 + node.phase) * 0.2;
                ctx.fillStyle = `rgba(168, 85, 247, ${brightness})`;
                ctx.shadowColor = 'rgba(168, 85, 247, 0.3)';
                ctx.shadowBlur = 8;
                ctx.fill();
            }
        });

        if (Math.random() < 0.001) this.updateWires();
        requestAnimationFrame(() => this.draw());
    }

    animate() { this.draw(); }
}

// ============================================================
// SPARKLE EFFECT (with logs)
// ============================================================
console.log('✨ Initializing Sparkle Effect...');
class SparkleEffect {
    constructor() {
        this.container = document.getElementById('centerPanel') || document.body;
        this.particles = [];
        this.running = false;
        console.log('✅ Sparkle Effect ready');
    }

    burst(x, y, count = 30) {
        console.log(`💥 Sparkle burst at (${Math.round(x)}, ${Math.round(y)}) with ${count} particles`);
        const colors = ['#a855f7', '#ec4899', '#22d3ee', '#c084fc', '#f472b6', '#fbbf24', '#34d399'];
        for (let i = 0; i < count; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = 50 + Math.random() * 150;
            const size = 4 + Math.random() * 8;
            this.particles.push({
                x: x,
                y: y,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed - 50,
                size: size,
                life: 1,
                decay: 0.01 + Math.random() * 0.02,
                color: colors[Math.floor(Math.random() * colors.length)],
                gravity: 120
            });
        }
        if (!this.running) {
            this.running = true;
            this.animate();
        }
    }

    animate() {
        if (this.particles.length === 0) {
            this.running = false;
            return;
        }
        this.particles.forEach(p => {
            p.x += p.vx * 0.016;
            p.y += p.vy * 0.016;
            p.vy += p.gravity * 0.016;
            p.life -= p.decay;
        });
        this.particles = this.particles.filter(p => p.life > 0);
        const html = this.particles.map(p => `
            <div style="
                position: fixed;
                left: ${p.x}px;
                top: ${p.y}px;
                width: ${p.size}px;
                height: ${p.size}px;
                background: ${p.color};
                border-radius: 50%;
                opacity: ${p.life};
                pointer-events: none;
                z-index: 9999;
                box-shadow: 0 0 ${p.size * 2}px ${p.color};
                transition: none;
            "></div>
        `).join('');
        const div = document.createElement('div');
        div.innerHTML = html;
        div.style.position = 'fixed';
        div.style.top = '0';
        div.style.left = '0';
        div.style.width = '100%';
        div.style.height = '100%';
        div.style.pointerEvents = 'none';
        div.style.zIndex = '9999';
        document.body.appendChild(div);
        setTimeout(() => {
            if (div.parentNode) div.parentNode.removeChild(div);
        }, 50);
        requestAnimationFrame(() => this.animate());
    }
}

const sparkle = new SparkleEffect();

// ============================================================
// RIPPLE EFFECT
// ============================================================
console.log('💧 Initializing Ripple Effect...');

function createRipple(e, element) {
    const rect = element.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const size = Math.max(rect.width, rect.height) * 0.6;
    console.log(`💧 Ripple at (${Math.round(x)}, ${Math.round(y)}) on ${element.tagName}`);
    const ripple = document.createElement('span');
    ripple.style.cssText = `
        position: absolute;
        left: ${x - size/2}px;
        top: ${y - size/2}px;
        width: ${size}px;
        height: ${size}px;
        border-radius: 50%;
        background: rgba(168, 85, 247, 0.3);
        transform: scale(0);
        animation: rippleAnim 0.8s ease-out forwards;
        pointer-events: none;
        z-index: 10;
    `;
    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);
    setTimeout(() => {
        if (ripple.parentNode) ripple.parentNode.removeChild(ripple);
    }, 800);
}

if (!document.querySelector('#rippleStyle')) {
    const style = document.createElement('style');
    style.id = 'rippleStyle';
    style.textContent = `
        @keyframes rippleAnim {
            0% { transform: scale(0); opacity: 1; }
            100% { transform: scale(4); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
    console.log('✅ Ripple styles injected');
}

// ============================================================
// DOM Elements
// ============================================================
console.log('📦 Initializing DOM Elements...');
const messages = document.getElementById('messages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const micBtn = document.getElementById('micBtn');
const typingIndicator = document.getElementById('typing');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const chatStatus = document.getElementById('chatStatus');
const emojiBtn = document.getElementById('emojiBtn');
const emojiPicker = document.getElementById('emojiPicker');
const themeToggle = document.getElementById('themeToggle');
const fullscreenToggle = document.getElementById('fullscreenToggle');
const footerTime = document.getElementById('footerTime');
const headerTime = document.getElementById('headerTime');
const chatBox = document.getElementById('chatBox');
const minimizeBtn = document.getElementById('minimizeBtn');
const toggleBtn = document.getElementById('toggleBtn');
const chatHeader = document.getElementById('chatHeader');
const chatToggle = document.getElementById('chatToggle');
const historyBtn = document.getElementById('historyBtn');
const chatHistory = document.getElementById('chatHistory');
const historyList = document.getElementById('historyList');
const quickPanel = document.getElementById('quickPanel');
const quickToggle = document.getElementById('quickToggle');
const quickCloseBtn = document.getElementById('quickCloseBtn');
const quickToggleBar = document.getElementById('quickToggleBar');
const leftPanel = document.getElementById('leftPanel');
const panelToggle = document.getElementById('panelToggle');
const centerPanel = document.getElementById('centerPanel');
const focusToggle = document.getElementById('focusToggle');

console.log('✅ All DOM elements loaded');

// ============================================================
// UPDATE TOGGLE POSITIONS (Fixes all glitches)
// ============================================================
function updateTogglePositions() {
    // ---- Persona Toggle ----
    const isPersonaHidden = leftPanel.classList.contains('collapsed');
    const panelRect = leftPanel.getBoundingClientRect();
    const toggleWidth = 22;
    
    if (isPersonaHidden) {
        // Hidden: Move to the FAR LEFT edge of the screen
        panelToggle.style.left = '0px';
        panelToggle.style.right = 'auto';
        panelToggle.style.borderRadius = '0 10px 10px 0';
        panelToggle.style.borderLeft = '2px solid var(--primary)';
        panelToggle.style.borderRight = 'none';
        panelToggle.style.boxShadow = '4px 0 25px rgba(168, 85, 247, 0.5)';
    } else {
        // Visible: Attach to the RIGHT edge of the panel
        const rightEdge = panelRect.right;
        panelToggle.style.left = (rightEdge - 1) + 'px';
        panelToggle.style.right = 'auto';
        panelToggle.style.borderRadius = '0 10px 10px 0';
        panelToggle.style.borderLeft = 'none';
        panelToggle.style.borderRight = '1px solid var(--glass-border)';
        panelToggle.style.boxShadow = '2px 0 12px rgba(0,0,0,0.1)';
    }

    // ---- Quick Toggle ----
    const isQuickHidden = quickPanel.classList.contains('collapsed');
    const quickRect = quickPanel.getBoundingClientRect();
    
    if (isQuickHidden) {
        // Hidden: Move to the FAR RIGHT edge of the screen
        quickToggleBar.style.right = '10px';
        quickToggleBar.style.left = 'auto';
    } else {
        // Visible: Attach to the LEFT edge of the quick panel
        const leftEdge = quickRect.left;
        quickToggleBar.style.right = 'auto';
        quickToggleBar.style.left = (leftEdge - 22) + 'px';
    }
}

// ============================================================
// START CIRCUIT BACKGROUND
// ============================================================
const circuit = new CircuitBackground();
console.log('🔌 Circuit Background started');

// ============================================================
// ADD RIPPLE TO ALL BUTTONS
// ============================================================
console.log('🔗 Adding ripple to all interactive elements...');
document.querySelectorAll('.action-btn, .chat-btn, .input-btn, .send-btn, .quick-card, .panel-toggle, .quick-toggle-bar, .chat-toggle').forEach(btn => {
    btn.addEventListener('click', function(e) {
        createRipple(e, this);
    });
});
console.log('✅ Ripple added to all buttons');

// ============================================================
// INITIAL THEME SETUP
// ============================================================
console.log('🌓 Setting up initial theme...');
applyTheme(getThemeFromTime());
scheduleNextSwitch();

// ============================================================
// FOCUS MODE TOGGLE
// ============================================================
console.log('👁️ Focus Mode ready');
let focusMode = false;
focusToggle.addEventListener('click', () => {
    focusMode = !focusMode;
    console.log(`👁️ Focus Mode: ${focusMode ? 'ON' : 'OFF'}`);
    document.body.classList.toggle('focus-mode', focusMode);
    focusToggle.innerHTML = focusMode ? '<i class="fas fa-eye-slash"></i>' : '<i class="fas fa-eye"></i>';
    const toast = document.getElementById('themeToast');
    if (toast) {
        const icon = focusMode ? '🧘' : '👁️';
        const label = focusMode ? 'Focus Mode On' : 'Focus Mode Off';
        toast.innerHTML = `<i>${icon}</i> ${label}`;
        toast.classList.add('show');
        clearTimeout(themeToastTimeout);
        themeToastTimeout = setTimeout(() => {
            toast.classList.remove('show');
        }, 1500);
    }
    addActivity(focusMode ? 'Focus Mode: All panels hidden' : 'Focus Mode: All panels restored', '🧘');
});

// ============================================================
// PANEL TOGGLE (Persona Box) - With Position Update
// ============================================================
console.log('📐 Left Panel toggle ready');
panelToggle.addEventListener('click', () => {
    leftPanel.classList.toggle('collapsed');
    const isCollapsed = leftPanel.classList.contains('collapsed');
    console.log(`📐 Left Panel: ${isCollapsed ? 'collapsed' : 'expanded'}`);
    addActivity(isCollapsed ? 'Persona box hidden' : 'Persona box shown', '📐');
    updateTogglePositions(); // Fix position immediately
});

// ============================================================
// QUICK PANEL TOGGLE - With Position Update
// ============================================================
console.log('⚡ Quick Panel toggle ready');
let quickPanelVisible = true;

function toggleQuickPanel() {
    quickPanelVisible = !quickPanelVisible;
    console.log(`⚡ Quick Panel: ${quickPanelVisible ? 'visible' : 'hidden'}`);
    quickPanel.classList.toggle('collapsed', !quickPanelVisible);
    quickToggle.innerHTML = quickPanelVisible ? '<i class="fas fa-th-large"></i>' : '<i class="fas fa-th-large" style="opacity:0.5;"></i>';
    addActivity(quickPanelVisible ? 'Quick commands shown' : 'Quick commands hidden', '📋');
    updateTogglePositions(); // Fix position immediately
}

quickToggleBar.addEventListener('click', toggleQuickPanel);
quickToggle.addEventListener('click', toggleQuickPanel);
quickCloseBtn.addEventListener('click', () => {
    if (quickPanelVisible) toggleQuickPanel();
});

// ============================================================
// QUICK COMMANDS - POPULATE & SHUFFLE
// ============================================================
console.log('📋 Building Quick Commands...');
const quickCommandsData = [
    { cmd: 'open youtube', icon: 'fab fa-youtube', bg: 'linear-gradient(135deg, #ff0033, #ff6b6b)' },
    { cmd: 'open google', icon: 'fab fa-google', bg: 'linear-gradient(135deg, #4285f4, #34a853)' },
    { cmd: 'open instagram', icon: 'fab fa-instagram', bg: 'linear-gradient(135deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888)' },
    { cmd: 'open spotify', icon: 'fab fa-spotify', bg: 'linear-gradient(135deg, #1db954, #169c46)' },
    { cmd: 'volume up', icon: 'fas fa-volume-up', bg: 'linear-gradient(135deg, #667eea, #764ba2)' },
    { cmd: 'volume down', icon: 'fas fa-volume-down', bg: 'linear-gradient(135deg, #f093fb, #f5576c)' },
    { cmd: 'brightness up', icon: 'fas fa-sun', bg: 'linear-gradient(135deg, #f6d365, #fda085)' },
    { cmd: 'brightness down', icon: 'fas fa-moon', bg: 'linear-gradient(135deg, #a18cd1, #fbc2eb)' },
    { cmd: 'screenshot', icon: 'fas fa-camera', bg: 'linear-gradient(135deg, #a8edea, #fed6e3)' },
    { cmd: 'system status', icon: 'fas fa-chart-line', bg: 'linear-gradient(135deg, #89f7fe, #66a6ff)' },
    { cmd: 'weather', icon: 'fas fa-cloud-sun', bg: 'linear-gradient(135deg, #fa709a, #fee140)' },
    { cmd: 'who are you', icon: 'fas fa-heart', bg: 'linear-gradient(135deg, #f093fb, #f5576c)' },
    { cmd: 'play', icon: 'fas fa-play', bg: 'linear-gradient(135deg, #4facfe, #00f2fe)' },
    { cmd: 'pause', icon: 'fas fa-pause', bg: 'linear-gradient(135deg, #43e97b, #38f9d7)' },
    { cmd: 'lock pc', icon: 'fas fa-lock', bg: 'linear-gradient(135deg, #f5576c, #ff6b6b)' },
    { cmd: 'restart', icon: 'fas fa-sync', bg: 'linear-gradient(135deg, #fa709a, #fee140)' }
];

const quickGrid = document.getElementById('quickGridRight');

function buildQuickCards() {
    console.log(`📋 Building ${quickCommandsData.length} quick cards...`);
    quickGrid.innerHTML = '';
    quickCommandsData.forEach((item, index) => {
        const card = document.createElement('div');
        card.className = 'quick-card';
        card.dataset.cmd = item.cmd;
        card.innerHTML = `
            <div class="quick-icon" style="background: ${item.bg};">
                <i class="${item.icon}"></i>
            </div>
            <span>${item.cmd.charAt(0).toUpperCase() + item.cmd.slice(1)}</span>
        `;
        card.addEventListener('click', function(e) {
            console.log(`⚡ Quick command clicked: ${item.cmd}`);
            createRipple(e, this);
            userInput.value = item.cmd;
            sendMessage();
            addActivity(`Quick action: ${item.cmd}`, '⚡');
        });
        quickGrid.appendChild(card);
    });
    console.log('✅ Quick cards built');
}

function shuffleQuickCards() {
    console.log('🔀 Shuffling quick cards...');
    const cards = Array.from(quickGrid.children);
    for (let i = cards.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [cards[i], cards[j]] = [cards[j], cards[i]];
    }
    cards.forEach(card => quickGrid.appendChild(card));
    console.log('✅ Cards shuffled');
}

buildQuickCards();
let shuffleInterval = setInterval(shuffleQuickCards, 5000);
console.log('🔄 Quick cards will shuffle every 5 seconds');

// ============================================================
// DRAG FOR CHAT BOX
// ============================================================
console.log('🖱️ Chat drag handler ready');
let isDragging = false;
let offsetX = 0;
let offsetY = 0;

function startDrag(e) {
    if (!chatHeader.contains(e.target)) return;
    if (chatBox.classList.contains('minimized')) return;
    isDragging = true;
    const rect = chatBox.getBoundingClientRect();
    const clientX = e.clientX || e.touches?.[0]?.clientX || 0;
    const clientY = e.clientY || e.touches?.[0]?.clientY || 0;
    offsetX = clientX - rect.left;
    offsetY = clientY - rect.top;
    chatBox.classList.add('dragging');
    chatBox.style.cursor = 'grabbing';
    console.log('🖱️ Chat drag started');
}

function onDrag(e) {
    if (!isDragging) return;
    e.preventDefault();
    const clientX = e.clientX || e.touches?.[0]?.clientX || 0;
    const clientY = e.clientY || e.touches?.[0]?.clientY || 0;
    let newX = clientX - offsetX;
    let newY = clientY - offsetY;
    const rect = chatBox.getBoundingClientRect();
    const maxX = window.innerWidth - rect.width;
    const maxY = window.innerHeight - rect.height - 60;
    newX = Math.max(0, Math.min(newX, maxX));
    newY = Math.max(0, Math.min(newY, maxY));
    chatBox.style.left = newX + 'px';
    chatBox.style.right = 'auto';
    chatBox.style.top = newY + 'px';
    chatBox.style.bottom = 'auto';
}

function stopDrag() {
    if (isDragging) {
        isDragging = false;
        chatBox.classList.remove('dragging');
        chatBox.style.cursor = 'grab';
        console.log('🖱️ Chat drag ended');
    }
}

chatHeader.addEventListener('mousedown', startDrag);
document.addEventListener('mousemove', onDrag);
document.addEventListener('mouseup', stopDrag);
chatHeader.addEventListener('touchstart', startDrag, { passive: true });
document.addEventListener('touchmove', onDrag, { passive: false });
document.addEventListener('touchend', stopDrag);

// ============================================================
// TIME UPDATES
// ============================================================
console.log('⏰ Time updater ready');
function updateTimes() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', { hour12: true, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    if (footerTime) footerTime.textContent = timeStr;
    if (headerTime) headerTime.textContent = timeStr;
}
setInterval(updateTimes, 1000);
updateTimes();

// ============================================================
// ACTIVITY LOG
// ============================================================
console.log('📜 Activity log ready');
function addActivity(text, icon = '💬') {
    if (!historyList) return;
    const item = document.createElement('div');
    item.className = 'history-item';
    const now = new Date();
    const time = now.toLocaleTimeString('en-US', { hour12: true, hour: '2-digit', minute: '2-digit' });
    item.innerHTML = `<span class="history-time">${time}</span><span class="history-text">${icon} ${text}</span>`;
    historyList.prepend(item);
    if (historyList.children.length > 30) {
        historyList.removeChild(historyList.lastChild);
    }
}

// ============================================================
// HISTORY TOGGLE
// ============================================================
console.log('📜 History toggle ready');
historyBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    chatHistory.classList.toggle('open');
    console.log(`📜 History: ${chatHistory.classList.contains('open') ? 'open' : 'closed'}`);
    historyBtn.style.color = chatHistory.classList.contains('open') ? 'var(--primary-light)' : '';
});

// ============================================================
// PARTICLES SYSTEM
// ============================================================
console.log('✨ Initializing Particles System...');
class ParticleSystem {
    constructor() {
        this.container = document.getElementById('particles-js');
        if (!this.container) {
            console.warn('⚠️ particles-js not found');
            return;
        }
        this.particles = [];
        this.init();
        console.log('✅ Particles System ready');
    }

    init() {
        const count = 40;
        for (let i = 0; i < count; i++) {
            this.particles.push({
                x: Math.random() * window.innerWidth,
                y: Math.random() * window.innerHeight,
                size: Math.random() * 1.5 + 0.5,
                speedX: (Math.random() - 0.5) * 0.2,
                speedY: (Math.random() - 0.5) * 0.2,
                opacity: Math.random() * 0.2 + 0.05,
                color: ['#a855f7', '#ec4899', '#c084fc', '#22d3ee'][Math.floor(Math.random() * 4)]
            });
        }
        this.animate();
    }

    animate() {
        const container = this.container;
        if (!container) return;
        const rect = container.getBoundingClientRect();
        let html = '';
        this.particles.forEach(p => {
            p.x += p.speedX;
            p.y += p.speedY;
            if (p.x < 0) p.x = rect.width;
            if (p.x > rect.width) p.x = 0;
            if (p.y < 0) p.y = rect.height;
            if (p.y > rect.height) p.y = 0;
            html += `<div style="position:absolute;left:${p.x}px;top:${p.y}px;width:${p.size}px;height:${p.size}px;background:${p.color};border-radius:50%;opacity:${p.opacity};pointer-events:none;box-shadow:0 0 4px ${p.color}20;"></div>`;
        });
        container.innerHTML = html;
        requestAnimationFrame(() => this.animate());
    }
}

new ParticleSystem();

// ============================================================
// CHAT FUNCTIONS
// ============================================================
console.log('💬 Chat functions ready');
function addMessage(text, sender = 'user') {
    console.log(`💬 ${sender === 'arya' ? 'ARYA' : 'User'}: "${text.substring(0, 50)}${text.length > 50 ? '...' : ''}"`);
    const div = document.createElement('div');
    div.className = `msg ${sender}`;
    const avatar = sender === 'arya' ? '💖' : '👤';
    const author = sender === 'arya' ? 'ARYA' : 'You';
    const time = new Date().toLocaleTimeString('en-US', { hour12: true, hour: '2-digit', minute: '2-digit' });
    div.innerHTML = `
        <div class="msg-avatar">${avatar}</div>
        <div class="msg-bubble">
            <div class="msg-meta"><span class="msg-author">${author}</span><span class="msg-time">${time}</span></div>
            <div class="msg-text">${text}</div>
        </div>
    `;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

function showTyping(show) {
    console.log(`⌨️ Typing: ${show ? 'started' : 'stopped'}`);
    typingIndicator.style.display = show ? 'flex' : 'none';
    messages.scrollTop = messages.scrollHeight;
}

// ============================================================
// SEND MESSAGE
// ============================================================
console.log('📤 Send message ready');
async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) {
        console.log('📤 Empty message - ignored');
        return;
    }
    console.log(`📤 Sending: "${text}"`);
    userInput.value = '';

    addMessage(text, 'user');
    addActivity(`You: ${text.substring(0, 30)}${text.length > 30 ? '...' : ''}`, '👤');
    showTyping(true);

    const rect = sendBtn.getBoundingClientRect();
    sparkle.burst(rect.left + rect.width/2, rect.top + rect.height/2, 20);

    try {
        console.log('📡 Fetching /chat endpoint...');
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        const data = await response.json();
        console.log('📡 Response received:', data);

        showTyping(false);
        const reply = data.reply || 'Sorry, I didn\'t get that.';
        console.log(`💬 ARYA replied: "${reply.substring(0, 50)}${reply.length > 50 ? '...' : ''}"`);
        addMessage(reply, 'arya');
        addActivity(`ARYA: ${reply.substring(0, 30)}${reply.length > 30 ? '...' : ''}`, '💖');

        setTimeout(() => {
            const lastMsg = messages.lastElementChild;
            if (lastMsg) {
                const rect2 = lastMsg.getBoundingClientRect();
                sparkle.burst(rect2.left + rect2.width/2, rect2.top + rect2.height/2, 15);
            }
        }, 300);

    } catch (error) {
        console.error('❌ Error in sendMessage:', error);
        showTyping(false);
        addMessage('Oops! I\'m having trouble connecting. 😅', 'arya');
        addActivity('Error: Connection failed', '⚠️');
    }
}

// ============================================================
// EVENT LISTENERS
// ============================================================
console.log('🎯 Setting up event listeners...');
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        console.log('⌨️ Enter key pressed');
        sendMessage();
    }
});

sendBtn.addEventListener('click', () => {
    console.log('🖱️ Send button clicked');
    sendMessage();
});

// ============================================================
// EMOJI PICKER
// ============================================================
console.log('😊 Emoji picker ready');
emojiBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    emojiPicker.classList.toggle('show');
    console.log(`😊 Emoji picker: ${emojiPicker.classList.contains('show') ? 'open' : 'closed'}`);
});

document.querySelectorAll('.emoji-grid span').forEach(emoji => {
    emoji.addEventListener('click', () => {
        console.log(`😊 Emoji selected: ${emoji.textContent}`);
        userInput.value += emoji.textContent;
        userInput.focus();
        emojiPicker.classList.remove('show');
    });
});

document.addEventListener('click', () => {
    if (emojiPicker.classList.contains('show')) {
        emojiPicker.classList.remove('show');
        console.log('😊 Emoji picker closed (outside click)');
    }
});

// ============================================================
// CHAT CONTROLS
// ============================================================
console.log('🔄 Chat controls ready');
minimizeBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    chatBox.classList.toggle('minimized');
    const state = chatBox.classList.contains('minimized') ? 'minimized' : 'expanded';
    console.log(`🔄 Chat: ${state}`);
    minimizeBtn.innerHTML = chatBox.classList.contains('minimized') ? '<i class="fas fa-expand"></i>' : '<i class="fas fa-minus"></i>';
    if (chatBox.classList.contains('minimized')) {
        chatToggle.style.display = 'flex';
        addActivity('Chat minimized to side', '🔄');
    } else {
        chatToggle.style.display = 'none';
        chatBox.style.display = 'flex';
        chatBox.classList.remove('hidden');
        addActivity('Chat restored', '💬');
    }
});

chatToggle.addEventListener('click', () => {
    console.log('🔄 Chat restored from side toggle');
    chatBox.classList.remove('minimized');
    chatBox.style.display = 'flex';
    chatBox.classList.remove('hidden');
    minimizeBtn.innerHTML = '<i class="fas fa-minus"></i>';
    chatToggle.style.display = 'none';
    addActivity('Chat restored from side', '💬');
});

chatBox.addEventListener('click', (e) => {
    if (chatBox.classList.contains('minimized')) {
        console.log('🔄 Chat expanded (click on minimized)');
        chatBox.classList.remove('minimized');
        minimizeBtn.innerHTML = '<i class="fas fa-minus"></i>';
        chatToggle.style.display = 'none';
        addActivity('Chat expanded', '💬');
    }
});

toggleBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    if (chatBox.classList.contains('minimized')) {
        console.log('🔄 Chat expanded (toggle button)');
        chatBox.classList.remove('minimized');
        minimizeBtn.innerHTML = '<i class="fas fa-minus"></i>';
        chatToggle.style.display = 'none';
        addActivity('Chat expanded', '💬');
    } else {
        console.log('🔄 Chat minimized (toggle button)');
        chatBox.classList.add('minimized');
        minimizeBtn.innerHTML = '<i class="fas fa-expand"></i>';
        chatToggle.style.display = 'flex';
        addActivity('Chat minimized', '🔄');
    }
});

// ============================================================
// THEME TOGGLE
// ============================================================
console.log('🌓 Theme toggle ready');
themeToggle.addEventListener('click', () => {
    const current = getCurrentTheme();
    const newTheme = current === 'light' ? 'dark' : 'light';
    console.log(`🌓 Manual theme switch: ${current} → ${newTheme}`);
    applyTheme(newTheme);
    showThemeToast(newTheme);
    addActivity(`Theme manually changed to ${newTheme} mode`, '🎨');
});

// ============================================================
// FULLSCREEN TOGGLE
// ============================================================
console.log('🖥️ Fullscreen toggle ready');
fullscreenToggle.addEventListener('click', () => {
    if (!document.fullscreenElement) {
        console.log('🖥️ Entering fullscreen');
        document.documentElement.requestFullscreen();
        fullscreenToggle.innerHTML = '<i class="fas fa-compress"></i>';
        addActivity('Fullscreen mode enabled', '🖥️');
    } else {
        console.log('🖥️ Exiting fullscreen');
        document.exitFullscreen();
        fullscreenToggle.innerHTML = '<i class="fas fa-expand"></i>';
        addActivity('Fullscreen mode disabled', '🖥️');
    }
});

document.addEventListener('fullscreenchange', () => {
    if (!document.fullscreenElement) {
        fullscreenToggle.innerHTML = '<i class="fas fa-expand"></i>';
        console.log('🖥️ Fullscreen exited (event)');
    } else {
        console.log('🖥️ Fullscreen entered (event)');
    }
});

// ============================================================
// VOICE INPUT
// ============================================================
console.log('🎤 Voice input ready');
let recognition = null;
let isListening = false;

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = 'en-IN';
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 3;
    console.log('🎤 Speech Recognition supported');

    recognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        console.log(`🎤 Voice transcript: "${transcript}"`);
        userInput.value = transcript;
        if (event.results[0].isFinal) {
            addActivity(`Voice input: "${transcript}"`, '🎤');
            sendMessage();
        }
    };

    recognition.onstart = () => {
        console.log('🎤 Listening started');
    };

    recognition.onend = () => {
        isListening = false;
        micBtn.classList.remove('listening');
        micBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        console.log('🎤 Listening ended');
    };

    recognition.onerror = (event) => {
        console.error('🎤 Speech error:', event.error);
        isListening = false;
        micBtn.classList.remove('listening');
        micBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        if (event.error !== 'no-speech') {
            addMessage('I couldn\'t hear you, dear. Try again? 🎤', 'arya');
            addActivity('Voice recognition error', '❌');
        }
    };
} else {
    console.warn('🎤 Speech Recognition NOT supported in this browser');
}

micBtn.addEventListener('click', () => {
    if (!recognition) {
        console.warn('🎤 Speech recognition not available');
        addMessage('Voice input is not supported in this browser, dear. 😅', 'arya');
        return;
    }
    if (isListening) {
        console.log('🎤 Stopping listening...');
        recognition.stop();
        return;
    }
    try {
        console.log('🎤 Starting listening...');
        recognition.start();
        isListening = true;
        micBtn.classList.add('listening');
        micBtn.innerHTML = '<i class="fas fa-stop"></i>';
        addActivity('Listening...', '🎤');
    } catch (e) {
        console.error('🎤 Error starting recognition:', e);
    }
});

// ============================================================
// SYSTEM STATUS WITH REAL BATTERY & RAM + ALL LOGS
// ============================================================
console.log('📊 System Status updater ready');

// Mood data
const moods = [
    { emoji: '😊', text: 'Happy', color: '#22d3ee' },
    { emoji: '😢', text: 'Sad', color: '#3b82f6' },
    { emoji: '😡', text: 'Angry', color: '#f43f5e' },
    { emoji: '🤩', text: 'Excited', color: '#f59e0b' },
    { emoji: '😌', text: 'Calm', color: '#10b981' },
    { emoji: '🥰', text: 'Loved', color: '#ec4899' },
    { emoji: '😎', text: 'Cool', color: '#8b5cf6' },
    { emoji: '🤔', text: 'Confused', color: '#f97316' },
];

let currentMoodIndex = 0;
let moodInterval = null;

function updateMood() {
    const randomIndex = Math.floor(Math.random() * moods.length);
    const mood = moods[randomIndex];
    console.log(`😊 Mood updated: ${mood.emoji} ${mood.text}`);
    const emojiEl = document.getElementById('moodEmoji');
    const textEl = document.getElementById('moodText');
    const fillEl = document.getElementById('moodFill');
    if (emojiEl) emojiEl.textContent = mood.emoji;
    if (textEl) textEl.textContent = mood.text;
    if (fillEl) {
        const width = 30 + Math.random() * 65;
        fillEl.style.width = width + '%';
        fillEl.style.background = `linear-gradient(90deg, ${mood.color}, ${mood.color}cc)`;
        console.log(`😊 Mood bar: ${width}%`);
    }
}

function startMoodRotation() {
    if (moodInterval) clearInterval(moodInterval);
    updateMood();
    const interval = 6000 + Math.random() * 4000;
    console.log(`😊 Mood will update every ${Math.round(interval/1000)} seconds`);
    moodInterval = setInterval(updateMood, interval);
}

startMoodRotation();

// ----- REAL STATS HELPERS -----

async function getBatteryLevel() {
    try {
        if (navigator.getBattery) {
            const battery = await navigator.getBattery();
            const level = Math.round(battery.level * 100);
            console.log(`🔋 Battery: ${level}% ${battery.charging ? '(charging)' : '(not charging)'}`);
            return { level, charging: battery.charging };
        }
    } catch (e) {
        console.warn('⚠️ Battery API not available', e);
    }
    return null;
}

function getMemoryUsage() {
    if (window.performance && window.performance.memory) {
        const mem = window.performance.memory;
        const used = mem.usedJSHeapSize / (1024 * 1024);
        const limit = mem.jsHeapSizeLimit / (1024 * 1024);
        const percent = Math.round((used / limit) * 100);
        console.log(`🧠 RAM: ${percent}% (${Math.round(used)}MB / ${Math.round(limit)}MB)`);
        return { usedMB: Math.round(used), totalMB: Math.round(limit), percent: Math.min(100, percent) };
    }
    console.warn('⚠️ performance.memory not available (not Chrome)');
    return null;
}

function simulateStats() {
    const stats = {
        battery: 50 + Math.random() * 45,
        ram: 20 + Math.random() * 60,
        cpu: 10 + Math.random() * 70,
        gpu: 5 + Math.random() * 35,
        storage: 30 + Math.random() * 50,
        network: Math.random() > 0.2 ? 'Good' : 'Poor',
        networkVal: Math.random() > 0.2 ? 70 + Math.random() * 25 : 20 + Math.random() * 30,
        temp: 35 + Math.random() * 25
    };
    console.log(`📊 Simulated stats: Battery=${Math.round(stats.battery)}%, RAM=${Math.round(stats.ram)}%, CPU=${Math.round(stats.cpu)}%, GPU=${Math.round(stats.gpu)}%`);
    return stats;
}

// Update function
async function updateStatus() {
    console.log('🔄 Updating system status...');
    try {
        let data = null;
        try {
            console.log('📡 Fetching /system_status...');
            const response = await fetch('/system_status');
            if (response.ok) {
                data = await response.json();
                console.log('📡 Backend data received:', data);
            } else {
                console.warn('⚠️ Backend returned status:', response.status);
            }
        } catch (e) {
            console.warn('⚠️ Backend not available:', e.message);
        }

        // Get real battery
        const batteryInfo = await getBatteryLevel();
        const realBattery = batteryInfo ? batteryInfo.level : null;

        // Get real memory
        const memInfo = getMemoryUsage();
        const realRam = memInfo ? memInfo.percent : null;

        // Build final values
        let finalBattery = data?.battery ?? (realBattery !== null ? realBattery : null);
        let finalRam = data?.ram ?? (realRam !== null ? realRam : null);
        let finalCpu = data?.cpu ?? null;
        let finalGpu = data?.gpu ?? null;
        let finalStorage = data?.storage ?? null;
        let finalNetwork = data?.network ?? null;
        let finalNetworkVal = data?.networkVal ?? null;
        let finalTemp = data?.temp ?? null;

        // If still null, simulate
        if (finalBattery === null) { finalBattery = 50 + Math.random() * 45; console.log('📊 Simulated battery'); }
        if (finalRam === null) { finalRam = 20 + Math.random() * 60; console.log('📊 Simulated RAM'); }
        if (finalCpu === null) { finalCpu = 10 + Math.random() * 70; console.log('📊 Simulated CPU'); }
        if (finalGpu === null) { finalGpu = 5 + Math.random() * 35; console.log('📊 Simulated GPU'); }
        if (finalStorage === null) { finalStorage = 30 + Math.random() * 50; console.log('📊 Simulated Storage'); }
        if (finalNetwork === null || finalNetworkVal === null) {
            finalNetwork = Math.random() > 0.2 ? 'Good' : 'Poor';
            finalNetworkVal = finalNetwork === 'Good' ? 70 + Math.random() * 25 : 20 + Math.random() * 30;
            console.log(`📊 Simulated Network: ${finalNetwork}`);
        }
        if (finalTemp === null) { finalTemp = 35 + Math.random() * 25; console.log('📊 Simulated Temp'); }

        // Uptime
        const uptimeSeconds = Math.floor((performance.now() / 1000));
        const uptimeHours = Math.floor(uptimeSeconds / 3600);
        const uptimeMinutes = Math.floor((uptimeSeconds % 3600) / 60);
        const uptimeStr = uptimeHours > 0 ? `${uptimeHours}h ${uptimeMinutes}m` : `${uptimeMinutes}m`;
        console.log(`⏱️ Uptime: ${uptimeStr}`);

        // Online status
        const online = data?.online !== undefined ? data.online : true;
        console.log(`🌐 Online: ${online}`);

        if (online) {
            statusDot.style.background = '#22d3ee';
            statusText.textContent = `ONLINE · ${Math.round(finalBattery)}%`;
            if (chatStatus) {
                chatStatus.textContent = 'Online';
                chatStatus.style.color = '#22d3ee';
            }
        } else {
            statusDot.style.background = '#f43f5e';
            statusText.textContent = 'OFFLINE';
            if (chatStatus) {
                chatStatus.textContent = 'Offline';
                chatStatus.style.color = '#f43f5e';
            }
        }

        // Animate all stats
        console.log(`📊 Final stats: Battery=${Math.round(finalBattery)}%, RAM=${Math.round(finalRam)}%, CPU=${Math.round(finalCpu)}%, GPU=${Math.round(finalGpu)}%, Storage=${Math.round(finalStorage)}%, Temp=${Math.round(finalTemp)}°C`);
        animateMetric('batteryFill', 'batteryValue', finalBattery, '%');
        animateMetric('cpuFill', 'cpuValue', finalCpu, '%');
        animateMetric('ramFill', 'ramValue', finalRam, '%');
        animateMetric('gpuFill', 'gpuValue', finalGpu, '%');
        animateMetric('storageFill', 'storageValue', finalStorage, '%');
        animateMetric('networkFill', 'networkValue', finalNetworkVal, '%', true);
        animateMetric('tempFill', 'tempValue', finalTemp, '°C');

        document.getElementById('networkValue').textContent = finalNetwork;
        document.getElementById('uptimeValue').textContent = uptimeStr;

        const onlineDot = document.querySelector('.pc-online-dot');
        if (onlineDot) {
            onlineDot.style.background = online ? '#22d3ee' : '#f43f5e';
        }

        console.log('✅ Status update complete');

    } catch (error) {
        console.error('❌ Status update error:', error);
        const sim = simulateStats();
        animateMetric('batteryFill', 'batteryValue', sim.battery, '%');
        animateMetric('cpuFill', 'cpuValue', sim.cpu, '%');
        animateMetric('ramFill', 'ramValue', sim.ram, '%');
        animateMetric('gpuFill', 'gpuValue', sim.gpu, '%');
        animateMetric('storageFill', 'storageValue', sim.storage, '%');
        animateMetric('networkFill', 'networkValue', sim.networkVal, '%', true);
        document.getElementById('networkValue').textContent = sim.network;
        document.getElementById('uptimeValue').textContent = '--';
        animateMetric('tempFill', 'tempValue', sim.temp, '°C');
    }
}

function animateMetric(fillId, valueId, value, suffix, isNetwork = false) {
    const fill = document.getElementById(fillId);
    const valueEl = document.getElementById(valueId);
    if (fill && valueEl) {
        const target = Math.min(100, Math.max(0, value));
        fill.style.width = target + '%';
        if (!isNetwork) {
            valueEl.textContent = Math.round(target) + suffix;
        }
    }
}

// Update every 5 seconds
setInterval(updateStatus, 5000);
updateStatus();
console.log('🔄 Status will update every 5 seconds');

// ============================================================
// KEYBOARD SHORTCUTS
// ============================================================
console.log('⌨️ Keyboard shortcuts ready');
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        console.log('⌨️ Ctrl+Enter: Send message');
        e.preventDefault();
        sendMessage();
    }
    if (e.key === 'Escape') {
        console.log('⌨️ Escape: Clear input');
        userInput.value = '';
        userInput.blur();
    }
    if (e.ctrlKey && e.shiftKey && e.key === 'L') {
        console.log('⌨️ Ctrl+Shift+L: Toggle chat minimize');
        e.preventDefault();
        if (chatBox.classList.contains('minimized')) {
            chatBox.classList.remove('minimized');
            minimizeBtn.innerHTML = '<i class="fas fa-minus"></i>';
            chatToggle.style.display = 'none';
            chatBox.style.display = 'flex';
            chatBox.classList.remove('hidden');
            addActivity('Chat restored (shortcut)', '⌨️');
        } else {
            chatBox.classList.add('minimized');
            minimizeBtn.innerHTML = '<i class="fas fa-expand"></i>';
            chatToggle.style.display = 'flex';
            addActivity('Chat minimized (shortcut)', '⌨️');
        }
    }
});

// ============================================================
// WELCOME ANIMATION
// ============================================================
console.log('👋 Welcome animation ready');
setTimeout(() => {
    const welcome = document.querySelector('.msg.arya');
    if (welcome) {
        welcome.style.animation = 'messageIn 0.6s ease';
        console.log('👋 Welcome message animated');
    }
    addActivity('ARYA is online and ready!', '💖');
}, 500);

// ============================================================
// FINAL CONSOLE LOG
// ============================================================
console.log('✅ ========================================');
console.log('✅ ARYA AI - FULLY INITIALIZED');
console.log('✅ All systems ready');
console.log('✅ ========================================');
console.log('📊 To monitor:');
console.log('   - Theme changes → look for 🌓 or 🎨');
console.log('   - Chat messages → look for 💬');
console.log('   - Status updates → look for 📊 or 🔋 or 🧠');
console.log('   - Errors → look for ❌ or ⚠️');
console.log('✅ ========================================');

// One final position update after everything loads
setTimeout(() => {
    updateTogglePositions();
}, 300);
