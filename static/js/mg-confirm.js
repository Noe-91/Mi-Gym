/* ===== Confirmaciones globales por data-confirm (forms, links, botones) ===== */
(function(){
  const backdrop = document.getElementById('mgConfirmBackdrop');
  const msgEl    = document.getElementById('mgConfirmMsg');
  const okBtn    = document.getElementById('mgConfirmOk');
  const cancelBt = document.getElementById('mgConfirmCancel');

  let pending = null; // { type:'form'|'link'|'button', form?, href?, action?, okText?, cancelText? }

  function openModal(message, okText, cancelText){
    msgEl.textContent = message || '¿Estás seguro de continuar?';
    okBtn.textContent = okText || 'Sí, continuar';
    cancelBt.textContent = cancelText || 'Cancelar';
    backdrop.style.display = 'flex';
    okBtn.focus();
    document.addEventListener('keydown', onEsc);
  }
  function closeModal(){
    backdrop.style.display = 'none';
    document.removeEventListener('keydown', onEsc);
  }
  function onEsc(e){ if(e.key === 'Escape'){ handle(false); } }

  function handle(confirmed){
    if (!pending) return closeModal();
    if (confirmed){
      if (pending.type === 'form' && pending.form){
        pending.form.dataset.confirmed = 'true';
        pending.form.submit();
      }else if (pending.type === 'link' && pending.href){
        window.location.href = pending.href;
      }else if (pending.type === 'button' && typeof pending.action === 'function'){
        pending.action();
      }
    }
    pending = null;
    closeModal();
  }

  okBtn.addEventListener('click', ()=>handle(true));
  cancelBt.addEventListener('click', ()=>handle(false));
  backdrop.addEventListener('click', (e)=>{ if(e.target === backdrop) handle(false); });

  // Intercepta SUBMIT de formularios con data-confirm
  document.addEventListener('submit', function(e){
    const form = e.target;
    if (!(form instanceof HTMLFormElement)) return;
    if (form.dataset.confirmed === 'true') return;
    const msg = form.getAttribute('data-confirm');
    if (!msg) return;

    e.preventDefault();
    pending = {
      type: 'form',
      form,
      okText: form.getAttribute('data-confirm-ok'),
      cancelText: form.getAttribute('data-confirm-cancel')
    };
    openModal(msg, pending.okText, pending.cancelText);
  }, true);

  // Intercepta CLICK en elementos con data-confirm (links/botones no-submit)
  document.addEventListener('click', function(e){
    const el = e.target.closest('[data-confirm]');
    if (!el) return;

    const isLink   = el.tagName === 'A' && el.hasAttribute('href');
    const isButton = el.tagName === 'BUTTON' || el.getAttribute('role') === 'button';
    if (isButton && (el.type === 'submit' || el.getAttribute('type') === 'submit')) return;

    const msg        = el.getAttribute('data-confirm');
    const okText     = el.getAttribute('data-confirm-ok');
    const cancelText = el.getAttribute('data-confirm-cancel');

    e.preventDefault();
    if (isLink){
      pending = { type:'link', href: el.getAttribute('href'), okText, cancelText };
    }else{
      const actionName = el.getAttribute('data-confirm-action');
      let action = null;
      if (actionName && typeof window[actionName] === 'function') action = window[actionName];
      pending = { type:'button', action, okText, cancelText };
    }
    openModal(msg, okText, cancelText);
  }, true);

  // Helper global: confirmThen('mensaje', ()=>accion(), 'OK','Cancelar')
  window.confirmThen = function(message, action, okText, cancelText){
    pending = { type:'button', action, okText, cancelText };
    openModal(message, okText, cancelText);
  };
})();
