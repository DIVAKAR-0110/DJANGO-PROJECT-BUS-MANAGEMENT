document.addEventListener("DOMContentLoaded", () => {
  const paymentOptions = document.querySelectorAll('input[name="payment_method"]');
  const sections = {
    card: document.getElementById("card-section"),
    upi: document.getElementById("upi-section"),
    netbanking: document.getElementById("netbanking-section"),
    wallet: document.getElementById("wallet-section"),
    prepaid: document.getElementById("prepaid-section"),
  };

  function showSection(selected) {
    for (let key in sections) {
      sections[key].classList.add("hidden");
    }
    if (sections[selected]) {
      sections[selected].classList.remove("hidden");
    }
  }

  // Handle radio button change
  paymentOptions.forEach(option => {
    option.addEventListener("change", () => {
      showSection(option.value);
    });
  });

  // Show the default selected section on page load
  const selectedOption = document.querySelector('input[name="payment_method"]:checked');
  if (selectedOption) {
    showSection(selectedOption.value);
  }

  // AJAX form submission
  document.getElementById("payment-form").addEventListener("submit", function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    console.log("Selected method:", formData.get("payment_method"));  // Debug in console

    fetch("/process_payment/", {
      method: "POST",
      headers: { "X-CSRFToken": getCookie("csrftoken") },
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      document.getElementById("payment-response").textContent = data.message;
    })
    .catch(err => console.error("Payment error:", err));
  });

  function getCookie(name) {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      const trimmed = cookie.trim();
      if (trimmed.startsWith(name + "=")) return decodeURIComponent(trimmed.split("=")[1]);
    }
    return null;
  }
});
