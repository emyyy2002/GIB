console.log("dashboard.js chargé");

async function loadLatest() {
  try {
    const res = await fetch("/api/");     // ✅ liste triée DESC
    const arr = await res.json();

    const last = arr && arr.length ? arr[0] : null;

    const tempEl = document.getElementById("tempValue");
    const humEl  = document.getElementById("humValue");
    const tempTimeEl = document.getElementById("tempTime");
    const humTimeEl  = document.getElementById("humTime");

    if (!last) {
      tempEl.textContent = "--";
      humEl.textContent  = "--";
      tempTimeEl.textContent = "Aucune mesure pour le moment";
      humTimeEl.textContent  = "Aucune mesure pour le moment";
      return;
    }

    const temp = last.temperature;        // ✅ bons champs
    const hum  = last.humidity;
    const dateStr = last.created_at;

    tempEl.textContent = (typeof temp === "number") ? temp.toFixed(1) : "--";
    humEl.textContent  = (typeof hum  === "number") ? hum.toFixed(1)  : "--";

    if (dateStr) {
      const date = new Date(dateStr);
      if (!isNaN(date.getTime())) {
        const diffSec = Math.round((Date.now() - date.getTime()) / 1000);
        const msg = "il y a : " + diffSec + " secondes (" + date.toLocaleTimeString() + ")";
        tempTimeEl.textContent = msg;
        humTimeEl.textContent  = msg;
      } else {
        tempTimeEl.textContent = "Date invalide";
        humTimeEl.textContent  = "Date invalide";
      }
    } else {
      tempTimeEl.textContent = "Aucune mesure pour le moment";
      humTimeEl.textContent  = "Aucune mesure pour le moment";
    }

  } catch (e) {
    console.error("Erreur API /api/ :", e);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadLatest();
  setInterval(loadLatest, 5000);
});
