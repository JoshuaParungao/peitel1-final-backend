// Simple UI helpers for Dental POS
(function(){
  function qs(sel){return document.querySelector(sel)}
  function qsa(sel){return Array.from(document.querySelectorAll(sel))}

  // Sidebar toggle for mobile
  var toggle = qs('#nav-toggle');
  var sidebar = qs('.sidebar');
  var backdrop = qs('.sidebar-backdrop');
  if(toggle && sidebar){
    toggle.addEventListener('click', function(){
      var isOpen = sidebar.classList.toggle('open');
      // ensure backdrop exists
      if(!backdrop){
        backdrop = document.createElement('div');
        backdrop.className = 'sidebar-backdrop';
        sidebar.parentNode.insertBefore(backdrop, sidebar.nextSibling);
      }
      if(isOpen){ backdrop.classList.add('visible'); toggle.setAttribute('aria-expanded','true'); }
      else { backdrop.classList.remove('visible'); toggle.setAttribute('aria-expanded','false'); }
    });
  }

  // Close sidebar when clicking backdrop
  if(backdrop){
    backdrop.addEventListener('click', function(){ sidebar.classList.remove('open'); backdrop.classList.remove('visible'); toggle && toggle.setAttribute('aria-expanded','false'); });
  }

  // Close sidebar when clicking a nav link (mobile)
  qsa('.sidebar-nav a').forEach(function(a){ a.addEventListener('click', function(){ if(sidebar.classList.contains('open')){ sidebar.classList.remove('open'); if(backdrop) backdrop.classList.remove('visible'); toggle && toggle.setAttribute('aria-expanded','false'); } }); });

  // Simple client-side form validation highlight
  qsa('form').forEach(function(form){
    form.addEventListener('submit', function(e){
      var invalid = false;
      qsa('input,select,textarea', form).forEach(function(el){
        el.classList.remove('invalid');
        if (el.hasAttribute('required') && !el.value) {
          el.classList.add('invalid'); invalid = true;
        }
      });
      if (invalid){
        e.preventDefault();
        var el = document.querySelector('.invalid'); if(el) el.focus();
      }
    });
  });
})();
