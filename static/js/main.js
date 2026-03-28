/* EPS Sura — main.js v3
   Navigation guard: libre dentro del dashboard,
   bloquea solo cuando intentas salir del sistema.
*/

/* ---- DATE ---- */
const topDate = document.getElementById('topDate');
if (topDate) {
  const now = new Date();
  topDate.textContent = now.toLocaleDateString('es-CO', {
    weekday: 'long', day: 'numeric', month: 'long'
  });
}

/* ---- AUTO-HIDE FLASH ---- */
document.querySelectorAll('.flash').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity .4s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 400);
  }, 4500);
});

/* ---- SMOOTH SCROLL ---- */
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const t = document.querySelector(a.getAttribute('href'));
    if (t) { e.preventDefault(); t.scrollIntoView({ behavior: 'smooth' }); }
  });
});

/* ---- NAVBAR SCROLL ---- */
const navbar = document.querySelector('.navbar');
if (navbar) {
  window.addEventListener('scroll', () => {
    navbar.style.boxShadow = window.scrollY > 10
      ? '0 4px 20px rgba(0,0,0,.08)' : 'none';
  });
}

/* ============================================================
   MODAL SYSTEM
============================================================ */
function openModal(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeModal(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.remove('open');
  document.body.style.overflow = '';
}

// Close on overlay click
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) {
    closeModal(e.target.id);
  }
});

// Close on Escape
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.open, .nav-guard-overlay.open')
      .forEach(m => {
        m.classList.remove('open');
        document.body.style.overflow = '';
      });
  }
});

/* ============================================================
   CONFIRM MODAL — reemplaza browser confirm()
============================================================ */
function showConfirm({ title, desc, icon = 'danger', onConfirm }) {
  let overlay = document.getElementById('suraConfirmOverlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'suraConfirmOverlay';
    overlay.className = 'modal-overlay';
    overlay.innerHTML = `
      <div class="modal confirm-modal">
        <div class="modal-body" style="padding:28px 24px 20px;text-align:center">
          <div id="sConfirmIcon" style="width:56px;height:56px;border-radius:16px;display:flex;align-items:center;justify-content:center;margin:0 auto 16px">
          </div>
          <div id="sConfirmTitle" style="font-size:1.05rem;font-weight:700;margin-bottom:8px;letter-spacing:-.2px"></div>
          <div id="sConfirmDesc" style="font-size:.88rem;color:var(--text-secondary);line-height:1.6"></div>
        </div>
        <div class="modal-footer" style="justify-content:center;gap:10px;padding:0 24px 24px">
          <button onclick="closeModal('suraConfirmOverlay')" class="btn-secondary" style="min-width:110px">Cancelar</button>
          <button id="sConfirmOk" style="min-width:110px"></button>
        </div>
      </div>`;
    document.body.appendChild(overlay);
    overlay.addEventListener('click', e => {
      if (e.target === overlay) closeModal('suraConfirmOverlay');
    });
  }

  const iconEl = document.getElementById('sConfirmIcon');
  const okBtn  = document.getElementById('sConfirmOk');

  document.getElementById('sConfirmTitle').textContent = title || '¿Confirmar acción?';
  document.getElementById('sConfirmDesc').textContent  = desc  || 'Esta acción no se puede deshacer.';

  if (icon === 'danger') {
    iconEl.style.background = 'rgba(255,59,48,.1)';
    iconEl.innerHTML = `<svg width="26" height="26" fill="none" viewBox="0 0 24 24" stroke="#FF3B30" stroke-width="2.2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"/></svg>`;
    okBtn.className = 'btn-danger';
    okBtn.style.minWidth = '110px';
    okBtn.innerHTML = 'Confirmar';
  } else {
    iconEl.style.background = 'rgba(255,159,10,.1)';
    iconEl.innerHTML = `<svg width="26" height="26" fill="none" viewBox="0 0 24 24" stroke="#FF9F0A" stroke-width="2.2"><path stroke-linecap="round" stroke-linejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z"/></svg>`;
    okBtn.className = 'btn-primary';
    okBtn.style.minWidth = '110px';
    okBtn.innerHTML = 'Confirmar';
  }

  okBtn.onclick = () => {
    closeModal('suraConfirmOverlay');
    onConfirm && onConfirm();
  };
  openModal('suraConfirmOverlay');
}

/* ============================================================
   ATENDER MODAL (Doctor)
============================================================ */
function openAtenderModal(citaId, pacienteNombre) {
  let overlay = document.getElementById('atenderOverlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'atenderOverlay';
    overlay.className = 'modal-overlay';
    overlay.innerHTML = `
      <div class="modal" style="max-width:440px">
        <div class="modal-header">
          <span class="modal-title" id="atenderTitle">Marcar como atendido</span>
          <button class="modal-close" onclick="closeModal('atenderOverlay')">×</button>
        </div>
        <form id="atenderForm" method="POST">
          <div class="modal-body">
            <div style="display:flex;align-items:center;gap:10px;background:rgba(48,209,88,.08);border:1px solid rgba(48,209,88,.2);border-radius:12px;padding:12px 14px;margin-bottom:18px">
              <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="#30D158" stroke-width="2.2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
              <span style="font-size:.86rem;color:#1a7a38;font-weight:600">La cita quedará marcada como Atendida</span>
            </div>
            <div class="form-group">
              <label>Notas de la consulta (opcional)</label>
              <textarea name="notas" rows="3" placeholder="Diagnóstico, indicaciones, observaciones..."></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" onclick="closeModal('atenderOverlay')" class="btn-secondary">Cancelar</button>
            <button type="submit" class="btn-success" style="padding:9px 20px;font-size:.87rem">
              <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/></svg>
              Confirmar atendido
            </button>
          </div>
        </form>
      </div>`;
    document.body.appendChild(overlay);
    overlay.addEventListener('click', e => {
      if (e.target === overlay) closeModal('atenderOverlay');
    });
  }
  document.getElementById('atenderTitle').textContent = `Atendido — ${pacienteNombre}`;
  document.getElementById('atenderForm').action = `/doctor/marcar-atendido/${citaId}`;
  openModal('atenderOverlay');
}

/* Navigation guard removed */

/* ============================================================
   LOGOUT — usa replace() para limpiar historial del navegador
   El botón Atrás no puede volver a páginas privadas
============================================================ */
function doLogout() {
  // Primero hace la petición al servidor para limpiar la sesión
  fetch('/logout', { method: 'GET', redirect: 'manual' })
    .finally(() => {
      // replace() reemplaza la entrada actual del historial
      // El botón Atrás no puede navegar de vuelta
      window.location.replace('/login');
    });
}

/* ============================================================
   SIDEBAR MÓVIL — hamburguesa
============================================================ */
function openSidebar() {
  document.getElementById('mainSidebar').classList.add('open');
  document.getElementById('sidebarOverlay').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeSidebar() {
  document.getElementById('mainSidebar').classList.remove('open');
  document.getElementById('sidebarOverlay').classList.remove('open');
  document.body.style.overflow = '';
}

// Cerrar sidebar al hacer click en un link (móvil)
document.querySelectorAll('.sidebar .nav-item').forEach(item => {
  item.addEventListener('click', () => {
    if (window.innerWidth <= 900) closeSidebar();
  });
});

// Cerrar sidebar al rotar pantalla
window.addEventListener('resize', () => {
  if (window.innerWidth > 900) closeSidebar();
});
