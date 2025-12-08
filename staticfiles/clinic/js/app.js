// Simple UI helpers for Dental POS
(function(){
  function qs(sel){return document.querySelector(sel)}
  function qsa(sel){return Array.from(document.querySelectorAll(sel))}

  // Sidebar toggle for mobile
  var toggle = qs('#nav-toggle');
  var sidebar = qs('.sidebar');
  if(toggle && sidebar){
    toggle.addEventListener('click', function(){
      sidebar.classList.toggle('open');
    });
  }

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
