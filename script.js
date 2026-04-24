/* ============================================================
   VSMS — Client-side Interactions
   ============================================================ */

// ── Modal ──────────────────────────────────────────────────
function openModal(id) {
  document.getElementById(id).classList.add('open');
  document.getElementById('modal-overlay').classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  document.querySelectorAll('.modal.open').forEach(m => m.classList.remove('open'));
  document.getElementById('modal-overlay').classList.remove('open');
  document.body.style.overflow = '';
}

// Close on Escape
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeModal();
});

// ── Flash auto-dismiss ─────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(f => {
    setTimeout(() => {
      f.style.transition = 'opacity 0.4s, transform 0.4s';
      f.style.opacity    = '0';
      f.style.transform  = 'translateY(-4px)';
      setTimeout(() => f.remove(), 400);
    }, 4000);
  });
});
