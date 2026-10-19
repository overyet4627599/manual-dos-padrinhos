document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("order-form");
  if (form) {
    const total = document.getElementById("order-total");
    const fmt = n => n.toLocaleString("pt-BR", {style:"currency", currency:"BRL"});
    function updateTotal() {
      let sum = 0;
      form.querySelectorAll(".product-select:checked").forEach(box => {
        const qty = form.querySelector(`[name="qty_${box.value}"]`);
        sum += Number(box.dataset.price || 0) * Math.max(1, Number(qty?.value || 1));
      });
      total.textContent = fmt(sum);
    }
    form.querySelectorAll(".product-select, .qty-input").forEach(el => el.addEventListener("change", updateTotal));
    form.querySelectorAll(".product-select").forEach(box => {
      box.addEventListener("change", () => {
        const card = box.closest(".product-card");
        card.classList.toggle("is-selected", box.checked);
        updateTotal();
      });
    });
    form.addEventListener("submit", e => {
      if (!form.querySelector(".product-select:checked")) {
        e.preventDefault();
        alert("Selecione pelo menos um produto antes de enviar o pedido.");
        document.getElementById("catalogo")?.scrollIntoView({behavior:"smooth"});
      }
    });
    updateTotal();
  }
  document.querySelectorAll(".flash").forEach(el => {
    setTimeout(() => { el.classList.add("fade"); }, 5000);
  });
});
